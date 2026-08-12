# 05 Regulating Energy and Resources

**Lecture slides:** 67-76

## What this section is about

The lecture closes by asking how institutions can encourage useful AI-for-climate work while requiring enough transparency to evaluate resource use and public impacts. It also broadens data-center governance from an energy-efficiency problem to a question of land, water, infrastructure, and community planning.

## Support AI-for-climate applications

The lecture lists dedicated public research and development funding, large monitoring programs such as Copernicus and NASA Harvest, and strategies that identify climate change as an application area. These measures can build capacity for climate-relevant uses without assuming that every use needs a large general-purpose model.

Funding and procurement can reward systems that track performance alongside energy, water, and other resource requirements.

## Transparency initiatives

The lecture discusses:

- the EU AI Act (2024), including reporting related to compute resources and energy use for high-risk systems and large models;
- the proposed U.S. Artificial Intelligence Environmental Impacts Act (2024), described as covering environmental-impact assessment through EPA and NIST;
- the EU Energy Efficiency Directive 2023/1791 and Commission Delegated Regulation 2024/1364 for data centers;
- the German 2023 Energy Efficiency Act.

The legal details and implementation status can change, so treat the slides as a starting point for current legal research rather than legal advice.

## Why omissions matter

The lecture highlights several gaps in the EU AI Act framing presented in the slides:

- energy disclosure for general-purpose AI is described as focusing on model development and omitting inference;
- where energy information is required, access may be limited to authorities rather than downstream providers or the public;
- AI application emissions are not fully covered;
- water consumption is not addressed in the same way;
- environmental harm may be a relevant criterion without being made explicit for every system.

A disclosure regime improves accountability only when it covers the impact categories and lifecycle stages that determine the outcome, and when the data reaches the people making deployment decisions.

## Data-center reporting and siting

The lecture states that the EU data-center rules apply to facilities with a power demand of at least 500 kW and require annual reporting to an EU database. The listed information includes energy consumption, power utilization, temperature set points, waste-heat utilization, water use, and renewable-energy use.

The lecture calls for integrated oversight of data-center siting. Location choices interact with:

- energy and water availability;
- local zoning and land use;
- property values and ecosystem restoration;
- community infrastructure and service reliability;
- compensation and community-benefit frameworks;
- digital-economy, environmental, and territorial policy.

Siting decisions also distribute costs. A data center may satisfy a national energy target while imposing concentrated costs on a local community.

## Questions to revisit

- Who needs environmental data to make a meaningful decision?
- Which lifecycle stages should a disclosure rule cover?
- What information should be public, and what is only useful to regulators?
- Can a data-center permit account for seasonal water stress and grid peaks?
- What community benefits or compensation would make siting decisions legitimate?

## Challenge: build a policy coverage matrix

Create a small table or web app with rows for:

- training;
- inference;
- hardware production;
- electricity generation;
- cooling and water;
- application effects;
- system-level effects;
- siting and community impacts.

Use columns for regulation or initiative, responsible actor, required metric, reporting audience, geographic scope, and known omission. Populate it with the lecture's EU and U.S. examples and link each entry to a source or slide.

**Success check:** a reader can see at a glance which lifecycle stages are measured, who receives the information, and where a claimed transparency regime leaves a gap.

**Reflection:** Which missing disclosure would most improve a real deployment or siting decision, and why is it currently difficult to collect?

## Sources

- [Local lecture PDF](CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf), slides 67-76.
- [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) - verify the current text and implementation status.
- [EU Energy Efficiency Directive](https://eur-lex.europa.eu/eli/dir/2023/1791/oj) - verify current reporting requirements.
- [Kaack et al. 2022, Aligning artificial intelligence with climate change mitigation](https://www.nature.com/articles/s41558-022-01377-7).
- [Ketan Joshi 2026, The AI Climate Hoax](https://drive.google.com/file/d/12l1W4W25b-_ff6yFNJABkfal9_9oevxe/view).
- [Ren and Luers 2025, The Real Story on AI's Water Use](https://spectrum.ieee.org/ai-water-usage).