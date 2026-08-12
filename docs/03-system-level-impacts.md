# 03 System-Level Impacts

**Lecture slides:** 53-60

## What this section is about

An AI application can change the larger system around it. People adapt, demand shifts, infrastructure locks in, and control or access moves between groups, so the system outcome can diverge from the application's direct technical effect.

## Four system-level pathways

### Rebound and lock-in

If AI makes a service cheaper, faster, or more convenient, people may use more of it. The lecture uses autonomous vehicles and ridesharing as examples to prompt questions about additional travel, congestion, vehicle ownership, and infrastructure. An efficiency gain does not guarantee lower total emissions.

Lock-in can happen when an application encourages long-lived infrastructure, business models, or habits that make lower-carbon alternatives harder to adopt later.

### Increased societal consumption

The lecture points to personalized advertising and on-demand delivery. AI can improve targeting and convenience while also encouraging more purchases, shorter delivery times, packaging, traffic, and material throughput. The relevant unit is not only energy per recommendation; it is the resulting consumption system.

### Misinformation and polarization

Personalization and amplification can influence what information people see and how groups understand climate risks or policy choices. This can slow collective action even when the immediate computing footprint is small. A climate claim that spreads widely can have a system effect through trust, attention, and political capacity.

### Societal power shifts

Access to models, data, compute, and decision systems can shift agency and bargaining power. The lecture asks who can use AI, who controls the infrastructure, who is represented in the data, and who can contest an automated decision. These are sustainability questions because equitable access and institutional power affect whose environmental costs are accepted.

## Include system effects in the assessment

System-level effects are difficult to quantify, but excluding them can bias an assessment toward the application owner's preferred story. A complete assessment should at least name plausible pathways and state which ones are outside the calculation.

Use a causal chain:

`AI capability -> changed decision or price -> changed behavior -> changed demand or power -> environmental and social outcome`

Then ask where a feedback loop enters. For example, an efficiency gain can lower cost, increase use, raise total demand, and create pressure for more infrastructure.

## Questions to revisit

- What behavior changes once the service becomes cheaper or more convenient?
- Does the application displace an existing activity or add a new one?
- Which infrastructure and institutions become harder to change?
- Who can opt out, appeal, or benefit from the system?
- What evidence would show that a rebound effect is occurring?

## Challenge: build a rebound-loop simulator

Create a small interactive model for a service that becomes 20% more resource-efficient after AI deployment. Let the user vary:

- baseline demand;
- efficiency improvement;
- adoption rate;
- rebound demand increase;
- infrastructure lock-in period;
- emissions or resource intensity per unit of activity.

Render the result as a simple causal diagram plus a chart of total annual impact under low, medium, and high rebound assumptions. Add a text box listing the social or governance effects that the numeric model does not capture.

**Success check:** the tool can show a case where per-unit efficiency improves while total impact increases, and it labels that result as a rebound scenario rather than an efficiency success.

**Reflection:** Which system-level effect is most likely to be ignored in your chosen use case, and what stakeholder could provide evidence about it?

## Sources

- [Local lecture PDF](CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf), slides 53-60.
- [Kaack et al. 2022, Aligning artificial intelligence with climate change mitigation](https://www.nature.com/articles/s41558-022-01377-7).
- [Ketan Joshi 2026, The AI Climate Hoax](https://drive.google.com/file/d/12l1W4W25b-_ff6yFNJABkfal9_9oevxe/view).