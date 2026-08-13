import csv
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).resolve().parent / "models.csv"

REQUIRED_COLUMNS = [
    "task",
    "model",
    "accuracy",
    "energy_kwh_per_1000_requests",
    "grid_gco2e_per_kwh",
    "direct_water_ml_per_1000_requests",
    "indirect_water_ml_per_1000_requests",
    "embodied_carbon_kgco2e_per_device",
    "devices",
    "training_energy_kwh",
]
RESOURCE_COLUMNS = [
    "energy_kwh_per_1000_requests",
    "grid_gco2e_per_kwh",
    "direct_water_ml_per_1000_requests",
    "indirect_water_ml_per_1000_requests",
]
ANNUAL_COLUMNS = [
    "annual_energy_kwh",
    "annual_carbon_tco2e",
    "annual_direct_water_l",
    "annual_indirect_water_l",
]

GRID_PRESETS = {
    "Renewable-heavy (100 g CO2e/kWh)": 100.0,
    "EU average (250 g CO2e/kWh)": 250.0,
    "US average (450 g CO2e/kWh)": 450.0,
    "Coal-heavy (800 g CO2e/kWh)": 800.0,
}
DEFAULT_GRID = 450.0

COOLING_OPTIONS = {
    "Evaporative (baseline)": {"energy_multiplier": 1.0, "direct_water_multiplier": 1.0},
    "Closed-loop / liquid": {"energy_multiplier": 1.10, "direct_water_multiplier": 0.10},
    "Air-cooled": {"energy_multiplier": 1.15, "direct_water_multiplier": 0.0},
}

DEFAULT_HARDWARE_LIFETIME = 4
DEFAULT_TRAINING_YEARS = 2


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
    numeric = [
        "accuracy",
        "energy_kwh_per_1000_requests",
        "grid_gco2e_per_kwh",
        "direct_water_ml_per_1000_requests",
        "indirect_water_ml_per_1000_requests",
        "embodied_carbon_kgco2e_per_device",
        "devices",
        "training_energy_kwh",
    ]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' has non-numeric values")
    return df


def compute_metrics(
    df,
    task,
    volume,
    grid,
    include_embodied=False,
    hardware_lifetime=DEFAULT_HARDWARE_LIFETIME,
    include_training=False,
    training_years=DEFAULT_TRAINING_YEARS,
    rebound=0.0,
    cooling="Evaporative (baseline)",
):
    volume = float(volume)
    if volume < 0:
        raise ValueError("Request volume cannot be negative")
    grid = float(grid)
    rebound = float(rebound)
    hardware_lifetime = float(hardware_lifetime)
    training_years = float(training_years)
    if cooling not in COOLING_OPTIONS:
        raise ValueError(f"Unknown cooling option: {cooling}")
    effective_volume = volume * (1 + rebound / 100.0)
    energy_mult = COOLING_OPTIONS[cooling]["energy_multiplier"]
    water_mult = COOLING_OPTIONS[cooling]["direct_water_multiplier"]

    task_df = df[df["task"] == task]
    rows = []
    for _, row in task_df.iterrows():
        annual_energy = (
            float(row["energy_kwh_per_1000_requests"])
            * energy_mult
            * effective_volume
            / 1000.0
        )
        annual_carbon = annual_energy * grid / 1e6
        annual_direct = (
            float(row["direct_water_ml_per_1000_requests"])
            * water_mult
            * effective_volume
            / 1e6
        )
        annual_indirect = (
            float(row["indirect_water_ml_per_1000_requests"])
            * effective_volume
            / 1e6
        )
        embodied_carbon = 0.0
        if include_embodied:
            embodied_carbon = (
                float(row["embodied_carbon_kgco2e_per_device"])
                * float(row["devices"])
                / hardware_lifetime
                / 1000.0
            )
        training_carbon = 0.0
        training_energy = 0.0
        if include_training:
            training_energy = float(row["training_energy_kwh"]) / training_years
            training_carbon = training_energy * grid / 1e6
        rows.append(
            {
                "task": row["task"],
                "model": row["model"],
                "accuracy": float(row["accuracy"]),
                "grid_gco2e_per_kwh": grid,
                "annual_energy_kwh": annual_energy,
                "annual_carbon_tco2e": annual_carbon,
                "annual_direct_water_l": annual_direct,
                "annual_indirect_water_l": annual_indirect,
                "annual_embodied_tco2e": embodied_carbon,
                "annual_training_tco2e": training_carbon,
                "annual_training_energy_kwh": training_energy,
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


def classify(metrics, min_accuracy, dominated):
    labels = {}
    for _, row in metrics.iterrows():
        if row["accuracy"] < min_accuracy:
            labels[row["model"]] = "below"
        elif dominated[row["model"]]:
            labels[row["model"]] = "dominated"
        else:
            labels[row["model"]] = "candidate"
    return labels


def recommend(metrics, min_accuracy, dominated):
    eligible = metrics[metrics["accuracy"] >= min_accuracy]
    if eligible.empty:
        return None, None
    non_dominated = eligible[
        ~eligible["model"].isin([m for m, dom in dominated.items() if dom])
    ]
    candidates = non_dominated if not non_dominated.empty else eligible
    best = candidates.loc[candidates["annual_carbon_tco2e"].idxmin()]
    top_accuracy = eligible["accuracy"].max()
    return best, top_accuracy
