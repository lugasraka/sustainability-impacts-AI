import csv
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

CSV_PATH = Path(__file__).resolve().parent / "scenarios.csv"

BASE_COLUMNS = {
    "baseline": "baseline_tco2e_per_year",
    "efficiency": "efficiency_pct",
    "adoption": "adoption_pct",
    "ai": "ai_emissions_tco2e_per_year",
    "rebound": "rebound_pct",
}
UNC_COLUMNS = {
    "baseline": "unc_baseline_pct",
    "efficiency": "unc_efficiency_pct",
    "adoption": "unc_adoption_pct",
    "ai": "unc_ai_pct",
    "rebound": "unc_rebound_pct",
}
WIDGET_RANGES = {
    "baseline": (0.0, 5_000_000.0),
    "efficiency": (0.0, 30.0),
    "adoption": (0.0, 100.0),
    "ai": (0.0, 5_000.0),
    "rebound": (-20.0, 50.0),
    "unc": (0.0, 50.0),
}
LABELS = {
    "baseline": "Baseline activity emissions (tCO2e/yr)",
    "efficiency": "Efficiency improvement (%)",
    "adoption": "Adoption rate (%)",
    "ai": "Additional AI emissions (tCO2e/yr)",
    "rebound": "Rebound / demand growth (%)",
}
MCS_DRAWS = 2000
MCS_SEED = 42


