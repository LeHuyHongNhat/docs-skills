#!/usr/bin/env python3
"""post_check.py — readability & platform checker for community posts (English / Vietnamese).

Usage:
    python post_check.py post.md [--platform forum|viblo|devto|medium|reddit|facebook|linkedin|x]
                                 [--title "..."] [--json] [--export post.txt]

What it checks (severity high / medium / low / info):
- platform: Markdown the platform cannot render (Facebook/LinkedIn/X), hard length limits,
  ```chart blocks that need exporting as images                                  (high/medium)
- title: length, ALL-CAPS words, "!!!"/"?!", hype/clickbait words                (high/medium)
- hype & clichés anywhere in the body (VI + EN lists)                             (medium)
- readability: average/max sentence length, long paragraphs, missing headings in
  long Markdown posts, a long or filler opening, undefined acronyms              (medium/low)
- evidence: sentences with figures (%, ×, "lần", pp) in paragraphs with no link,
  citation or test-condition wording nearby                                      (low)
- discussion: last paragraph without a question                                  (info)

Design notes:
- Heuristics, not a grade: every finding names the exact sentence so the writer decides.
  Vietnamese is measured in syllables (space-separated), so thresholds are higher than English.
- Code blocks, chart blocks, inline code and URLs are excluded from prose metrics.
- `--export` writes a platform-safe plain-text version (no Markdown symbols) for
  Facebook/LinkedIn/X; for X it keeps `---` separators between thread posts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

PLATFORMS: dict[str, dict[str, object]] = {
    "forum": {"markdown": True, "limit": None, "words": (600, 1800)},
    "viblo": {"markdown": True, "limit": None, "words": (800, 2500)},
    "devto": {"markdown": True, "limit": None, "words": (800, 2000)},
    "medium": {"markdown": "rich", "limit": None, "words": (800, 2000)},
    "reddit": {"markdown": True, "limit": 40000, "words": (300, 900)},
    "facebook": {"markdown": False, "limit": 63206, "words": (120, 300)},
    "linkedin": {"markdown": False, "limit": 3000, "words": (120, 300)},
    "x": {"markdown": False, "limit": 280, "words": (40, 400)},
}

VI_CHARS_RE = re.compile(r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)

HYPE_EN = ["game-changer", "game changer", "revolutionary", "mind-blowing", "mind blowing", "insane",
           "ultimate guide", "you won't believe", "must-read", "must read", "10x", "skyrocket",
           "unlock the power", "supercharge", "crushing it", "secret sauce"]
HYPE_VI = ["cực kỳ", "cực kì", "vô cùng", "đỉnh cao", "bá đạo", "thần thánh", "bí kíp", "đột phá",
           "không thể bỏ qua", "chắc chắn 100%", "gây bão", "cực phẩm", "xịn sò", "siêu đỉnh", "sốc"]
CLICHE_EN = ["delve", "in today's fast-paced world", "ever-evolving landscape", "it's important to note",
             "it is important to note", "let's dive in", "a testament to", "navigate the complexities",
             "embark on a journey", "in conclusion"]
CLICHE_VI = ["thời đại công nghệ 4.0", "trong thế giới ngày nay", "hãy cùng khám phá", "hãy cùng tìm hiểu",
             "đóng vai trò vô cùng quan trọng", "có thể nói rằng", "nhìn chung thì", "tóm lại là"]
FILLER_OPEN = re.compile(
    r"^\s*(hello everyone|hi everyone|hey everyone|in this (post|article)|today i (want|would like) to|"
    r"xin chào (mọi người|các bạn|cả nhà)|chào (mọi người|các bạn|cả nhà)|hôm nay mình (xin |muốn )?(chia sẻ|giới thiệu)|"
    r"chắc hẳn ai cũng)", re.I)
COMMON_ACRONYMS = {"AI", "API", "APIs", "URL", "PDF", "CEO", "CTO", "USD", "VND", "OK", "FAQ", "HTML", "CSS", "SQL",
                   "JSON", "UI", "UX", "ID", "IT", "PR", "QA", "CPU", "GPU", "RAM", "OS", "PC", "TV", "VN", "US",
                   "UK", "EU", "HR", "KPI", "CV", "TL", "DR", "TLDR", "AM", "PM", "IOS", "GB", "MB", "KB", "TB",
                   "HTTP", "HTTPS", "CLI", "SDK", "IDE", "LLM", "LLMs", "NOTE", "TODO", "FYI", "NB", "VS", "ML"}
EVIDENCE_HINT = re.compile(
    r"https?://|\]\(|\[\d+\]|\bsource\b|\baccording to\b|\bin (our|my) (test|experiment|benchmark)|"
    r"\bwe measured\b|\bthe paper\b|\breports?\b|nguồn|theo |thử nghiệm|đo được|đo trên|mình đo|số liệu từ|paper", re.I)
FIGURE_RE = re.compile(r"\d+(?:[.,]\d+)?\s?(?:%|pp\b|×|x\b|lần\b|điểm phần trăm|percentage points)", re.I)


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    excerpt: str = ""


# ----------------------------------------------------------------- text helpers
def lang_of(text: str) -> str:
    letters = sum(ch.isalpha() for ch in text) or 1
    return "vi" if len(VI_CHARS_RE.findall(text)) / letters > 0.01 else "en"


def strip_front_matter(md: str) -> tuple[str, dict[str, str]]:
    meta: dict[str, str] = {}
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip().strip("'\"")
        md = md[m.end():]
    return md, meta


def prose_blocks(md: str) -> list[tuple[str, str]]:
    """Split Markdown into (kind, text) blocks: heading | para | list | table | code | chart."""
    blocks: list[tuple[str, str]] = []
    lines = md.splitlines()
    i = 0
    buf: list[str] = []
    kind = ""

    def flush() -> None:
        nonlocal buf, kind
        if buf:
            blocks.append((kind or "para", "\n".join(buf).strip()))
        buf, kind = [], ""

    while i < len(lines):
        line = lines[i]
        fence = re.match(r"^\s*(```|~~~)\s*(\w*)", line)
        if fence:
            flush()
            lang = fence.group(2)
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(fence.group(1)):
                j += 1
            blocks.append(("chart" if lang == "chart" else "code", "\n".join(lines[i + 1:j])))
            i = j + 1
            continue
        if not line.strip():
            flush()
        elif re.match(r"^#{1,6}\s", line):
            flush()
            blocks.append(("heading", line))
        elif re.match(r"^\s*\|", line):
            if kind != "table":
                flush()
                kind = "table"
            buf.append(line)
        elif re.match(r"^\s*([-*+•–]|\d+[.)])\s+", line):
            if kind != "list":
                flush()
                kind = "list"
            buf.append(line)
        else:
            if kind in ("table",):
                flush()
            if kind != "list":
                kind = "para"
            buf.append(line)
        i += 1
    flush()
    return blocks


def clean(text: str) -> str:
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[*_>#]+", " ", text)
    text = re.sub(r"^\s*([-*+•–]|\d+[.)])\s+", "", text, flags=re.M)
    return re.sub(r"[ \t]+", " ", text).strip()


def sentences(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        for s in re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-Ỹ0-9\"“(])", clean(line)):
            if len(s.split()) >= 2:
                out.append(s.strip())
    return out


def n_words(s: str) -> int:
    return len(re.findall(r"[\wÀ-ỹ%]+(?:[-'][\wÀ-ỹ]+)*", s))


def short(s: str, n: int = 90) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


# ----------------------------------------------------------------- checks
def check(md: str, platform: str = "forum", title: str | None = None) -> tuple[list[Finding], dict[str, object]]:
    md_body, meta = strip_front_matter(md)
    if title is None:
        title = meta.get("title")
    blocks = prose_blocks(md_body)
    if title is None:
        h1 = next((t for k, t in blocks if k == "heading" and re.match(r"^#\s", t)), None)
        title = re.sub(r"^#\s+", "", h1).strip() if h1 else None
    prose = "\n".join(t for k, t in blocks if k in ("para", "list", "heading"))
    lang = lang_of(prose)
    vi = lang == "vi"
    f: list[Finding] = []
    cfg = PLATFORMS[platform]

    # --- platform
    if cfg["markdown"] is False:
        rules = [(r"^#{1,6}\s", "heading markers (#)"), (r"\*\*[^*]+\*\*|__[^_]+__", "bold (**…**)"),
                 (r"\[[^\]]+\]\([^)]+\)", "Markdown links [text](url)"), (r"^\s*\|.*\|\s*$", "tables"),
                 (r"^\s*(```|~~~)", "code fences")]
        for pat, what in rules:
            if re.search(pat, md_body, re.M):
                f.append(Finding("high", "PLATFORM-MD", f"{platform} does not render {what}; they will show as raw "
                                 f"symbols. Rewrite as plain text or use --export."))
    elif cfg["markdown"] == "rich" and re.search(r"^\s*\|.*\|\s*$", md_body, re.M):
        f.append(Finding("medium", "PLATFORM-MD", f"{platform} editors have no Markdown tables: use a list or an image."))
    if any(k == "chart" for k, _ in blocks):
        f.append(Finding("medium", "CHART-EXPORT", "```chart blocks are not rendered by community platforms: export "
                         "them with `render_doc.py <post.md> --to charts` and attach/insert the PNGs."))
    limit = cfg["limit"]
    if platform == "x":
        for idx, part in enumerate(re.split(r"^\s*---\s*$", md_body, flags=re.M), 1):
            n = len(part.strip())
            if n > 280:
                f.append(Finding("high", "LENGTH", f"Thread post {idx} has {n} characters (> 280).", short(part)))
    elif limit and len(md_body) > int(limit):  # type: ignore[arg-type]
        f.append(Finding("high", "LENGTH", f"{len(md_body)} characters > {platform} limit {limit}."))
    words = n_words(clean(prose))
    lo, hi = cfg["words"]  # type: ignore[misc]
    if words < lo * 0.6 or words > hi * 1.3:
        f.append(Finding("low", "LENGTH-FIT", f"{words} words; typical for {platform}: {lo}–{hi}. "
                         "Fine if intentional (e.g. a series part or a quick question)."))

    # --- title
    if title:
        tmax = 90 if vi else 70
        if len(title) > tmax:
            f.append(Finding("medium", "TITLE-LEN", f"Title has {len(title)} characters (> {tmax}).", title))
        caps = [w for w in re.findall(r"\b[A-ZÀ-Ỹ]{4,}\b", title) if w not in COMMON_ACRONYMS]
        if caps:
            f.append(Finding("medium", "TITLE-CAPS", f"ALL-CAPS words in title: {', '.join(caps)}.", title))
        if re.search(r"!{2,}|\?!|!\?", title):
            f.append(Finding("medium", "TITLE-PUNCT", "Title uses !!! / ?! — reads as clickbait.", title))
        for w in HYPE_EN + HYPE_VI:
            if re.search(rf"(?<![\w]){re.escape(w)}(?![\w])", title, re.I):
                f.append(Finding("high", "TITLE-HYPE", f"Hype/clickbait word in title: “{w}”.", title))

    # --- hype & clichés in body
    body_txt = clean("\n".join(t for k, t in blocks if k in ("para", "list") or (k == "heading" and not t.startswith("# "))))
    for words_list, code in ((HYPE_EN + HYPE_VI, "HYPE"), (CLICHE_EN + CLICHE_VI, "CLICHE")):
        for w in words_list:
            for m in re.finditer(rf"(?<![\w]){re.escape(w)}(?![\w])", body_txt, re.I):
                ctx = body_txt[max(0, m.start() - 40): m.end() + 40]
                msg = ("Hype word — replace with the specific fact/number." if code == "HYPE"
                       else "Cliché that makes the post sound generic — cut it or say the concrete thing.")
                f.append(Finding("medium", code, f"“{w}”: {msg}", short(ctx)))
                break

    # --- readability
    paras = [t for k, t in blocks if k == "para"]
    all_sents = [s for k, t in blocks if k in ("para", "list") for s in sentences(t)]
    lens = [n_words(s) for s in all_sents]
    avg = sum(lens) / len(lens) if lens else 0.0
    avg_max, sent_max, para_max = (28, 45, 110) if vi else (20, 35, 80)
    if avg > avg_max:
        f.append(Finding("medium", "SENT-AVG", f"Average sentence length {avg:.1f} {'syllables' if vi else 'words'} "
                         f"(target ≤ {avg_max}). Split long sentences."))
    for s, n in zip(all_sents, lens):
        if n > sent_max:
            f.append(Finding("medium", "SENT-LONG", f"Sentence of {n} {'syllables' if vi else 'words'} (> {sent_max}).",
                             short(s)))
    for p in paras:
        ns, nw = len(sentences(p)), n_words(clean(p))
        if ns > 4 or nw > para_max:
            f.append(Finding("low", "PARA-LONG", f"Paragraph with {ns} sentences / {nw} words — split it.", short(p)))
    if cfg["markdown"] is True and words > 600 and not any(k == "heading" and t.startswith("## ") for k, t in blocks):
        f.append(Finding("medium", "NO-HEADINGS", f"{words} words without any ## heading: readers cannot skim."))
    first = next((t for k, t in blocks if k == "para"), "")
    if first:
        if n_words(clean(first)) > 60:
            f.append(Finding("medium", "HOOK-LONG", "Opening paragraph > 60 words: the hook should fit in 2 lines.",
                             short(first)))
        if FILLER_OPEN.search(clean(first)):
            f.append(Finding("medium", "HOOK-FILLER", "Opening starts with a greeting/announcement — lead with the "
                             "result, the problem or the question.", short(first)))

    # --- acronyms
    seen: set[str] = set()
    for m in re.finditer(r"(?<![\w-])[A-Z][A-Z0-9]{1,5}s?(?![\w-])", body_txt):
        a = m.group(0)
        base = a[:-1] if a.endswith("s") and a[:-1].isupper() else a
        if base in COMMON_ACRONYMS or a in seen or base.isdigit() or re.fullmatch(r"H[1-6]", a):
            continue
        seen.add(a)
        win = body_txt[max(0, m.start() - 80): m.end() + 100]
        defined = (body_txt[m.start() - 1: m.start()] == "(" or f"({base})" in win or f"({a})" in win or re.search(rf"{re.escape(a)}\s*(\(|—|–|:|là\b|stands for|"
                   rf"means|viết tắt)", win))
        if not defined:
            f.append(Finding("medium", "ACRONYM", f"“{a}” is not spelled out or explained at first use.",
                             short(body_txt[max(0, m.start() - 40): m.end() + 40])))

    # --- evidence near figures
    for k, t in blocks:
        if k not in ("para", "list"):
            continue
        if FIGURE_RE.search(t) and not EVIDENCE_HINT.search(t):
            f.append(Finding("low", "UNSOURCED", "Figure with no source, link or test conditions in this "
                             "paragraph — add where it comes from (or confirm it is cited nearby).", short(clean(t))))

    # --- discussion ending
    tail = [t for k, t in blocks if k in ("para", "list")]
    if tail and "?" not in "\n".join(tail[-2:]):
        f.append(Finding("info", "NO-QUESTION", "The post does not end with a question to the community "
                         "(fine for tutorials/announcements)."))

    stats = {"platform": platform, "lang": lang, "words": words, "characters": len(md_body),
             "reading_minutes": round(words / (200 if vi else 230), 1), "sentences": len(lens),
             "avg_sentence_len": round(avg, 1), "max_sentence_len": max(lens) if lens else 0,
             "headings": sum(1 for k, t in blocks if k == "heading"), "title": title}
    return f, stats


# ----------------------------------------------------------------- export
def to_plain(md: str, platform: str) -> str:
    """Markdown → platform-safe plain text (Facebook/LinkedIn/X)."""
    md, _ = strip_front_matter(md)
    out: list[str] = []
    for k, t in prose_blocks(md):
        if k == "heading":
            out.append(re.sub(r"^#{1,6}\s+", "", t).strip())
        elif k == "chart":
            m = re.search(r"^title:\s*(.+)$", t, re.M)
            out.append(f"[{'Ảnh' if lang_of(md) == 'vi' else 'Image'}: {m.group(1).strip() if m else 'chart'}]")
        elif k == "code":
            out.append("\n".join("    " + line for line in t.splitlines()))
        elif k == "table":
            rows = [r for r in t.splitlines() if not re.match(r"^\s*\|[\s:|-]+\|\s*$", r)]
            out.append("\n".join("• " + " – ".join(c.strip() for c in r.strip().strip("|").split("|")) for r in rows[1:]))
        else:
            t = re.sub(r"^\s*[-*+]\s+", "• ", t, flags=re.M)
            out.append(t)
    text = "\n\n".join(out)
    text = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: m.group(1) or m.group(2), text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?!\w)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    if platform != "x":
        text = re.sub(r"^\s*---\s*$", "", text, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


# ----------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("post")
    ap.add_argument("--platform", choices=sorted(PLATFORMS), default="forum")
    ap.add_argument("--title", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--export", default=None, help="write a platform-safe plain-text version to this path")
    a = ap.parse_args(argv)
    md = Path(a.post).read_text(encoding="utf-8")
    findings, stats = check(md, a.platform, a.title)
    if a.export:
        Path(a.export).write_text(to_plain(md, a.platform), encoding="utf-8")
        stats["exported"] = a.export
        if a.platform in ("facebook", "linkedin", "x"):  # re-check the exported text against the platform
            plain_findings, _ = check(to_plain(md, a.platform), a.platform, a.title)
            stats["export_high_findings"] = sum(1 for x in plain_findings if x.severity == "high")
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings.sort(key=lambda x: order[x.severity])
    counts = {s: sum(1 for x in findings if x.severity == s) for s in order}
    if a.json:
        print(json.dumps({"stats": stats, "counts": counts, "findings": [asdict(x) for x in findings]},
                         ensure_ascii=False, indent=2))
        return 0
    print(f"## post_check: {a.post}  [{a.platform}, {stats['lang']}]\n")
    print(f"{stats['words']} words · ~{stats['reading_minutes']} min read · avg sentence {stats['avg_sentence_len']} · "
          f"max {stats['max_sentence_len']} · headings {stats['headings']}")
    print(" · ".join(f"{k}={v}" for k, v in counts.items()) + "\n")
    for x in findings:
        print(f"- [{x.severity}] {x.code}: {x.message}" + (f"\n    > {x.excerpt}" if x.excerpt else ""))
    if not findings:
        print("No findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
