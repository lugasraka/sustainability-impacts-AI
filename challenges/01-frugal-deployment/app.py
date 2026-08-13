import pandas as pd
import streamlit as st

import model

METRIC_LABELS = {
    "annual_energy_kwh": "Energy (kWh/yr)",
    "annual_carbon_tco2e": "Carbon (tCO2e/yr)",
    "annual_direct_water_l": "Direct water (L/yr)",
    "annual_indirect_water_l": "Indirect water (L/yr)",
}


def format_table(metrics, labels, min_accuracy):
    display = metrics.copy()
    display["annual_energy_kwh"] = display["annual_energy_kwh"].map(lambda v: f"{v:,.1f}")
    display["annual_carbon_tco2e"] = display["annual_carbon_tco2e"].map(lambda v: f"{v:,.3f}")
    display["annual_direct_water_l"] = display["annual_direct_water_l"].map(lambda v: f"{v:,.0f}")
    display["annual_indirect_water_l"] = display["annual_indirect_water_l"].map(lambda v: f"{v:,.0f}")
    display["annual_embodied_tco2e"] = display["annual_embodied_tco2e"].map(lambda v: f"{v:,.3f}")
    display["annual_training_tco2e"] = display["annual_training_tco2e"].map(lambda v: f"{v:,.3f}")
    status = []
    for _, row in metrics.iterrows():
        if row["accuracy"] < min_accuracy:
            status.append("below min accuracy")
        elif labels[row["model"]] == "dominated":
            status.append("dominated")
        else:
            status.append("candidate")
    display["status"] = status
    cols = ["model", "accuracy"] + model.ANNUAL_COLUMNS + [
        "annual_embodied_tco2e", "annual_training_tco2e", "status",
    ]
    return display[cols]


def row_style(row):
    if row["status"] == "candidate":
        color = "lightgreen"
    elif row["status"] == "dominated":
        color = "lightcoral"
    else:
        color = "lightgray"
    return [f"background-color: {color}"] * len(row)


