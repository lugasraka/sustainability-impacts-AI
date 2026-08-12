import streamlit as st

import card


def run_ui():
    st.set_page_config(page_title="Evidence Audit Card", layout="wide")
    st.title("Evidence audit card")
    st.caption(
        "Challenge from lecture 04: take one sustainability claim through nine audit "
        "fields and let explicit rules assign a confidence label — then read why."
    )

    with st.sidebar:
        st.header("Structured criteria")
        evidence = st.radio(
            "Evidence kind",
            card.EVIDENCE_KINDS,
            index=card.EVIDENCE_KINDS.index(card.EXAMPLE_FLAGS["evidence"]),
            key="f_evidence",
        )
        baseline_clear = st.checkbox(
            "Baseline or counterfactual is clear", value=card.EXAMPLE_FLAGS["baseline_clear"], key="f_baseline"
        )
        method_disclosed = st.checkbox(
            "Method and units are disclosed", value=card.EXAMPLE_FLAGS["method_disclosed"], key="f_method"
        )
        boundary_relevant = st.checkbox(
            "Boundary covers relevant lifecycle stages and impacts",
            value=card.EXAMPLE_FLAGS["boundary_relevant"], key="f_boundary",
        )
        validated = st.checkbox(
            "Estimate has some empirical validation", value=card.EXAMPLE_FLAGS["validated"], key="f_validated"
        )
        adoption_specified = st.checkbox(
            "Adoption conditions and actors are specified",
            value=card.EXAMPLE_FLAGS["adoption_specified"], key="f_adoption",
        )
        categories_complete = st.checkbox(
            "Positive, negative, and system-level pathways are included",
            value=card.EXAMPLE_FLAGS["categories_complete"], key="f_categories",
        )

    flags = {
        "evidence": evidence,
        "baseline_clear": baseline_clear,
        "method_disclosed": method_disclosed,
        "boundary_relevant": boundary_relevant,
        "validated": validated,
        "adoption_specified": adoption_specified,
        "categories_complete": categories_complete,
    }

    st.subheader("Rules")
    st.table(card.rules_table())
    st.caption(card.DISCLAIMER)

    st.subheader("Field audit")
    cols = st.columns(3)
    for i, (key, label_name) in enumerate(card.FIELDS):
        with cols[i % 3]:
            st.text_area(label_name, value=card.EXAMPLE.get(key, ""), key=f"field_{key}", height=90)

    fields = {key: st.session_state[f"field_{key}"] for key, _ in card.FIELDS}

    label, reasons = card.classify(**flags)
    gaps = card.missing_evidence(fields, **flags)

    st.subheader("Evidence card")
    if label == "High":
        st.success(f"Confidence label: **{label}**")
    elif label == "Medium":
        st.warning(f"Confidence label: **{label}**")
    else:
        st.error(f"Confidence label: **{label}**")
    st.markdown(f"*{card.LABEL_NOTES[label]}*")

    col_reasons, col_gaps = st.columns(2)
    with col_reasons:
        st.markdown("**Why this label**")
        for reason in reasons:
            st.write(f"- {reason}")
    with col_gaps:
        st.markdown("**Missing evidence**")
        if gaps:
            for gap in gaps:
                st.write(f"- {gap}")
        else:
            st.write("- none identified")

    st.subheader("Reflection")
    reflection = st.text_area(
        "Which missing piece of evidence would most change your judgment about this claim?",
        key="f_reflection", height=70,
    )
    markdown = card.to_markdown(fields, **flags, reflection=reflection)
    st.download_button(
        "Download card as Markdown", markdown, file_name="evidence-audit-card.md", mime="text/markdown"
    )

    with st.expander("Preview Markdown card"):
        st.code(markdown, language="markdown")


if __name__ == "__main__":
    run_ui()
