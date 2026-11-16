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
