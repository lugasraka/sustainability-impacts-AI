# Sustainability Impacts of AI

These notes cover the Climate Change AI Summer School 2026 lecture **Sustainability Impacts of AI** by Nikola Milojevic-Dupont. They summarize the local lecture PDF and connect its main ideas to the optional pre-readings.

The lecture argues that model energy use alone is not enough. Assess an AI system across its lifecycle, distinguish application types, include system-level effects, and state assumptions and uncertainty.

## Reading route

1. [Computing-related impacts](01-computing-related-impacts.md) - energy, hardware, materials, water, and frugal AI.
2. [Application impacts](02-application-impacts.md) - when AI may support mitigation and when it may accelerate emissions.
3. [System-level impacts](03-system-level-impacts.md) - rebound, lock-in, consumption, information, and power.
4. [Overarching considerations](04-overarching-considerations.md) - estimates, narratives, comparisons, and evidence quality.
5. [Regulating energy and resources](05-regulating-energy-and-resources.md) - incentives, transparency, data-center rules, and siting.
6. [Optional pre-readings](Pre-readings-lecture.md) - the original source list and a source-mapping exercise.

## Lecture map

| Slides | Section | Guiding question | Main reading connection |
| --- | --- | --- | --- |
| 3-11 | Framing and lifecycle | What kinds of climate and environmental impacts can AI have? | Kaack et al. 2022 |
| 12-43 | Computing-related impacts | What resources are used to build, run, cool, and dispose of AI hardware? | Ren and Luers 2025; Kaack et al. 2022 |
| 44-52 | Application impacts | Can an AI application reduce emissions, increase them, or do both through different pathways? | Kaack et al. 2022; Joshi 2026 |
| 53-60 | System-level impacts | What happens when an application changes behavior, demand, institutions, or power? | Kaack et al. 2022; Joshi 2026 |
| 61-66 | Overarching considerations | How should we interpret large estimates and claims about net benefit? | Joshi 2026; Kaack et al. 2022 |
| 67-76 | Regulation | What should be incentivized, measured, disclosed, and governed? | All three readings |
| 77-85 | Resources and review | Which questions should remain open after the lecture? | Pre-reading list |

## Four impact categories

Slide 3 groups the topic into four connected categories:

1. **Impacts from computation and hardware** - electricity, cooling, hardware manufacturing, mining, transport, and disposal.
2. **ML applications in climate-change mitigation** - applications intended to reduce emissions or improve adaptation and resilience.
3. **ML applications that increase emissions** - applications that expand or optimize emissions-intensive activity.
4. **ML's system-level impacts** - rebound effects, lock-in, changing consumption, information flows, and shifts in agency or power.

These categories can overlap. A climate application may have a useful operational effect while its deployment adds computing demand or causes a rebound effect.

## Key concepts

### Lifecycle assessment

Lifecycle assessment follows a product or service from raw-material extraction through manufacturing and use to end-of-life. For AI, the boundary should include more than the model: chips, servers, data centers, networks, electricity generation, cooling, and disposal can all matter.

### Scope 1, 2, and 3

The lecture uses the GHG Protocol framing:

- **Scope 1:** direct fuel emissions from an organization's operations.
- **Scope 2:** emissions associated with purchased electricity or heat.
- **Scope 3:** value-chain emissions, including suppliers, customers, and end-of-life.

The lecture also notes that similar accounting distinctions can be extended to water.

### Direct and indirect impacts

Direct impacts happen at the point of operation, such as electricity used by servers or water evaporated in cooling. Indirect impacts occur elsewhere in the value chain, such as emissions from electricity generation, mining, manufacturing, or the water used by power plants.

### Rebound and lock-in

An efficiency improvement can lower the cost of an activity and increase its use. That is a **rebound effect**. A system can also become dependent on a high-emission infrastructure or behavior, making future change harder. That is a **lock-in effect**.

### Water accounting

Keep **withdrawal**, **consumption**, and **discharge** separate. Withdrawal is water taken from a source; consumption is the portion not returned to that source, often because it evaporates; discharge is water returned, potentially with changed quality.

## Evidence hygiene

When reading a claim about AI and climate, ask:

- What is the system boundary: model, data center, organization, sector, or global economy?
- Is the number measured, modeled, extrapolated, or a best-case scenario?
- What is the baseline or counterfactual?
- Does the estimate include training, inference, hardware, and downstream use?
- Are adoption, rebound, and unintended effects included?
- Are the units, time horizon, location, and uncertainty stated?
- Does the source disclose its method and possible incentives?

A potential reduction is not necessarily a realized, additional, or net reduction.

## Working position

The lecture takes a demanding position:

- Use evidence-based lifecycle accounting.
- Prefer small, task-specific, and frugal systems when they are sufficient.
- Match climate applications to real decision needs rather than using climate as a justification for larger models.
- Treat water, energy, materials, land, and social effects as connected rather than isolated metrics.
- Regulate and disclose enough information for public oversight and meaningful comparison.
- Be cautious with future estimates and narratives that omit negative or system-level effects.

## Overview challenge: build an AI impact map

Create a one-page Markdown table or small web app for one AI use case. Add one row for each of the four impact categories and record:

- the claimed benefit or burden;
- the lifecycle stage;
- the baseline or counterfactual;
- one measurable indicator;
- one missing effect or uncertainty;
- the source for the claim.

**Success check:** another reader can identify the use case's main benefit, main burden, system boundary, and largest unknown without asking you for more context.

**Reflection:** Which category would be easiest to measure, and which could still dominate the outcome despite having the weakest data?

## Sources

- [Local lecture PDF](CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf), especially slides 3-11 and 76.
- [Kaack et al. 2022, Aligning artificial intelligence with climate change mitigation](https://www.nature.com/articles/s41558-022-01377-7).
- [Ketan Joshi 2026, The AI Climate Hoax](https://drive.google.com/file/d/12l1W4W25b-_ff6yFNJABkfal9_9oevxe/view).
- [Ren and Luers 2025, The Real Story on AI's Water Use](https://spectrum.ieee.org/ai-water-usage).

The Nature and Google Drive sources may require institutional access. Check details attributed only to those sources against the originals before using them as evidence.