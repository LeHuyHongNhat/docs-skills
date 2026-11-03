#!/usr/bin/env python3
"""render_doc.py — xuất tài liệu Markdown thành HTML / PDF / DOCX / XLSX có thiết kế, kèm visual QA.

Usage:
    python render_doc.py doc.md --to pdf,docx,xlsx [--out-dir dist] [--qa] [--landscape] [--toc auto|on|off]

Design notes:
- Markdown là *single source of truth*; mọi định dạng khác sinh ra từ nó, nên sửa nội dung một chỗ.
- Mermaid được render trước bằng mmdc (SVG cho HTML/PDF, PNG 2x cho DOCX) — Word/PDF không
  hiểu code block mermaid.
- `[CẦN XÁC NHẬN: ...]` / `[TO CONFIRM: ...]` được tô thành callout (HTML class `.confirm`,
  DOCX character style `Confirm`) để người đọc quét nhanh các điểm chưa chốt.
- XLSX chỉ lấy các bảng trong tài liệu (mỗi bảng một sheet, tên theo heading gần nhất) — hợp
  cho data dictionary, ma trận truy vết, bảng finding mà người đọc muốn lọc/sắp xếp.
- Mỗi công cụ ngoài (pandoc, mmdc, Chrome) là tùy chọn: thiếu thì bỏ qua định dạng đó và báo
  WARN, không làm hỏng các định dạng còn lại.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
THEME_CSS = ASSETS / "doc-theme.css"
REFERENCE_DOCX = ASSETS / "reference.docx"

FENCE_RE = re.compile(r"^(```|~~~)")
MERMAID_RE = re.compile(r"^```mermaid\s*\n(.*?)^```\s*$", re.S | re.M)
CONFIRM_RE = re.compile(r"\[(CẦN XÁC NHẬN|TO CONFIRM)([^\[\]]*)\]")
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
H2_RE = re.compile(r"^##\s+", re.M)
CHROME_CANDIDATES = ["google-chrome", "chromium", "chromium-browser", "google-chrome-stable"]


@dataclass
class Report:
    outputs: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    qa: dict[str, object] = field(default_factory=dict)


# ----------------------------------------------------------------- pre-processing
def render_mermaid(md: str, work: Path, fmt: str, rep: Report) -> str:
    """Thay block mermaid bằng ảnh. fmt='svg' (HTML/PDF) hoặc 'png' (DOCX)."""
    mmdc = shutil.which("mmdc")
    counter = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        if not mmdc:
            return m.group(0)
        src = work / f"diagram-{counter}.mmd"
        out = work / f"diagram-{counter}.{fmt}"
        src.write_text(m.group(1), encoding="utf-8")
        pp = work / "puppeteer.json"
        pp.write_text('{"args":["--no-sandbox"]}')
        cfg = work / "mermaid.json"
        cfg.write_text(json.dumps({"theme": "neutral", "themeVariables": {
            "fontFamily": "Inter, DejaVu Sans, Arial, sans-serif", "fontSize": "14px"}}))
        cmd = [mmdc, "-p", str(pp), "-c", str(cfg), "-i", str(src), "-o", str(out), "-b", "white"]
        if fmt == "png":
            cmd += ["-s", "2"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode != 0 or not out.exists():
            rep.warnings.append(f"Mermaid #{counter} không render được: {r.stderr.strip()[-200:]}")
            return m.group(0)
        return f"![Hình {counter}]({out.as_posix()}){{.diagram}}\n"

    new = MERMAID_RE.sub(repl, md)
    if counter and not mmdc:
        rep.warnings.append("Không có mmdc: diagram Mermaid giữ dạng code (cài @mermaid-js/mermaid-cli để render).")
    return new


def mark_confirm(md: str) -> str:
    """Bọc marker cần xác nhận thành span có class/style, bỏ qua code fence và inline code."""
    out: list[str] = []
    in_fence = False
    for line in md.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        line = re.sub(r"`(\[(?:CẦN XÁC NHẬN|TO CONFIRM)[^`]*\])`", r"\1", line)
        parts = re.split(r"(`[^`]*`)", line)
        parts = [p if p.startswith("`") else CONFIRM_RE.sub(
            lambda m: f'[⚑ {m.group(1)}{m.group(2)}]{{.confirm custom-style="Confirm"}}', p) for p in parts]
        out.append("".join(parts))
    return "\n".join(out) + "\n"


def doc_title(md: str, fallback: str) -> str:
    m = H1_RE.search(md)
    return re.sub(r"[*_`]", "", m.group(1)).strip() if m else fallback


def _toc_title(md: str) -> str:
    """Tài liệu tiếng Việt (có ký tự dấu đặc trưng) → 'Mục lục', còn lại 'Contents'."""
    return "Mục lục" if re.search(r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", md, re.I) else "Contents"


def pandoc_ok(rep: Report) -> bool:
    if shutil.which("pandoc"):
        return True
    rep.warnings.append("Không có pandoc: bỏ qua HTML/PDF/DOCX.")
    return False


# ----------------------------------------------------------------- HTML / PDF
def to_html(md: str, src: Path, out: Path, toc: bool, title: str, rep: Report, mobile: bool = False) -> Path | None:
    if not pandoc_ok(rep):
        return None
    work = Path(tempfile.mkdtemp(prefix="render-html-"))
    body = mark_confirm(render_mermaid(md, work, "svg", rep))
    tmp_md = work / "doc.md"
    tmp_md.write_text(body, encoding="utf-8")
    cmd = ["pandoc", str(tmp_md), "-f", "gfm+attributes+bracketed_spans+implicit_figures+pipe_tables",
           "-t", "html5", "--standalone", "--embed-resources", "--css", str(THEME_CSS),
           "--metadata", f"pagetitle={title}", "--resource-path", f"{work}:{src.parent}", "-o", str(out)]
    if toc:
        cmd += ["--toc", "--toc-depth=2"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        rep.warnings.append(f"pandoc HTML lỗi: {r.stderr[-300:]}")
        return None
    _post_html(out, mobile)
    return out


def _cardify(soup, table) -> None:
    """Bảng ≥ 4 cột → mỗi dòng thành một thẻ (nhãn: giá trị) để đọc trên màn hình hẹp."""
    heads = [th.get_text(" ", strip=True) for th in table.select("thead th")]
    if not heads:
        return
    wrap = soup.new_tag("div", attrs={"class": "cards"})
    for tr in table.select("tbody tr"):
        cells = tr.find_all("td")
        card = soup.new_tag("div", attrs={"class": "card"})
        for i, td in enumerate(cells):
            if not td.get_text(strip=True) or td.get_text(strip=True) in {"—", "-"}:
                continue
            row = soup.new_tag("div", attrs={"class": "card-title" if i == 0 else "card-row"})
            if i > 0:
                lab = soup.new_tag("span", attrs={"class": "card-label"})
                lab.string = heads[i] if i < len(heads) else ""
                row.append(lab)
            val = soup.new_tag("span", attrs={"class": "card-value"})
            for child in list(td.contents):
                val.append(child)
            row.append(val)
            card.append(row)
        wrap.append(card)
    table.replace_with(wrap)


def _post_html(path: Path, mobile: bool = False) -> None:
    """Đánh dấu bảng rộng (≥ 7 cột) để CSS thu nhỏ chữ; đặt figure cho diagram."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for t in soup.find_all("table"):
        first = t.find("tr")
        if first and len(first.find_all(["th", "td"])) >= 7:
            t["class"] = (t.get("class") or []) + ["wide"]
    for img in soup.select("img.diagram"):
        fig = img.find_parent("figure")
        if fig:
            fig["class"] = (fig.get("class") or []) + ["diagram"]
    # ID nằm giữa câu (FR-004, AC-006.3) không được gãy ở dấu gạch nối
    id_re = re.compile(r"\b[A-ZĐ]{1,5}-\d{1,4}(?:\.\d+)*\b")
    for node in list(soup.find_all(string=id_re)):
        if node.parent and node.parent.name in ("code", "pre", "script", "style"):
            continue
        parts, last, txt = [], 0, str(node)
        for m in id_re.finditer(txt):
            parts.append(txt[last:m.start()])
            sp = soup.new_tag("span", attrs={"class": "nb"})
            sp.string = m.group(0)
            parts.append(sp)
            last = m.end()
        parts.append(txt[last:])
        for piece in parts:
            node.insert_before(piece)
        node.extract()
    # ô chỉ chứa ID (FR-001, AC-002.1, OQ-12) không được xuống dòng giữa ID
    for td in soup.find_all(["td", "th"]):
        if re.fullmatch(r"\s*[A-ZĐ]{1,5}-\d{1,4}(\.\d+)*\s*", td.get_text()):
            td["class"] = (td.get("class") or []) + ["id"]
    if mobile:
        body = soup.find("body")
        if body:
            body["class"] = (body.get("class") or []) + ["mobile"]
        h1 = soup.find("h1")
        meta = h1.find_next_sibling() if h1 else None
        for t in soup.find_all("table"):
            if t is meta:
                continue
            first = t.find("tr")
            if first and len(first.find_all(["th", "td"])) >= 4:
                _cardify(soup, t)
    # Mục lục: chuyển xuống sau tiêu đề + bảng metadata, bỏ cấp H1 (chỉ có một H1)
    toc = soup.find("nav", id="TOC")
    h1 = soup.find("h1")
    if toc and h1:
        top = toc.find("ul")
        items = top.find_all("li", recursive=False) if top else []
        if len(items) == 1 and items[0].find("ul"):
            top.replace_with(items[0].find("ul"))
        toc.extract()
        anchor = h1
        nxt = h1.find_next_sibling()
        while nxt is not None and nxt.name in ("table", "p") and nxt.name == "table" or (nxt is not None and nxt.name == "p" and "doc-kicker" in (nxt.get("class") or [])):
            anchor, nxt = nxt, nxt.find_next_sibling()
        anchor.insert_after(toc)
    path.write_text(str(soup), encoding="utf-8")


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        p = shutil.which(c)
        if p:
            return p
    return None