def load_scenarios(path=CSV_PATH):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV is empty")
    required = ["scenario", "kind", "direction"] + list(BASE_COLUMNS.values()) + list(UNC_COLUMNS.values())
    missing = [c for c in required if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    df = pd.DataFrame(rows)
    numeric = ["direction"] + list(BASE_COLUMNS.values()) + list(UNC_COLUMNS.values())
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' has non-numeric values")
    return df


def net_change(baseline, direction, efficiency, adoption, rebound, ai):
    return baseline * (1 + direction * efficiency * adoption) * (1 + rebound) + ai - baseline


def low_high(value, unc_pct):
    return value * (1 - unc_pct / 100.0), value * (1 + unc_pct / 100.0)


def monte_carlo(baseline, direction, efficiency, adoption, ai, rebound, uncs, draws=MCS_DRAWS, seed=MCS_SEED):
    rng = np.random.default_rng(seed)
    sampled = {}
    for key, value in [
        ("baseline", baseline),
        ("efficiency", efficiency),
        ("adoption", adoption),
        ("ai", ai),
        ("rebound", rebound),
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


def tornado(baseline, direction, efficiency, adoption, ai, rebound, uncs):
    base = {
        "baseline": baseline,
        "efficiency": efficiency / 100.0,
        "adoption": adoption / 100.0,
        "ai": ai,
        "rebound": rebound / 100.0,
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
        )
        net_hi = net_change(
            args_hi["baseline"], direction, args_hi["efficiency"],
            args_hi["adoption"], args_hi["rebound"], args_hi["ai"],
        )
        results[key] = abs(net_hi - net_lo)
    return results


def assumption_rows(row):
    rows = []
    for key, col in BASE_COLUMNS.items():
        value = float(row[col])
        unc = float(row[UNC_COLUMNS[key]])
        lo, hi = low_high(value, unc)
        rows.append(
            {
                "assumption": key,
                "base": value,
                "unc_pct": unc,
                "low": lo,
                "high": hi,
            }
        )
    return pd.DataFrame(rows)


def run_ui():
    st.set_page_config(page_title="Counterfactual Explorer", layout="wide")
    st.title("Climate-application counterfactual explorer")
    st.caption(
        "Challenge from lecture 02: one net outcome is never enough. Compare a "
        "mitigation application with an emissions-increasing one, vary the "
        "assumptions, and see a range of net outcomes plus which assumption "
        "drives the result."
    )

    try:
        scenarios = load_scenarios()
    except (ValueError, OSError) as exc:
        st.error(f"Cannot load scenarios: {exc}")
        st.stop()

    with st.sidebar:
        st.header("Inputs")
        scenario_name = st.radio("Scenario", scenarios["scenario"].tolist())
        row = scenarios[scenarios["scenario"] == scenario_name].iloc[0]
        direction = int(row["direction"])
        st.caption(
            f"{row['kind']} application (direction {'increases' if direction > 0 else 'reduces'} "
            f"emissions where adopted). Values below are toy assumptions."
        )
        values = {}
        uncs = {}
        for key in BASE_COLUMNS:
            vmin, vmax = WIDGET_RANGES[key]
            default = float(row[BASE_COLUMNS[key]])
            if key in ("baseline", "ai"):
                values[key] = st.number_input(
                    LABELS[key], min_value=vmin, max_value=vmax, value=default,
                    step=vmax / 100.0, format="%.0f",
                )
            else:
                values[key] = st.slider(
                    LABELS[key], min_value=vmin, max_value=vmax, value=default,
                    step=1.0, format="%.0f",
                )
            uncs[key] = st.slider(
                f"Uncertainty ±% on {LABELS[key]}", min_value=0.0, max_value=50.0,
                value=float(row[UNC_COLUMNS[key]]), step=1.0, format="%.0f",
            )

    baseline, efficiency, adoption = values["baseline"], values["efficiency"], values["adoption"]
    ai, rebound = values["ai"], values["rebound"]

    stats = monte_carlo(baseline, direction, efficiency, adoption, ai, rebound, uncs)
    ranges = tornado(baseline, direction, efficiency, adoption, ai, rebound, uncs)
    base_net = net_change(baseline, direction, efficiency / 100.0, adoption / 100.0, rebound / 100.0, ai)
    top_key = max(ranges, key=ranges.get)

    st.subheader("Assumptions used")
    rows_df = assumption_rows(row)
    rows_df["base"] = rows_df["base"].map(lambda v: f"{v:,.0f}")
    rows_df["low"] = rows_df["low"].map(lambda v: f"{v:,.0f}")
    rows_df["high"] = rows_df["high"].map(lambda v: f"{v:,.0f}")
    rows_df["unc_pct"] = rows_df["unc_pct"].map(lambda v: f"±{v:.0f}%")
    st.table(
        rows_df.rename(columns={
            "assumption": "assumption", "base": "base value", "unc_pct": "uncertainty",
            "low": "low", "high": "high",
        })
    )
    st.caption("Assumptions are toy values for demonstration; net change is "
               "baseline × (1 + direction × efficiency × adoption) × (1 + rebound) + AI − baseline.")

    st.subheader("Net outcome range (Monte Carlo, 2000 draws)")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Base net change", f"{base_net:+,.0f} tCO2e")
    col2.metric("Mean", f"{stats['mean']:+,.0f} tCO2e")
    col3.metric("Median", f"{stats['median']:+,.0f} tCO2e")
    col4.metric("p5–p95", f"{stats['p5']:+,.0f} … {stats['p95']:+,.0f}")
    col5.metric("P(net reduction)", f"{stats['p_negative'] * 100:.0f}%")

    draws = stats["draws"]
    hist, edges = np.histogram(draws, bins=25)
    centers = (edges[:-1] + edges[1:]) / 2
    hist_df = pd.DataFrame({"count": hist}, index=[f"{c:+,.0f}" for c in centers])
    st.bar_chart(hist_df, height=300)
    verdict = (
        "reduction" if stats["p_negative"] >= 0.5 else "increase"
    )
    st.write(
        f"The range of outcomes centers on a net **{verdict}** "
        f"(probability of a net reduction: **{stats['p_negative'] * 100:.0f}%**). "
        f"The sign can flip: it depends on the assumptions, not on the application label."
    )

    st.subheader("Which assumption drives the result?")
    tornado_df = pd.DataFrame(
        {"range_tco2e_per_year": [ranges[k] for k in ranges]},
        index=[LABELS[k] for k in ranges],
    )
    st.bar_chart(tornado_df, horizontal=True, height=260)
    st.write(
        f"**Most sensitive assumption: {LABELS[top_key]}** — varying it across its "
        f"uncertainty range moves the net outcome by {ranges[top_key]:,.0f} tCO2e/yr, "
        f"more than any other assumption."
    )

    st.caption(
        "Would you act on a 'reduction' before it is realized? Evidence that "
        "distinguishes a genuine reduction from a claim based on potential "
        "adoption: measured adoption in real deployments, the decision actually "
        "changed, the counterfactual activity, realized (not modeled) emission "
        "outcomes, and the additional AI-related emissions."
    )


if __name__ == "__main__":
    run_ui()
