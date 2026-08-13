import csv
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).resolve().parent / "policy.csv"

COLUMNS = [
    "initiative",
    "stage",
    "impact_category",
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
IMPACT_CATEGORIES = ["energy", "carbon", "water", "materials", "land", "community"]

STATUS_STYLE = {
    "covered": "green",
    "partial": "yellow",
    "not_covered": "red",
}
STATUS_SCORE = {
    "covered": 1.0,
    "partial": 0.5,
    "not_covered": 0.0,
}
STATUS_LABEL = {
    "covered": "covers",
    "partial": "partially covers",
    "not_covered": "does not cover",
}

# Audiences a given persona can actually receive data from. The lecture's point:
# "authorities only" data is invisible to downstream providers and the public.
PERSONA_AUDIENCES = {
    "Regulator / authority": {
        "Authorities (limited access)",
        "Authorities / public (per the act)",
        "Public (EU database)",
        "Public (to be defined)",
    },
    "Downstream app provider": {
        "Authorities / public (per the act)",
        "Public (EU database)",
        "Public (to be defined)",
    },
    "Researcher / public": {
        "Authorities / public (per the act)",
        "Public (EU database)",
        "Public (to be defined)",
    },
    "Local community": {
        "Public (EU database)",
        "Public (to be defined)",
    },
    "Grid / energy operator": {
        "Public (EU database)",
        "Public (to be defined)",
    },
}
PERSONAS = list(PERSONA_AUDIENCES.keys())

# Reference URLs for linkifying the `source` column.
SOURCE_LINKS = {
    "eur-lex 2024/1689": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
    "eur-lex 2023/1791": "https://eur-lex.europa.eu/eli/dir/2023/1791/oj",
    "2024/1364": "https://eur-lex.europa.eu/eli/reg_del/2024/1364/oj",
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


def split_categories(value):
    if not isinstance(value, str) or value.strip() == "" or value.strip() == "n/a":
        return []
    return [c.strip() for c in value.split(";") if c.strip()]


def match_category(df, category):
    return df["impact_category"].apply(lambda v: category in split_categories(v))


def heatmap_df(df):
    pivot = df.pivot_table(index="stage", columns="initiative", values="coverage_status", aggfunc="first")
    pivot = pivot.reindex(STAGES)
    return pivot


def style_heatmap(pivot):
    def cell(v):
        return f"background-color: {STATUS_STYLE.get(v, 'white')}" if isinstance(v, str) else ""
    return pivot.style.map(cell)


def stage_scores(df):
    scores = []
    for stage in STAGES:
        rows = df[df["stage"] == stage]
        if rows.empty:
            scores.append({"stage": stage, "score": 0.0, "rows": 0})
            continue
        scores.append(
            {
                "stage": stage,
                "score": rows["coverage_status"].map(STATUS_SCORE).mean(),
                "rows": len(rows),
            }
        )
    return pd.DataFrame(scores).sort_values("score")


def initiative_scores(df):
    scores = []
    for initiative in df["initiative"].unique():
        rows = df[df["initiative"] == initiative]
        scores.append(
            {
                "initiative": initiative,
                "score": rows["coverage_status"].map(STATUS_SCORE).mean(),
                "rows": len(rows),
            }
        )
    return pd.DataFrame(scores).sort_values("score", ascending=False)


def overall_score(df):
    return df["coverage_status"].map(STATUS_SCORE).mean()


def is_measuring(df):
    return df["coverage_status"].isin(["covered", "partial"])


def persona_accessibility(df, persona):
    audiences = PERSONA_AUDIENCES[persona]
    rows = df[is_measuring(df)].copy()
    rows["persona_can_see"] = rows["reporting_audience"].isin(audiences)
    return rows


def persona_matrix(df, persona):
    rows = persona_accessibility(df, persona)
    pivot = rows.pivot_table(
        index="stage", columns="initiative", values="persona_can_see", aggfunc="first"
    ).reindex(STAGES)
    return pivot


def gap_ranking(df):
    gaps = []

    stage_totals = df.groupby("stage")["coverage_status"].apply(
        lambda s: (s == "not_covered").sum()
    )
    fully_uncovered = stage_totals[stage_totals == df["initiative"].nunique()].index.tolist()
    for stage in fully_uncovered:
        gaps.append(
            {
                "severity": "high",
                "kind": "stage",
                "text": f"'{stage}' is measured by no initiative",
                "detail": f"Every initiative in the matrix leaves this lifecycle stage unmeasured.",
            }
        )

    measured_but_hidden = df[
        (is_measuring(df)) & (df["reporting_audience"] == "Authorities (limited access)")
    ]
    for _, row in measured_but_hidden.iterrows():
        gaps.append(
            {
                "severity": "high",
                "kind": "audience",
                "text": f"{row['initiative']} measures '{row['stage']}' but discloses only to authorities",
                "detail": f"Downstream providers and the public cannot see this data, which weakens deployment-side accountability.",
            }
        )

    never_split = {
        "inference": "inference energy is not separated from facility totals",
        "cooling and water": "water withdrawal, consumption, and discharge are not separated",
        "electricity generation": "marginal grid intensity is not reported",
        "application effects": "application-level emissions sit outside facility reporting",
    }
    for stage, detail in never_split.items():
        gaps.append(
            {
                "severity": "medium",
                "kind": "metric",
                "text": f"'{stage}' is never split into the metric that matters",
                "detail": detail + ".",
            }
        )

    order = {"high": 0, "medium": 1, "low": 2}
    gaps.sort(key=lambda g: order[g["severity"]])
    return gaps


def diff_df(df, initiative_a, initiative_b):
    a = df[df["initiative"] == initiative_a].set_index("stage")["coverage_status"]
    b = df[df["initiative"] == initiative_b].set_index("stage")["coverage_status"]
    out = pd.DataFrame(
        {
            initiative_a: [a.get(s, "") for s in STAGES],
            initiative_b: [b.get(s, "") for s in STAGES],
            "same": [a.get(s, "") == b.get(s, "") for s in STAGES],
        },
        index=STAGES,
    )
    return out


def drill_row(df, stage, initiative):
    rows = df[(df["stage"] == stage) & (df["initiative"] == initiative)]
    if rows.empty:
        return None
    return rows.iloc[0]


def filter_rows(df, stages=None, initiatives=None, audiences=None, statuses=None, categories=None):
    result = df
    if stages:
        result = result[result["stage"].isin(stages)]
    if initiatives:
        result = result[result["initiative"].isin(initiatives)]
    if audiences:
        result = result[result["reporting_audience"].isin(audiences)]
    if statuses:
        result = result[result["coverage_status"].isin(statuses)]
    if categories:
        result = result[match_category(result, categories)]
    return result.reset_index(drop=True)


def source_links(source):
    links = []
    for key, url in SOURCE_LINKS.items():
        if key in source:
            links.append((key, url))
    return links


def to_markdown(df, gaps, overall, stage_scores_df, initiative_scores_df):
    lines = [
        "# Policy coverage report",
        "",
        f"- **Overall transparency coverage score: {overall * 100:.0f}%** (covered = 1, partial = 0.5, not covered = 0).",
        f"- {len(df)} rows across {df['initiative'].nunique()} initiatives and {len(STAGES)} lifecycle stages.",
        "",
        "## Least-measured lifecycle stages",
    ]
    for _, row in stage_scores_df.head(3).iterrows():
        lines.append(f"- {row['stage']}: {row['score'] * 100:.0f}%")
    lines += ["", "## Broadest initiatives"]
    for _, row in initiative_scores_df.head(3).iterrows():
        lines.append(f"- {row['initiative']}: {row['score'] * 100:.0f}%")
    lines += ["", "## Darkest gaps"]
    for gap in gaps:
        lines.append(f"- [{gap['severity']}] {gap['text']} — {gap['detail']}")
    lines += [
        "",
        "*Derived from lecture slides 67-76. Legal details and implementation status change; "
        "verify current texts before relying on any entry.*",
    ]
    return "\n".join(lines)
