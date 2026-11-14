"""Helpers that edit a rendered review sheet the way a reviewer would."""

from backend.bintanong_tools.prospectus_extractor.sheet import COLUMNS, esc, split_cells


def edit_row(text, rid, **cols):
    """Fill the editable columns of one row."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"| {rid} |"):
            cells = split_cells(line)
            cells += [""] * (len(COLUMNS) - len(cells))
            for name, value in cols.items():
                cells[COLUMNS.index(name.replace("_", " "))] = value
            lines[i] = "| " + " | ".join(esc(c) for c in cells) + " |"
    return "\n".join(lines) + "\n"


def set_line(text, sid, key, value):
    lines, inside = text.splitlines(), False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            inside = line.startswith(f"## {sid} ")
        elif inside and line.startswith(f"{key}:"):
            lines[i] = f"{key}: {value}"
    return "\n".join(lines) + "\n"
