#!/usr/bin/env python3
"""One-off: slice the monolith at BASE into bintanong_tools/prospectus_extractor/.

Code is copied byte-for-byte per top-level statement; only imports are generated.
Run from anywhere:  python scripts/split_prospectus_extractor.py
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = "7591264"
MONOLITH = "backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py"
PACKAGE = REPO / "backend" / "bintanong_tools" / "prospectus_extractor"

# (module, first line, last line, docstring) in import order: a module may only
# import from modules listed above it.
MODULES = [
    ("common", 1, 101, "Schema versions and optional Rich console objects."),
    ("docling_env", 102, 333, "Lazy Docling import, version guard, CUDA check and converter cache."),
    ("text", 334, 446, "Text cleaning, course-code keys, year and semester labels."),
    ("footnotes", 447, 593, "Footnote marker detection and stripping."),
    ("units", 594, 657, "Lecture, laboratory and total unit parsing."),
    ("prerequisites", 658, 859, "Prerequisite tokenising and resolution."),
    ("grid", 1304, 1473, "Course-code recognition, total rows and the parse result container."),
    ("layout", 860, 1128, "Column-group and header detection."),
    ("evidence", 1129, 1303, "Normalized Docling evidence: cells, tables, source boxes."),
    ("sections", 1482, 2818, "Structural tokenizer, curriculum sections and course row assembly."),
    ("repair", 2819, 3054, "Evidence-constrained semantic repair validation."),
    ("parse", 3055, 3198, "Evidence-to-curriculum entry points."),
    ("legacy", 1474, 1481, "Deprecated names kept for reference; nothing in the package calls them."),
    ("courses", 3199, 3363, "Course finalisation, classification and elective tracks."),
    ("metadata", 3364, 3509, "Program, college and school-year metadata."),
    ("audit", 3510, 3804, "Audit that fails loudly instead of emitting plausible garbage."),
    ("views", 3805, 3879, "Derived views: term tree, prerequisite edges, review CSV."),
    ("prolog", 3880, 4058, "Candidate Prolog knowledge base."),
    ("rag", 4059, 4216, "Semantic and layout RAG chunks."),
    ("paths", 4217, 4237, "Default input and output locations."),
    ("loader", 4238, 4676, "Docling-to-evidence adapter, conversion cache and document loading."),
    ("pipeline", 4677, 4937, "Payload assembly and single-document processing."),
    ("batch", 4938, 5179, "In-process batch engine and manifest."),
    ("selftest", 5493, 6203, "Built-in fixtures and the 80-check self-test."),
    ("tui", 5180, 5492, "Interactive terminal UI."),
    ("cli", 6204, 6319, "Command-line interface."),
]
# Definitions placed outside the module their line number falls in, to keep the
# import graph acyclic.
MOVES = {
    "MULTIPART_CODE": "grid",
    "is_probable_course_code": "grid",
    "_two_course_codes_in_cell": "grid",
    "build_hierarchical_rag_chunks": "rag",
    "find_default_input_root": "paths",
    "find_default_output_root": "paths",
}


def bound_names(node: ast.stmt) -> list[str]:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [t.id for t in node.targets if isinstance(t, ast.Name)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    if isinstance(node, ast.Try):
        names: list[str] = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign):
                names += [t.id for t in sub.targets if isinstance(t, ast.Name)]
            elif isinstance(sub, ast.ImportFrom):
                names += [a.asname or a.name for a in sub.names]
        return list(dict.fromkeys(names))
    return []


def strip_banner(text: str) -> str:
    rows = text.split("\n")
    while rows and not rows[0].strip():
        rows.pop(0)
    if rows and rows[0].startswith("# ====="):
        close = next(i for i in range(1, len(rows)) if rows[i].startswith("# ====="))
        rows = rows[close + 1:]
    return "\n".join(rows).strip("\n")


def main() -> None:
    source = subprocess.run(["git", "show", f"{BASE}:{MONOLITH}"], cwd=REPO, check=True,
                            capture_output=True).stdout.decode("utf-8")
    lines = source.splitlines()
    order = [name for name, *_ in MODULES]
    stdlib: dict[str, str] = {}
    chunks: dict[str, list[tuple[ast.stmt, str]]] = {name: [] for name in order}
    owner: dict[str, str] = {}
    optional: set[str] = set()

    previous_end = 0
    for index, node in enumerate(ast.parse(source).body):
        start, previous_end = previous_end, node.end_lineno
        if isinstance(node, ast.Import):
            for alias in node.names:
                stdlib[alias.asname or alias.name.split(".")[0]] = (
                    f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
            continue
        if isinstance(node, ast.ImportFrom):
            for alias in node.names if node.module != "__future__" else []:
                stdlib[alias.asname or alias.name] = (
                    f"from {node.module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
            continue
        if index == 0 or isinstance(node, ast.If):  # module docstring, __main__ guard
            continue
        names = bound_names(node)
        if not names:
            raise SystemExit(f"unhandled top-level statement at line {node.lineno}")
        module = MOVES.get(names[0]) or next(m for m, a, b, _ in MODULES if a <= node.lineno <= b)
        chunks[module].append((node, strip_banner("\n".join(lines[start:node.end_lineno]))))
        for name in names:
            if name in owner:
                raise SystemExit(f"{name} is defined twice (line {node.lineno})")
            owner[name] = module
        if isinstance(node, ast.Try):
            optional |= {a.asname or a.name for sub in ast.walk(node)
                         if isinstance(sub, ast.ImportFrom) for a in sub.names}

    PACKAGE.mkdir(parents=True, exist_ok=True)
    for module, _first, _last, doc in MODULES:
        used = {n.id for node, _ in chunks[module] for n in ast.walk(node) if isinstance(n, ast.Name)}
        own = {name for name, home in owner.items() if home == module}
        deps: dict[str, list[str]] = {}
        for name in sorted(used - own):
            if name in owner:
                deps.setdefault(owner[name], []).append(name)
        for dep, names in deps.items():
            if order.index(dep) >= order.index(module):
                raise SystemExit(f"{module} needs {names} from later module {dep}; add a MOVES entry")
        out = [f'"""{doc}"""', "", "from __future__ import annotations", ""]
        std = sorted({stdlib[name] for name in used - own if name in stdlib})
        out += std + [""] * bool(std)
        for dep in sorted(deps, key=order.index):
            hard = [n for n in deps[dep] if n not in optional]
            soft = [n for n in deps[dep] if n in optional]
            if soft and "RICH_AVAILABLE" not in hard:
                hard.append("RICH_AVAILABLE")
            out.append(f"from .{dep} import {', '.join(sorted(hard))}")
            if soft:  # these names only exist when Rich imported successfully
                out += ["", "if RICH_AVAILABLE:", f"    from .{dep} import {', '.join(soft)}"]
        out += [""] * bool(deps)
        for _node, text in chunks[module]:
            out += ["", text, ""]
        (PACKAGE / f"{module}.py").write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
        print(f"{module:14} {len(chunks[module]):3} definitions")


if __name__ == "__main__":
    main()
