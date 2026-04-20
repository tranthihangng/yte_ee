from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Iterable


def rows_to_csv_bytes(fieldnames: list[str], rows: Iterable[dict]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8-sig")


def public_path(absolute_path: str | Path, backend_root: str | Path) -> str:
    path = Path(absolute_path).resolve()
    backend_root = Path(backend_root).resolve()
    relative = path.relative_to(backend_root)
    return "/" + relative.as_posix()
