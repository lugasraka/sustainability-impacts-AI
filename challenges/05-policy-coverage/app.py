import pandas as pd
import streamlit as st

import coverage


def render_source_links(source):
    links = coverage.source_links(source)
    if not links:
        return source
    parts = []
    for key, url in links:
        parts.append(f"[{key}]({url})")
    return source + " — " + ", ".join(parts)


def style_heatmap(pivot):
    def cell(v):
        if not isinstance(v, str):
            return ""
        return f"background-color: {coverage.STATUS_STYLE.get(v, 'white')}"

    return pivot.style.map(cell)


def persona_labeled_matrix(df, persona):
    pm = coverage.persona_matrix(df, persona)
    labeled = pm.copy()
    for stage in labeled.index:
        for col in labeled.columns:
            v = labeled.loc[stage, col]
            if pd.isna(v):
                labeled.loc[stage, col] = "not measured"
            elif bool(v):
                labeled.loc[stage, col] = "sees it"
            else:
                labeled.loc[stage, col] = "hidden"
    return labeled


def style_persona(pivot):
    def cell(v):
        if v == "sees it":
            return "background-color: lightgreen"
        if v == "hidden":
            return "background-color: lightcoral"
        return "background-color: lightgray"

    return pivot.style.map(cell)


def run_ui():
    st.set_page_config(page_title="Policy Coverage Matrix", layout="wide")
    st.title("Policy coverage matrix")
    st.caption(
        "Challenge from lecture 05: see at a glance which lifecycle stages a transparency "
        "regime measures, who receives the information, and where it leaves a gap. All rows "
        "are derived from the lecture slides (67-76); legal details and implementation "
        "status change, so verify current texts before relying on any entry."
    )

    try:
        df = coverage.load_policy()
    except (ValueError, OSError) as exc:
        st.error(f"Cannot load policy data: {exc}")
        st.stop()

    all_stages = coverage.STAGES
    all_initiatives = df["initiative"].unique().tolist()
    all_audiences = sorted(df["reporting_audience"].unique().tolist())

    with st.sidebar:
        st.header("Filters (Overview, Explore)")
        stages = st.multiselect("Lifecycle stage", all_stages, default=all_stages)
        initiatives = st.multiselect("Initiative", all_initiatives, default=all_initiatives)
        audiences = st.multiselect("Reporting audience", all_audiences, default=all_audiences)
        statuses = st.multiselect("Coverage status", coverage.STATUSES, default=coverage.STATUSES)
        categories = st.multiselect(
            "Impact category", coverage.IMPACT_CATEGORIES, default=[]
        )
        st.caption(
            "Color legend: covered = green, partial = yellow, not_covered = red. "
            "Empty cells mean the initiative has no entry for that stage."
        )

    filtered = coverage.filter_rows(df, stages, initiatives, audiences, statuses, categories)

    tab_overview, tab_persona, tab_category, tab_gaps, tab_compare, tab_explore = st.tabs(
        [
            "Overview & scorecard",
            "Decision-maker lens",
            "Impact-category cross-cut",
            "Darkest gaps",
            "Compare regimes",
            "Explore & export",
        ]
    )

    with tab_overview:
        overall = coverage.overall_score(filtered)
        stage_scores = coverage.stage_scores(filtered)
        initiative_scores = coverage.initiative_scores(filtered)

        c1, c2, c3 = st.columns(3)
        c1.metric("Overall transparency score", f"{overall * 100:.0f}%")
        c2.metric("Rows shown", f"{len(filtered)} of {len(df)}")
        c3.metric("Initiatives", len(filtered["initiative"].unique()))

        left, right = st.columns(2)
        with left:
            st.markdown("**Lifecycle stages, least to most measured**")
            st.bar_chart(
                stage_scores.set_index("stage")["score"], height=300, horizontal=True
            )
        with right:
            st.markdown("**Initiative breadth (average coverage)**")
            st.bar_chart(
                initiative_scores.set_index("initiative")["score"], height=300, horizontal=True
            )

        st.markdown("**Coverage heatmap**")
        pivot = coverage.heatmap_df(filtered)
        st.dataframe(style_heatmap(pivot), width="stretch")

    with tab_persona:
        persona = st.radio(
            "I am a…",
            coverage.PERSONAS,
            index=coverage.PERSONAS.index("Downstream app provider"),
            horizontal=True,
        )
        st.caption(
            "What this persona can actually receive. A regime only improves "
            "accountability when the data reaches the people making deployment decisions."
        )
        labeled = persona_labeled_matrix(df, persona)
        st.dataframe(style_persona(labeled), width="stretch")

        acc = coverage.persona_accessibility(df, persona)
        hidden = acc[~acc["persona_can_see"]]
        if hidden.empty:
            st.success("Nothing measured is hidden from this persona.")
        else:
            st.markdown("**Measured, but hidden from this persona**")
            for _, row in hidden.iterrows():
                st.write(
                    f"- **{row['initiative']}** measures **{row['stage']}** "
                    f"({row['required_metric']}), but discloses it only to "
                    f"**{row['reporting_audience']}**."
                )

    with tab_category:
        category = st.radio(
            "Impact category", coverage.IMPACT_CATEGORIES, horizontal=True
        )
        cat_rows = filtered[coverage.match_category(filtered, category)]
        st.caption(
            f"Where '{category}' appears across the lifecycle, across the initiatives. "
            f"Empty stages mean no initiative touches this category there."
        )
        pivot = cat_rows.pivot_table(
            index="stage", columns="initiative", values="coverage_status", aggfunc="first"
        ).reindex(coverage.STAGES)
        st.dataframe(style_heatmap(pivot), width="stretch")

        uncovered = cat_rows[cat_rows["coverage_status"] == "not_covered"]
        if uncovered.empty:
            st.success(f"No explicit '{category}' gaps in the current view.")
        else:
            st.markdown(f"**'{category}' gaps (not covered)**")
            for _, row in uncovered.iterrows():
                st.write(f"- **{row['initiative']}** — {row['known_omission']}")

    with tab_gaps:
        st.caption(
            "Auto-ranked omissions: stages measured by no initiative, data disclosed only "
            "to authorities, and metrics that are never split in the way the outcome depends on."
        )
        gaps = coverage.gap_ranking(df)
        for i, gap in enumerate(gaps, 1):
            icon = {"high": "🔴", "medium": "🟠", "low": "🟡"}[gap["severity"]]
            st.write(f"{icon} **{i}. {gap['text']}** — {gap['detail']}")

    with tab_compare:
        col_a, col_b = st.columns(2)
        with col_a:
            initiative_a = st.selectbox("Initiative A", all_initiatives, index=0)
        with col_b:
            initiative_b = st.selectbox(
                "Initiative B", all_initiatives, index=min(1, len(all_initiatives) - 1)
            )
        diff = coverage.diff_df(df, initiative_a, initiative_b)
        n_agree = int(diff["same"].sum())

        def diff_cell(v):
            if v == "covered":
                return "background-color: green"
            if v == "partial":
                return "background-color: yellow"
            if v == "not_covered":
                return "background-color: red"
            return ""

        styled = diff[[initiative_a, initiative_b]].style.map(diff_cell)
        st.dataframe(styled, width="stretch")
        st.write(f"The two initiatives agree on **{n_agree} of {len(coverage.STAGES)}** stages.")

    with tab_explore:
        st.markdown("**Filtered policy rows**")
        display = filtered.drop(columns=["impact_category"]) if "impact_category" in filtered.columns else filtered
        st.dataframe(display, width="stretch", hide_index=True)
        st.caption(f"{len(filtered)} of {len(df)} rows shown.")

        st.markdown("**Cell drill-down**")
        dc1, dc2 = st.columns(2)
        with dc1:
            drill_stage = st.selectbox("Stage", all_stages)
        with dc2:
            drill_initiative = st.selectbox("Initiative", all_initiatives)
        row = coverage.drill_row(df, drill_stage, drill_initiative)
        if row is None:
            st.info("No entry for this stage and initiative.")
        else:
            fields = [
                ("Coverage", row["coverage_status"]),
                ("Impact category", row["impact_category"]),
                ("Responsible actor", row["responsible_actor"]),
                ("Required metric", row["required_metric"]),
                ("Reporting audience", row["reporting_audience"]),
                ("Geographic scope", row["geographic_scope"]),
                ("Known omission", row["known_omission"]),
                ("Source", render_source_links(row["source"])),
            ]
            for label, value in fields:
                st.markdown(f"**{label}:** {value}")

        st.markdown("**Export gap report**")
        report = coverage.to_markdown(
            df, coverage.gap_ranking(df), coverage.overall_score(df),
            coverage.stage_scores(df), coverage.initiative_scores(df),
        )
        st.download_button(
            "Download report (Markdown)", report,
            file_name="policy-coverage-report.md", mime="text/markdown",
        )
        with st.expander("Preview Markdown report"):
            st.code(report, language="markdown")

    st.subheader("Reflection")
    st.write(
        "Which missing disclosure would most improve a real deployment or siting "
        "decision, and why is it currently difficult to collect? Candidates from the "
        "lecture: inference-level energy, separated water withdrawal/consumption, "
        "marginal grid intensity, application-level emissions, and seasonal water or "
        "grid-peak conditions at the permit level."
    )


if __name__ == "__main__":
    run_ui()
