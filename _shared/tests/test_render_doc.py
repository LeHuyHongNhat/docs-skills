"""Tests cho render_doc.py: logic thuần + smoke test end-to-end (skip nếu thiếu công cụ)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import render_doc as rd  # noqa: E402

SAMPLE = """# PRD: Đổi điểm
| Phiên bản | Ngày | Owner | Trạng thái |
|---|---|---|---|
| 0.1 | 2026-11-03 | Nhật | Draft |

## 1. Business rules
| ID | Quy tắc | Nguồn |
|---|---|---|
| BR-001 | 100 điểm = 10.000 VND. Hạn điểm [CẦN XÁC NHẬN: 6 hay 12 tháng] | note `a\\|b` |

## 2. Luồng
```mermaid
flowchart LR
  A[Đổi điểm] --> B{Đủ điểm?}
  B -->|Có| C[Phát voucher]
  B -->|Không| D[Báo lỗi]
```
Marker trong code: `[CẦN XÁC NHẬN: OQ-001]` và `x = 1`.
"""


def test_extract_tables_and_heading() -> None:
    ts = rd.extract_tables(SAMPLE)
    assert [t.heading for t in ts] == ["PRD: Đổi điểm", "1. Business rules"]
    assert ts[1].rows[0][0] == "BR-001" and ts[1].rows[0][2] == "note a|b"


def test_mark_confirm_skips_real_code_but_unwraps_marker() -> None:
    out = rd.mark_confirm(SAMPLE)
    assert out.count('{.confirm custom-style="Confirm"}') == 2
    assert "`x = 1`" in out


def test_mermaid_left_alone_without_mmdc(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rd.shutil, "which", lambda _: None)
    rep = rd.Report()
    assert "```mermaid" in rd.render_mermaid(SAMPLE, tmp_path, "svg", rep)
    assert rep.warnings


@pytest.mark.skipif(not (shutil.which("pandoc") and shutil.which("mmdc")), reason="thiếu pandoc/mmdc")
def test_end_to_end(tmp_path: Path) -> None:
    src = tmp_path / "prd.md"
    src.write_text(SAMPLE, encoding="utf-8")
    assert rd.main([str(src), "--to", "html,pdf,docx,xlsx", "--out-dir", str(tmp_path / "out"), "--qa"]) == 0
    html = (tmp_path / "out" / "prd.html").read_text(encoding="utf-8")
    assert 'class="confirm"' in html and "image/svg+xml" in html and "flowchart LR" not in html
    import docx
    import openpyxl
    d = docx.Document(str(tmp_path / "out" / "prd.docx"))
    assert d.inline_shapes and d.tables
    wb = openpyxl.load_workbook(tmp_path / "out" / "prd.xlsx")
    assert wb.sheetnames[0] == "Mục lục" and len(wb.sheetnames) == 2  # Vietnamese doc → Vietnamese labels  # bảng metadata không thành sheet
    assert wb.worksheets[1].freeze_panes == "A2"
    assert (tmp_path / "out" / "prd.pdf").stat().st_size > 5000


@pytest.mark.skipif(not shutil.which("pandoc"), reason="thiếu pandoc")
def test_mobile_cards(tmp_path: Path) -> None:
    md = "# T\n\n## A\n| ID | Kiểu | Null | Mô tả |\n|---|---|---|---|\n| id | BIGINT | Không | Khóa chính |\n"
    src = tmp_path / "m.md"
    src.write_text(md, encoding="utf-8")
    assert rd.main([str(src), "--to", "html", "--page", "mobile", "--out-dir", str(tmp_path)]) == 0
    html = (tmp_path / "m.html").read_text(encoding="utf-8")
    assert 'class="cards"' in html and "<table" not in html.split("<body")[1]


def test_sheet_names_keep_identifiers(tmp_path: Path) -> None:
    md = ("# DD\n## 4.3 Bảng `order_items` — chi tiết\n| Cột | Kiểu |\n|---|---|\n| id | BIGINT |\n"
          "## 4.1 Bảng customers\n| Cột | Kiểu |\n|---|---|\n| id | BIGINT |\n")
    src = tmp_path / "d.md"
    src.write_text(md, encoding="utf-8")
    out = rd.to_xlsx(md, tmp_path / "d.xlsx", "DD", src, rd.Report())
    import openpyxl
    assert openpyxl.load_workbook(out).sheetnames == ["Mục lục", "order_items", "customers"]


def test_labels_follow_document_language(tmp_path: Path) -> None:
    en = "# DD\n## Table `orders`\n| Column | Type |\n|---|---|\n| id | BIGINT |\n"
    src = tmp_path / "e.md"
    src.write_text(en, encoding="utf-8")
    import openpyxl
    out = rd.to_xlsx(en, tmp_path / "e.xlsx", "DD", src, rd.Report())
    assert openpyxl.load_workbook(out).sheetnames == ["Index", "orders"]
    assert rd.doc_lang(en) == "en" and rd.doc_lang("# Tài liệu đặc tả yêu cầu nghiệp vụ") == "vi"
