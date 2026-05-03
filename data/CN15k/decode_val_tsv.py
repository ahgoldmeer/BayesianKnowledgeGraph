"""Decode CN15k val.tsv numeric IDs into readable strings.

Input files expected in the same directory by default:
- entity_id.csv   (columns: entity string,id)
- relation_id.csv (columns: relation string,id)
- val.tsv         (columns: Subject,Predicate,Object,Confidence)

Output:
- val_decoded.tsv (tab-separated with string Subject/Predicate/Object)
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def load_id_map(csv_path: Path, value_column: str, id_column: str = "id") -> dict[int, str]:
    id_map: dict[int, str] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"No header found in {csv_path}")
        for row in reader:
            raw_id = row.get(id_column)
            raw_value = row.get(value_column)
            if raw_id is None or raw_value is None:
                continue
            id_map[int(raw_id)] = raw_value
    return id_map


def decode_val_file(
    val_path: Path,
    out_path: Path,
    entity_map: dict[int, str],
    relation_map: dict[int, str],
) -> tuple[int, int]:
    total_rows = 0
    missing_lookups = 0

    with val_path.open("r", encoding="utf-8", newline="") as src, out_path.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        reader = csv.DictReader(src, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"No header found in {val_path}")

        required = ["Subject", "Predicate", "Object", "Confidence"]
        missing_columns = [col for col in required if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(
                f"Missing expected columns in {val_path}: {', '.join(missing_columns)}"
            )

        writer = csv.DictWriter(dst, fieldnames=required, delimiter="\t")
        writer.writeheader()

        for row in reader:
            total_rows += 1

            subject_id = int(row["Subject"])
            predicate_id = int(row["Predicate"])
            object_id = int(row["Object"])

            subject = entity_map.get(subject_id)
            predicate = relation_map.get(predicate_id)
            obj = entity_map.get(object_id)

            if subject is None:
                missing_lookups += 1
                subject = row["Subject"]
            if predicate is None:
                missing_lookups += 1
                predicate = row["Predicate"]
            if obj is None:
                missing_lookups += 1
                obj = row["Object"]

            writer.writerow(
                {
                    "Subject": subject,
                    "Predicate": predicate,
                    "Object": obj,
                    "Confidence": row["Confidence"],
                }
            )

    return total_rows, missing_lookups


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replace numeric Subject/Predicate/Object IDs in val.tsv with strings."
    )
    parser.add_argument(
        "--entity-csv",
        type=Path,
        default=Path("entity_id.csv"),
        help="Path to entity_id.csv",
    )
    parser.add_argument(
        "--relation-csv",
        type=Path,
        default=Path("relation_id.csv"),
        help="Path to relation_id.csv",
    )
    parser.add_argument(
        "--val-tsv",
        type=Path,
        default=Path("val.tsv"),
        help="Path to source val.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("val_decoded.tsv"),
        help="Path to decoded output TSV",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    entity_map = load_id_map(args.entity_csv, value_column="entity string")
    relation_map = load_id_map(args.relation_csv, value_column="relation string")

    row_count, missing_count = decode_val_file(
        args.val_tsv, args.output, entity_map, relation_map
    )

    print(f"Decoded {row_count} rows to: {args.output}")
    if missing_count:
        print(
            f"Warning: {missing_count} ID lookups were missing and left as numeric strings."
        )


if __name__ == "__main__":
    main()
