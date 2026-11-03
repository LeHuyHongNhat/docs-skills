"""Unit tests cho check_diagram.py (diagram-to-doc) và scan_repo.py (codebase-doc-writer)."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REPO = Path("/home/claude/fixtures/order-service")


def load(rel: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(Path(rel).stem, ROOT / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclass cần module đã đăng ký
    spec.loader.exec_module(mod)
    return mod


cd = load("diagram-to-doc/scripts/check_diagram.py")
sr = load("codebase-doc-writer/scripts/scan_repo.py")


def levels(issues: list[tuple[str, str]], level: str) -> list[str]:
    return [m for lv, m in issues if lv == level]


# ---------------- check_diagram: flow ----------------

GOOD_FLOW = {
    "diagram_type": "flowchart",
    "nodes": [
        {"id": "S", "type": "start", "label": "Bắt đầu"},
        {"id": "A", "type": "task", "label": "Tạo đề nghị"},
        {"id": "D", "type": "decision", "label": "Giá trị?"},
        {"id": "B", "type": "task", "label": "GĐ duyệt"},
        {"id": "E", "type": "end", "label": "Hoàn tất"},
    ],
    "edges": [
        {"from": "S", "to": "A"}, {"from": "A", "to": "D"},
        {"from": "D", "to": "B", "label": "> 50tr"}, {"from": "D", "to": "E", "label": "< 50tr"},
        {"from": "B", "to": "E"},
    ],
}


def test_good_flow_has_no_errors() -> None:
    assert levels(cd.run(GOOD_FLOW), "ERROR") == []


def test_decision_missing_branch_is_error() -> None:
    inv = {**GOOD_FLOW, "edges": [e for e in GOOD_FLOW["edges"] if e.get("label") != "< 50tr"]}
    errs = levels(cd.run(inv), "ERROR")
    assert any("chỉ có 1 nhánh" in m for m in errs)


def test_unlabeled_decision_branch_is_error() -> None:
    edges = [dict(e) for e in GOOD_FLOW["edges"]]
    edges[2].pop("label")
    assert any("không có nhãn" in m for m in levels(cd.run({**GOOD_FLOW, "edges": edges}), "ERROR"))


def test_dead_end_and_dangling_edge() -> None:
    inv = {**GOOD_FLOW, "edges": GOOD_FLOW["edges"][:-1] + [{"from": "B", "to": "ZZ"}]}
    errs = levels(cd.run(inv), "ERROR")
    assert any("không tồn tại" in m for m in errs)


def test_loop_without_exit_warns() -> None:
    inv = {
        "diagram_type": "flowchart",
        "nodes": [{"id": "S", "type": "start"}, {"id": "A", "label": "a"}, {"id": "B", "label": "b"},
                  {"id": "E", "type": "end"}],
        "edges": [{"from": "S", "to": "A"}, {"from": "A", "to": "B"}, {"from": "B", "to": "A"}],
    }
    warns = levels(cd.run(inv), "WARN")
    assert any("không có đường tới end" in m for m in warns)


def test_unreadable_is_surfaced() -> None:
    inv = {**GOOD_FLOW, "unreadable": ["nhãn cạnh góc phải dưới"]}
    assert any("không đọc được" in m for m in levels(cd.run(inv), "WARN"))


# ---------------- check_diagram: ERD & sequence ----------------

ERD = {
    "diagram_type": "erd",
    "entities": [
        {"name": "customers", "attributes": [{"name": "id", "pk": True}]},
        {"name": "orders", "attributes": [{"name": "id", "pk": True}, {"name": "customer_id", "fk": "customers.id"}]},
    ],
    "relationships": [{"from": "customers", "to": "orders", "cardinality": "1:0..N"}],
}


def test_good_erd() -> None:
    assert cd.run(ERD) == []


def test_fk_to_missing_table_and_missing_relationship() -> None:
    bad = {**ERD, "entities": ERD["entities"] + [
        {"name": "payments", "attributes": [{"name": "id", "pk": True}, {"name": "order_id", "fk": "orderz.id"}]}]}
    assert any("orderz" in m for m in levels(cd.run(bad), "ERROR"))
    no_rel = {**ERD, "relationships": []}
    assert any("không có relationship" in m for m in levels(cd.run(no_rel), "WARN"))


def test_sequence_unknown_participant() -> None:
    inv = {"diagram_type": "sequence", "participants": ["User", "API"],
           "messages": [{"seq": 1, "from": "User", "to": "DB", "label": "q"}]}
    assert levels(cd.run(inv), "ERROR")


@pytest.mark.skipif(subprocess.run(["which", "mmdc"], capture_output=True).returncode != 0, reason="no mmdc")
@pytest.mark.parametrize("inv", [GOOD_FLOW, ERD, {"diagram_type": "sequence", "participants": ["User", "API"],
                                                     "messages": [{"seq": 1, "from": "User", "to": "API", "label": "POST /login"}]}])
def test_generated_mermaid_renders(inv: dict, tmp_path: Path) -> None:
    mmd = tmp_path / "d.mmd"
    mmd.write_text(cd.to_mermaid(inv), encoding="utf-8")
    pp = tmp_path / "pp.json"
    pp.write_text('{"args":["--no-sandbox"]}')
    r = subprocess.run(["mmdc", "-p", str(pp), "-i", str(mmd), "-o", str(tmp_path / "d.svg")],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr


# ---------------- scan_repo ----------------

@pytest.mark.skipif(not FIXTURE_REPO.exists(), reason="fixture repo missing")
def test_scan_repo_ground_truth() -> None:
    inv = sr.scan(FIXTURE_REPO)
    routes = {(h.detail["method"], h.detail["path"]) for h in inv.routes}
    assert routes == {
        ("GET", "/health"), ("POST", "/api/v1/orders"), ("GET", "/api/v1/orders"),
        ("GET", "/api/v1/orders/{order_id}"), ("POST", "/api/v1/orders/{order_id}/cancel"),
    }
    envs = {h.detail["name"] for h in inv.env_vars}
    assert envs == {"DATABASE_URL", "REDIS_URL", "JWT_SECRET", "ORDER_MAX_ITEMS", "LOG_LEVEL", "SMTP_HOST"}
    assert any(h.detail["instr"] == "FROM" and "3.11" in h.detail["value"] for h in inv.docker)
    assert any("idempotency" in h.detail["text"] for h in inv.todos)


def test_scan_repo_express_and_flask(tmp_path: Path) -> None:
    (tmp_path / "server.js").write_text("const r = express.Router();\nrouter.get('/users/:id', h)\napp.post(\"/login\", h)\n"
                                        "const k = process.env.API_KEY;\n")
    (tmp_path / "web.py").write_text("@bp.route('/items', methods=['GET', 'POST'])\ndef f(): pass\n")
    inv = sr.scan(tmp_path)
    routes = {(h.detail["method"], h.detail["path"]) for h in inv.routes}
    assert ("GET", "/users/:id") in routes and ("POST", "/login") in routes and ("GET,POST", "/items") in routes
    assert {h.detail["name"] for h in inv.env_vars} == {"API_KEY"}
