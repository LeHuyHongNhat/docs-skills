#!/usr/bin/env python3
"""lint_doc.py — flag vague / unverifiable wording in documents (English + Vietnamese).

Usage:
    python lint_doc.py <file.md> [--format md|json] [--fail-on high|medium|never]
                       [--terms terms.json] [--disable R04,R07]

Design notes:
- Regex + dictionaries only, no LLM call: runs anywhere, deterministic, cheap. The price is
  limited recall/precision — the linter is a safety net, not a replacement for human review.
- Skipped: fenced code blocks, inline code, double-quoted strings (usually UI copy or verbatim
  quotes), the contents of [TO CONFIRM: ...] / [CẦN XÁC NHẬN: ...], regions between
  <!-- lint-disable --> and <!-- lint-enable -->, and "Open Questions" / "Câu hỏi mở" sections.
- Severity depends on context: the same vague term is `high` in a requirement sentence
  (has an ID or a mandatory modal) but only `medium` in descriptive prose.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

SEVERITY_ORDER: dict[str, int] = {"high": 3, "medium": 2, "low": 1, "info": 0}

# IDs may carry hierarchical suffixes: AC-001.1 and AC-001.2 are two different IDs.
ID_RE = re.compile(r"\b(?:BR|FR|NFR|US|AC|UC|DR|REQ|AS|OQ|SR|TC)-\d{1,4}(?:\.\d+)*\b")
# An ID *definition* is an ID at the start of a line (after markdown markers), not a mid-sentence reference.
ID_DEF_RE = re.compile(
    r"^\s*(?:[-*+]\s+|#{1,6}\s+|\|\s*)?(?:\*\*|__)?\s*"
    r"((?:BR|FR|NFR|US|AC|UC|DR|REQ|SR|TC)-\d{1,4}(?:\.\d+)*)\b"
)
MANDATORY_MODAL_RE = re.compile(
    r"(?<!\w)(?:phải|không được|bắt buộc|shall|must|must not|shall not)(?!\w)", re.I
)


@dataclass(frozen=True)
class Term:
    pattern: str
    suggestion: str
    exclude: tuple[str, ...] = ()  # phrases containing the term that are not vague (e.g. "tốt nghiệp", "at most")
    strong: bool = True  # False = term often used legitimately ("many", "nhiều", "đầy đủ") → at most medium


@dataclass
class Finding:
    line: int
    col: int
    rule: str
    severity: str
    match: str
    message: str
    suggestion: str
    context: str = field(default="")


def _t(words: Iterable[str], suggestion: str, exclude: tuple[str, ...] = (), strong: bool = True) -> list[Term]:
    return [Term(w, suggestion, exclude, strong) for w in words]


TIME = "State a measurable time threshold, e.g. '≤ 2 s (p95) at 100 RPS'."
USAB = "Replace with a measurable criterion (number of steps, task success rate) or remove."
RULE = "State the concrete rule that defines what 'appropriate' means."
QTY = "Replace with a number or the complete list."
APPROX = "Give the value with a tolerance (±) or min/max."
COND = "State the exact triggering condition."
METRIC = "Replace with a measurable metric (uptime %, error rate, throughput...)."
COMPLETE = "List the exact fields/information."

VAGUE_TERMS: list[Term] = [
    # --- Vietnamese ---
    *_t(["nhanh chóng", "nhanh", "ngay lập tức", "tức thì", "kịp thời", "sớm nhất có thể"], TIME),
    Term("liền", TIME, ("liền mạch", "liền kề", "liên tiếp", "liền nhau")),
    *_t(["dễ dàng", "dễ dùng", "dễ sử dụng", "thân thiện", "trực quan", "đơn giản"], USAB),
    *_t(["hợp lý", "phù hợp", "thích hợp", "tương ứng phù hợp"], RULE),
    *_t(["một số", "vài", "đa số", "phần lớn", "hầu hết"], QTY),
    Term("nhiều", QTY, strong=False, exclude=("một hoặc nhiều", "nhiều nhất", "nhiều hơn", "nhiều-nhiều", "nhiều - nhiều",
                        "một-nhiều", "một - nhiều", "1-nhiều", "1 - nhiều", "1-n", "nhiều-một", "nhiều - một")),
    Term("khoảng", APPROX, ("khoảng thời gian", "khoảng cách", "khoảng trắng", "khoảng giá trị", "khoảng ngày")),
    *_t(["tầm", "xấp xỉ", "chừng"], APPROX, ("tầm nhìn", "tầm quan trọng", "tầm ảnh hưởng")),
    *_t(["nếu cần", "khi cần", "khi cần thiết", "tùy trường hợp", "tuỳ trường hợp", "tùy tình huống", "tuỳ tình huống"], COND),
    *_t(["tối ưu", "hiệu quả", "mạnh mẽ", "linh hoạt", "ổn định", "hiệu năng cao", "mượt mà", "liền mạch"], METRIC),
    Term("tốt", METRIC, ("tốt nghiệp",)),
    *_t(["đầy đủ", "cần thiết", "liên quan"], COMPLETE, ("các bên liên quan", "bên liên quan"), strong=False),
    *_t(["tương tự", "như trên"], "Viết lại đầy đủ hoặc tham chiếu ID cụ thể."),
    # --- English ---
    *_t(["fast", "quick", "quickly", "immediately", "instantly", "timely", "as soon as possible", "asap"], TIME),
    *_t(["easy", "easily", "user-friendly", "user friendly", "intuitive", "simple", "simply"], USAB),
    *_t(["appropriate", "appropriately", "reasonable", "suitable", "adequate", "sufficient", "proper", "properly"], RULE),
    *_t(["some", "several", "many", "most", "various", "numerous", "a few"], QTY,
        ("at most", "many-to-many", "one-to-many", "many-to-one", "most recent", "most recently"), strong=False),
    *_t(["approximately", "roughly", "about", "around"], APPROX,
        ("about us", "information about", "details about", "data about", "questions about", "about the", "around the")),
    *_t(["as needed", "if necessary", "if needed", "as appropriate", "when needed", "when necessary"], COND),
    *_t(["optimal", "optimize", "optimise", "efficient", "efficiently", "robust", "flexible", "seamless",
         "seamlessly", "stable", "scalable", "high-performance", "state-of-the-art", "best-in-class",
         "minimize", "maximize", "minimise", "maximise"], METRIC),
    *_t(["relevant", "necessary"], COMPLETE, ("if necessary", "when necessary"), strong=False),
    *_t(["similar", "same as above", "as above"], "Viết lại đầy đủ hoặc tham chiếu ID cụ thể."),
]

PLACEHOLDER_RE = re.compile(r"(?<!\w)(?:TBD|TBC|TODO|FIXME|XXX)(?!\w)|\?{3,}")
OPEN_LIST_RE = re.compile(r"(?<!\w)(?:v\.v\.?|vv\.|etc\.?|and so on|và các loại khác|và các [^\s,.]+ khác)(?!\w)|,\s*\.\.\.|…", re.I)
AND_OR_RE = re.compile(r"(?<!\w)(?:và\s*/\s*hoặc|and\s*/\s*or)(?!\w)", re.I)
WEAK_MODAL_RE = re.compile(r"(?<!\w)(?:có thể|could|might|would)(?!\w)", re.I)
COMPARATIVE_RE = re.compile(
    r"(?<!\w)(?:nhanh hơn|tốt hơn|cao hơn|thấp hơn|ít hơn|nhiều hơn|lớn hơn|nhỏ hơn|"
    r"faster|better|higher|lower|fewer|greater|smaller|more efficient)(?!\w)", re.I
)
PRONOUN_START_RE = re.compile(
    r"(?:^|[.!?]\s+)(Nó|Điều này|Cái này|Việc này|Chúng|It|This is|This will|This should|That is)(?!\w)"
)
PASSIVE_RE = re.compile(
    r"(?<!không )(?<!\w)(?:được (?!phép)(?:xử lý|lưu|gửi|cập nhật|tạo|xóa|xoá|kiểm tra|xác thực|duyệt|tính|ghi nhận|thông báo|đồng bộ))"
    r"|(?<!\w)(?:is|are|will be|be) (?:processed|stored|sent|updated|created|deleted|validated|approved|calculated|notified|synced)(?!\w)",
    re.I,
)
PASSIVE_AGENT_RE = re.compile(r"(?<!\w)(?:bởi|by)(?!\w)", re.I)

DEFAULT_TERM_GROUPS: list[list[str]] = [
    ["người dùng", "người sử dụng", "user"],
    ["đăng nhập", "log in", "login", "sign in", "sign-in"],
    ["mật khẩu", "password", "pass"],
    ["đơn hàng", "order"],
]

SKIP_SECTION_RE = re.compile(r"^#{1,6}\s*.*(open questions|câu hỏi mở|vấn đề mở)", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s")
CONFIRM_RE = re.compile(r"\[(?:CẦN XÁC NHẬN|TO CONFIRM|CONFIRM)[^\]]*\]", re.I)
QUOTE_RE = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|«[^»\n]*»")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def _mask(text: str, pattern: re.Pattern[str]) -> str:
    """Replace matches with spaces so column positions are preserved."""
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def prepare_lines(raw: str) -> list[tuple[int, str, str]]:
    """Return (line_no, original, masked) for the lines to lint."""
    out: list[tuple[int, str, str]] = []
    in_fence = False
    disabled = False
    skip_level: int | None = None
    for i, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if "<!-- lint-disable -->" in line:
            disabled = True
            continue
        if "<!-- lint-enable -->" in line:
            disabled = False
            continue
        if in_fence or disabled:
            continue
        h = HEADING_RE.match(line)
        if h:
            level = len(h.group(1))
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if SKIP_SECTION_RE.match(line):
                skip_level = level
                continue
        if skip_level is not None:
            continue
        if re.fullmatch(r"\s*\|?[\s:\-|]+\|?\s*", line):  # table separator
            continue
        masked = _mask(line, INLINE_CODE_RE)
        masked = _mask(masked, CONFIRM_RE)
        masked = _mask(masked, QUOTE_RE)
        out.append((i, line, masked))
    return out


def is_requirement_line(line: str) -> bool:
    return bool(ID_RE.search(line) or MANDATORY_MODAL_RE.search(line))


def _excluded(masked_lower: str, start: int, end: int, excludes: tuple[str, ...]) -> bool:
    for ex in excludes:
        for m in re.finditer(re.escape(ex.lower()), masked_lower):
            if m.start() <= start and end <= m.end():
                return True
    return False


def lint_text(
    raw: str,
    term_groups: list[list[str]] | None = None,
    disabled_rules: set[str] | None = None,
) -> list[Finding]:
    disabled_rules = disabled_rules or set()
    groups = DEFAULT_TERM_GROUPS if term_groups is None else term_groups
    findings: list[Finding] = []
    lines = prepare_lines(raw)

    def add(ln: int, col: int, rule: str, sev: str, match: str, msg: str, sugg: str, ctx: str) -> None:
        if rule not in disabled_rules:
            findings.append(Finding(ln, col + 1, rule, sev, match, msg, sugg, ctx.strip()[:160]))

    vague_compiled = [
        (t, re.compile(r"(?<!\w)" + re.escape(t.pattern) + r"(?!\w)", re.I)) for t in VAGUE_TERMS
    ]

    for ln, orig, masked in lines:
        req = is_requirement_line(masked)
        low = masked.lower()
        taken: list[tuple[int, int]] = []  # avoid double-reporting (e.g. "nhanh" inside "nhanh chóng", "quick" inside "quickly")

        for m in PLACEHOLDER_RE.finditer(masked):
            add(ln, m.start(), "R01", "high", m.group(0), "Unresolved placeholder.",
                "Move it to Open Questions (with an owner) or fill in the value.", orig)
        for m in OPEN_LIST_RE.finditer(masked):
            add(ln, m.start(), "R02", "high" if req else "medium", m.group(0),
                "Open-ended list ('etc.'/'v.v.') — the scope cannot be tested.",
                "List every item, or point to the configuration source of the list.", orig)
        for m in AND_OR_RE.finditer(masked):
            add(ln, m.start(), "R03", "high", m.group(0), "'and/or' has two readings.",
                "Split into two sentences, or write 'at least one of ...'.", orig)

        for term, rx in vague_compiled:
            for m in rx.finditer(masked):
                s, e = m.start(), m.end()
                if any(a <= s and e <= b for a, b in taken):
                    continue
                if _excluded(low, s, e, term.exclude):
                    continue
                if COMPARATIVE_RE.match(masked, s):
                    continue  # handled by R06
                taken.append((s, e))
                add(ln, s, "R04", "high" if (req and term.strong) else "medium", m.group(0),
                    f"Vague term '{m.group(0)}'" + (" in a requirement sentence." if req else "."),
                    term.suggestion, orig)

        if req:
            for m in WEAK_MODAL_RE.finditer(masked):
                add(ln, m.start(), "R05", "medium", m.group(0),
                    "Modal does not state the obligation level in a requirement sentence.",
                    "Use MUST / MUST NOT / SHOULD / MAY (RFC 2119) — VI: phải / không được / nên / được phép.", orig)

        for m in COMPARATIVE_RE.finditer(masked):
            if not re.search(r"\d", masked):
                add(ln, m.start(), "R06", "medium", m.group(0), "Comparison without a baseline.",
                    "State before/after values, e.g. 'from 8 s to ≤ 4 s'.", orig)

        for m in PRONOUN_START_RE.finditer(masked):
            add(ln, m.start(1), "R07", "low", m.group(1), "Sentence-initial pronoun may have an unclear referent.",
                "Repeat the specific noun.", orig)

        if req:
            for m in PASSIVE_RE.finditer(masked):
                tail = masked[m.end(): m.end() + 60]
                if not PASSIVE_AGENT_RE.search(tail):
                    add(ln, m.start(), "R08", "low", m.group(0), "Passive sentence without an actor.",
                        "Name the actor/service that performs the action.", orig)

    # R09: duplicate ID definitions
    # Context = header of the table holding the line (or "body" outside tables). The same ID at the
    # start of a line in *two different tables* (definition table + traceability matrix) is fine.
    raw_lines = raw.splitlines()
    ctx_of: dict[int, str] = {}
    cur_ctx = "body"
    for i, line in enumerate(raw_lines, start=1):
        st = line.strip()
        if st.startswith("|"):
            nxt = raw_lines[i] if i < len(raw_lines) else ""
            if re.fullmatch(r"\s*\|?[\s:\-|]+\|?\s*", nxt):
                cur_ctx = "table:" + st
            ctx_of[i] = cur_ctx
        else:
            cur_ctx = "body"
            ctx_of[i] = "body"
    defs: dict[str, list[int]] = defaultdict(list)
    for ln, orig, _ in lines:
        m = ID_DEF_RE.match(orig)
        if m:
            defs[m.group(1) + "@" + ctx_of.get(ln, "body")].append(ln)
    # Mapping/traceability/changelog tables legitimately repeat IDs; they are not duplicate definitions.
    mapping_hdr = re.compile(r"truy vết|traceab|mapping|ánh xạ|đối chiếu|changelog|thay đổi|v\d+\.\d+|\bcũ\b|\bold\b", re.I)
    for key, lns in defs.items():
        rid, ctx = key.split("@", 1)
        if ctx.startswith("table:") and mapping_hdr.search(ctx):
            continue
        if len(lns) > 1:
            add(lns[1], 0, "R09", "high", rid, f"ID {rid} is defined {len(lns)} times (lines {lns}).",
                "One unique ID per requirement; never reuse IDs.", "")

    # R10: inconsistent terminology
    full = "\n".join(masked for _, _, masked in lines).lower()
    # fixed compounds are not names for the actor ("user story", "user journey")
    full = re.sub(r"\buser\s+(?:stor(?:y|ies)|journey|flow|persona)s?\b", " ", full)
    for group in groups:
        counts = {
            t: len(re.findall(r"(?<!\w)" + re.escape(t.lower()) + r"(?!\w)", full)) for t in group
        }
        used = {t: c for t, c in counts.items() if c > 0}
        if len(used) >= 2:
            first_line = next(
                (ln for ln, _, mk in lines if any(re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", mk.lower()) for t in used)),
                0,
            )
            add(first_line, 0, "R10", "medium", " / ".join(used),
                f"One concept, several names: {used}.",
                "Pick one term, define it in the Glossary, use it consistently.", "")

    findings.sort(key=lambda f: (f.line, f.col))
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    c = Counter(f.severity for f in findings)
    return {s: c.get(s, 0) for s in ("high", "medium", "low", "info")}


def render_md(path: str, findings: list[Finding]) -> str:
    s = summarize(findings)
    out = [f"## lint_doc: {path}", "",
           f"high={s['high']} medium={s['medium']} low={s['low']} total={len(findings)}", ""]
    if not findings:
        out.append("No findings.")
        return "\n".join(out)
    out += ["| Line | Rule | Severity | Match | Issue | Suggestion |", "|---|---|---|---|---|---|"]
    for f in findings:
        out.append(f"| {f.line} | {f.rule} | {f.severity} | `{f.match}` | {f.message} | {f.suggestion} |")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--fail-on", choices=["high", "medium", "never"], default="never")
    ap.add_argument("--terms", help="JSON: list of synonym groups, e.g. [[\"user\",\"customer\"]]")
    ap.add_argument("--disable", default="", help="Comma-separated rules to disable, e.g. R07,R08")
    args = ap.parse_args(argv)

    raw = Path(args.file).read_text(encoding="utf-8")
    groups = json.loads(Path(args.terms).read_text(encoding="utf-8")) if args.terms else None
    disabled = {r.strip() for r in args.disable.split(",") if r.strip()}
    findings = lint_text(raw, groups, disabled)

    if args.format == "json":
        print(json.dumps({"file": args.file, "summary": summarize(findings),
                          "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=2))
    else:
        print(render_md(args.file, findings))

    if args.fail_on == "never":
        return 0
    threshold = SEVERITY_ORDER[args.fail_on]
    return 1 if any(SEVERITY_ORDER[f.severity] >= threshold for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
