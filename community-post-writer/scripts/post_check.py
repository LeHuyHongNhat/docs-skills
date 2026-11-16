#!/usr/bin/env python3
"""post_check.py — readability & platform checker for community posts (English / Vietnamese).

Usage:
    python post_check.py post.md [--platform forum|viblo|devto|medium|reddit|facebook|linkedin|x]
                                 [--title "..."] [--rigor] [--json] [--export post.txt]

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
- structure tells of machine-written prose (stronger and longer-lived than word lists):
  "not X but Y" contrasts, staged run-ups, one-line closers, chatbot residue, inflated
  significance → reported on one sighting; dash density, bold-label lists, staccato
  fragments, decorated or echoed headings, overused words → "weak alone", reported as a
  cluster only when two or more kinds co-occur                                    (medium/info)
- headings that carry no information ("Background", "Kết quả")                    (low)
- a number in the title/opening that never reappears in the body                  (medium)
- --rigor (posts that compare, claim causes, summarise a study, show a backtest/benchmark):
  sample size stated, uncertainty near comparative claims, "significant" with a test,
  causal wording vs design, absolute words, limitations, sources, reproducibility, date of
  evidence, backtest caveats (out-of-sample, costs, number of trials), ML eval caveats
  (runs/seeds, baseline). Mechanical proxies for references/research-rigor.md — the
  claims themselves are checked with stats_check.py.                             (medium/low)

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
    r"\bwe measured\b|\bthe paper\b|\breports?\b|nguồn|theo |thử nghiệm|đo được|đo trên|mình đo|số liệu từ|paper|"
    r"\b(table|section|appendix|figure)\s+[\dA-Z]|\b(bảng|mục|phụ lục|hình)\s+[\dA-Z]|§\s?\d|"
    r"khoảng tin cậy|confidence interval|\bCI\b|\bn\s*=\s*\d|\b\d+\s*/\s*\d+\b", re.I)
SOURCES_HEAD_RE = re.compile(r"^#{1,6}\s*(\d+[.)]?\s*)?(sources?|references?|nguồn|tài liệu tham khảo)\b", re.I)
FIGURE_RE = re.compile(r"\d+(?:[.,]\d+)?\s?(?:%|pp\b|×|x\b|lần\b(?!\s*(?:chạy|đo|thử))|điểm phần trăm|percentage points)", re.I)


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
def check(md: str, platform: str = "forum", title: str | None = None,
          rigor: bool = False) -> tuple[list[Finding], dict[str, object]]:
    md_body, meta = strip_front_matter(md)
    if title is None:
        title = meta.get("title")
    blocks = prose_blocks(md_body)
    if title is None:
        h1 = next((t for k, t in blocks if k == "heading" and re.match(r"^#\s", t)), None)
        title = re.sub(r"^#\s+", "", h1).strip() if h1 else None
    prose = "\n".join(t for k, t in blocks if k in ("para", "list", "heading"))
    body_only = "\n".join(t for k, t in blocks if k in ("para", "list"))  # an acronym used in the body is not shouting
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
        caps = [w for w in re.findall(r"\b[A-ZÀ-Ỹ]{4,}\b", title)
                if w not in COMMON_ACRONYMS and not re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", body_only)]
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
        hook_max = 85 if vi else 60
        if n_words(clean(first)) > hook_max:
            f.append(Finding("medium", "HOOK-LONG", f"Opening paragraph > {hook_max} {'syllables' if vi else 'words'}: "
                             "the hook should fit in 2–3 lines.",
                             short(first)))
        if FILLER_OPEN.search(clean(first)):
            f.append(Finding("medium", "HOOK-FILLER", "Opening starts with a greeting/announcement — lead with the "
                             "result, the problem or the question.", short(first)))

    # --- acronyms (not inside the sources/references section; not part of a proper name like "NBER Working Paper")
    src_idx = next((i for i, (k, t) in enumerate(blocks) if k == "heading" and SOURCES_HEAD_RE.search(t)), None)
    has_sources = src_idx is not None
    pre_src = blocks[:src_idx] if has_sources else blocks
    post_src = []
    if has_sources:  # the section ends at the next heading
        end = next((j for j in range(src_idx + 1, len(blocks)) if blocks[j][0] == "heading"), len(blocks))
        post_src = blocks[end:]
    acr_txt = clean("\n".join(t for k, t in pre_src + post_src if k in ("para", "list") or (k == "heading" and not t.startswith("# "))))
    seen: set[str] = set()
    for m in re.finditer(r"(?<![\w-])[A-Z][A-Z0-9]{1,5}s?(?![\w-])", acr_txt):
        if re.match(r"\s[A-Z][a-z]+", acr_txt[m.end(): m.end() + 14]):
            continue
        a = m.group(0)
        base = a[:-1] if a.endswith("s") and a[:-1].isupper() else a
        if base in COMMON_ACRONYMS or a in seen or base.isdigit() or re.fullmatch(r"H[1-6]", a):
            continue
        seen.add(a)
        win = acr_txt[max(0, m.start() - 80): m.end() + 100]
        defined = (acr_txt[m.start() - 1: m.start()] == "(" or f"({base})" in win or f"({a})" in win or re.search(rf"{re.escape(a)}\s*(\(|—|–|:|là\b|stands for|"
                   rf"means|viết tắt)", win))
        if not defined:
            f.append(Finding("medium", "ACRONYM", f"“{a}” is not spelled out or explained at first use.",
                             short(acr_txt[max(0, m.start() - 40): m.end() + 40])))

    # --- evidence near figures
    unsourced = [t for k, t in blocks if k in ("para", "list") and FIGURE_RE.search(t) and not EVIDENCE_HINT.search(t)]
    if unsourced and has_sources:
        f.append(Finding("info", "UNSOURCED", f"{len(unsourced)} paragraph(s) with figures rely on the Sources section: "
                         "check that each number can be located there (section/table)."))
    else:
        for t in unsourced:
            f.append(Finding("low", "UNSOURCED", "Figure with no source, link or test conditions in this "
                             "paragraph — add where it comes from (or confirm it is cited nearby).", short(clean(t))))

    # --- structural tells
    f.extend(tell_checks(blocks, words, vi))

    # --- headings that carry no information
    generic = []
    for k, t in blocks:
        if k == "heading" and not t.startswith("# "):
            h = re.sub(r"^#{1,6}\s+(\d+(?:\.\d+)*[.)]?\s*)?", "", t).strip().strip(":").lower()
            if h in GENERIC_HEADINGS:
                generic.append(h)
    if generic:
        f.append(Finding("low", "HEADING-GENERIC", "Headings that name a slot, not a point: " + ", ".join(generic) +
                         ". Write what the section says (\"Why fixed-size chunks split tables\")."))

    # --- headline numbers must come back in the body
    paras_all = [t for k, t in blocks if k == "para"]
    head_txt = (title or "") + "\n" + (paras_all[0] if paras_all else "")
    first_seen = False
    rest_parts = []
    for k, t in blocks:
        if k == "para" and not first_seen:
            first_seen = True
            continue
        if k != "heading" or not t.startswith("# "):
            rest_parts.append(t)
    rest_txt = "\n".join(rest_parts)
    rest_pcts = {m.replace(",", ".") for m in PCT_RE.findall(rest_txt)}
    rest_nums = {m.replace(",", ".") for m in re.findall(r"(?<![\w.])-?(\d+(?:[.,]\d+)?)(?![\w%])", rest_txt)}
    for num in dict.fromkeys(PCT_RE.findall(head_txt)):
        n_ = num.replace(",", ".")
        if n_ not in rest_pcts and n_ not in rest_nums:
            f.append(Finding("medium", "HEADLINE-NUMBER", f"“{num}%” appears in the title/opening but nowhere in the "
                             "body: show where it comes from, or remove it."))

    # --- discussion ending
    tail = [t for k, t in blocks if k in ("para", "list")]
    if tail and "?" not in "\n".join(tail[-2:]):
        f.append(Finding("info", "NO-QUESTION", "The post does not end with a question to the community "
                         "(fine for tutorials/announcements)."))

    if rigor:
        f.extend(rigor_checks(blocks, title))

    stats = {"platform": platform, "lang": lang, "words": words, "characters": len(md_body),
             "reading_minutes": round(words / (200 if vi else 230), 1), "sentences": len(lens),
             "avg_sentence_len": round(avg, 1), "max_sentence_len": max(lens) if lens else 0,
             "headings": sum(1 for k, t in blocks if k == "heading"), "title": title}
    return f, stats


# ----------------------------------------------------------------- structural tells
# Patterns of prose written "by default" rather than for one reader. Word lists age with every
# model release; these shapes persist. Strong tells are reported on one sighting; weak ones only
# count when several kinds appear together, because a careful human makes any one of them on purpose.
A = r"(?:'|’)"
STRONG_TELLS: list[tuple[str, str, re.Pattern[str]]] = [
    ("CONTRAST", "“not X but Y” used for weight, not for a real contrast — state Y directly",
     re.compile(rf"\bnot (?:just|only|merely|simply) [^.!?\n]{{2,70}}?,? but\b|"
                rf"\b(?:it|this|that){A}?s not (?:about |just )?[^.!?\n]{{2,60}}[.,;—–-]+\s*(?:it|this|that){A}?s\b|"
                rf"\bisn{A}?t (?:just |only |really )?about\b|"
                r"không (?:chỉ|đơn thuần|chỉ đơn giản)(?: là)? [^.!?\n]{2,70}? mà (?:còn|là)|"
                r"không phải(?: là)? [^.!?\n,]{2,60}, mà là", re.I)),
    ("RUN-UP", "staged run-up before the point — start with the point",
     re.compile(rf"\blet{A}?s (?:dive in|break (?:this|it) down|unpack)\b|\bhere{A}?s the thing\b|"
                rf"\bhere{A}?s what you need to know\b|\bwithout further ado\b|\bthe thing is,|\blet{A}?s be honest\b|"
                r"\breal talk\b|hãy cùng (?:đi sâu|bắt đầu|mổ xẻ|điểm qua)|sự thật là|nói thật (?:thì|là)|"
                r"vấn đề (?:là )?ở chỗ|điều (?:thú vị|đáng nói) (?:ở đây )?là", re.I)),
    ("CLOSER", "one-line closer that restates the paragraph — cut it or add a fact",
     re.compile(rf"(?:^|(?<=[.!?…]\s))(?:that{A}?s it\.|that{A}?s all(?: you need)?\.|read that again\.|let that sink in\.|"
                rf"full stop\.|that{A}?s the (?:real )?(?:point|win|difference|lesson)\.|and that matters\.|"
                r"chỉ vậy thôi\.|thế thôi\.|đơn giản vậy thôi\.|hãy đọc lại câu (?:đó|này)\.|và đó (?:mới )?là điều quan trọng\.)",
                re.I | re.M)),
    ("CHATBOT", "chat residue — a post is not a reply to a prompt",
     re.compile(r"\bI hope this (?:helps|was helpful)\b|\b(?:great|good) question\b|\blet me know if\b|\bfeel free to\b|"
                r"hy vọng bài viết(?: này)? (?:hữu ích|giúp ích|mang lại)|chúc (?:các )?bạn thành công|"
                r"đừng ngần ngại (?:để lại|liên hệ|hỏi)", re.I)),
    ("SIGNIFICANCE", "inflated significance — say what happened and how much",
     re.compile(r"\b(?:stands|serves) as a testament\b|\bplays? an? (?:key|crucial|pivotal|vital) role\b|\bpivotal moment\b|"
                r"\bunderscores? (?:the|its) importance\b|\bevolving landscape\b|\bgame of\b(?= [a-z]+, not)|"
                r"đóng vai trò (?:then chốt|cốt lõi|quan trọng|không thể thiếu)|là minh chứng(?: rõ ràng)? cho|"
                r"bước ngoặt(?: lớn| quan trọng)?|không thể phủ nhận", re.I)),
]
AI_WORDS = ["delve", "crucial", "pivotal", "robust", "landscape", "leverage", "seamless", "seamlessly", "foster",
            "showcase", "underscore", "intricate", "tapestry", "realm", "testament", "meticulous", "streamline",
            "empower", "holistic", "vibrant", "elevate"]
GENERIC_HEADINGS = {"background", "introduction", "intro", "overview", "results", "result", "conclusion", "conclusions",
                    "summary", "discussion", "method", "methods", "methodology", "context", "details", "analysis",
                    "bối cảnh", "giới thiệu", "tổng quan", "kết quả", "kết luận", "tóm tắt", "thảo luận", "phương pháp",
                    "mở đầu", "chi tiết", "phân tích", "nội dung chính", "lời kết"}
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿←-⇿⬀-⯿]")
QUOTED_RE = re.compile(r"“[^”\n]{1,200}”|\"[^\"\n]{1,200}\"")
PCT_RE = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)\s?%")


def tell_checks(blocks: list[tuple[str, str]], words: int, vi: bool) -> list[Finding]:
    f: list[Finding] = []
    prose_blocks_ = [(k, t) for k, t in blocks if k in ("para", "list")]
    text = "\n".join(clean(t) for _, t in prose_blocks_)
    unquoted = QUOTED_RE.sub(" ", text)  # a phrase that is quoted or discussed is not a phrase that is used
    strong_hits = 0
    for code, advice, rx in STRONG_TELLS:
        m = rx.search(unquoted)
        if m:
            strong_hits += 1
            n = len(rx.findall(unquoted))
            ctx = unquoted[max(0, m.start() - 30): m.end() + 40]
            f.append(Finding("medium", f"TELL-{code}", f"{advice}" + (f" ({n} occurrences)" if n > 1 else "") + ".",
                             short(ctx)))
    weak: list[str] = []
    raw = "\n".join(t for _, t in prose_blocks_)
    dashes = len(re.findall(r"\s[—–]\s|\w—\w|\s--\s", raw))
    if dashes >= 4 and dashes / max(words, 1) * 100 > 1.0:
        weak.append(f"dashes as the default connector ({dashes} in {words} words)")
    items = [ln for k, t in blocks if k == "list" for ln in t.splitlines() if re.match(r"^\s*(?:[-*+•–]|\d+[.)])\s+", ln)]
    labelled = [ln for ln in items if re.match(r"^\s*(?:[-*+•–]|\d+[.)])\s+\*\*[^*]{2,60}\*\*\s*[:.—–-]?\s", ln)]
    if len(labelled) >= 4 and len(labelled) / max(len(items), 1) >= 0.6:
        weak.append(f"bold label on {len(labelled)} of {len(items)} list items")
    sents = [s for _, t in prose_blocks_ for s in re.split(r"(?<=[.!?…])\s+", clean(t)) if s.strip()]
    run = best = 0
    for s_ in sents:
        run = run + 1 if n_words(s_) <= (4 if vi else 3) and s_.rstrip().endswith((".", "!")) else 0
        best = max(best, run)
    if best >= 3:
        weak.append(f"{best} clipped fragments in a row")
    heads = [re.sub(r"^#{1,6}\s+", "", t).strip() for k, t in blocks if k == "heading"]
    if any(EMOJI_RE.search(h) for h in heads):
        weak.append("emoji or arrows in headings")
    if not vi:
        title_case = [h for h in heads[1:] if len(h.split()) >= 3 and
                      sum(w[:1].isupper() for w in h.split() if len(w) > 3) >= 0.8 * sum(1 for w in h.split() if len(w) > 3)]
        if len(title_case) >= 2:
            weak.append(f"{len(title_case)} headings in Title Case")
    for i, (k, t) in enumerate(blocks[:-1]):
        if k == "heading" and blocks[i + 1][0] == "para":
            hw = {w.lower() for w in re.findall(r"[\wÀ-ỹ]{3,}", re.sub(r"^#{1,6}\s+(\d+[.)]\s*)?", "", t))}
            first = re.split(r"(?<=[.!?…])\s+", clean(blocks[i + 1][1]))[0]
            fw = {w.lower() for w in re.findall(r"[\wÀ-ỹ]{3,}", first)}
            if len(hw) >= 3 and len(hw & fw) / len(hw) >= 0.8 and n_words(first) <= len(hw) + 6:
                weak.append("a heading restated by the sentence under it")
                break
    used = sorted({w for w in AI_WORDS if re.search(rf"\b{w}\w*\b", unquoted, re.I)})
    if len(used) >= 3:
        weak.append("overused words: " + ", ".join(used[:6]))
    if len(weak) >= 2 or (weak and strong_hits):
        f.append(Finding("medium", "TELL-CLUSTER", "Several default-choice patterns together: " + "; ".join(weak) +
                         ". Rewrite the passages around their point instead of patching phrases."))
    elif weak:
        f.append(Finding("info", "TELL-WEAK", f"One weak signal on its own ({weak[0]}): fine if deliberate."))
    return f


# ----------------------------------------------------------------- rigor mode
N_RE = re.compile(
    r"\bn\s*=\s*\d|\b\d[\d.,]*\s+(?:questions?|tasks?|issues?|developers?|users?|samples?|items?|runs?|seeds?|trials?|"
    r"participants?|predictors?|stocks?|firms?|requests?|documents?|examples?|observations?|months|years|"
    r"câu|mẫu|người|lần chạy|tác vụ|lập trình viên|nhà phát triển|biến|cổ phiếu|tháng|năm|tài liệu|quan sát)\b|"
    r"\b\d+\s*/\s*\d+\b", re.I)
COMPARE_RE = re.compile(
    r"\b(beats?|outperform\w*|better than|worse than|faster than|slower than|higher than|lower than|more accurate|"
    r"wins?|won|improv\w+|reduc\w+|increas\w+)\b|thắng|thua|tốt hơn|kém hơn|nhanh hơn|chậm hơn|cao hơn|thấp hơn|"
    r"vượt|cải thiện|giảm|tăng", re.I)
UNCERT_RE = re.compile(
    r"\bCI\b|confidence interval|khoảng tin cậy|±|\+/-|standard error|sai số chuẩn|độ lệch chuẩn|standard deviation|"
    r"\bSD\b|\bSE\b|\bp\s*[=<>≈]\s*0?[.,]\d|p-value|t-stat|t\s*=\s*\d|not (statistically )?significant|inconclusive|"
    r"could not tell|chưa phân biệt được|chưa đủ (mẫu|dữ liệu)|không có ý nghĩa thống kê|chưa kết luận được|"
    r"biên nhiễu|McNemar|bootstrap|Wilson", re.I)
SIG_RE = re.compile(r"\bsignificant(ly)?\b|có ý nghĩa thống kê|đáng kể", re.I)
CAUSAL_RE = re.compile(
    r"\b(because of|caused?|causes|leads? to|led to|thanks to|due to|results? in|drives?|makes? \w+ (faster|slower|better))\b|"
    r"\bnhờ\b|khiến|làm cho|dẫn đến|gây ra|là do|vì vậy mà", re.I)
DESIGN_RE = re.compile(r"randomi[sz]|\bRCT\b|controlled (trial|experiment)|A/B|ngẫu nhiên|đối chứng|ablation|"
                       r"tách riêng từng yếu tố", re.I)
ABSOLUTE_RE = re.compile(
    r"\b(proves?|proven|always|never|guarantees?|definitely|undeniabl\w+|it'?s official|everyone)\b|"
    r"chứng minh rằng|đã chứng minh|luôn luôn|chắc chắn|tất cả mọi|mọi trường hợp|không bao giờ", re.I)
ABSOLUTE_CS_RE = re.compile(r"(?<![\w])(?:ai|Ai) cũng (?:nên|phải|cần|biết)")  # case-sensitive: "AI cũng" is not "ai cũng"
CI_OVERLAP_RE = re.compile(
    r"(?:khoảng tin cậy|confidence intervals?|\bCIs?\b|intervals?|vùng)[^.!?\n]{0,80}(?:chồng (?:lên|lấn)|overlap\w*)|"
    r"(?:chồng (?:lên|lấn)|overlap\w*)[^.!?\n]{0,80}(?:khoảng tin cậy|confidence intervals?|\bCIs?\b|intervals?)", re.I)
CI_MEANING_RE = re.compile(
    r"95\s?%\s*(?:chance|probability|xác suất|khả năng)|"
    r"(?:khoảng tin cậy|confidence interval|\bCI\b)[^.!?\n]{0,80}(?:nhiều khả năng nằm|most likely (?:lies|falls)|"
    r"probably (?:lies|falls)|chắc (?:là )?nằm)", re.I)
LIMIT_RE = re.compile(r"limitation|caveat|threats? to validity|does not show|doesn'?t show|did not test|not tested|"
                      r"giới hạn|hạn chế|chưa chứng minh|chưa test|chưa kiểm|không cho thấy|chưa đo", re.I)
SOURCE_RE = re.compile(r"https?://|\]\(|\bdoi:|arXiv:\d|^source:\s*\S|our own (data|experiment|measurement)|"
                       r"internal (data|experiment)|số liệu (từ|của)|thử nghiệm nội bộ|dữ liệu nội bộ", re.I | re.M)
REPRO_RE = re.compile(r"github|gitlab|\brepo\b|dataset|\bcode\b|\bversion\b|\bv\d+\.\d+|phiên bản|\bseed\b|dữ liệu|"
                      r"mã nguồn|không công bố|cannot be published|not public|không thể chia sẻ", re.I)
DATE_RE = re.compile(r"\b(19|20)\d{2}\b")
QUANT_RE = re.compile(r"backtest|sharpe|\balpha\b|drawdown|long-short|long/short|factor returns?|hedge portfolio|"
                      r"chiến lược giao dịch|lợi nhuận chiến lược", re.I)
OOS_RE = re.compile(r"out-of-sample|out of sample|\bOOS\b|ngoài mẫu|walk-forward|live trading|paper trading|"
                    r"post-publication|sau khi công bố", re.I)
COST_RE = re.compile(r"transaction cost|trading cost|slippage|commission|net of|gross of|phí giao dịch|chi phí giao dịch|"
                     r"trượt giá|trước phí|sau phí", re.I)
TRIALS_RE = re.compile(r"multiple testing|data[- ]mining|data snooping|overfit|number of (trials|strategies|signals)|"
                       r"deflated|khai phá dữ liệu|quá khớp|số (lần|chiến lược|tín hiệu) (đã )?thử", re.I)
LOOKAHEAD_RE = re.compile(r"look-?ahead|point-in-time|survivorship|nhìn trước|dữ liệu tương lai", re.I)
ML_RE = re.compile(r"\baccuracy\b|\bF1\b|\bBLEU\b|\bbenchmark(s|ed)?\b|fine-?tun|độ chính xác|test set|tập test", re.I)
RUNS_RE = re.compile(r"\bseeds?\b|\bruns?\b|lần chạy|chạy \d+ lần|repeated|lặp lại", re.I)
BASELINE_RE = re.compile(r"baseline|compared (with|to)|so với|đối chứng|control", re.I)


def rigor_checks(blocks: list[tuple[str, str]], title: str | None) -> list[Finding]:
    """Mechanical proxies for the research-rigor rubric. Each finding names what a reviewer would ask."""
    f: list[Finding] = []
    paras = [t for k, t in blocks if k in ("para", "list", "table")]
    text = "\n".join(t for k, t in blocks if k in ("para", "list", "table", "heading", "chart"))
    if title:
        text = title + "\n" + text

    if not N_RE.search(text):
        f.append(Finding("medium", "RIGOR-N", "No sample size found (n, number of items/runs/participants/period). "
                         "State n and the unit of analysis."))
    has_compare = False
    for p in paras:
        c = clean(p)
        if COMPARE_RE.search(c) and re.search(r"\d", c):
            has_compare = True
            break
    if has_compare and not UNCERT_RE.search(text):
        f.append(Finding("medium", "RIGOR-UNCERTAINTY", "Comparative claims with numbers but no uncertainty anywhere "
                         "(CI, SD/SE, p-value, or an explicit 'could not tell apart'). Run stats_check.py and report it."))
    for p in paras:
        c = clean(p)
        m = SIG_RE.search(c)
        if m and not UNCERT_RE.search(c):
            f.append(Finding("medium", "RIGOR-SIGNIFICANT", f"“{m.group(0)}” without a test, p-value or CI in the same "
                             "paragraph: give the statistic or use a neutral word.", short(c)))
        m = ABSOLUTE_RE.search(c) or ABSOLUTE_CS_RE.search(c)
        if m:
            f.append(Finding("medium", "RIGOR-ABSOLUTE", f"Absolute wording “{m.group(0)}”: data supports claims within "
                             "a sample and a scope, rarely an absolute.", short(c)))
    m = CI_OVERLAP_RE.search(text)
    if m:
        f.append(Finding("medium", "RIGOR-CI-OVERLAP", "Reasoning from overlapping intervals: overlap is not a test of "
                         "the difference (two intervals can overlap while the difference is clear). Report the "
                         "interval of the difference itself (stats_check.py diff-prop / mcnemar / paired).",
                         short(text[max(0, m.start() - 40): m.end() + 40])))
    m = CI_MEANING_RE.search(text)
    if m:
        f.append(Finding("low", "RIGOR-CI-MEANING", "A 95% confidence interval is not a 95% probability that the true "
                         "value lies in this interval. Say 'the range of values the data does not rule out' or give "
                         "the repeated-sampling meaning.", short(text[max(0, m.start() - 40): m.end() + 40])))
    if title and (ABSOLUTE_RE.search(title) or ABSOLUTE_CS_RE.search(title)):
        f.append(Finding("high", "RIGOR-TITLE", "Title makes an absolute/universal claim.", title))
    if not DESIGN_RE.search(text):
        for p in paras:
            c = clean(p)
            m = CAUSAL_RE.search(c)
            if m and re.search(r"\d", c):
                f.append(Finding("low", "RIGOR-CAUSAL", f"Causal wording “{m.group(0)}” next to a number, but no "
                                 "randomised/controlled design is mentioned: confirm the design supports causation "
                                 "or write 'after' / 'associated with'.", short(c)))
                break
    if not LIMIT_RE.search(text):
        f.append(Finding("medium", "RIGOR-LIMITS", "No limitations / 'what this does not show' found. Add ≥ 2 specific "
                         "limits of this evidence."))
    if not SOURCE_RE.search("\n".join(t for _, t in blocks)):
        f.append(Finding("medium", "RIGOR-SOURCE", "No link or citation to a primary source or to the data."))
    if not REPRO_RE.search(text):
        f.append(Finding("low", "RIGOR-REPRO", "No reproducibility information (code, data, versions) and no statement "
                         "that it cannot be shared."))
    if not DATE_RE.search(text):
        f.append(Finding("low", "RIGOR-DATE", "No year/date for the evidence: results expire, state when the data is from."))
    if QUANT_RE.search(text):
        for rx, code, msg in ((OOS_RE, "RIGOR-QUANT-OOS", "in-sample vs out-of-sample (or live) is not distinguished"),
                              (COST_RE, "RIGOR-QUANT-COSTS", "no statement on transaction costs (gross or net?)"),
                              (TRIALS_RE, "RIGOR-QUANT-TRIALS", "number of strategies/parameters tried and "
                               "overfitting/multiple testing not addressed"),
                              (LOOKAHEAD_RE, "RIGOR-QUANT-LOOKAHEAD", "look-ahead / survivorship bias not addressed")):
            if not rx.search(text):
                f.append(Finding("medium", code, f"Trading/backtest content: {msg}."))
    if ML_RE.search(text):
        if not RUNS_RE.search(text):
            f.append(Finding("low", "RIGOR-ML-RUNS", "Model/eval results: number of runs or seeds not stated."))
        if not BASELINE_RE.search(text):
            f.append(Finding("low", "RIGOR-ML-BASELINE", "Model/eval results: no baseline or comparison described."))
    return f


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
    ap.add_argument("--rigor", action="store_true",
                    help="research-grade checks: sample size, uncertainty, limitations, sources, backtest/eval caveats")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--export", default=None, help="write a platform-safe plain-text version to this path")
    a = ap.parse_args(argv)
    md = Path(a.post).read_text(encoding="utf-8")
    findings, stats = check(md, a.platform, a.title, a.rigor)
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
