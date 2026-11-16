"""Tests cho post_check.py (community-post-writer)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("post_check", ROOT / "community-post-writer/scripts/post_check.py")
assert _spec and _spec.loader
pc = importlib.util.module_from_spec(_spec)
sys.modules["post_check"] = pc
_spec.loader.exec_module(pc)

GOOD_VI = """Mình thử 3 cách cắt tài liệu (chunking) cho chatbot nội bộ, và cách "đắt" nhất không thắng.

Chunking là bước chia tài liệu dài thành các đoạn nhỏ trước khi tìm kiếm. Mình đo trên 50 câu hỏi thật của team:
• Cắt cố định 500 token: 31/50 câu đúng
• Cắt theo heading: 38/50

Mình mới chạy 1 lần, nên chưa dám kết luận cho mọi loại tài liệu.

Mọi người đang chunk theo cách nào?
"""

BAD_VI = """# SỐC: Semantic chunking là GAME-CHANGER cho RAG!!!

Xin chào mọi người, hôm nay mình xin chia sẻ về một chủ đề cực kỳ hay mà ai làm AI cũng nên biết, đó là chunking trong RAG, một kỹ thuật đóng vai trò vô cùng quan trọng trong thời đại công nghệ 4.0 khi các mô hình ngày càng mạnh và được ứng dụng rộng rãi trong doanh nghiệp.

**Kết quả**: semantic chunking tăng độ chính xác 40% so với cách cũ.

| Cách | Điểm |
|---|---|
| A | 1 |
"""


def codes(findings) -> set[str]:
    return {f.code for f in findings}


def test_clean_facebook_post_has_no_findings() -> None:
    findings, stats = pc.check(GOOD_VI, "facebook")
    assert not [f for f in findings if f.severity in ("high", "medium")], findings
    assert stats["lang"] == "vi"


def test_bad_post_is_caught_on_every_axis() -> None:
    findings, _ = pc.check(BAD_VI, "facebook")
    c = codes(findings)
    assert {"PLATFORM-MD", "TITLE-HYPE", "TITLE-CAPS", "TITLE-PUNCT", "HYPE", "CLICHE",
            "HOOK-FILLER", "SENT-LONG", "ACRONYM", "UNSOURCED"} <= c
    assert not any(f.code == "ACRONYM" and "GAME" in f.message for f in findings)  # hyphenated word ≠ acronym
    assert any(f.code == "ACRONYM" and "RAG" in f.message for f in findings)


def test_markdown_is_fine_on_forums() -> None:
    findings, _ = pc.check(BAD_VI, "forum")
    assert "PLATFORM-MD" not in codes(findings)


def test_defined_acronym_and_sourced_number_pass() -> None:
    md = ("Retrieval-Augmented Generation (RAG) ghép tìm kiếm với LLM. "
          "Trong thử nghiệm của mình, độ chính xác tăng 14% trên 50 câu.\n")
    c = codes(pc.check(md, "forum")[0])
    assert "ACRONYM" not in c and "UNSOURCED" not in c


def test_length_limits() -> None:
    long_post = "Một câu ngắn có nguồn. " * 200
    assert "LENGTH" in codes(pc.check(long_post, "linkedin")[0])
    thread = "a" * 100 + "\n---\n" + "b" * 300
    f = [x for x in pc.check(thread, "x")[0] if x.code == "LENGTH"]
    assert len(f) == 1 and "post 2" in f[0].message


def test_long_markdown_post_needs_headings() -> None:
    body = "\n\n".join("This short sentence explains one idea clearly. It has a second line." for _ in range(60))
    assert "NO-HEADINGS" in codes(pc.check(body, "forum")[0])


def test_export_plain_text_is_platform_safe() -> None:
    md = ("---\ntitle: T\n---\n## Kết quả\n**Đậm** và [link](https://a.b).\n\n- ý 1\n\n"
          "| A | B |\n|---|---|\n| 1 | 2 |\n\n```chart\ntype: bar\ntitle: Biểu đồ X\n```\n")
    out = pc.to_plain(md, "facebook")
    assert "**" not in out and "](" not in out and "|" not in out and "#" not in out
    assert "link (https://a.b)" in out and "• ý 1" in out and "[Ảnh: Biểu đồ X]" in out
    assert "PLATFORM-MD" not in codes(pc.check(out, "facebook")[0])


def test_cli_json(tmp_path: Path, capsys) -> None:
    p = tmp_path / "p.md"
    p.write_text(GOOD_VI, encoding="utf-8")
    assert pc.main([str(p), "--platform", "facebook", "--json"]) == 0
    assert '"words"' in capsys.readouterr().out


RIGOROUS_EN = """In our test, heading-based chunking answered 38 of 50 questions and fixed-size chunking 31 of 50.
The difference is +14 points (95% CI -4 to +31), so we could not tell the two apart.

## Limits
- One run per configuration, n = 50 questions, September 2026.
- Scanned PDFs were not tested. The data is internal and cannot be published; versions: bge-m3, pgvector 0.7.

