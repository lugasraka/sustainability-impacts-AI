import csv
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

CSV_PATH = Path(__file__).resolve().parent / "models.csv"
RESOURCE_COLUMNS = [
    "energy_kwh_per_1000_requests",
    "grid_gco2e_per_kwh",
    "direct_water_ml_per_1000_requests",
    "indirect_water_ml_per_1000_requests",
]
REQUIRED_COLUMNS = ["task", "model", "accuracy"] + RESOURCE_COLUMNS
ANNUAL_COLUMNS = [
    "annual_energy_kwh",
    "annual_carbon_tco2e",
    "annual_direct_water_l",
    "annual_indirect_water_l",
]


def load_models(path=CSV_PATH):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV is empty")
    missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    df = pd.DataFrame(rows)
    if df["model"].duplicated().any():
        raise ValueError("model column contains duplicate names")
    for col in ["accuracy"] + RESOURCE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' has non-numeric values")
    return df


def grid_for_model(row, grid_override):
    if grid_override is not None:
        return float(grid_override), "override"
    return float(row["grid_gco2e_per_kwh"]), "csv"


def compute_metrics(df, volume, grid_override=None):
    volume = float(volume)
    if volume < 0:
        raise ValueError("Request volume cannot be negative")
    rows = []
    for _, row in df.iterrows():
        grid, grid_source = grid_for_model(row, grid_override)
        annual_energy = float(row["energy_kwh_per_1000_requests"]) * volume / 1000.0
        annual_carbon = annual_energy * grid / 1e6
        annual_direct = float(row["direct_water_ml_per_1000_requests"]) * volume / 1e6
        annual_indirect = float(row["indirect_water_ml_per_1000_requests"]) * volume / 1e6
        rows.append(
            {
                "task": row["task"],
                "model": row["model"],
                "accuracy": float(row["accuracy"]),
                "grid_gco2e_per_kwh": grid,
                "grid_source": grid_source,
                "annual_energy_kwh": annual_energy,
                "annual_carbon_tco2e": annual_carbon,
                "annual_direct_water_l": annual_direct,
                "annual_indirect_water_l": annual_indirect,
            }
        )
    return pd.DataFrame(rows)


def find_dominated(metrics, min_accuracy):
    eligible = metrics[metrics["accuracy"] >= min_accuracy]
    dominated = {name: [] for name in metrics["model"]}
    for _, row in eligible.iterrows():
        for _, other in eligible.iterrows():
            if other["model"] == row["model"]:
                continue
            if other["accuracy"] < row["accuracy"]:
                continue
            not_worse = all(other[c] <= row[c] for c in ANNUAL_COLUMNS)
            strictly_better = any(other[c] < row[c] for c in ANNUAL_COLUMNS)
            if not_worse and strictly_better:
                dominated[row["model"]].append(other["model"])
    return dominated


def recommend(metrics, min_accuracy, dominated):
    eligible = metrics[metrics["accuracy"] >= min_accuracy]
    if eligible.empty:
        return None, None
    non_dominated = eligible[~eligible["model"].isin(
        [m for m, dom in dominated.items() if dom]
    )]
    candidates = non_dominated if not non_dominated.empty else eligible
    best = candidates.loc[candidates["annual_carbon_tco2e"].idxmin()]
    top_accuracy = eligible["accuracy"].max()
    return best, top_accuracy


