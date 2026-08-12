FIELDS = [
    ("claim", "Claim"),
    ("metric", "Metric"),
    ("boundary", "Boundary"),
    ("baseline", "Baseline"),
    ("mechanism", "Mechanism"),
    ("adoption", "Adoption"),
    ("negative_pathways", "Negative pathways"),
    ("uncertainty", "Uncertainty"),
    ("incentives", "Incentives"),
]

EVIDENCE_KINDS = ["measured", "modeled", "potential"]

EXAMPLE = {
    "claim": "AI could reduce global greenhouse-gas emissions by 4% in 2030 (2.4 Gt CO2e).",
    "metric": "Global GHG emissions; % reduction and Gt CO2e in 2030.",
    "boundary": "Unclear; appears global, across unspecified sectors and lifecycle stages.",
    "baseline": "Not specified; unclear which emissions trajectory the 4% is compared with.",
    "mechanism": "AI applications improve forecasting, optimization, and detection, which reduces emissions.",
    "adoption": "Assumes broad best-case adoption, but no adoption pathway or actors are specified.",
    "negative_pathways": "",
    "uncertainty": "Undisclosed model assumptions and extrapolated interviews; no uncertainty range.",
    "incentives": "Produced in a context where AI providers benefit from a positive framing.",
}

EXAMPLE_FLAGS = {
    "evidence": "potential",
    "baseline_clear": False,
    "method_disclosed": False,
    "boundary_relevant": False,
    "validated": False,
    "adoption_specified": False,
    "categories_complete": False,
}

FIELD_LABELS = dict(FIELDS)

CRITERIA = [
    ("evidence", "Evidence kind (measured / modeled / potential)"),
    ("baseline_clear", "Baseline or counterfactual is clear"),
    ("method_disclosed", "Method and units are disclosed"),
    ("boundary_relevant", "Boundary covers the relevant lifecycle stages and impacts"),
    ("validated", "Estimate has some empirical validation"),
    ("adoption_specified", "Adoption conditions and actors are specified"),
    ("categories_complete", "Positive, negative, and system-level pathways are included"),
]

LABEL_NOTES = {
    "High": "Measured outcome, clear baseline, disclosed method, and relevant boundary.",
    "Medium": "Modeled estimate with disclosed assumptions but limited validation.",
    "Low": "Potential estimate with unclear baseline, adoption, method, or omitted impact categories.",
}

DISCLAIMER = (
    "The label is a heuristic derived from explicit rules, not a scientific certainty. "
    "Read the reasons below before relying on it, and treat any empty field as missing evidence."
)


def classify(evidence, baseline_clear, method_disclosed, boundary_relevant,
             validated, adoption_specified, categories_complete):
    low_conditions = [
        (evidence == "potential", "the evidence is a potential estimate, not a measured or validated outcome"),
        (not baseline_clear, "the baseline or counterfactual is unclear"),
        (not method_disclosed, "the method and units are not disclosed"),
        (not adoption_specified, "adoption conditions and actors are not specified"),
        (not categories_complete, "impact categories are omitted"),
    ]
    low_reasons = [message for fired, message in low_conditions if fired]
    if low_reasons:
        return "Low", low_reasons

    high_conditions = [
        (evidence == "measured", "the outcome is measured rather than modeled"),
        (baseline_clear, "the baseline or counterfactual is clear"),
        (method_disclosed, "the method and units are disclosed"),
        (boundary_relevant, "the boundary covers the relevant lifecycle stages and impacts"),
        (categories_complete, "positive, negative, and system-level pathways are included"),
    ]
    high_reasons = [message for fired, message in high_conditions if fired]
    if all(fired for fired, _ in high_conditions):
        return "High", high_reasons

    medium_reasons = []
    if evidence == "measured":
        medium_reasons.append("the outcome is measured but one or more High prerequisites are missing")
    else:
        medium_reasons.append("the estimate is modeled with disclosed assumptions and limited validation")
    return "Medium", medium_reasons


def missing_evidence(fields, evidence, baseline_clear, method_disclosed,
                     boundary_relevant, validated, adoption_specified, categories_complete):
    gaps = []
    if evidence == "potential":
        gaps.append("a realized or measured outcome instead of a potential estimate")
    if not baseline_clear:
        gaps.append("a clear baseline or counterfactual")
    if not method_disclosed:
        gaps.append("a disclosed method with units")
    if not boundary_relevant:
        gaps.append("a boundary that covers the relevant lifecycle stages and impacts")
    if not validated:
        gaps.append("empirical validation of the estimate")
    if not adoption_specified:
        gaps.append("specified adoption conditions and the actors who must change behavior")
    if not categories_complete:
        gaps.append("at least one omitted impact category or system-level pathway")
    for key, label in FIELDS:
        if not fields.get(key, "").strip():
            gaps.append(f"the '{label}' field is empty or not addressed")
    return gaps


def rules_table():
    return [
        ("Evidence kind", "measured / modeled / potential", "measured for High; potential always Low"),
        ("Baseline clear", "yes / no", "required for High and Medium"),
        ("Method disclosed", "yes / no", "required for High and Medium"),
        ("Boundary relevant", "yes / no", "required for High"),
        ("Validated", "yes / no", "supporting for Medium"),
        ("Adoption specified", "yes / no", "required for High and Medium"),
        ("Categories complete", "yes / no", "required for High"),
    ]


def to_markdown(fields, evidence, baseline_clear, method_disclosed,
                boundary_relevant, validated, adoption_specified,
                categories_complete, reflection=""):
    label, reasons = classify(
        evidence, baseline_clear, method_disclosed, boundary_relevant,
        validated, adoption_specified, categories_complete,
    )
    gaps = missing_evidence(
        fields, evidence, baseline_clear, method_disclosed,
        boundary_relevant, validated, adoption_specified, categories_complete,
    )
    lines = ["# Evidence Audit Card", ""]
    lines.append(f"**Claim:** {fields.get('claim', '').strip() or '(not stated)'}")
    lines.append(f"**Confidence label:** **{label}** ({LABEL_NOTES[label]})")
    lines.append("")
    lines.append("## Field audit")
    for key, label_name in FIELDS:
        lines.append(f"- **{label_name}:** {fields.get(key, '').strip() or '(not stated)'}")
    lines.append("")
    lines.append("## Why this label")
    for reason in reasons:
        lines.append(f"- {reason}")
    lines.append("")
    lines.append("## Missing evidence")
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.append("")
    lines.append("## Reflection")
    lines.append(reflection.strip() or "(not stated)")
    return "\n".join(lines)
