"""Unit tests cho lint_doc.py — kiểm cả true positive lẫn false positive đã biết."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lint_doc import lint_text, main  # noqa: E402


def rules(text: str) -> list[tuple[str, str, str]]:
    return [(f.rule, f.severity, f.match.lower()) for f in lint_text(text, term_groups=[])]


# ---------- True positives ----------

def test_vague_in_requirement_is_high() -> None:
    r = rules("FR-001. Hệ thống phải phản hồi nhanh chóng.")
    assert ("R04", "high", "nhanh chóng") in r
    # "nhanh" không bị báo trùng trong "nhanh chóng"
    assert sum(1 for x in r if x[0] == "R04") == 1


def test_vague_in_prose_is_medium() -> None:
    assert ("R04", "medium", "thân thiện") in rules("Giao diện thân thiện với khách.")


def test_placeholder_open_list_and_or() -> None:
    r = rules("FR-002. Hệ thống phải hỗ trợ PDF, DOCX, v.v. và/hoặc gửi email. Ngưỡng: TBD")
    kinds = {x[0] for x in r}
    assert {"R01", "R02", "R03"} <= kinds


def test_english_terms() -> None:
    r = rules("The API shall respond quickly and handle errors appropriately, etc.")
    m = {x[2] for x in r}
    assert {"quickly", "appropriately"} <= m
    assert any(x[0] == "R02" for x in r)


def test_weak_modal_only_in_requirement() -> None:
    assert any(x[0] == "R05" for x in rules("FR-003. Người dùng có thể xuất file CSV."))
    assert not any(x[0] == "R05" for x in rules("Ở bước này người dùng có thể đọc hướng dẫn."))


def test_comparative_without_number() -> None:
    assert any(x[0] == "R06" for x in rules("Phiên bản mới xử lý nhanh hơn."))
    assert not any(x[0] == "R06" for x in rules("Giảm thời gian từ 8 s xuống 4 s, nhanh hơn 50%."))


def test_duplicate_id() -> None:
    text = "- FR-010. A phải làm X.\n- FR-010. B phải làm Y.\nXem FR-010 ở trên."
    dups = [f for f in lint_text(text, term_groups=[]) if f.rule == "R09"]
    assert len(dups) == 1 and dups[0].match == "FR-010"


def test_reference_is_not_definition() -> None:
    text = "- FR-010. A phải làm X.\nAC-001 kiểm tra FR-010."
    assert not [f for f in lint_text(text, term_groups=[]) if f.rule == "R09"]


def test_term_inconsistency() -> None:
    text = "Người dùng đăng nhập.\nNgười sử dụng đăng xuất."
    found = [f for f in lint_text(text) if f.rule == "R10"]
    assert len(found) == 1


def test_passive_without_agent() -> None:
    assert any(x[0] == "R08" for x in rules("FR-004. Dữ liệu phải được xử lý trước 23:00."))
    assert not any(x[0] == "R08" for x in rules("FR-005. Dữ liệu phải được xử lý bởi service billing-worker."))


# ---------- False positives đã biết phải KHÔNG báo ----------

@pytest.mark.parametrize("text", [
    "Ứng viên đã tốt nghiệp đại học.",
    "Quan hệ một-nhiều giữa Order và OrderItem.",
    "Mỗi đơn chứa một hoặc nhiều sản phẩm.",
    "Tối đa 5 lần, at most 5 retries.",
    "Tầm nhìn sản phẩm năm 2027.",
    "Khoảng thời gian hiệu lực là 30 ngày.",
    "Họp với các bên liên quan.",
    "Sort by most recent first.",
])
def test_no_false_positive(text: str) -> None:
    assert not [x for x in rules(text) if x[0] == "R04"], rules(text)


def test_skip_code_quotes_confirm_and_open_questions() -> None:
    text = (
        "```\nfast = True  # TBD\n```\n"
        "Hiển thị thông báo \"Vui lòng thử lại sau ít phút\" và `quick_mode`.\n"
        "FR-006. Thời gian chờ là [CẦN XÁC NHẬN: khoảng bao nhiêu giây?].\n"
        "## Open Questions\n| OQ-001 | Ngưỡng hợp lý là bao nhiêu? TBD |\n"
        "## Phần khác\nGiao diện đơn giản.\n"
    )
    r = rules(text)
    assert [x for x in r if x[2] == "đơn giản"], "section sau Open Questions phải được lint lại"
    assert not [x for x in r if x[2] in {"fast", "tbd", "khoảng", "hợp lý", "ít"}], r


def test_lint_disable_block() -> None:
    text = "<!-- lint-disable -->\nNhanh, dễ dùng, v.v.\n<!-- lint-enable -->\nỔn định."
    r = rules(text)
    assert [x[2] for x in r] == ["ổn định"]


def test_clean_requirement_has_no_findings() -> None:
    text = ("FR-020. Khi người dùng nhấn **Thanh toán**, hệ thống phải trả kết quả trong ≤ 5 giây (p95).\n"
            "FR-021. Nếu cổng thanh toán trả mã lỗi `51`, hệ thống phải hiển thị \"Số dư không đủ\".")
    assert lint_text(text, term_groups=[]) == []


def test_cli_fail_on(tmp_path: Path) -> None:
    f = tmp_path / "a.md"
    f.write_text("FR-001. Hệ thống phải chạy nhanh.", encoding="utf-8")
    assert main([str(f), "--fail-on", "high"]) == 1
    f.write_text("FR-001. Hệ thống phải phản hồi trong ≤ 2 giây.", encoding="utf-8")
    assert main([str(f), "--fail-on", "high", "--format", "json"]) == 0


def test_hierarchical_ids_not_duplicates() -> None:
    text = "- AC-007.1 Given A When B Then C\n- AC-007.2 Given A When D Then E\n- AC-007.1 trùng thật"
    dups = [f.match for f in lint_text(text, term_groups=[]) if f.rule == "R09"]
    assert dups == ["AC-007.1"]


def test_prohibition_modal_not_passive() -> None:
    assert not any(x[0] == "R08" for x in rules("FR-009. OTP dạng plaintext không được lưu trong database."))


def test_same_id_in_definition_and_traceability_table_ok() -> None:
    text = ("| ID | Yêu cầu |\n|---|---|\n| FR-001 | Hệ thống phải gửi OTP. |\n\n"
            "## Truy vết\n| FR | AC |\n|---|---|\n| FR-001 | AC-001 |\n")
    assert not [f for f in lint_text(text, term_groups=[]) if f.rule == "R09"]


def test_soft_term_never_high() -> None:
    r = rules("FR-030. Hệ thống phải cho phép áp dụng nhiều voucher trong một đơn.")
    assert ("R04", "medium", "nhiều") in r


def test_user_story_heading_not_term_conflict() -> None:
    text = "## User stories\nNgười dùng đổi điểm."
    assert not [f for f in lint_text(text) if f.rule == "R10"]


def test_mapping_table_ids_not_duplicates() -> None:
    text = "| ID v0.3 | ID v0.4 | Ghi chú |\n|---|---|---|\n| FR-004 | FR-004 | giữ |\n| FR-004 | FR-007 | tách |\n"
    assert not [f for f in lint_text(text, term_groups=[]) if f.rule == "R09"]


def test_english_gaps_found_in_smoke_run() -> None:
    r = rules("FR-040. When the user clicks Export, the system shall return the file right away. Users can export a lot of rows.")
    kinds = {(x[0], x[2]) for x in r}
    assert ("R04", "right away") in kinds and ("R04", "a lot of") in kinds and ("R05", "can") in kinds
