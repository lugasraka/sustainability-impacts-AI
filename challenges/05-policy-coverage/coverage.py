import csv
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).resolve().parent / "policy.csv"

COLUMNS = [
    "initiative",
    "stage",
    "coverage_status",
    "responsible_actor",
    "required_metric",
    "reporting_audience",
    "geographic_scope",
    "known_omission",
    "source",
]
STATUSES = ["covered", "partial", "not_covered"]
STAGES = [
    "training",
    "inference",
    "hardware production",
    "electricity generation",
    "cooling and water",
    "application effects",
    "system-level effects",
    "siting and community impacts",
]

STATUS_STYLE = {
    "covered": "green",
    "partial": "yellow",
    "not_covered": "red",
}


def load_policy(path=CSV_PATH):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV is empty")
    missing = [c for c in COLUMNS if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    df = pd.DataFrame(rows)
    malformed = [i for i, row in enumerate(rows) if set(row.keys()) != set(reader.fieldnames)]
    if malformed:
        raise ValueError(f"Rows {malformed} do not match the header; check for unquoted commas in fields")
    invalid = sorted(set(df["coverage_status"]) - set(STATUSES))
    if invalid:
        raise ValueError(f"Invalid coverage_status values: {', '.join(invalid)}")
    return df


def heatmap_df(df):
    pivot = df.pivot_table(index="stage", columns="initiative", values="coverage_status", aggfunc="first")
    pivot = pivot.reindex(STAGES)
    return pivot


def gap_summary(df, stage):
    rows = df[df["stage"] == stage]
    if rows.empty:
        return None
    return rows[["initiative", "coverage_status", "known_omission"]].to_dict("records")


def stage_coverage_counts(df, stage):
    rows = df[df["stage"] == stage]
    total = len(rows)
    covered = (rows["coverage_status"] == "covered").sum()
    partial = (rows["coverage_status"] == "partial").sum()
    not_covered = (rows["coverage_status"] == "not_covered").sum()
    return {"total": total, "covered": covered, "partial": partial, "not_covered": not_covered}


def filter_rows(df, stages=None, initiatives=None, audiences=None, statuses=None):
    result = df
    if stages:
        result = result[result["stage"].isin(stages)]
    if initiatives:
        result = result[result["initiative"].isin(initiatives)]
    if audiences:
        result = result[result["reporting_audience"].isin(audiences)]
    if statuses:
        result = result[result["coverage_status"].isin(statuses)]
    return result.reset_index(drop=True)
