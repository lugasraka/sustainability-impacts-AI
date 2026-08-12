import pandas as pd
import streamlit as st

import model

LABELS = {
    "demand": "Baseline demand (units of activity per year)",
    "efficiency": "Efficiency improvement after AI (%)",
    "adoption": "Adoption rate (%)",
    "rebound": "Rebound demand increase (%)",
    "lock_in": "Infrastructure lock-in period (years)",
    "intensity": "Resource intensity (kg CO2e per unit of activity)",
}


def run_ui():
    st.set_page_config(page_title="Rebound-Loop Simulator", layout="wide")
    st.title("Rebound-loop simulator")
    st.caption(
        "Challenge from lecture 03: an AI service gets more resource-efficient, but the "
        "rebound loop can make total impact rise anyway. Vary the assumptions and watch "
        "the label switch between 'efficiency scenario' and 'rebound scenario'."
    )

    with st.sidebar:
        st.header("Inputs")
        demand = st.number_input(
            LABELS["demand"], min_value=0.0, max_value=10_000_000.0,
            value=float(model.DEFAULT_DEMAND), step=50_000.0, format="%.0f",
        )
        efficiency = st.slider(
            LABELS["efficiency"], 0.0, 50.0, model.DEFAULT_EFFICIENCY, 1.0
        )
        adoption = st.slider(LABELS["adoption"], 0.0, 100.0, model.DEFAULT_ADOPTION, 1.0)
        rebound = st.slider(LABELS["rebound"], 0.0, 100.0, model.DEFAULT_REBOUND, 1.0)
        lock_in = st.slider(LABELS["lock_in"], 1, 30, model.DEFAULT_LOCK_IN, 1)
        intensity = st.number_input(
            LABELS["intensity"], min_value=0.0, max_value=10.0,
            value=float(model.DEFAULT_INTENSITY), step=0.1, format="%.1f",
        )
        st.caption("All values are toy assumptions for demonstration.")

    baseline = model.annual_impact_tco2e(demand, intensity)
    levels = model.rebound_levels(rebound)
    impacts = {
        "baseline": baseline,
        "low": model.impact_with_ai(demand, intensity, efficiency, adoption, levels["low"]),
        "medium": model.impact_with_ai(demand, intensity, efficiency, adoption, levels["medium"]),
        "high": model.impact_with_ai(demand, intensity, efficiency, adoption, levels["high"]),
    }

    st.subheader("Causal diagram")
    st.markdown(model.causal_diagram_html(), unsafe_allow_html=True)

    st.subheader("Total annual impact under low, medium, and high rebound")
    chart_df = pd.DataFrame(
        {"annual_tco2e": [impacts[k] for k in ("baseline", "low", "medium", "high")]},
        index=["baseline\n(no AI)", f"low rebound\n(0%)", f"medium rebound\n({levels['medium']:.0f}%)",
               f"high rebound\n({levels['high']:.0f}%)"],
    )
    st.bar_chart(chart_df, height=320)
    verdict = model.verdict_text(demand, intensity, efficiency, adoption, rebound)
    if model.is_rebound_scenario(demand, intensity, efficiency, adoption, rebound):
        st.error(verdict)
    else:
        st.success(verdict)

    st.subheader("Cumulative impact over the lock-in period")
    cum = pd.DataFrame(
        {
            "scenario": ["baseline", "low", "medium", "high"],
            "annual_tco2e": [impacts[k] for k in ("baseline", "low", "medium", "high")],
        }
    )
    cum["cumulative_tco2e"] = cum["annual_tco2e"] * lock_in
    cum["annual_tco2e"] = cum["annual_tco2e"].map(lambda v: f"{v:,.0f}")
    cum["cumulative_tco2e"] = cum["cumulative_tco2e"].map(lambda v: f"{v:,.0f}")
    st.table(cum.set_index("scenario"))
    st.caption(
        f"Assumes each rebound level persists for the whole {lock_in} year lock-in period; "
        "per-unit intensity after AI: "
        f"{model.intensity_after(intensity, efficiency, adoption):.3f} kg CO2e/unit "
        f"({(1 - model.intensity_after(intensity, efficiency, adoption) / intensity) * 100:.1f}% "
        "lower than baseline)."
    )

    st.subheader("Social and governance effects the numeric model does not capture")
    for effect in model.SOCIAL_EFFECTS:
        st.write(f"- {effect}")
    st.caption(
        "Reflection: which system-level effect is most likely to be ignored in your use "
        "case, and which stakeholder could provide evidence about it?"
    )


if __name__ == "__main__":
    run_ui()
