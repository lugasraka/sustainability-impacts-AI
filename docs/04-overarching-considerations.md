# 04 Overarching Considerations

**Lecture slides:** 61-66

## What this section is about

This section examines the quality of the stories and estimates used to describe individual impacts. It challenges optimistic narratives about AI-for-climate and simplistic comparisons between AI's costs and its possible benefits.

## The GenAI fallacy

The lecture describes a "GenAI fallacy": using AI-for-climate as a justification for the energy consumption of large models. Climate applications are presented as a welcome narrative for large-model expansion, even though many climate-relevant applications do not require large generative models.

Choose a model for the task, then demonstrate its climate value:

- large models may be useful for some tasks;
- many climate tasks can use smaller, specialized, or conventional models;
- the climate value of an application must be demonstrated rather than assumed;
- the computing burden of the chosen model remains part of the application assessment.

## Chronic potential-itis

The lecture uses "chronic potential-itis" for a recurring focus on what AI could achieve under favorable conditions. Barriers to deployment can include data quality, institutional capacity, regulation, cost, interoperability, skills, safety, trust, and the absence of a decision-maker who can act on the output.

Best-case adoption scenarios can look precise while hiding the assumptions that make them possible. A chart or summary can therefore communicate more confidence than the evidence deserves.

## Holistic estimates require comparable boundaries

The lecture compares several 2023-2025 estimates and shows that they cover different parts of the problem. Some include data-center growth, some include selected application reductions, some include a rebound effect, and many do not assess application-related increases or system-level effects.

This makes a single net number difficult to interpret. Before comparing two estimates, align:

- lifecycle stages;
- direct and indirect impacts;
- positive and negative application pathways;
- system-level effects;
- geography and time horizon;
- baseline and adoption assumptions;
- units and treatment of uncertainty.

## Compare a specific intervention with its alternative

The lecture rejects a comparison between a known or estimated energy cost and a broad, potential benefit when the counterfactual is missing. Assess whether a particular intervention produces an additional net benefit compared with the best non-AI alternative, after computing and system effects are included.

AI-for-climate may be useful, but each case needs evidence that connects model output to a real-world outcome.

## Greening the grid is not sufficient

Renewable electricity can reduce the carbon intensity of computation, but it does not solve unbounded demand growth or other resource and social impacts. The narrow path to net zero requires rapid deployment of clean energy and major improvements in energy efficiency at the same time.

For AI, this means efficiency, demand management, and appropriate use matter alongside cleaner supply.

## A claim-audit checklist

For every large sustainability claim, record:

1. Claim: what exactly is being promised?
2. Metric: what is measured, and in which units?
3. Boundary: what is included and excluded?
4. Baseline: compared with what?
5. Mechanism: how does the claimed benefit happen?
6. Adoption: who must change behavior or infrastructure?
7. Negative pathways: what could increase emissions or resource use?
8. Uncertainty: which assumptions dominate the result?
9. Incentives: who produced the estimate and who benefits from its framing?

## Challenge: create an evidence audit card

Build a Markdown form, CSV workflow, or tiny web app that takes one sustainability claim and produces an evidence card using the nine fields above. Add a confidence label based on explicit rules, such as:

- **High:** measured outcome, clear baseline, disclosed method, and relevant boundary.
- **Medium:** modeled estimate with disclosed assumptions but limited validation.
- **Low:** potential estimate with unclear baseline, adoption, method, or omitted impact categories.

Do not let the tool pretend that the label is scientific certainty; show the reasons for the label and a list of missing evidence.

**Success check:** two readers can see why the same claim received its label and can identify at least one omitted category or assumption.

**Reflection:** Which missing piece of evidence would most change your judgment about the claim?

## Sources

- [Local lecture PDF](CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf), slides 61-66.
- [Kaack et al. 2022, Aligning artificial intelligence with climate change mitigation](https://www.nature.com/articles/s41558-022-01377-7).
- [Ketan Joshi 2026, The AI Climate Hoax](https://drive.google.com/file/d/12l1W4W25b-_ff6yFNJABkfal9_9oevxe/view).

The lecture's comparison table names Stern et al. 2025, IEA 2025, PwC 2025, Schneider Electric 2024, and de Vries 2023. Use the original publications to verify what each estimate includes before comparing them.