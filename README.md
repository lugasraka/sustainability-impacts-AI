# Sustainability Impacts of AI

Study notes and interactive exercises for the Climate Change AI Summer School 2026 lecture **Sustainability Impacts of AI**.

The material traces AI's impacts from computation and hardware through applications, rebound effects, and regulation. The challenge apps use toy assumptions to make the reasoning visible; they are not lifecycle assessments.

## Start here

Read [00-overview.md](docs/00-overview.md) first. It gives the reading route, key concepts, an evidence checklist, and an exercise for mapping the impacts of one AI use case.

The five lecture topics are:

1. [Computing-related impacts](docs/01-computing-related-impacts.md): energy, hardware, materials, water, and frugal AI.
2. [Application impacts](docs/02-application-impacts.md): when AI may reduce emissions and when it may increase them.
3. [System-level impacts](docs/03-system-level-impacts.md): rebound, lock-in, consumption, information, and power.
4. [Overarching considerations](docs/04-overarching-considerations.md): estimates, narratives, comparisons, and evidence quality.
5. [Regulating energy and resources](docs/05-regulating-energy-and-resources.md): incentives, transparency, data-center rules, and siting.

Optional sources and the source-mapping exercise are in [Pre-readings-lecture.md](docs/Pre-readings-lecture.md).

## Project structure

```text
.
|-- README.md
|-- LICENSE
|-- .gitignore
|-- docs/
|   |-- 00-overview.md
|   |-- 01-computing-related-impacts.md
|   |-- 02-application-impacts.md
|   |-- 03-system-level-impacts.md
|   |-- 04-overarching-considerations.md
|   |-- 05-regulating-energy-and-resources.md
|   |-- Pre-readings-lecture.md
|   `-- CCAI Summer School 2026 _ Sustainability impacts of AI.pdf
`-- challenges/
	|-- 01-frugal-deployment/
	|-- 02-counterfactual-explorer/
	|-- 03-rebound-loop/
	|-- 04-evidence-audit/
	`-- 05-policy-coverage/
```

## Interactive challenges

Each challenge keeps its example inputs beside its entry point.

| Challenge | What it explores | Streamlit entry point |
| --- | --- | --- |
| [Frugal deployment](challenges/01-frugal-deployment/app.py) | Compare models for the same task by accuracy, energy, carbon, and water, then vary the grid, cooling, embodied hardware, training, and usage growth. | `python -m streamlit run challenges/01-frugal-deployment/app.py` |
| [Counterfactual explorer](challenges/02-counterfactual-explorer/app.py) | Vary adoption, efficiency, rebound, leakage, additionality, and AI emissions; inspect outcome ranges, sensitivity, and potential vs realized. | `python -m streamlit run challenges/02-counterfactual-explorer/app.py` |
| [Rebound-loop simulator](challenges/03-rebound-loop/app.py) | Test whether efficiency gains survive demand growth and infrastructure lock-in. | `python -m streamlit run challenges/03-rebound-loop/app.py` |
| [Evidence audit card](challenges/04-evidence-audit/app.py) | Audit one sustainability claim against nine fields and explicit confidence rules. | `python -m streamlit run challenges/04-evidence-audit/app.py` |
| [Policy coverage matrix](challenges/05-policy-coverage/app.py) | See which lifecycle stages and impact categories regimes measure, who can access the data, and where the biggest gaps are. | `python -m streamlit run challenges/05-policy-coverage/app.py` |

The counterfactual explorer has a browser-only version: [explorer.html](challenges/02-counterfactual-explorer/explorer.html). The evidence audit card also has a browser-only version: [evidence-card.html](challenges/04-evidence-audit/evidence-card.html). The rebound-loop simulator has a Gradio entry point:

```text
python challenges/03-rebound-loop/gradio_app.py
```

## Run the apps

From the repository root, create or activate a Python environment, then install the packages used by the examples:

```text
python -m pip install streamlit pandas numpy gradio
```

Run any entry point above. Streamlit prints a local URL in the terminal.

## Use the exercises critically

For each scenario, record:

- the system boundary;
- the baseline or counterfactual;
- the lifecycle stage involved;
- one measurable indicator;
- one missing effect or uncertainty; and
- the source for the claim.

Keep withdrawal, consumption, and discharge separate when discussing water. Treat a modeled potential reduction as different from a realized, additional, or net reduction.

## Reference material

The notes draw on the local [lecture PDF](docs/CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf) and the readings listed in [Pre-readings-lecture.md](docs/Pre-readings-lecture.md).