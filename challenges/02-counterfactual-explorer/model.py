import csv
from pathlib import Path

import numpy as np
import pandas as pd

CSV_PATH = Path(__file__).resolve().parent / "scenarios.csv"

BASE_COLUMNS = {
    "baseline": "baseline_tco2e_per_year",
    "efficiency": "efficiency_pct",
    "adoption": "adoption_pct",
    "ai": "ai_emissions_tco2e_per_year",
    "rebound": "rebound_pct",
    "leakage": "leakage_pct",
    "additionality": "additionality_pct",
}
UNC_COLUMNS = {
    "baseline": "unc_baseline_pct",
    "efficiency": "unc_efficiency_pct",
    "adoption": "unc_adoption_pct",
    "ai": "unc_ai_pct",
    "rebound": "unc_rebound_pct",
    "leakage": "unc_leakage_pct",
    "additionality": "unc_additionality_pct",
}
STORY_FIELDS = [
    ("decision", "Decision the model changes"),
    ("baseline_practice", "Baseline practice without AI"),
    ("mechanism", "Mechanism of the reduction or increase"),
    ("actors", "Actors and infrastructure that must adopt it"),
    ("scope", "Time period and geographic scope"),
    ("failure_modes", "Rebound, leakage, and failure modes"),
]
WIDGET_RANGES = {
    "baseline": (0.0, 5_000_000.0),
    "efficiency": (0.0, 30.0),
    "adoption": (0.0, 100.0),
    "ai": (0.0, 5_000.0),
    "rebound": (-20.0, 50.0),
    "leakage": (0.0, 100.0),
    "additionality": (0.0, 100.0),
}
LABELS = {
    "baseline": "Baseline activity emissions (tCO2e/yr)",
    "efficiency": "Efficiency improvement (%)",
    "adoption": "Adoption rate (%)",
    "ai": "Additional AI emissions (tCO2e/yr)",
    "rebound": "Rebound / demand growth (%)",
    "leakage": "Leakage — effect shifted elsewhere (%)",
    "additionality": "Additionality / attribution (%)",
}
MCS_DRAWS = 2000
MCS_SEED = 42