def format_table(metrics, dominated, min_accuracy):
    display = metrics.copy()
    display["annual_energy_kwh"] = display["annual_energy_kwh"].map(
        lambda v: f"{v:,.1f}"
    )
    display["annual_carbon_tco2e"] = display["annual_carbon_tco2e"].map(
        lambda v: f"{v:,.3f}"
    )
    display["annual_direct_water_l"] = display["annual_direct_water_l"].map(
        lambda v: f"{v:,.0f}"
    )
    display["annual_indirect_water_l"] = display["annual_indirect_water_l"].map(
        lambda v: f"{v:,.0f}"
    )
    display["grid_gco2e_per_kwh"] = display["grid_gco2e_per_kwh"].map(
        lambda v: f"{v:,.0f}"
    )
    display["grid_source"] = display["grid_source"].map(
        lambda v: "override" if v == "override" else "csv"
    )
    status = []
    for _, row in metrics.iterrows():
        if row["accuracy"] < min_accuracy:
            status.append("below min accuracy - excluded")
        elif dominated[row["model"]]:
            status.append("dominated by " + ", ".join(dominated[row["model"]]))
        else:
            status.append("candidate")
    display["status"] = status
    return display[["model", "accuracy", "grid_gco2e_per_kwh", "grid_source"] + ANNUAL_COLUMNS + ["status"]]


def run_ui():
    st.set_page_config(page_title="Frugal Deployment Selector", layout="wide")
    st.title("Frugal deployment selector")
    st.caption(
        "Challenge from lecture 01: compare hypothetical models for the same task "
        "and flag models dominated by another with equal or better accuracy and "
        "lower resource use."
    )

    with st.sidebar:
        st.header("Inputs")
        volume = st.number_input(
            "Annual request volume",
            min_value=0.0,
            value=1_000_000.0,
            step=100_000.0,
            format="%.0f",
        )
        min_accuracy = st.slider("Minimum acceptable accuracy", 0.0, 1.0, 0.90, 0.01)
        use_override = st.checkbox("Override grid intensity for all models")
        grid_override = None
        if use_override:
            grid_override = st.number_input(
                "Grid intensity (g CO2e / kWh)",
                min_value=0.0,
                value=450.0,
                step=25.0,
                format="%.0f",
            )

    try:
        df = load_models()
        metrics = compute_metrics(df, volume, grid_override)
    except (ValueError, OSError) as exc:
        st.error(f"Cannot load or compute models: {exc}")
        st.stop()

    dominated = find_dominated(metrics, min_accuracy)
    best, top_accuracy = recommend(metrics, min_accuracy, dominated)

    st.subheader("Assumptions used")
    st.write(
        f"Request volume: **{volume:,.0f}** requests/year | "
        f"minimum accuracy: **{min_accuracy:.2f}** | "
        f"annual figures scale the per-1000-request values in `models.csv`."
    )
    st.table(
        metrics[["model", "grid_gco2e_per_kwh", "grid_source"]].rename(
            columns={
                "grid_gco2e_per_kwh": "grid intensity applied (g CO2e/kWh)",
                "grid_source": "source",
            }
        )
    )

    st.subheader("Annual results")
    display = format_table(metrics, dominated, min_accuracy)
    color_map = {"candidate": "lightgreen", "dominated": "lightcoral", "below": "lightgray"}

    def row_style(row):
        status = row["status"]
        if status == "candidate":
            return [f"background-color: {color_map['candidate']}"] * len(row)
        if status.startswith("dominated"):
            return [f"background-color: {color_map['dominated']}"] * len(row)
        return [f"background-color: {color_map['below']}"] * len(row)

    st.dataframe(display.style.apply(row_style, axis=1))

    st.subheader("Recommendation")
    if best is None:
        st.info("No model meets the minimum accuracy bar.")
    else:
        accuracy_gap = top_accuracy - best["accuracy"]
        st.write(
            f"Lowest-footprint non-dominated model meeting the bar: **{best['model']}** "
            f"(accuracy {best['accuracy']:.2f})."
        )
        if accuracy_gap > 0:
            st.write(
                f"The most accurate eligible model reaches {top_accuracy:.2f}, "
                f"so you give up {accuracy_gap:.2f} accuracy points. Trade-offs to "
                f"weigh: latency, reliability, quality on edge cases, and whether "
                f"the accuracy gap matters for the task."
            )
        st.caption(
            "Would you accept this model if it were slightly less accurate, slower, "
            "or less reliable? Evidence that would help: measured task-level quality, "
            "latency/service-level agreements, and failure-cost analysis."
        )


if __name__ == "__main__":
    run_ui()
