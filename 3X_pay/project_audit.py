#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
project_audit.py — статический аудит Python-проекта (акцент на aiogram-боты).

Запускайте из корня проекта:
    python project_audit.py --root . --out ARCHITECTURE_REPORT.md

Скрипт НЕ модифицирует проект, только читает файлы и пишет отчеты.
Выходные файлы по умолчанию:
  - ARCHITECTURE_REPORT.md
  - handlers_map.md
  - inventory.json
"""
from __future__ import annotations

import os
import re
import ast
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Iterable, Set, Any, Optional
from collections import defaultdict

# -------------------------- Utils --------------------------

PY_EXT = (".py",)
TEXT_EXT = (".md", ".txt", ".ini", ".cfg", ".env", ".sample", ".example")
CONF_FILES = ("requirements.txt", "requirements-prod.txt", "requirements-dev.txt", "Pipfile", "Pipfile.lock", "pyproject.toml", ".env", ".env.example", ".env.sample", "docker-compose.yml", "Dockerfile")
IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", ".idea", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", "build", "dist"}

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def walk_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # filter ignored dirs
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            files.append(Path(dirpath) / fn)
    return files

def is_python_file(p: Path) -> bool:
    return p.suffix in PY_EXT and p.name not in ("__init__.py",)

def short(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)

# -------------------------- AST helpers --------------------------

def parse_tree(code: str, filename: str="") -> Optional[ast.AST]:
    try:
        return ast.parse(code)
    except SyntaxError:
        return None

def extract_imports(tree: ast.AST) -> Tuple[Set[str], Set[str]]:
    """Return (imported_modules, from_imported_modules)."""
    modules = set()
    from_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                from_modules.add(node.module.split('.')[0])
    return modules, from_modules

def extract_aiogram_routers_and_handlers(tree: ast.AST) -> Dict[str, Any]:
    """
    Возвращает структуру:
    {
      'routers': {var_name -> {'lineno': int}},
      'handlers': [ {'name': func, 'decorators': [...], 'lineno': int} ],
    }
    """
    routers: Dict[str, Dict[str, Any]] = {}
    handlers: List[Dict[str, Any]] = []

    # 1) найти переменные, которым присваивается Router(...)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            try:
                value = node.value
                if isinstance(value, ast.Call):
                    func = value.func
                    func_name = ""
                    if isinstance(func, ast.Name):
                        func_name = func.id
                    elif isinstance(func, ast.Attribute):
                        func_name = func.attr
                    if func_name == "Router":
                        # targets could be a list
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                routers[target.id] = {"lineno": getattr(node, "lineno", -1)}
            except Exception:
                pass

    # 2) собрать функции с декораторами .message/.callback_query/... либо dp.message
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            decos = []
            for d in node.decorator_list:
                # Строковый вид декоратора
                deco_text = ast.unparse(d) if hasattr(ast, "unparse") else ""
                decos.append(deco_text)
            if any(".message(" in x or ".callback_query(" in x or ".inline_query(" in x or ".chat_member(" in x for x in decos):
                handlers.append({
                    "name": node.name,
                    "decorators": decos,
                    "lineno": getattr(node, "lineno", -1),
                })
    return {"routers": routers, "handlers": handlers}

def extract_states(tree: ast.AST) -> List[Dict[str, Any]]:
    """
    Находит классы состояний (FSM) — наследники StatesGroup.
    """
    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            base_names = []
            for base in node.bases:
                base_names.append(ast.unparse(base) if hasattr(ast, "unparse") else getattr(base, "id", ""))
            if any("StatesGroup" in b for b in base_names):
                # собрать State-поля
                states = []
                for body_item in node.body:
                    if isinstance(body_item, ast.Assign):
                        try:
                            if isinstance(body_item.value, ast.Call):
                                fn = body_item.value.func
                                fn_name = ast.unparse(fn) if hasattr(ast, "unparse") else getattr(fn, "id", "")
                                if fn_name.endswith("State"):
                                    for t in body_item.targets:
                                        if isinstance(t, ast.Name):
                                            states.append(t.id)
                        except Exception:
                            pass
                result.append({
                    "class": node.name,
                    "lineno": getattr(node, "lineno", -1),
                    "states": states,
                })
    return result

def find_http_calls(code: str) -> List[str]:
    """
    Грубый поиск URL в коде.
    """
    urls = re.findall(r"https?://[^\s\"']+", code)
    return sorted(set(urls))

# -------------------------- Analysis core --------------------------

def analyze_project(root: Path) -> Dict[str, Any]:
    files = walk_files(root)
    py_files = [p for p in files if is_python_file(p) or p.name == "__init__.py"]
    conf_files = [p for p in files if p.name in CONF_FILES or p.suffix in (".toml", ".yml", ".yaml")]

    import_graph: Dict[str, Dict[str, Any]] = {}
    aiogram_map: Dict[str, Any] = {}

    frameworks: Set[str] = set()
    all_imports: Set[str] = set()
    from_imports: Set[str] = set()
    states_index: Dict[str, List[Dict[str, Any]]] = {}
    urls_index: Dict[str, List[str]] = {}
    errors: List[str] = []

    for p in py_files:
        rel = short(p, root)
        code = read_text(p)
        tree = parse_tree(code, rel)
        if not tree:
            errors.append(f"Не удалось распарсить {rel}")
            continue
        imps, fimps = extract_imports(tree)
        all_imports |= imps
        from_imports |= fimps

        # framework hints
        if "aiogram" in imps or "aiogram" in fimps or "aiogram" in code:
            frameworks.add("aiogram")
        if "sqlalchemy" in imps or "sqlalchemy" in fimps or "sqlalchemy" in code:
            frameworks.add("sqlalchemy")
        if "yookassa" in imps or "yookassa" in fimps or "YooKassa" in code or "YooKassa" in code:
            frameworks.add("yookassa")

        # imports per file
        import_graph[rel] = {
            "imports": sorted(list(imps | fimps)),
        }

        # aiogram routers/handlers
        a = extract_aiogram_routers_and_handlers(tree)
        states = extract_states(tree)
        aiogram_map[rel] = a
        if states:
            states_index[rel] = states

        # urls
        urls = find_http_calls(code)
        if urls:
            urls_index[rel] = urls

    # Try to read requirements & pyproject
    requirements = ""
    for name in ("requirements.txt", "requirements-prod.txt", "requirements-dev.txt"):
        rp = root / name
        if rp.exists():
            requirements += f"\n# {name}\n" + read_text(rp)

    pyproject = ""
    pp = root / "pyproject.toml"
    if pp.exists():
        pyproject = read_text(pp)

    env_example = ""
    for name in (".env", ".env.example", ".env.sample"):
        ep = root / name
        if ep.exists():
            env_example += f"\n# {name}\n" + read_text(ep)

    return {
        "files_total": len(files),
        "python_files": [short(p, root) for p in py_files],
        "conf_files": [short(p, root) for p in conf_files],
        "import_graph": import_graph,
        "frameworks": sorted(list(frameworks)),
        "all_imports": sorted(list(all_imports | from_imports)),
        "aiogram_map": aiogram_map,
        "states_index": states_index,
        "urls_index": urls_index,
        "requirements_text": requirements.strip(),
        "pyproject_text": pyproject.strip(),
        "env_text": env_example.strip(),
        "errors": errors,
    }

# -------------------------- Reporting --------------------------

def mk_mermaid_import_graph(import_graph: Dict[str, Dict[str, Any]]) -> str:
    nodes = []
    edges = []
    # Build node ids
    idx = {name: f"n{n}" for n, name in enumerate(import_graph.keys())}
    for name, data in import_graph.items():
        nodes.append(f'{idx[name]}["{name}"]')
        for mod in data.get("imports", []):
            # only local modules? Try heuristic: if mod looks like package path starting with project top-level?
            # Keep only "app" or local-style names for clarity
            if mod.startswith("app") or mod.startswith("bot") or mod.startswith("utils"):
                edges.append(f"{idx[name]} --> {mod}")
    # edges to nodes by label
    edge_lines = []
    for e in edges:
        src, dst = e.split(" --> ")
        edge_lines.append(f"{src} --> {dst}")
    return "graph TD\n" + "\n".join(nodes + edge_lines)

def write_handlers_map(aiogram_map: Dict[str, Any], root: Path, out_path: Path):
    lines = ["# Handlers map", ""]
    for rel, data in sorted(aiogram_map.items()):
        handlers = data.get("handlers") or []
        routers = data.get("routers") or {}
        if not handlers and not routers:
            continue
        lines.append(f"## {rel}")
        if routers:
            lines.append("**Routers:** " + ", ".join(sorted(routers.keys())))
        if handlers:
            lines.append("")
            lines.append("| line | function | decorators |")
            lines.append("|-----:|---------|------------|")
            for h in sorted(handlers, key=lambda x: x.get("lineno", 0)):
                dec = "<br>".join(h.get("decorators", []))
                lines.append(f"| {h.get('lineno','')} | `{h.get('name','')}` | {dec} |")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")

def write_inventory_json(data: Dict[str, Any], out_path: Path):
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_report_md(data: Dict[str, Any], root: Path, out_path: Path):
    lines: List[str] = []
    lines.append(f"# Архитектурный отчёт по проекту\n")
    lines.append(f"Путь проекта: `{root}`  \nВсего файлов: **{data['files_total']}**, Python-файлов: **{len(data['python_files'])}**")
    lines.append("")
    if data["frameworks"]:
        lines.append("**Обнаруженные ключевые зависимости (по коду):** " + ", ".join(data["frameworks"]))
        lines.append("")
    if data["requirements_text"]:
        lines.append("## requirements*\n")
        lines.append("```text\n" + data["requirements_text"] + "\n```")
    if data["pyproject_text"]:
        lines.append("\n## pyproject.toml\n")
        lines.append("```toml\n" + data["pyproject_text"] + "\n```")
    if data["env_text"]:
        lines.append("\n## Примеры/текущие .env\n")
        lines.append("```dotenv\n" + data["env_text"] + "\n```")
    # Files
    if data["conf_files"]:
        lines.append("\n## Конфигурационные файлы\n")
        for f in sorted(data["conf_files"]):
            lines.append(f"- {f}")
    if data["python_files"]:
        lines.append("\n## Python-файлы\n")
        for f in sorted(data["python_files"]):
            lines.append(f"- {f}")
    # Imports mermaid
    mg = mk_mermaid_import_graph(data["import_graph"])
    lines.append("\n## Граф импортов (упрощённо)\n")
    lines.append("```mermaid\n" + mg + "\n```")

    # Handlers summary
    lines.append("\n## Aiogram: routers и обработчики\n")
    total_handlers = 0
    for rel, d in sorted(data["aiogram_map"].items()):
        handlers = d.get("handlers") or []
        routers = d.get("routers") or {}
        if not handlers and not routers:
            continue
        total_handlers += len(handlers)
        lines.append(f"### {rel}")
        if routers:
            lines.append("Routers: " + ", ".join(sorted(routers.keys())))
        if handlers:
            for h in sorted(handlers, key=lambda x: x.get("lineno", 0)):
                lines.append(f"- L{h.get('lineno')}: `{h.get('name')}` — {', '.join(h.get('decorators', []))}")
    if total_handlers == 0:
        lines.append("_Обработчики не найдены эвристикой. Возможно, используются другие паттерны._")

    # States
    lines.append("\n## FSM состояния\n")
    if data["states_index"]:
        for rel, states in data["states_index"].items():
            lines.append(f"### {rel}")
            for st in states:
                lines.append(f"- Класс `{st['class']}` (L{st['lineno']}), стейты: {', '.join(st['states']) if st['states'] else '—'}")
    else:
        lines.append("_Состояния не найдены._")

    # URLs
    lines.append("\n## Внешние HTTP-эндпоинты/URL, обнаруженные в коде\n")
    if data["urls_index"]:
        for rel, urls in data["urls_index"].items():
            lines.append(f"### {rel}")
            for u in urls:
                lines.append(f"- {u}")
    else:
        lines.append("_Явные URL не найдены._")

    # Errors
    if data["errors"]:
        lines.append("\n## Ошибки парсинга\n")
        for e in data["errors"]:
            lines.append(f"- {e}")

    out_path.write_text("\n".join(lines), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Статический аудит aiogram-проекта")
    ap.add_argument("--root", default=".", help="Корень проекта")
    ap.add_argument("--out", default="ARCHITECTURE_REPORT.md", help="Файл вывода markdown отчёта")
    ap.add_argument("--handlers", default="handlers_map.md", help="Файл с таблицей обработчиков")
    ap.add_argument("--json", default="inventory.json", help="JSON сводка")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[!] Путь {root} не существует", file=sys.stderr)
        sys.exit(2)

    data = analyze_project(root)

    write_report_md(data, root, Path(args.out))
    write_handlers_map(data["aiogram_map"], root, Path(args.handlers))
    write_inventory_json(data, Path(args.json))

    print(f"[OK] Сформированы файлы: {args.out}, {args.handlers}, {args.json}")

if __name__ == "__main__":
    main()
