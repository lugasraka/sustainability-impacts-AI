import pandas as pd
import streamlit as st

import model


def run_ui():
    st.set_page_config(page_title="Counterfactual Explorer", layout="wide")
    st.title("Climate-application counterfactual explorer")
    st.caption(
        "Challenge from lecture 02: one net outcome is never enough. Compare a "
        "mitigation application with an emissions-increasing one, vary the "
        "assumptions, and see a range of net outcomes, which assumption drives the "
        "result, and how the headline potential compares with the realized net."
    )

    try:
        scenarios = model.load_scenarios()
    except (ValueError, OSError) as exc:
        st.error(f"Cannot load scenarios: {exc}")
        st.stop()

    names = scenarios["scenario"].tolist()

    with st.sidebar:
        st.header("Inputs")
        scenario_name = st.radio("Scenario", names)
        row = scenarios[scenarios["scenario"] == scenario_name].iloc[0]
        direction = int(row["direction"])
        compare_name = st.selectbox(
            "Compare with", ["none"] + [n for n in names if n != scenario_name]
        )
        st.caption(
            f"{row['kind']} application (direction "
            f"{'increases' if direction > 0 else 'reduces'} emissions where adopted). "
            f"Values below are toy assumptions."
        )
        values = {}
        uncs = {}
        for key in model.BASE_COLUMNS:
            vmin, vmax = model.WIDGET_RANGES[key]
            default = float(row[model.BASE_COLUMNS[key]])
            if key in ("baseline", "ai"):
                values[key] = st.number_input(
                    model.LABELS[key], min_value=vmin, max_value=vmax, value=default,
                    step=vmax / 100.0, format="%.0f",
                )
            else:
                values[key] = st.slider(
                    model.LABELS[key], min_value=vmin, max_value=vmax, value=default,
                    step=1.0, format="%.0f",
                )
        with st.expander("Uncertainty ranges (±%)"):
            for key in model.BASE_COLUMNS:
                uncs[key] = st.slider(
                    f"±% on {model.LABELS[key]}", min_value=0.0, max_value=50.0,
                    value=float(row[model.UNC_COLUMNS[key]]), step=1.0, format="%.0f",
                )
        st.divider()
        horizon = st.slider("Projection horizon (years)", 1, 30, 10, 1)
        ramp_years = st.slider(
            "Adoption ramp (years)", 1, 20, int(row["adoption_ramp_years"]), 1
        )

    baseline, efficiency, adoption = values["baseline"], values["efficiency"], values["adoption"]
    ai, rebound, leakage, additionality = (
        values["ai"], values["rebound"], values["leakage"], values["additionality"],
    )

    stats = model.monte_carlo(
        baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality, uncs
    )
    ranges = model.tornado(
        baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality, uncs
    )
    base_net = model.net_change(
        baseline, direction, efficiency / 100.0, adoption / 100.0,
        rebound / 100.0, ai, leakage / 100.0, additionality / 100.0,
    )
    headline = model.headline_potential(baseline, direction, efficiency)
    realized = model.realized_net(
        baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality
    )
    ramp_df = model.ramp_projection(
        baseline, direction, efficiency, adoption, ai, rebound, leakage, additionality,
        ramp_years, horizon,
    )
    top_key = max(ranges, key=ranges.get)

    compare_stats = None
    compare_direction = None
    if compare_name != "none":
        c_row = scenarios[scenarios["scenario"] == compare_name].iloc[0]
        compare_direction = int(c_row["direction"])
        c_vals = {k: float(c_row[model.BASE_COLUMNS[k]]) for k in model.BASE_COLUMNS}
        c_uncs = {k: float(c_row[model.UNC_COLUMNS[k]]) for k in model.BASE_COLUMNS}
        compare_stats = model.monte_carlo(
            c_vals["baseline"], compare_direction, c_vals["efficiency"],
            c_vals["adoption"], c_vals["ai"], c_vals["rebound"],
            c_vals["leakage"], c_vals["additionality"], c_uncs,
        )

    st.subheader("Assumptions used")
    rows_df = model.assumption_rows(values, uncs)
    rows_df["base"] = rows_df["base"].map(lambda v: f"{v:,.0f}")
    rows_df["low"] = rows_df["low"].map(lambda v: f"{v:,.0f}")
    rows_df["high"] = rows_df["high"].map(lambda v: f"{v:,.0f}")
    rows_df["unc_pct"] = rows_df["unc_pct"].map(lambda v: f"±{v:.0f}%")
    rows_df["assumption"] = rows_df["assumption"].map(model.LABELS)
    st.table(
        rows_df.rename(columns={
            "assumption": "assumption", "base": "base value", "unc_pct": "uncertainty",
            "low": "low", "high": "high",
        })
    )
    st.caption(
        "Assumptions are toy values for demonstration; net change is baseline × "
        "(1 + direction × efficiency × adoption × additionality × (1 − leakage)) × "
        "(1 + rebound) + AI − baseline."
    )

    st.subheader("Net outcome range (Monte Carlo, 2000 draws)")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Base net change", f"{base_net:+,.0f} tCO2e")
    col2.metric("Mean", f"{stats['mean']:+,.0f} tCO2e")
    col3.metric("Median", f"{stats['median']:+,.0f} tCO2e")
    col4.metric("p5–p95", f"{stats['p5']:+,.0f} … {stats['p95']:+,.0f}")
    col5.metric("P(net reduction)", f"{stats['p_negative'] * 100:.0f}%")

    if compare_stats is not None:
        overlay_df = model.overlay_histogram_df(
            stats["draws"], scenario_name, compare_stats["draws"], compare_name
        )
        st.bar_chart(overlay_df, height=320)
        main_verdict = "reduction" if stats["p_negative"] >= 0.5 else "increase"
        comp_verdict = "reduction" if compare_stats["p_negative"] >= 0.5 else "increase"
        st.write(
            f"**{scenario_name}** centers on a net **{main_verdict}** "
            f"(P(reduction) {stats['p_negative'] * 100:.0f}%); "
            f"**{compare_name}** centers on a net **{comp_verdict}** "
            f"(P(reduction) {compare_stats['p_negative'] * 100:.0f}%). The sign depends "
            f"on the assumptions, not on the application label."
        )
    else:
        hist_df = model.histogram_df(stats["draws"])
        st.bar_chart(hist_df, height=320)
        verdict = "reduction" if stats["p_negative"] >= 0.5 else "increase"
        st.write(
            f"The range of outcomes centers on a net **{verdict}** "
            f"(probability of a net reduction: **{stats['p_negative'] * 100:.0f}%**). "
            f"The sign can flip: it depends on the assumptions, not on the application label."
        )

    st.subheader("Which assumption drives the result?")
    tornado_df = pd.DataFrame(
        {"range_tco2e_per_year": [ranges[k] for k in ranges]},
        index=[model.LABELS[k] for k in ranges],
    )
    st.bar_chart(tornado_df, horizontal=True, height=300)
    st.write(
        f"**Most sensitive assumption: {model.LABELS[top_key]}** — varying it across its "
        f"uncertainty range moves the net outcome by {ranges[top_key]:,.0f} tCO2e/yr, "
        f"more than any other assumption."
    )

    st.subheader("Potential vs realized")
    p1, p2, p3 = st.columns(3)
    p1.metric("Headline potential", f"{headline:+,.0f} tCO2e/yr")
    p2.metric("Realized net", f"{realized:+,.0f} tCO2e/yr")
    p3.metric("Gap", f"{headline - realized:+,.0f} tCO2e/yr")
    ramp_chart = ramp_df.set_index("year")[
        ["net_tco2e", "headline_potential_tco2e"]
    ].rename(columns={
        "net_tco2e": "realized net (with ramp)",
        "headline_potential_tco2e": "headline potential",
    })
    st.line_chart(ramp_chart, height=280)
    st.caption(
        "Headline potential assumes full adoption with no leakage, additionality "
        "discount, rebound, or AI-side cost — the style of claim the lecture warns "
        "against. Realized net applies the current assumptions and an adoption ramp."
    )

    st.subheader("Counterfactual story")
    story = {}
    cols = st.columns(2)
    for i, (key, label) in enumerate(model.STORY_FIELDS):
        with cols[i % 2]:
            story[key] = st.text_area(
                label, value=str(row[key]), key=f"story_{key}", height=70
            )

    markdown = model.to_markdown(
        scenario_name, row["kind"], direction, values, uncs, stats, base_net,
        top_key, headline, realized, story, ramp_years, horizon,
    )
    st.download_button(
        "Download report (Markdown)", markdown,
        file_name="counterfactual-assessment.md", mime="text/markdown",
    )
    with st.expander("Preview Markdown report"):
        st.code(markdown, language="markdown")

    st.subheader("Reflection")
    st.caption(
        "Would you act on a 'reduction' before it is realized? Evidence that "
        "distinguishes a genuine reduction from a claim based on potential "
        "adoption: measured adoption in real deployments, the decision actually "
        "changed, the counterfactual activity, realized (not modeled) emission "
        "outcomes, and the additional AI-related emissions."
    )


if __name__ == "__main__":
    run_ui()