def load_scenarios(path=CSV_PATH):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV is empty")
    required = (
        ["scenario", "kind", "direction", "adoption_ramp_years"]
        + list(BASE_COLUMNS.values())
        + list(UNC_COLUMNS.values())
        + [key for key, _ in STORY_FIELDS]
    )
    missing = [c for c in required if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    df = pd.DataFrame(rows)
    numeric = (
        ["direction", "adoption_ramp_years"]
        + list(BASE_COLUMNS.values())
        + list(UNC_COLUMNS.values())
    )
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' has non-numeric values")
    return df


def net_change(
    baseline, direction, efficiency, adoption, rebound, ai, leakage=0.0, additionality=1.0
):
    effect = direction * efficiency * adoption * additionality * (1 - leakage)
    return baseline * (1 + effect) * (1 + rebound) + ai - baseline


def low_high(value, unc_pct):
    return value * (1 - unc_pct / 100.0), value * (1 + unc_pct / 100.0)


def monte_carlo(
    baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality,
    uncs, draws=MCS_DRAWS, seed=MCS_SEED,
):
    rng = np.random.default_rng(seed)
    sampled = {}
    for key, value in [
        ("baseline", baseline),
        ("efficiency", efficiency),
        ("adoption", adoption),
        ("ai", ai),
        ("rebound", rebound),
        ("leakage", leakage),
        ("additionality", additionality),
    ]:
        lo, hi = low_high(value, uncs[key])
        sampled[key] = rng.uniform(lo, hi, draws)
    net = net_change(
        sampled["baseline"],
        direction,
        sampled["efficiency"] / 100.0,
        sampled["adoption"] / 100.0,
        sampled["rebound"] / 100.0,
        sampled["ai"],
        sampled["leakage"] / 100.0,
        sampled["additionality"] / 100.0,
    )
    p_negative = float((net < 0).mean())
    return {
        "mean": float(net.mean()),
        "median": float(np.median(net)),
        "p5": float(np.percentile(net, 5)),
        "p95": float(np.percentile(net, 95)),
        "p_negative": p_negative,
        "draws": net,
    }


def tornado(
    baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality, uncs
):
    base = {
        "baseline": baseline,
        "efficiency": efficiency / 100.0,
        "adoption": adoption / 100.0,
        "ai": ai,
        "rebound": rebound / 100.0,
        "leakage": leakage / 100.0,
        "additionality": additionality / 100.0,
    }
    results = {}
    for key, base_value in base.items():
        lo, hi = low_high(base_value, uncs[key])
        args_lo = dict(base)
        args_hi = dict(base)
        args_lo[key] = lo
        args_hi[key] = hi
        net_lo = net_change(
            args_lo["baseline"], direction, args_lo["efficiency"],
            args_lo["adoption"], args_lo["rebound"], args_lo["ai"],
            args_lo["leakage"], args_lo["additionality"],
        )
        net_hi = net_change(
            args_hi["baseline"], direction, args_hi["efficiency"],
            args_hi["adoption"], args_hi["rebound"], args_hi["ai"],
            args_hi["leakage"], args_hi["additionality"],
        )
        results[key] = abs(net_hi - net_lo)
    return results


def headline_potential(baseline, direction, efficiency):
    return baseline * (1 + direction * efficiency / 100.0) - baseline


def realized_net(baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality):
    return net_change(
        baseline, direction, efficiency / 100.0, adoption / 100.0,
        rebound / 100.0, ai, leakage / 100.0, additionality / 100.0,
    )


def ramp_projection(
    baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality,
    ramp_years, horizon,
):
    ramp_years = max(1, int(ramp_years))
    horizon = max(1, int(horizon))
    headline = headline_potential(baseline, direction, efficiency)
    rows = []
    cumulative = 0.0
    for year in range(1, horizon + 1):
        ramp_frac = min(1.0, year / float(ramp_years))
        year_net = net_change(
            baseline, direction, efficiency / 100.0, adoption * ramp_frac / 100.0,
            rebound / 100.0, ai * ramp_frac, leakage / 100.0, additionality / 100.0,
        )
        cumulative += year_net
        rows.append(
            {
                "year": year,
                "net_tco2e": year_net,
                "cumulative_tco2e": cumulative,
                "headline_potential_tco2e": headline,
            }
        )
    return pd.DataFrame(rows)


def histogram_df(draws, bins=25):
    hist, edges = np.histogram(draws, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    return pd.DataFrame({"count": hist}, index=[f"{c:+,.0f}" for c in centers])


def overlay_histogram_df(draws_a, label_a, draws_b, label_b, bins=25):
    lo = min(draws_a.min(), draws_b.min())
    hi = max(draws_a.max(), draws_b.max())
    if lo == hi:
        lo -= 1.0
        hi += 1.0
    edges = np.linspace(lo, hi, bins + 1)
    hist_a, _ = np.histogram(draws_a, bins=edges)
    hist_b, _ = np.histogram(draws_b, bins=edges)
    centers = (edges[:-1] + edges[1:]) / 2
    return pd.DataFrame(
        {label_a: hist_a, label_b: hist_b}, index=[f"{c:+,.0f}" for c in centers]
    )


def assumption_rows(values, uncs):
    rows = []
    for key in BASE_COLUMNS:
        value = float(values[key])
        unc = float(uncs[key])
        lo, hi = low_high(value, unc)
        rows.append(
            {"assumption": key, "base": value, "unc_pct": unc, "low": lo, "high": hi}
        )
    return pd.DataFrame(rows)


def to_markdown(
    scenario, kind, direction, values, uncs, stats, base_net, top_key,
    headline, realized, story, ramp_years, horizon,
):
    sign_word = "reduces" if direction < 0 else "increases"
    lines = [
        f"# Counterfactual assessment: {scenario}",
        "",
        f"- **Kind:** {kind} — where adopted, this application {sign_word} emissions.",
        f"- **Projection:** {horizon} years, adoption ramping over {ramp_years} years.",
        "",
        "## Assumptions (toy values)",
    ]
    for key in BASE_COLUMNS:
        lines.append(
            f"- {LABELS[key]}: {values[key]:,.0f} (uncertainty ±{uncs[key]:.0f}%)"
        )
    lines += [
        "",
        "## Net outcome (Monte Carlo, 2000 seeded draws)",
        f"- Base net change: {base_net:+,.0f} tCO2e/yr",
        f"- Mean: {stats['mean']:+,.0f} tCO2e/yr",
        f"- Median: {stats['median']:+,.0f} tCO2e/yr",
        f"- p5–p95: {stats['p5']:+,.0f} … {stats['p95']:+,.0f} tCO2e/yr",
        f"- P(net reduction): {stats['p_negative'] * 100:.0f}%",
        f"- Most sensitive assumption: {LABELS[top_key]}",
        "",
        "## Potential vs realized",
        f"- Headline potential (full adoption, no leakage/additionality/rebound/AI cost): {headline:+,.0f} tCO2e/yr",
        f"- Realized net at current assumptions: {realized:+,.0f} tCO2e/yr",
        "",
        "## Counterfactual story",
    ]
    for key, label in STORY_FIELDS:
        lines.append(f"- **{label}:** {story.get(key, '')}")
    lines += ["", "*Toy assumptions for demonstration; not a lifecycle assessment.*"]
    return "\n".join(lines)