def to_pdf(html: Path, out: Path, title: str, landscape: bool, rep: Report, mobile: bool = False) -> Path | None:
    chrome = find_chrome()
    footer = (f'<div style="font-family:Inter,DejaVu Sans,sans-serif;font-size:7.5pt;color:#6b7385;'
              f'width:100%;padding:0 16mm;display:flex;justify-content:space-between;">'
              f'<span>{title}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            kw = {"executable_path": chrome} if chrome else {}
            browser = p.chromium.launch(args=["--no-sandbox"], **kw)
            page = browser.new_page()
            page.goto(html.as_uri(), wait_until="networkidle")
            if mobile:  # khổ ~ màn hình điện thoại, lề hẹp
                # Viewport = bề rộng nội dung trang (94 mm ≈ 355 px) để Chrome không dàn trang rộng rồi thu nhỏ
                page.set_viewport_size({"width": 355, "height": 640})
                page.add_style_tag(content="@page { size: 108mm 192mm; margin: 8mm 7mm 12mm; }")
                page.pdf(path=str(out), width="108mm", height="192mm", print_background=True, prefer_css_page_size=True,
                         display_header_footer=True, header_template="<span></span>",
                         footer_template=footer.replace("padding:0 16mm", "padding:0 7mm").replace("7.5pt", "6pt"),
                         margin={"top": "8mm", "bottom": "12mm", "left": "7mm", "right": "7mm"})
            else:
                page.pdf(path=str(out), format="A4", landscape=landscape, print_background=True,
                         display_header_footer=True, header_template="<span></span>", footer_template=footer,
                         margin={"top": "18mm", "bottom": "20mm", "left": "16mm", "right": "16mm"})
            browser.close()
        return out
    except Exception as e:  # noqa: BLE001 — fallback sang Chrome CLI
        rep.warnings.append(f"Playwright lỗi ({type(e).__name__}), thử Chrome CLI (không có số trang).")
    if not chrome:
        rep.warnings.append("Không có Chrome/Chromium: bỏ qua PDF.")
        return None
    r = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", html.as_uri()], capture_output=True, text=True, timeout=180)
    return out if r.returncode == 0 and out.exists() else None


# ----------------------------------------------------------------- DOCX
def to_docx(md: str, src: Path, out: Path, toc: bool, rep: Report) -> Path | None:
    if not pandoc_ok(rep):
        return None
    work = Path(tempfile.mkdtemp(prefix="render-docx-"))
    body = mark_confirm(render_mermaid(md, work, "png", rep))
    tmp_md = work / "doc.md"
    tmp_md.write_text(body, encoding="utf-8")
    cmd = ["pandoc", str(tmp_md), "-f", "gfm+attributes+bracketed_spans+implicit_figures+pipe_tables",
           "-t", "docx", "--resource-path", f"{work}:{src.parent}", "-o", str(out)]
    if len(H1_RE.findall(md)) == 1:  # một H1 duy nhất → thành Title, H2 → Heading 1 (Navigation Pane đúng cấp)
        cmd += ["--shift-heading-level-by=-1"]
    if REFERENCE_DOCX.exists():
        cmd += ["--reference-doc", str(REFERENCE_DOCX)]
    else:
        rep.warnings.append("Thiếu assets/reference.docx: DOCX dùng style mặc định của pandoc.")
    if toc:
        cmd += ["--toc", "--toc-depth=2", "--metadata", f"toc-title={_toc_title(md)}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        rep.warnings.append(f"pandoc DOCX lỗi: {r.stderr[-300:]}")
        return None
    _post_docx(out)
    return out


def _nobreak_ids(d) -> None:
    """Thay '-' trong ID (FR-004, AC-006.3) bằng w:noBreakHyphen của Word — không phụ thuộc font,
    tìm kiếm trong Word vẫn khớp, và ID không bị gãy cuối dòng."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    id_re = re.compile(r"\b([A-ZĐ]{1,5})-(\d{1,4}(?:\.\d+)*)\b")

    def paragraphs():
        yield from d.paragraphs
        for t in d.tables:
            for row in t.rows:
                for cell in row.cells:
                    yield from cell.paragraphs

    for p in paragraphs():
        for r in p.runs:
            txt = r.text
            if not id_re.search(txt):
                continue
            el = r._r
            for t_el in el.findall(qn("w:t")):
                el.remove(t_el)
            pieces = re.split(r"(?<=[A-ZĐ])-(?=\d)", txt)
            for i, piece in enumerate(pieces):
                if i:
                    el.append(OxmlElement("w:noBreakHyphen"))
                te = OxmlElement("w:t")
                te.set(qn("xml:space"), "preserve")
                te.text = piece
                el.append(te)


def _column_widths(t, usable: int) -> list[int]:
    """Cột ngắn (ID, Có/Không, kiểu dữ liệu) được đủ rộng cho từ dài nhất để không gãy giữa từ;
    phần còn lại chia theo độ dài nội dung trung bình."""
    char_tw = 118  # twips/ký tự ở cỡ 9pt (ước lượng có dư cho chữ có dấu & mono)
    ncol = len(t.columns)
    mins, weights = [], []
    for ci in range(ncol):
        texts = [r.cells[ci].text for r in t.rows if ci < len(r.cells)]
        longest = max((len(w) for tx in texts for w in tx.split()), default=3)
        mins.append(min(longest, 22) * char_tw + 240)
        weights.append(max(sum(min(len(tx), 80) for tx in texts) / max(len(texts), 1), 4))
    base = sum(mins)
    if base >= usable:  # quá nhiều cột: co theo tỉ lệ min
        return [int(usable * m / base) for m in mins]
    extra = usable - base
    # chỉ cột "dài" (văn bản mô tả) nhận phần dư; cột ngắn giữ min
    long_w = [w if w > 14 else 0 for w in weights]
    tot = sum(long_w) or sum(weights)
    src = long_w if sum(long_w) else weights
    return [int(m + extra * w / tot) for m, w in zip(mins, src)]


def _post_docx(path: Path) -> None:
    """Style bảng: header nền xám nhạt + đậm, viền dưới mảnh, padding; ảnh vừa khổ trang."""
    try:
        import docx
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Cm, Pt
    except ImportError:
        return
    d = docx.Document(str(path))

    def border(cell, color: str, size: int, sides: tuple[str, ...]) -> None:
        tcPr = cell._tc.get_or_add_tcPr()
        b = tcPr.find(qn("w:tcBorders"))
        if b is None:
            b = OxmlElement("w:tcBorders")
            tcPr.append(b)
        for s in sides:
            e = OxmlElement(f"w:{s}")
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), str(size))
            e.set(qn("w:color"), color)
            b.append(e)

    usable_twips = 9600  # ~16,9 cm: A4 trừ lề 2 cm mỗi bên
    for t in d.tables:
        # Bảng full chiều ngang, độ rộng cột theo độ dài nội dung (min/max để tránh cột ID bị bóp)
        widths = _column_widths(t, usable_twips)
        tblPr = t._tbl.tblPr
        for tag in ("w:tblW", "w:tblLayout"):
            old = tblPr.find(qn(tag))
            if old is not None:
                tblPr.remove(old)
        tw = OxmlElement("w:tblW")
        tw.set(qn("w:w"), str(usable_twips))
        tw.set(qn("w:type"), "dxa")
        tblPr.append(tw)
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblPr.append(lay)
        grid = t._tbl.tblGrid
        for gi, gc in enumerate(grid.findall(qn("w:gridCol"))):
            if gi < len(widths):
                gc.set(qn("w:w"), str(widths[gi]))
        for row in t.rows:
            for ci, cell in enumerate(row.cells):
                if ci < len(widths):
                    tcPr = cell._tc.get_or_add_tcPr()
                    old = tcPr.find(qn("w:tcW"))
                    if old is not None:
                        tcPr.remove(old)
                    w = OxmlElement("w:tcW")
                    w.set(qn("w:w"), str(widths[ci]))
                    w.set(qn("w:type"), "dxa")
                    tcPr.insert(0, w)
        for ri, row in enumerate(t.rows):
            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                mar = OxmlElement("w:tcMar")
                for side in ("top", "bottom", "left", "right"):
                    e = OxmlElement(f"w:{side}")
                    e.set(qn("w:w"), "80" if side in ("top", "bottom") else "110")
                    e.set(qn("w:type"), "dxa")
                    mar.append(e)
                tcPr.append(mar)
                if ri == 0:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:fill"), "F2F4F8")
                    tcPr.append(shd)
                    border(cell, "C9CED8", 8, ("bottom",))
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.bold = True
                else:
                    border(cell, "E3E6EC", 4, ("bottom",))
                for p in cell.paragraphs:
                    p.paragraph_format.space_after = Pt(0)
                    for run in p.runs:
                        run.font.size = Pt(9)
        for row in t.rows:  # không tách một hàng qua hai trang
            trp = row._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit")
            cs.set(qn("w:val"), "true")
            trp.append(cs)
        # lặp header khi bảng sang trang
        trPr = t.rows[0]._tr.get_or_add_trPr()
        h = OxmlElement("w:tblHeader")
        h.set(qn("w:val"), "true")
        trPr.append(h)
    _nobreak_ids(d)
    max_w, max_h = Cm(16.5), Cm(13)
    for shape in d.inline_shapes:
        ratio = min(1.0, max_w / shape.width, max_h / shape.height)
        if ratio < 1.0:
            shape.width = int(shape.width * ratio)
            shape.height = int(shape.height * ratio)
    d.save(str(path))


# ----------------------------------------------------------------- XLSX
@dataclass
class MdTable:
    heading: str
    heading_raw: str
    header: list[str]
    rows: list[list[str]]
    is_meta: bool = False  # bảng metadata ngay sau H1


def _clean_cell(s: str) -> str:
    s = s.strip().replace("\\|", "|")
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s


def _split_row(line: str) -> list[str]:
    line = line.strip()
    line = line[1:] if line.startswith("|") else line
    line = line[:-1] if line.endswith("|") and not line.endswith("\\|") else line
    return [_clean_cell(c) for c in re.split(r"(?<!\\)\|", line)]


def extract_tables(md: str) -> list[MdTable]:
    tables: list[MdTable] = []
    heading = heading_raw = "Bảng"
    lines = md.splitlines()
    i, in_fence = 0, False
    last_h_level = 0
    since_heading = 0  # số dòng không rỗng kể từ heading gần nhất
    while i < len(lines):
        ln = lines[i]
        if FENCE_RE.match(ln.strip()):
            in_fence = not in_fence
        elif not in_fence:
            hm = re.match(r"^(#{1,6})\s+(.+)", ln)
            if ln.strip() and not hm:
                since_heading += 1
            if hm:
                last_h_level, since_heading = len(hm.group(1)), 0
                heading_raw = hm.group(2).strip()
                heading = re.sub(r"\*\*|`", "", heading_raw).strip()
            elif ln.strip().startswith("|") and i + 1 < len(lines) and re.fullmatch(r"\s*\|?[\s:\-|]+\|?\s*", lines[i + 1]):
                header = _split_row(ln)
                rows: list[list[str]] = []
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    rows.append(_split_row(lines[j]))
                    j += 1
                tables.append(MdTable(heading, heading_raw, header, rows,
                                      is_meta=(last_h_level == 1 and since_heading <= 1)))
                i = j
                continue
        i += 1
    return tables


def to_xlsx(md: str, out: Path, title: str, src: Path, rep: Report) -> Path | None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        rep.warnings.append("Không có openpyxl: bỏ qua XLSX.")
        return None
    all_tables = extract_tables(md)
    meta = next((t for t in all_tables if t.is_meta), None)
    tables = [t for t in all_tables if len(t.header) >= 2 and t.rows and not t.is_meta]
    if not tables:
        rep.warnings.append("Tài liệu không có bảng nào ≥ 2 cột: không tạo XLSX.")
        return None
    font_name = "Arial"
    hdr_font = Font(name=font_name, bold=True, color="FFFFFF", size=10)
    body_font = Font(name=font_name, size=10, color="1B2130")
    hdr_fill = PatternFill("solid", fgColor="24324F")  # navy: header nổi rõ khi lọc/cuộn
    confirm_fill = PatternFill("solid", fgColor="FFF6E0")
    thin = Side(style="thin", color="E3E6EC")
    strong = Side(style="medium", color="C9CED8")
    wrap_top = Alignment(wrap_text=True, vertical="top")

    wb = Workbook()
    ov = wb.active
    ov.title = "Mục lục"
    ov["A1"] = title
    ov["A1"].font = Font(name=font_name, bold=True, size=14)
    ov["A2"] = f"Nguồn: {src.name} · Xuất lúc: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ov["A2"].font = Font(name=font_name, size=9, color="6B7385")
    r0 = 4
    if meta and meta.rows:  # metadata tài liệu (phiên bản, ngày, owner...) dạng key: value
        for k, v in zip(meta.header, meta.rows[0]):
            ov.cell(row=r0, column=1, value=k).font = Font(name=font_name, size=9, color="6B7385")
            ov.cell(row=r0, column=2, value=v).font = body_font
            r0 += 1
        r0 += 1
    ov.cell(row=r0, column=1, value="Sheet")
    ov.cell(row=r0, column=2, value="Mục trong tài liệu")
    ov.cell(row=r0, column=3, value="Số dòng")
    for ci in (1, 2, 3):
        ov.cell(row=r0, column=ci).font, ov.cell(row=r0, column=ci).fill = hdr_font, hdr_fill
    used: set[str] = {"Mục lục"}
    for n, t in enumerate(tables, 1):
        # Ưu tiên định danh trong `backtick` của heading (vd tên bảng `order_items`), nếu không có
        # thì bỏ số mục đầu dòng; Excel giới hạn tên sheet 31 ký tự.
        ident = (re.search(r"(?:Bảng|Table|Sheet)\s+`?([A-Za-z_][\w.]*)`?", t.heading, re.I)
                 or re.search(r"`([A-Za-z_][\w.]*)`", t.heading_raw))
        base = ident.group(1) if ident else re.sub(r"^[\d.]+\s*", "", t.heading)
        base = re.sub(r"[\[\]:*?/\\]", " ", base).strip()[:31] or f"Bảng {n}"
        name, k = base, 2
        while name in used:
            name, k = f"{base[:28]} {k}", k + 1
        used.add(name)
        ws = wb.create_sheet(name)
        ncol = len(t.header)
        ws.append(t.header)
        for r in t.rows:
            ws.append([(_num(v)) for v in (r + [""] * ncol)[:ncol]])
        for ci in range(1, ncol + 1):
            h = ws.cell(row=1, column=ci)
            h.font, h.fill, h.alignment = hdr_font, hdr_fill, wrap_top
            h.border = Border(bottom=strong)
            width = max(len(str(ws.cell(row=ri, column=ci).value or "").split("\n")[0])
                        for ri in range(1, ws.max_row + 1))
            ws.column_dimensions[get_column_letter(ci)].width = min(max(10, width * 1.1 + 2), 60)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font, c.alignment, c.border = body_font, wrap_top, Border(bottom=thin)
                if isinstance(c.value, str) and re.search(r"CẦN XÁC NHẬN|TO CONFIRM", c.value):
                    c.fill = confirm_fill
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        ws.sheet_view.showGridLines = False
        r = ov.max_row + 1
        ov.cell(row=r, column=1, value=name).hyperlink = f"#'{name}'!A1"
        ov.cell(row=r, column=1).font = Font(name=font_name, color="2A4FB8", underline="single")
        ov.cell(row=r, column=2, value=t.heading).font = body_font
        ov.cell(row=r, column=3, value=len(t.rows)).font = body_font
    ov.column_dimensions["A"].width, ov.column_dimensions["B"].width = 30, 60
    ov.sheet_view.showGridLines = False
    wb.save(str(out))
    return out


def _num(v: str) -> object:
    if re.fullmatch(r"-?\d+", v.strip() or "x"):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v.strip() or "x"):
        return float(v)
    return v


# ----------------------------------------------------------------- QA
def visual_qa(pdf: Path | None, md: str, out_dir: Path, rep: Report) -> None:
    """Render trang PDF thành PNG để agent xem bằng mắt + các check tự động."""
    qa: dict[str, object] = {}
    wide = [t.heading for t in extract_tables(md) if len(t.header) >= 7]
    if wide:
        qa["wide_tables"] = wide
        rep.warnings.append(f"{len(wide)} bảng ≥ 7 cột (dễ chật trên A4 dọc/mobile): {wide[:5]} — cân nhắc tách bảng hoặc --landscape.")
    if MERMAID_RE.search(md) and not shutil.which("mmdc"):
        qa["mermaid_unrendered"] = True
    if pdf and pdf.exists():
        if shutil.which("pdfinfo"):
            info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
            m = re.search(r"Pages:\s+(\d+)", info)
            qa["pages"] = int(m.group(1)) if m else None
        if shutil.which("pdffonts"):
            fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
            names = sorted({f.split()[0].split("+")[-1] for f in fonts if f.strip()})
            qa["fonts"] = names
            not_emb = [f for f in fonts if f.split() and " no " in f]
            if not_emb:
                rep.warnings.append(f"Có font không nhúng trong PDF: {len(not_emb)}")
        if shutil.which("pdftotext"):  # cỡ chữ hiệu dụng: phát hiện trang bị thu nhỏ (chữ tí hon)
            bb = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True).stdout
            hs = sorted(float(m.group(2)) - float(m.group(1))
                        for m in re.finditer(r'yMin="([\d.]+)"[^>]*yMax="([\d.]+)"', bb))
            if hs:
                med = hs[len(hs) // 2]
                qa["median_word_height_pt"] = round(med, 1)
                if med < 7.5:
                    rep.warnings.append(f"Chữ quá nhỏ trong PDF (≈{med:.1f}pt): có phần tử rộng hơn trang làm Chrome "
                                        "thu nhỏ cả trang — tìm bảng/code/ảnh không xuống dòng.")
        if shutil.which("pdftoppm"):
            prev = out_dir / f"{pdf.stem}-preview"
            prev.mkdir(exist_ok=True)
            subprocess.run(["pdftoppm", "-r", "70", "-png", str(pdf), str(prev / "page")], check=False)
            qa["preview_pages"] = sorted(str(p) for p in prev.glob("page*.png"))
    rep.qa = qa


# ----------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc")
    ap.add_argument("--to", default="html,pdf,docx", help="html,pdf,docx,xlsx (phân tách bằng dấu phẩy)")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--qa", action="store_true", help="Render PNG từng trang PDF + check tự động")
    ap.add_argument("--landscape", action="store_true")
    ap.add_argument("--page", choices=["a4", "mobile"], default="a4",
                    help="mobile: PDF khổ màn hình điện thoại, bảng ≥4 cột chuyển thành thẻ")
    ap.add_argument("--toc", choices=["auto", "on", "off"], default="auto")
    a = ap.parse_args(argv)

    src = Path(a.doc).resolve()
    md = src.read_text(encoding="utf-8")
    out_dir = Path(a.out_dir).resolve() if a.out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    fmts = {f.strip().lower() for f in a.to.split(",") if f.strip()}
    title = doc_title(md, src.stem)
    toc = a.toc == "on" or (a.toc == "auto" and len(H2_RE.findall(md)) >= 6)
    rep = Report()

    html_path: Path | None = None
    if fmts & {"html", "pdf"}:
        html_path = to_html(md, src, out_dir / f"{src.stem}.html", toc, title, rep, mobile=a.page == "mobile")
        if html_path and "html" in fmts:
            rep.outputs["html"] = str(html_path)
    pdf_path: Path | None = None
    if "pdf" in fmts and html_path:
        pdf_path = to_pdf(html_path, out_dir / f"{src.stem}.pdf", title, a.landscape, rep, mobile=a.page == "mobile")
        if pdf_path:
            rep.outputs["pdf"] = str(pdf_path)
        if "html" not in fmts:
            html_path.unlink(missing_ok=True)
    if "docx" in fmts:
        # DOCX: mục lục là field Word phải "Update field" mới hiện số trang → chỉ chèn khi người dùng yêu cầu
        p = to_docx(md, src, out_dir / f"{src.stem}.docx", a.toc == "on", rep)
        if p:
            rep.outputs["docx"] = str(p)
    if "xlsx" in fmts:
        p = to_xlsx(md, out_dir / f"{src.stem}.xlsx", title, src, rep)
        if p:
            rep.outputs["xlsx"] = str(p)
    if a.qa:
        visual_qa(pdf_path, md, out_dir, rep)

    print(json.dumps({"outputs": rep.outputs, "warnings": rep.warnings, "qa": rep.qa}, ensure_ascii=False, indent=2))
    return 0 if rep.outputs else 1


if __name__ == "__main__":
    sys.exit(main())
