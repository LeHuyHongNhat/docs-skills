#!/usr/bin/env python3
"""auto_checks.py — kiểm tra deterministic trên output của từng run, ghi <run>/auto_checks.json.

Các check này là bằng chứng cứng cho grader (LLM) và là thước đo không thiên vị
(không phụ thuộc judge). Usage: python auto_checks.py <iteration_dir>
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SHARED = Path("/home/claude/doc-skills/_shared/scripts")
sys.path.insert(0, str(SHARED))
from lint_doc import lint_text, summarize  # noqa: E402

CONFIRM_RE = re.compile(r"\[(?:CẦN XÁC NHẬN|TO CONFIRM)[^\]]*\]", re.I)

DELIVERABLE = {
    "prd-loyalty-from-meeting-notes": ["prd_doi_diem.md"],
    "metric-definition-dau-retention": ["metric_definitions.md"],
    "readme-order-service": ["README.md"],
    "architecture-doc-order-service": ["architecture.md"],
    "flowchart-purchase-approval": ["dac_ta_quy_trinh_mua_hang.md"],
    "erd-to-data-dictionary": ["data_dictionary.md"],
    "review-otp-srs-draft": ["srs_otp_v0.4.md", "review_srs_otp.md"],
    "rewrite-export-feature-brief": ["export_feature_spec.md"],
    "prd-referral-docx": ["prd_gioi_thieu_ban.md"],
    "erd-export-xlsx-pdf": ["data_dictionary.md"],
}
BINARY = {"prd-referral-docx": ["prd_gioi_thieu_ban.docx"],
          "erd-export-xlsx-pdf": ["data_dictionary.xlsx", "data_dictionary.pdf"]}


def mermaid_blocks(text: str) -> list[str]:
    return re.findall(r"```mermaid\s*\n(.*?)```", text, re.S)


def render_ok(block: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / "d.mmd").write_text(block, encoding="utf-8")
        (p / "pp.json").write_text('{"args":["--no-sandbox"]}')
        r = subprocess.run(["mmdc", "-p", str(p / "pp.json"), "-i", str(p / "d.mmd"), "-o", str(p / "d.svg")],
                           capture_output=True, text=True, timeout=120)
        return r.returncode == 0, (r.stderr or "")[-300:]


def binary_checks(case: str, run: Path) -> dict[str, Any]:
    """Check định dạng: XLSX (sheet/freeze/header đậm), PDF (font nhúng, text có dấu, không lộ mã Mermaid),
    DOCX (heading style, bảng full ngang, style marker). Kèm ảnh preview trang để grader xem bằng mắt."""
    res: dict[str, Any] = {}
    for fn in BINARY.get(case, []):
        f = run / "outputs" / fn
        if not f.exists():
            res[fn] = {"exists": False}
            continue
        info: dict[str, Any] = {"exists": True, "bytes": f.stat().st_size}
        prev = run / "previews"
        prev.mkdir(exist_ok=True)
        if f.suffix == ".xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(f)
            sheets = []
            for ws in wb.worksheets:
                hdr = [c for c in ws[1] if c.value is not None]
                sheets.append({"name": ws.title, "rows": ws.max_row, "cols": ws.max_column,
                               "freeze": ws.freeze_panes, "header_bold": bool(hdr) and all(bool(c.font and c.font.b) for c in hdr),
                               "autofilter": bool(ws.auto_filter and ws.auto_filter.ref)})
            info["sheets"] = sheets
            info["table_sheets_found"] = {t: any(t in sh["name"].lower() for sh in sheets)
                                          for t in ["customers", "orders", "order_items", "products", "payments"]}
        if f.suffix == ".pdf":
            txt = subprocess.run(["pdftotext", str(f), "-"], capture_output=True, text=True).stdout
            fonts = subprocess.run(["pdffonts", str(f)], capture_output=True, text=True).stdout.splitlines()[2:]
            info["pages"] = len(re.findall(r"\f", txt)) or None
            info["fonts_all_embedded"] = all(" yes " in ln for ln in fonts if ln.strip())
            info["vietnamese_ok"] = all(w in txt for w in ["Khóa", "bảng"]) or ("khóa" in txt.lower() and "bảng" in txt)
            info["mermaid_source_leak"] = any(k in txt for k in ["erDiagram", "||--o{", "flowchart TD", "sequenceDiagram"])
            subprocess.run(["pdftoppm", "-r", "60", "-png", str(f), str(prev / f.stem)], check=False)
        if f.suffix == ".docx":
            import docx
            d = docx.Document(str(f))
            styles = [pp.style.name for pp in d.paragraphs]
            info["heading_paragraphs"] = sum(1 for x in styles if x.lower().startswith("heading"))
            info["tables"] = len(d.tables)
            info["confirm_runs"] = sum(1 for pp in d.paragraphs for r in pp.runs if "XÁC NHẬN" in r.text)
            info["confirm_styled_runs"] = sum(1 for pp in d.paragraphs for r in pp.runs
                                              if "XÁC NHẬN" in r.text and (r.style.name != "Default Paragraph Font" or r.font.highlight_color or r.font.color.rgb))
            pdf_dir = run / "previews" / "docx2pdf"
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(pdf_dir), str(f)],
                           capture_output=True, timeout=180)
            pdf = pdf_dir / (f.stem + ".pdf")
            if pdf.exists():
                subprocess.run(["pdftoppm", "-r", "60", "-png", str(pdf), str(prev / (f.stem + "-docx"))], check=False)
        info["previews"] = sorted(str(x) for x in prev.glob("*.png"))
        res[fn] = info
    return res


def lint_stats(text: str) -> dict[str, Any]:
    fs = lint_text(text)
    high_outside_confirm = [f for f in fs if f.severity == "high"]
    return {"summary": summarize(fs), "dup_ids": [f.match for f in fs if f.rule == "R09"],
            "high_examples": [f"{f.line}:{f.rule}:{f.match}" for f in high_outside_confirm[:8]],
            "confirm_markers": len(CONFIRM_RE.findall(text)), "chars": len(text), "words": len(text.split())}


def case_specific(case: str, text: str) -> dict[str, Any]:
    t = text
    low = t.lower()
    out: dict[str, Any] = {}
    if case == "readme-order-service":
        eps = {"GET /health": r"GET`?\s*\|?\s*`?/health",
               "POST /api/v1/orders": r"POST`?\s*\|?\s*`?/api/v1/orders`?(?!/)",
               "GET /api/v1/orders": r"GET`?\s*\|?\s*`?/api/v1/orders`?(?![/{])",
               "GET /api/v1/orders/{order_id}": r"GET`?\s*\|?\s*`?/api/v1/orders/\{order_id\}`?(?!/)",
               "POST /api/v1/orders/{order_id}/cancel": r"POST`?\s*\|?\s*`?/api/v1/orders/\{order_id\}/cancel"}
        out["endpoints_found"] = {k: bool(re.search(v, t)) for k, v in eps.items()}
        out["invented_endpoint_markers"] = sorted(set(re.findall(r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+`?(/(?:login|auth|register|users)[^\s`|]*)", t)
                                                       + re.findall(r"\b(PUT|PATCH|DELETE)\s+`?/api", t)))
        out["env_vars_found"] = {v: v in t for v in ["DATABASE_URL", "REDIS_URL", "JWT_SECRET", "ORDER_MAX_ITEMS", "LOG_LEVEL", "SMTP_HOST"]}
        out["python_311"] = "3.11" in t
    if case in ("architecture-doc-order-service", "flowchart-purchase-approval", "readme-order-service"):
        blocks = mermaid_blocks(t)
        res = [render_ok(b) for b in blocks]
        out["mermaid_blocks"] = len(blocks)
        out["mermaid_render_ok"] = [ok for ok, _ in res]
        out["mermaid_errors"] = [e for ok, e in res if not ok]
    if case == "architecture-doc-order-service":
        out["mentions"] = {k: k in t for k in ["orders.created", "worker/main.py", "app/services/orders.py", "BRPOP", "LPUSH", "SMTP"]}
    if case == "flowchart-purchase-approval":
        truth = json.loads(Path("/home/claude/fixtures/diagrams/purchase_truth.json").read_text())
        keys = truth["actors"] + ["Tạo đề nghị mua hàng", "Bổ sung chứng từ", "vượt ngân sách", "Tạo PO",
                                  "nhà cung cấp", "Yêu cầu bổ sung", "Hoàn tất", "Hủy"]
        out["label_recall"] = {k: k.lower() in low for k in keys}
        out["label_recall_rate"] = round(sum(out["label_recall"].values()) / len(keys), 3)
        out["threshold_normalized"] = "50.000.000" in t
        out["equal_50tr_gap_hint"] = bool(re.search(r"(đúng|bằng)\s*(bằng\s*)?50(\.000\.000| triệu|tr)", low)) or "= 50" in t
    if case == "erd-to-data-dictionary":
        truth = json.loads(Path("/home/claude/fixtures/diagrams/erd_truth.json").read_text())
        cols = [(tb, c) for tb, cs in truth["tables"].items() for c in cs]
        # cột tìm theo tên trong toàn văn (xấp xỉ); tên chung như id luôn có
        out["tables_found"] = {tb: tb in t for tb in truth["tables"]}
        out["column_names_found_rate"] = round(sum(c in t for _, c in cols) / len(cols), 3)
        out["float_flagged"] = "FLOAT" in t and bool(re.search(r"float.{0,200}(decimal|numeric|làm tròn|sai số|precision)", low, re.S))
        out["fk_strings"] = {f"{a}->{b}": (a.split('.')[1] in t and b in t) for a, b in truth["fks"]}
    if case == "metric-definition-dau-retention":
        out["mentions"] = {k: k.lower() in low for k in ["push_received", "Asia/Ho_Chi_Minh", "is_internal", "anonymous_id",
                                                          "analytics.events", "analytics.users", "rolling", "unbounded"]}
        out["has_sql"] = "```sql" in low or "select" in low
    if case == "review-otp-srs-draft":
        out["mentions_5_vs_3"] = ("5 phút" in t and "3 phút" in t)
        out["mentions_fr004_dup"] = "FR-004" in t
    return out


def main() -> int:
    it = Path(sys.argv[1])
    for case_dir in sorted(p for p in it.iterdir() if p.is_dir() and (p / "eval_metadata.json").exists()):
        case = case_dir.name
        for run in sorted(p for p in case_dir.iterdir() if p.is_dir() and (p / "outputs").exists()):
            res: dict[str, Any] = {"case": case, "config": run.name, "files": {}}
            for fn in DELIVERABLE[case]:
                f = run / "outputs" / fn
                if not f.exists():
                    res["files"][fn] = {"exists": False}
                    continue
                text = f.read_text(encoding="utf-8", errors="replace")
                res["files"][fn] = {"exists": True, "lint": lint_stats(text), **case_specific(case, text)}
            res["binary"] = binary_checks(case, run)
            (run / "auto_checks.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
            print(case, run.name, json.dumps({k: (v.get("lint", {}).get("summary") if isinstance(v, dict) else v)
                                              for k, v in res["files"].items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
