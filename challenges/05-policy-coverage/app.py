import pandas as pd
import streamlit as st

import coverage


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

    all_stages = sorted(df["stage"].unique().tolist())
    all_initiatives = df["initiative"].unique().tolist()
    all_audiences = sorted(df["reporting_audience"].unique().tolist())

    with st.sidebar:
        st.header("Filters")
        stages = st.multiselect("Lifecycle stage", all_stages, default=all_stages)
        initiatives = st.multiselect("Initiative", all_initiatives, default=all_initiatives)
        audiences = st.multiselect("Reporting audience", all_audiences, default=all_audiences)
        statuses = st.multiselect(
            "Coverage status", coverage.STATUSES, default=coverage.STATUSES
        )
        st.caption(
            "Color legend: covered = green, partial = yellow, not_covered = red. "
            "Empty cells mean the initiative has no entry for that stage."
        )

    st.subheader("Coverage heatmap")
    pivot = coverage.heatmap_df(df)
    styled = pivot.style.map(
        lambda v: f"background-color: {coverage.STATUS_STYLE.get(v, 'white')}"
    )
    st.dataframe(styled, width="stretch")

    st.subheader("Filtered policy rows")
    filtered = coverage.filter_rows(df, stages, initiatives, audiences, statuses)
    st.dataframe(filtered, width="stretch", hide_index=True)
    st.caption(f"{len(filtered)} of {len(df)} rows shown.")

    st.subheader("Gap drill-down")
    stage = st.selectbox("Pick a lifecycle stage", all_stages)
    counts = coverage.stage_coverage_counts(df, stage)
    st.write(
        f"**{stage}:** {counts['covered']} initiative(s) fully cover it, "
        f"{counts['partial']} partially, {counts['not_covered']} do not cover it "
        f"(of {counts['total']} initiatives in the matrix)."
    )
    for entry in coverage.gap_summary(df, stage):
        label = {"covered": "covers", "partial": "partially covers", "not_covered": "does not cover"}[
            entry["coverage_status"]
        ]
        st.markdown(
            f"- **{entry['initiative']}** {label} this stage"
            + (f" — omission: {entry['known_omission']}" if entry["known_omission"] != "n/a" else "")
        )

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
