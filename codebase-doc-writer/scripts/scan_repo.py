#!/usr/bin/env python3
"""scan_repo.py — lập inventory có trích dẫn file:line cho một codebase, làm nền viết tài liệu.

Usage:
    python scan_repo.py <repo_dir> [--format md|json] [--max-depth 3]

Design notes:
- Chỉ dùng regex/heuristic (không import code của repo) → an toàn với repo lạ và chạy được
  mà không cần cài dependency. Đổi lại có thể sót route/env var khai báo theo cách lạ:
  output là *điểm khởi đầu để đọc code*, không phải nguồn sự thật cuối cùng.
- Mọi phát hiện kèm `file:line` để người viết tài liệu trích dẫn và kiểm lại.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
             ".mypy_cache", ".pytest_cache", ".idea", ".vscode", "target", ".next", "coverage", ".tox"}
LANG_EXT = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
            ".jsx": "JavaScript", ".go": "Go", ".java": "Java", ".kt": "Kotlin", ".rs": "Rust",
            ".rb": "Ruby", ".php": "PHP", ".cs": "C#", ".sql": "SQL", ".sh": "Shell"}
MANIFESTS = {"pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.py", "setup.cfg",
             "Pipfile", "poetry.lock", "package.json", "go.mod", "pom.xml", "build.gradle",
             "Cargo.toml", "Gemfile", "composer.json", "Dockerfile", "docker-compose.yml",
             "docker-compose.yaml", "compose.yaml", "Makefile", ".env.example", ".env.sample",
             "alembic.ini", "Procfile", "serverless.yml", "app.yaml"}
DOC_NAMES = re.compile(r"^(readme|changelog|contributing|architecture|adr-.*|.*\.md)$", re.I)

# (framework, extensions áp dụng, pattern) — lọc theo extension để decorator Python không bị khớp nhầm pattern Express.
ROUTE_PATTERNS: list[tuple[str, set[str], re.Pattern[str]]] = [
    ("fastapi", {".py"}, re.compile(r"@(?P<obj>\w+)\.(?P<method>get|post|put|patch|delete|head|options)\(\s*[\"'](?P<path>[^\"']*)[\"']")),
    ("flask", {".py"}, re.compile(r"@(?P<obj>\w+)\.route\(\s*[\"'](?P<path>[^\"']*)[\"'](?:.*methods\s*=\s*\[(?P<methods>[^\]]*)\])?")),
    ("express", {".js", ".ts", ".mjs", ".cjs"}, re.compile(r"(?<![@\w])(?P<obj>app|router)\.(?P<method>get|post|put|patch|delete)\(\s*[\"'`](?P<path>[^\"'`]*)[\"'`]")),
    ("spring", {".java", ".kt"}, re.compile(r"@(?P<method>Get|Post|Put|Patch|Delete)Mapping\(\s*(?:value\s*=\s*)?\"(?P<path>[^\"]*)\"")),
]
PREFIX_RE = re.compile(r"(?P<var>\w+)\s*=\s*(?:APIRouter|Blueprint)\((?P<args>[^)]*)\)")
PREFIX_ARG_RE = re.compile(r"(?:prefix|url_prefix)\s*=\s*[\"']([^\"']*)[\"']")
INCLUDE_RE = re.compile(r"include_router\(\s*(?:\w+\.)?(?P<var>\w+)(?:.*prefix\s*=\s*[\"'](?P<prefix>[^\"']*)[\"'])?")
ENV_PATTERNS = [
    re.compile(r"os\.environ\[\s*[\"'](?P<name>[A-Z][A-Z0-9_]+)[\"']\s*\]"),
    re.compile(r"os\.(?:environ\.get|getenv)\(\s*[\"'](?P<name>[A-Z][A-Z0-9_]+)[\"'](?:\s*,\s*(?P<default>[^)]+))?\)"),
    re.compile(r"process\.env\.(?P<name>[A-Z][A-Z0-9_]+)"),
    re.compile(r"process\.env\[\s*[\"'](?P<name>[A-Z][A-Z0-9_]+)[\"']\s*\]"),
    re.compile(r"System\.getenv\(\s*\"(?P<name>[A-Z][A-Z0-9_]+)\""),
    re.compile(r"^\s*(?P<name>[A-Z][A-Z0-9_]+)\s*=", re.M),  # chỉ áp dụng cho .env.example
]
SETTINGS_CLASS_RE = re.compile(r"class\s+(\w+)\((?:[\w.]*BaseSettings)\)")
SETTINGS_FIELD_RE = re.compile(r"^\s{4}(?P<name>[a-z_][a-z0-9_]*)\s*:\s*(?P<type>[^=\n]+?)(?:\s*=\s*(?P<default>.+))?$", re.M)
ENV_PREFIX_RE = re.compile(r"env_prefix\s*=\s*[\"']([^\"']*)[\"']")
CLI_PATTERNS = [
    re.compile(r"add_argument\(\s*[\"'](?P<arg>[-\w]+)[\"']"),
    re.compile(r"@(?:click|app|cli)\.command\((?:\s*[\"'](?P<arg>[\w-]+)[\"'])?"),
    re.compile(r"@(?:\w+)\.(?:command)\("),
]
ENTRY_RE = re.compile(r"if\s+__name__\s*==\s*[\"']__main__[\"']|uvicorn\.run\(|app\.listen\(|func main\(\)")
DOCKER_RE = re.compile(r"^\s*(FROM|EXPOSE|CMD|ENTRYPOINT|ENV)\s+(.+)$", re.M)
TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b[:\s]*(.*)")


@dataclass
class Hit:
    file: str
    line: int
    detail: dict[str, str] = field(default_factory=dict)


@dataclass
class Inventory:
    root: str
    languages: dict[str, int] = field(default_factory=dict)
    tree: list[str] = field(default_factory=list)
    manifests: list[str] = field(default_factory=list)
    docs: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    entrypoints: list[Hit] = field(default_factory=list)
    routes: list[Hit] = field(default_factory=list)
    env_vars: list[Hit] = field(default_factory=list)
    cli: list[Hit] = field(default_factory=list)
    docker: list[Hit] = field(default_factory=list)
    package_scripts: dict[str, str] = field(default_factory=dict)
    todos: list[Hit] = field(default_factory=list)


def iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") or d in {".github"})
        for fn in sorted(filenames):
            out.append(Path(dirpath) / fn)
    return out


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def build_tree(root: Path, max_depth: int) -> list[str]:
    lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        depth = len(rel.parts)
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        if depth >= max_depth:
            dirnames[:] = []
        indent = "  " * depth
        if depth:
            lines.append(f"{indent[:-2]}{rel.name}/")
        if depth < max_depth:
            for fn in sorted(filenames)[:40]:
                lines.append(f"{indent}{fn}")
    return lines


def scan(root: Path, max_depth: int = 3) -> Inventory:
    inv = Inventory(root=str(root))
    langs: Counter[str] = Counter()
    prefixes: dict[str, str] = {}
    include_prefix: dict[str, str] = {}
    files = iter_files(root)
    texts: dict[Path, str] = {}

    for p in files:
        rel = str(p.relative_to(root))
        if p.suffix in LANG_EXT:
            langs[LANG_EXT[p.suffix]] += 1
        if p.name in MANIFESTS:
            inv.manifests.append(rel)
        if DOC_NAMES.match(p.name) and p.suffix.lower() in {".md", ".rst", ".txt", ""}:
            inv.docs.append(rel)
        if re.search(r"(^|/)(tests?|__tests__|spec)(/|$)|(^|/)test_[^/]+\.py$|\.(test|spec)\.[jt]sx?$", rel):
            inv.tests.append(rel)
        if p.suffix in LANG_EXT or p.name in MANIFESTS or p.name.startswith(".env"):
            try:
                if p.stat().st_size < 1_000_000:
                    texts[p] = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass

    # Pass 1: router prefixes
    for p, t in texts.items():
        for m in PREFIX_RE.finditer(t):
            pm = PREFIX_ARG_RE.search(m.group("args"))
            prefixes[m.group("var")] = pm.group(1) if pm else ""
        for m in INCLUDE_RE.finditer(t):
            if m.group("prefix"):
                include_prefix[m.group("var")] = m.group("prefix")

    for p, t in texts.items():
        rel = str(p.relative_to(root))
        is_code = p.suffix in LANG_EXT
        if is_code:
            for kind, exts, rx in ROUTE_PATTERNS:
                if p.suffix not in exts:
                    continue
                for m in rx.finditer(t):
                    gd = m.groupdict()
                    obj = gd.get("obj") or ""
                    method = (gd.get("method") or "").upper()
                    if kind == "flask":
                        method = ",".join(x.strip(" '\"").upper() for x in (gd.get("methods") or "GET").split(","))
                    full = include_prefix.get(obj, "") + prefixes.get(obj, "") + gd["path"]
                    inv.routes.append(Hit(rel, line_of(t, m.start()),
                                          {"method": method, "path": full or "/", "router": obj, "framework": kind}))
            if ENTRY_RE.search(t):
                m = ENTRY_RE.search(t)
                assert m
                inv.entrypoints.append(Hit(rel, line_of(t, m.start()), {"match": m.group(0)}))
            for rx in CLI_PATTERNS:
                for m in rx.finditer(t):
                    inv.cli.append(Hit(rel, line_of(t, m.start()), {"match": m.group(0)[:80]}))
            for m in TODO_RE.finditer(t):
                inv.todos.append(Hit(rel, line_of(t, m.start()), {"text": m.group(0)[:100]}))
            # pydantic BaseSettings: mỗi field là một env var (có thể kèm env_prefix)
            for cm in SETTINGS_CLASS_RE.finditer(t):
                body_start = t.find("\n", cm.end()) + 1
                block = t[body_start:]
                nxt = re.search(r"^\S", block, re.M)
                block = block[: nxt.start()] if nxt else block
                pref_m = ENV_PREFIX_RE.search(block)
                pref = pref_m.group(1) if pref_m else ""
                base = body_start
                for fm in SETTINGS_FIELD_RE.finditer(block):
                    name = fm.group("name")
                    if name in {"model_config", "class", "env_prefix"}:
                        continue
                    inv.env_vars.append(Hit(rel, line_of(t, base + fm.start()), {
                        "name": (pref + name).upper(), "default": (fm.group("default") or "").strip(),
                        "source": f"BaseSettings {cm.group(1)}", "type": fm.group("type").strip()}))
        env_pats = ENV_PATTERNS if p.name.startswith(".env") else ENV_PATTERNS[:-1]
        if is_code or p.name.startswith(".env") or p.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yaml"}:
            for rx in env_pats:
                for m in rx.finditer(t):
                    gd = m.groupdict()
                    inv.env_vars.append(Hit(rel, line_of(t, m.start()), {
                        "name": gd["name"], "default": (gd.get("default") or "").strip(), "source": "code" if is_code else p.name}))
        if p.name == "Dockerfile":
            for m in DOCKER_RE.finditer(t):
                inv.docker.append(Hit(rel, line_of(t, m.start()), {"instr": m.group(1), "value": m.group(2).strip()}))
        if p.name == "package.json":
            try:
                inv.package_scripts = json.loads(t).get("scripts", {}) or {}
            except json.JSONDecodeError:
                pass

    inv.languages = dict(langs.most_common())
    inv.tree = build_tree(root, max_depth)
    return inv


def render_md(inv: Inventory) -> str:
    o: list[str] = [f"# Repo inventory: {inv.root}", "",
                    "> Sinh tự động bằng regex — dùng để định hướng đọc code; kiểm lại từng mục trước khi đưa vào tài liệu.", ""]
    o += ["## Languages", ", ".join(f"{k}: {v} files" for k, v in inv.languages.items()) or "(none)", ""]
    o += ["## Tree", "```", *inv.tree, "```", ""]
    o += ["## Manifests / config", *[f"- {m}" for m in inv.manifests], ""]
    o += ["## Existing docs", *([f"- {d}" for d in inv.docs] or ["(none)"]), ""]
    o += ["## Entrypoints", *[f"- {h.file}:{h.line} `{h.detail['match']}`" for h in inv.entrypoints], ""]
    o += ["## HTTP routes", "| Method | Path | File:line | Framework |", "|---|---|---|---|",
          *[f"| {h.detail['method']} | `{h.detail['path']}` | {h.file}:{h.line} | {h.detail['framework']} |" for h in inv.routes], ""]
    seen: dict[str, list[Hit]] = {}
    for h in inv.env_vars:
        seen.setdefault(h.detail["name"], []).append(h)
    o += ["## Environment variables", "| Name | Default | Defined at |", "|---|---|---|"]
    for name, hits in sorted(seen.items()):
        default = next((h.detail.get("default") for h in hits if h.detail.get("default")), "")
        o.append(f"| `{name}` | {default or '—'} | " + ", ".join(f"{h.file}:{h.line}" for h in hits) + " |")
    o += ["", "## CLI", *[f"- {h.file}:{h.line} `{h.detail['match']}`" for h in inv.cli], ""]
    o += ["## Docker", *[f"- {h.file}:{h.line} {h.detail['instr']} {h.detail['value']}" for h in inv.docker], ""]
    if inv.package_scripts:
        o += ["## package.json scripts", *[f"- `{k}`: `{v}`" for k, v in inv.package_scripts.items()], ""]
    o += ["## Tests", *([f"- {t}" for t in inv.tests[:50]] or ["(none found)"]), ""]
    o += ["## TODO/FIXME", *[f"- {h.file}:{h.line} {h.detail['text']}" for h in inv.todos[:50]], ""]
    return "\n".join(o)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--max-depth", type=int, default=3)
    a = ap.parse_args(argv)
    root = Path(a.repo).resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2
    inv = scan(root, a.max_depth)
    print(json.dumps(asdict(inv), ensure_ascii=False, indent=2) if a.format == "json" else render_md(inv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
