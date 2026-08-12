# 02 Application Impacts

**Lecture slides:** 44-52

## What this section is about

AI affects climate both through the resources needed to compute it and through what applications enable. An application might improve forecasting, optimize a process, or support detection. Another application might increase extraction, production, consumption, or the speed of an emissions-intensive activity. The same technology label does not determine the outcome.

## Potential climate benefits need a counterfactual

The lecture presents AI-for-climate as one of four impact categories and refers to estimates that AI applications could reduce global greenhouse-gas emissions by 4% in 2030, equivalent to 2.4 Gt CO2e. It immediately qualifies these figures as unreliable when they rely on undisclosed models, extrapolated interviews, or best-case adoption assumptions.

Assess the claim by asking:

> Compared with what alternative, under which adoption conditions, with what additional resource use, and with what unintended effects?

For a climate application, define:

- the decision it changes;
- the baseline practice without AI;
- the mechanism that produces a reduction;
- the people and infrastructure that must adopt it;
- the time period and geographic scope;
- the computing and hardware burden;
- rebound, leakage, and failure modes.

Examples named or implied in the lecture include solar forecasting, wildfire-risk classification, illegal-deforestation detection, and climate-disinformation detection. Their climate value depends on whether the result changes a real decision in a useful direction.

## Applications can increase emissions

The slides explicitly call out AI used to accelerate emissions-intensive industries, using oil drilling as an example. Better exploration, optimization, logistics, or extraction can increase the availability or profitability of fossil fuels. In that case, an application can be technically efficient while worsening the wider climate outcome.

This is why an application-level metric such as "accuracy" or "operational efficiency" is insufficient. Measure the activity that the model changes and the resulting physical output, not only the model's performance.

## Most AI serves other applications

The lecture notes that most AI use across society serves non-climate applications and characterizes much current AI-for-climate work as traditional AI rather than large generative models. That distinction has two consequences:

1. Climate-relevant progress does not necessarily require the largest models or the fastest growth in data-center demand.
2. Claims about AI-for-climate should not be used as a blanket justification for every form of large-model expansion.

Start with the climate decision and its evidence needs, then select the simplest adequate method.

## Questions to revisit

- Is the claimed benefit additional, or would the activity have happened anyway?
- Does increased efficiency lower total resource use, or does it increase demand?
- Does the application reduce emissions or merely move them to another part of the value chain?
- Who gets the benefit, who carries the cost, and who has agency over deployment?

## Challenge: build a climate-application counterfactual explorer

Create a small spreadsheet, notebook, or web app for one hypothetical application. Give it inputs for:

- baseline activity and emissions;
- percentage efficiency improvement;
- adoption rate;
- additional AI-related emissions;
- rebound or demand-growth rate;
- an uncertainty range for each assumption.

Show a range of net outcomes rather than one headline number. Include two scenarios: a mitigation application such as solar forecasting and an emissions-increasing application such as fossil-fuel extraction optimization. Use toy values if necessary, but label them clearly as assumptions.

**Success check:** changing adoption or rebound assumptions can change the sign of the net result, and the interface identifies which assumption drives the result most strongly.

**Reflection:** What evidence would distinguish a genuine emissions reduction from a claim based mainly on potential adoption?

## Sources

- [Local lecture PDF](CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf), slides 44-52.
- [Kaack et al. 2022, Aligning artificial intelligence with climate change mitigation](https://www.nature.com/articles/s41558-022-01377-7).
- [Ketan Joshi 2026, The AI Climate Hoax](https://drive.google.com/file/d/12l1W4W25b-_ff6yFNJABkfal9_9oevxe/view).

The 4% and 2.4 Gt CO2e figures are presented in the lecture as examples of unreliable potential estimates. Do not reuse them without checking the original method and scope.