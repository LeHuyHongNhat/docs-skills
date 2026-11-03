#!/usr/bin/env python3
"""lint_doc.py — phát hiện câu chữ mơ hồ / không kiểm chứng được trong tài liệu (VI + EN).

Usage:
    python lint_doc.py <file.md> [--format md|json] [--fail-on high|medium|never]
                       [--terms terms.json] [--disable R04,R07]

Design notes:
- Chỉ dựa trên regex + từ điển, không gọi LLM: chạy được mọi nơi, deterministic, rẻ.
  Cái giá là recall/precision có giới hạn — linter là lưới an toàn, không thay review thủ công.
- Bỏ qua: fenced code block, inline code, chuỗi trong ngoặc kép (thường là UI copy / trích dẫn
  nguyên văn), nội dung trong [CẦN XÁC NHẬN: ...]/[TO CONFIRM: ...], vùng giữa
  <!-- lint-disable --> và <!-- lint-enable -->, và mục "Open Questions"/"Câu hỏi mở".
- Severity phụ thuộc ngữ cảnh: cùng một từ mơ hồ là `high` trong câu requirement
  (có ID hoặc modal bắt buộc) nhưng chỉ `medium` trong văn mô tả.
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

# ID có thể có hậu tố phân cấp: AC-001.1, AC-001.2 là hai ID khác nhau.
ID_RE = re.compile(r"\b(?:BR|FR|NFR|US|AC|UC|DR|REQ|AS|OQ|SR|TC)-\d{1,4}(?:\.\d+)*\b")
# Định nghĩa ID = ID đứng đầu dòng (sau ký tự markdown), không phải tham chiếu giữa câu.
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
    exclude: tuple[str, ...] = ()  # cụm chứa term nhưng không mơ hồ (vd "tốt nghiệp")
    strong: bool = True  # False = từ hay dùng hợp lệ (nhiều, đầy đủ...) → tối đa medium


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


TIME = "Nêu ngưỡng thời gian đo được, vd '≤ 2 giây (p95) ở 100 RPS'."
USAB = "Thay bằng tiêu chí đo được (số bước, task success rate) hoặc bỏ."
RULE = "Nêu quy tắc cụ thể xác định thế nào là 'phù hợp'."
QTY = "Thay bằng con số hoặc danh sách đầy đủ."
APPROX = "Nêu giá trị + dung sai (±) hoặc min/max."
COND = "Nêu điều kiện kích hoạt cụ thể."
METRIC = "Thay bằng chỉ số đo được (uptime %, error rate, throughput...)."
COMPLETE = "Liệt kê chính xác các trường/thông tin."

VAGUE_TERMS: list[Term] = [
    # --- Tiếng Việt ---
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
    """Thay vùng match bằng khoảng trắng để giữ nguyên vị trí cột."""
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def prepare_lines(raw: str) -> list[tuple[int, str, str]]:
    """Trả về (line_no, original, masked) cho các dòng cần lint."""
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
        taken: list[tuple[int, int]] = []  # tránh báo trùng (vd "nhanh" trong "nhanh chóng")

        for m in PLACEHOLDER_RE.finditer(masked):
            add(ln, m.start(), "R01", "high", m.group(0), "Placeholder chưa giải quyết.",
                "Chuyển vào Open Questions (owner + hạn) hoặc điền giá trị.", orig)
        for m in OPEN_LIST_RE.finditer(masked):
            add(ln, m.start(), "R02", "high" if req else "medium", m.group(0),
                "Danh sách mở ('v.v.'/'etc.') — không kiểm thử được phạm vi.",
                "Liệt kê đầy đủ, hoặc chỉ ra nguồn cấu hình của danh sách.", orig)
        for m in AND_OR_RE.finditer(masked):
            add(ln, m.start(), "R03", "high", m.group(0), "'và/hoặc' có hai cách hiểu.",
                "Tách thành hai câu hoặc viết 'ít nhất một trong các ...'.", orig)

        for term, rx in vague_compiled:
            for m in rx.finditer(masked):
                s, e = m.start(), m.end()
                if any(a <= s and e <= b for a, b in taken):
                    continue
                if _excluded(low, s, e, term.exclude):
                    continue
                if COMPARATIVE_RE.match(masked, s):
                    continue  # để R06 xử lý
                taken.append((s, e))
                add(ln, s, "R04", "high" if (req and term.strong) else "medium", m.group(0),
                    f"Từ mơ hồ '{m.group(0)}'" + (" trong câu requirement." if req else "."),
                    term.suggestion, orig)

        if req:
            for m in WEAK_MODAL_RE.finditer(masked):
                add(ln, m.start(), "R05", "medium", m.group(0),
                    "Modal không xác định mức bắt buộc trong câu requirement.",
                    "Dùng phải / không được / nên / được phép (RFC 2119).", orig)

        for m in COMPARATIVE_RE.finditer(masked):
            if not re.search(r"\d", masked):
                add(ln, m.start(), "R06", "medium", m.group(0), "So sánh không có mốc (baseline).",
                    "Nêu giá trị trước/sau, vd 'từ 8 s xuống ≤ 4 s'.", orig)

        for m in PRONOUN_START_RE.finditer(masked):
            add(ln, m.start(1), "R07", "low", m.group(1), "Đại từ đầu câu có thể không rõ chỉ cái gì.",
                "Lặp lại danh từ cụ thể.", orig)

        if req:
            for m in PASSIVE_RE.finditer(masked):
                tail = masked[m.end(): m.end() + 60]
                if not PASSIVE_AGENT_RE.search(tail):
                    add(ln, m.start(), "R08", "low", m.group(0), "Câu bị động thiếu chủ thể thực hiện.",
                        "Nêu rõ actor/service thực hiện hành động.", orig)

    # R09: ID định nghĩa trùng
    # Ngữ cảnh = header của bảng chứa dòng (hoặc "body" ngoài bảng). Cùng một ID xuất hiện đầu
    # dòng trong *hai bảng khác nhau* (bảng định nghĩa + ma trận truy vết) là hợp lệ.
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
    # Bảng ánh xạ/truy vết/changelog liệt kê lại ID cũ là hợp lệ, không phải định nghĩa trùng.
    mapping_hdr = re.compile(r"truy vết|traceab|mapping|ánh xạ|đối chiếu|changelog|thay đổi|v\d+\.\d+|\bcũ\b|\bold\b", re.I)
    for key, lns in defs.items():
        rid, ctx = key.split("@", 1)
        if ctx.startswith("table:") and mapping_hdr.search(ctx):
            continue
        if len(lns) > 1:
            add(lns[1], 0, "R09", "high", rid, f"ID {rid} được định nghĩa {len(lns)} lần (dòng {lns}).",
                "Mỗi requirement một ID duy nhất; không tái sử dụng ID.", "")

    # R10: thuật ngữ không nhất quán
    full = "\n".join(masked for _, _, masked in lines).lower()
    # thuật ngữ ghép cố định không phải là cách gọi actor ("user story", "user journey")
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
                f"Một khái niệm dùng nhiều tên: {used}.",
                "Chọn một thuật ngữ, khai báo trong Glossary, dùng nhất quán.", "")

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
        out.append("Không có finding.")
        return "\n".join(out)
    out += ["| Dòng | Rule | Mức | Match | Vấn đề | Gợi ý |", "|---|---|---|---|---|---|"]
    for f in findings:
        out.append(f"| {f.line} | {f.rule} | {f.severity} | `{f.match}` | {f.message} | {f.suggestion} |")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--fail-on", choices=["high", "medium", "never"], default="never")
    ap.add_argument("--terms", help="JSON: list các nhóm từ đồng nghĩa, vd [[\"user\",\"người dùng\"]]")
    ap.add_argument("--disable", default="", help="Danh sách rule tắt, vd R07,R08")
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