def run_ui():
    st.set_page_config(page_title="Frugal Deployment Selector", layout="wide")
    st.title("Frugal deployment selector")
    st.caption(
        "Challenge from lecture 01: compare hypothetical models for the same task "
        "across accuracy, energy, carbon, and water — then explore how the grid, "
        "embodied hardware, training, cooling, and usage growth change which model "
        "looks frugal."
    )

    try:
        df = model.load_models()
    except (ValueError, OSError) as exc:
        st.error(f"Cannot load models: {exc}")
        st.stop()

    tasks = df["task"].unique().tolist()

    with st.sidebar:
        st.header("Inputs")
        task = st.radio("Task", tasks)
        task_models = df[df["task"] == task]
        volume = st.number_input(
            "Annual request volume",
            min_value=0.0,
            value=1_000_000.0,
            step=100_000.0,
            format="%.0f",
        )
        min_accuracy = st.slider("Minimum acceptable accuracy", 0.0, 1.0, 0.90, 0.01)
        st.divider()

        preset_names = list(model.GRID_PRESETS.keys())
        grid_preset = st.radio(
            "Grid carbon intensity",
            preset_names,
            index=preset_names.index("US average (450 g CO2e/kWh)"),
        )
        use_custom_grid = st.checkbox("Use a custom grid intensity")
        if use_custom_grid:
            grid = st.number_input(
                "Grid intensity (g CO2e / kWh)",
                min_value=0.0,
                value=model.GRID_PRESETS[grid_preset],
                step=25.0,
                format="%.0f",
            )
        else:
            grid = model.GRID_PRESETS[grid_preset]
        st.divider()

        include_embodied = st.checkbox("Include embodied (hardware) emissions", value=False)
        hardware_lifetime = st.slider(
            "Hardware lifetime (years)", 1, 10, model.DEFAULT_HARDWARE_LIFETIME, 1,
        )
        include_training = st.checkbox("Include amortized training emissions", value=False)
        training_years = st.slider(
            "Training amortization (years)", 1, 10, model.DEFAULT_TRAINING_YEARS, 1,
        )
        rebound = st.slider(
            "Usage growth / rebound (%)", 0.0, 200.0, 0.0, 5.0,
        )
        cooling = st.radio("Cooling technology", list(model.COOLING_OPTIONS.keys()))
        st.caption("All values are toy assumptions for demonstration.")

    metrics = model.compute_metrics(
        df, task, volume, grid, include_embodied, hardware_lifetime,
        include_training, training_years, rebound, cooling,
    )
    dominated = model.find_dominated(metrics, min_accuracy)
    labels = model.classify(metrics, min_accuracy, dominated)
    best, top_accuracy = model.recommend(metrics, min_accuracy, dominated)

    st.subheader("Assumptions used")
    st.write(
        f"Task: **{task}** | volume: **{volume:,.0f}** requests/yr "
        f"(scaled to **{volume * (1 + rebound / 100):,.0f}** after {rebound:.0f}% growth) | "
        f"minimum accuracy: **{min_accuracy:.2f}** | grid: **{grid:,.0f} g CO2e/kWh** | "
        f"cooling: **{cooling}**"
    )
    flags = []
    if include_embodied:
        flags.append(f"embodied amortized over {hardware_lifetime} yr")
    if include_training:
        flags.append(f"training amortized over {training_years} yr")
    st.caption(
        "Per-1000-request values come from `models.csv`. "
        + ("Included: " + ", ".join(flags) + "." if flags else "Embodied and training excluded by default.")
    )

    n_candidates = sum(1 for v in labels.values() if v == "candidate")
    n_dominated = sum(1 for v in labels.values() if v == "dominated")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lowest-carbon candidate", best["model"] if best is not None else "—")
    c2.metric(
        "Its carbon", f"{best['annual_carbon_tco2e']:,.3f} tCO2e/yr" if best is not None else "—",
    )
    c3.metric(
        "Its water (direct + indirect)",
        f"{best['annual_direct_water_l'] + best['annual_indirect_water_l']:,.0f} L/yr"
        if best is not None else "—",
    )
    c4.metric("Dominated models", n_dominated)

    st.subheader("Model comparison")
    metric_choice = st.radio(
        "Metric to compare", list(METRIC_LABELS.keys()),
        format_func=lambda k: METRIC_LABELS[k], horizontal=True,
    )
    chart_df = metrics.set_index("model")[[metric_choice]]
    chart_df = chart_df.rename(columns={metric_choice: METRIC_LABELS[metric_choice]})
    st.bar_chart(chart_df, height=320)

    water_col1, water_col2 = st.columns(2)
    with water_col1:
        st.markdown("**Direct vs indirect water**")
        water_df = metrics.set_index("model")[
            ["annual_direct_water_l", "annual_indirect_water_l"]
        ].rename(columns={
            "annual_direct_water_l": "direct",
            "annual_indirect_water_l": "indirect",
        })
        st.bar_chart(water_df, height=320)
    with water_col2:
        if include_training:
            st.markdown("**Inference vs training carbon**")
            split_df = metrics.set_index("model")[
                ["annual_carbon_tco2e", "annual_training_tco2e"]
            ].rename(columns={
                "annual_carbon_tco2e": "inference + embodied",
                "annual_training_tco2e": "training",
            })
            st.bar_chart(split_df, height=320)
        else:
            st.markdown("**Training split**")
            st.info(
                "Enable 'amortized training emissions' in the sidebar to compare "
                "inference against training carbon."
            )

    st.subheader("Accuracy vs carbon (Pareto frontier)")
    pareto_df = metrics[["model", "accuracy", "annual_carbon_tco2e"]].copy()
    pareto_df["status"] = [labels[m] for m in pareto_df["model"]]
    pareto_df["status_color"] = pareto_df["status"].map(
        {"candidate": "#2ca02c", "dominated": "#d62728", "below": "#7f7f7f"}
    )
    st.scatter_chart(
        pareto_df, x="accuracy", y="annual_carbon_tco2e", color="status_color",
        size=None, height=320,
    )
    st.caption(
        "Green = candidate (non-dominated), red = dominated by another model, "
        "gray = below minimum accuracy. A model is dominated when another meets or "
        "beats its accuracy while using no more energy, carbon, or water."
    )

    st.subheader("Annual results")
    display = format_table(metrics, labels, min_accuracy)
    st.dataframe(display.style.apply(row_style, axis=1), hide_index=True)

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
                f"The most accurate eligible model reaches {top_accuracy:.2f}, so you "
                f"give up {accuracy_gap:.2f} accuracy points. Trade-offs to weigh: "
                f"latency, reliability, quality on edge cases, and whether the accuracy "
                f"gap matters for the task."
            )
        st.caption(
            "Would you accept this model if it were slightly less accurate, slower, or "
            "less reliable? Evidence that would help: measured task-level quality, "
            "latency/service-level agreements, and failure-cost analysis. Watch how "
            "changing the grid, cooling, or growth can flip which model is frugal."
        )


if __name__ == "__main__":
    run_ui()