Source: our own experiment. What sample size do you use?
"""

SLOPPY_QUANT = """Our momentum strategy beats the index: Sharpe 2.1 in the backtest, which proves the alpha is real.
Returns increased 40% thanks to the new signal. The improvement is significant.
"""


def test_rigor_mode_passes_a_careful_post() -> None:
    findings, _ = pc.check(RIGOROUS_EN, "forum", rigor=True)
    assert not [f for f in findings if f.code.startswith("RIGOR")], findings


def test_rigor_mode_catches_unsupported_claims() -> None:
    c = codes(pc.check(SLOPPY_QUANT, "forum", rigor=True)[0])
    assert {"RIGOR-N", "RIGOR-UNCERTAINTY", "RIGOR-ABSOLUTE", "RIGOR-SIGNIFICANT", "RIGOR-CAUSAL", "RIGOR-LIMITS",
            "RIGOR-SOURCE", "RIGOR-QUANT-OOS", "RIGOR-QUANT-COSTS", "RIGOR-QUANT-TRIALS", "RIGOR-QUANT-LOOKAHEAD"} <= c


def test_rigor_is_opt_in_and_ai_is_not_ai_cung() -> None:
    assert not [f for f in pc.check(SLOPPY_QUANT, "forum")[0] if f.code.startswith("RIGOR")]
    md = "AI cũng cần dữ liệu tốt. Nguồn: thử nghiệm nội bộ năm 2026, n = 50 câu, giới hạn: chạy 1 lần, không công bố dữ liệu.\n"
    assert "RIGOR-ABSOLUTE" not in codes(pc.check(md, "forum", rigor=True)[0])
    assert "RIGOR-ABSOLUTE" in codes(pc.check("Ai cũng nên dùng cách này, n = 50.\n", "forum", rigor=True)[0])


def test_sources_section_proper_names_and_org_acronyms_are_not_flagged() -> None:
    md = ("# Nghiên cứu METR đo gì\n\n"
          "METR (Model Evaluation & Threat Research) đo 16 lập trình viên. Kết quả tăng 19%.\n\n"
          "Bản tóm tắt của CXO Advisory ghi khác. Giới hạn: n = 16, năm 2025, không công bố dữ liệu.\n\n"
          "## Nguồn\n\n- Jensen (2021), NBER Working Paper 28432, https://example.org/x\n")
    findings, _ = pc.check(md, "forum", rigor=True)
    c = codes(findings)
    assert "TITLE-CAPS" not in c and "RIGOR-ML-RUNS" not in c
    assert not [f for f in findings if f.code == "ACRONYM"], findings
    assert [f.severity for f in findings if f.code == "UNSOURCED"] == ["info"]


def test_shouting_title_is_still_flagged() -> None:
    assert "TITLE-CAPS" in codes(pc.check("# Cách này SIÊU NHANH\n\nNội dung ngắn có nguồn.\n", "forum")[0])


AI_SLOP_EN = """# Chunking Strategies

Here's the thing: chunking is not just a preprocessing step, but the foundation of retrieval. Let's dive in.

## Why It Matters

Chunking plays a crucial role in the evolving landscape of retrieval. It is robust — it is seamless — it is pivotal — and it helps you leverage your data — every day.

## Results

No errors. No warnings. All green. That's it.

I hope this helps!
"""


def test_structural_tells_strong_and_cluster() -> None:
    c = codes(pc.check(AI_SLOP_EN, "forum")[0])
    assert {"TELL-CONTRAST", "TELL-RUN-UP", "TELL-CLOSER", "TELL-CHATBOT", "TELL-SIGNIFICANCE", "TELL-CLUSTER",
            "HEADING-GENERIC"} <= c


def test_vietnamese_tells_and_quoted_phrases_are_left_alone() -> None:
    vi = "Chunking không chỉ là bước tiền xử lý mà còn là nền tảng của tìm kiếm. Sự thật là nhiều team bỏ qua nó.\n"
    assert {"TELL-CONTRAST", "TELL-RUN-UP"} <= codes(pc.check(vi, "forum")[0])
    quoted = 'Bài gốc mở đầu bằng câu "Here\'s the thing" và mình giữ nguyên khi trích. Nguồn: thử nghiệm nội bộ.\n'
    assert "TELL-RUN-UP" not in codes(pc.check(quoted, "forum")[0])


def test_one_weak_signal_alone_is_only_info() -> None:
    md = "\n".join(f"- **Mục {i}.** Nội dung của mục này được mô tả ngắn gọn." for i in range(5)) + "\n"
    findings, _ = pc.check(md, "forum")
    assert [f.severity for f in findings if f.code.startswith("TELL")] == ["info"]


def test_headline_number_must_reappear() -> None:
    bad = "# Nhanh hơn 40% với cache\n\nBài này kể cách team mình thêm cache.\n\n## Cách làm\n\nThêm Redis vào trước DB.\n"
    assert "HEADLINE-NUMBER" in codes(pc.check(bad, "forum")[0])
    good = bad + "\np95 giảm từ 500 ms xuống 300 ms, tức nhanh hơn 40% (đo trên 3 ngày).\n"
    assert "HEADLINE-NUMBER" not in codes(pc.check(good, "forum")[0])
    chart = bad + "\n```chart\ntype: bar\ncategories: [a]\nvalues: [40]\n```\n"
    assert "HEADLINE-NUMBER" not in codes(pc.check(chart, "forum")[0])


def test_ci_overlap_and_ci_meaning_are_flagged_in_rigor_mode() -> None:
    md = ("Ba khoảng tin cậy chồng lên nhau nên chưa xếp hạng được, n = 50, năm 2026. Giới hạn: 1 lần chạy.\n\n"
          "Khoảng tin cậy 95% là vùng mà giá trị thật nhiều khả năng nằm trong. Nguồn: thử nghiệm nội bộ, không công bố dữ liệu.\n")
    c = codes(pc.check(md, "forum", rigor=True)[0])
    assert {"RIGOR-CI-OVERLAP", "RIGOR-CI-MEANING"} <= c
