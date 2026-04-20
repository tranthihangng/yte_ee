import csv
from pathlib import Path


def export_cases_csv(rows: list[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()) if rows else ["empty"])
        writer.writeheader()
        if rows:
            writer.writerows(rows)
    return output_path
