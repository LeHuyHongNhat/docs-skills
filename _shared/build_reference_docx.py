"""Sinh assets/reference.docx (style template cho pandoc) từ default của pandoc.

Chạy lại khi muốn đổi thiết kế DOCX. Font Arial vì có sẵn trên mọi máy Windows/macOS và hỗ trợ
đầy đủ dấu tiếng Việt — font đẹp hơn nhưng không có sẵn sẽ bị Word thay bằng font mặc định.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

OUT = Path(__file__).parent / "assets" / "reference.docx"
INK, INK2, ACCENT, CONFIRM = "1B2130", "4A5263", "2A4FB8", "8A5A00"
FONT, MONO = "Arial", "Consolas"


def rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)


def set_font(style, name: str, size: float | None = None, color: str | None = None, bold: bool | None = None) -> None:
    f = style.font
    f.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rfonts.get(qn(attr)) is not None:
            del rfonts.attrib[qn(attr)]
    if size:
        f.size = Pt(size)
    if color:
        f.color.rgb = rgb(color)
    if bold is not None:
        f.bold = bold


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pandoc", "-o", str(OUT), "--print-default-data-file", "reference.docx"], check=True)
    d = docx.Document(str(OUT))
    raw = d.styles
    by_name = {x.name.lower(): x for x in raw}

    class _St:  # tra style theo tên, không phân biệt hoa thường (pandoc đặt "heading 1")
        def __getitem__(self, k: str):
            return by_name[k.lower()]

        def __iter__(self):
            return iter(raw)

        def add_style(self, *a):
            return raw.add_style(*a)

    st = _St()
    for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
        s = st[name]
        set_font(s, FONT, 10.5, INK)
        pf = s.paragraph_format
        pf.space_after = Pt(6)
        pf.line_spacing = 1.25
    st["Compact"].paragraph_format.space_after = Pt(2)
    # Sau khi shift heading: H2 markdown → Heading 1 của Word, nên Heading 1 cần khoảng trắng phía trên
    for lvl, size, sb, sa, color in ((1, 16, 20, 6, INK), (2, 13, 14, 4, INK), (3, 11.5, 10, 3, INK), (4, 10.5, 8, 2, INK2)):
        s = st[f"Heading {lvl}"]
        set_font(s, FONT, size, color, bold=True)
        s.paragraph_format.space_before = Pt(sb)
        s.paragraph_format.space_after = Pt(sa)
        s.paragraph_format.keep_with_next = True
    set_font(st["Title"], FONT, 24, INK, bold=True)
    set_font(st["Subtitle"], FONT, 13, INK2)
    for name in ("Caption", "Image Caption", "Table Caption"):
        set_font(st[name], FONT, 8.5, "6B7385")
    if "Source Code" in [s.name for s in st]:
        set_font(st["Source Code"], MONO, 9, INK)
    for name in ("Block Text",):
        s = st[name]
        set_font(s, FONT, 10, INK2)
    # Character style cho marker [CẦN XÁC NHẬN] — pandoc custom-style="Confirm"
    if "Confirm" not in [s.name for s in st]:
        c = st.add_style("Confirm", WD_STYLE_TYPE.CHARACTER)
    else:
        c = st["Confirm"]
    set_font(c, FONT, None, CONFIRM, bold=True)
    rpr = c.element.get_or_add_rPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "FFF6E0")
    rpr.append(shd)
    # Hyperlink
    for s in st:
        if s.name == "Hyperlink":
            s.font.color.rgb = rgb(ACCENT)
    # Lề trang A4
    from docx.shared import Mm
    for sec in d.sections:
        sec.page_width, sec.page_height = Mm(210), Mm(297)
        sec.left_margin = sec.right_margin = Mm(20)
        sec.top_margin, sec.bottom_margin = Mm(20), Mm(20)
    _footer(d)
    d.save(str(OUT))
    print("wrote", OUT)


def _field(run, instr: str) -> None:
    for kind, text in (("begin", None), ("instr", instr), ("separate", None), ("end", None)):
        if kind == "instr":
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = f" {text} "
            run._r.append(it)
        else:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            run._r.append(fc)


def _footer(d) -> None:
    """Footer: <Tiêu đề tài liệu> · Trang N/M — pandoc giữ header/footer của reference.docx;
    TITLE lấy từ core property mà pandoc đặt theo metadata title."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    for sec in d.sections:
        f = sec.footer
        f.is_linked_to_previous = False
        p = f.paragraphs[0] if f.paragraphs else f.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for txt, fld in ((None, "TITLE"), (" · Trang ", "PAGE"), ("/", "NUMPAGES")):
            if txt:
                r = p.add_run(txt)
                r.font.size, r.font.color.rgb = Pt(8), rgb("6B7385")
            r = p.add_run()
            r.font.size, r.font.color.rgb = Pt(8), rgb("6B7385")
            _field(r, fld)


if __name__ == "__main__":
    main()
