# Sustainability Impacts of AI

Study notes and interactive exercises for the Climate Change AI Summer School 2026 lecture **Sustainability Impacts of AI**.

The material follows AI impacts from computation and hardware through applications, rebound effects, and regulation. The challenge apps use toy assumptions to make the reasoning visible; they are not lifecycle assessments.

## Start here

Read [00-overview.md](00-overview.md) first. It gives the reading route, key concepts, an evidence checklist, and an exercise for mapping the impacts of one AI use case.

The lecture notes are split into five topics:

1. [Computing-related impacts](01-computing-related-impacts.md): energy, hardware, materials, water, and frugal AI.
2. [Application impacts](02-application-impacts.md): when AI may reduce emissions and when it may increase them.
3. [System-level impacts](03-system-level-impacts.md): rebound, lock-in, consumption, information, and power.
4. [Overarching considerations](04-overarching-considerations.md): estimates, narratives, comparisons, and evidence quality.
5. [Regulating energy and resources](05-regulating-energy-and-resources.md): incentives, transparency, data-center rules, and siting.

Optional sources and the source-mapping exercise are in [Pre-readings-lecture.md](Pre-readings-lecture.md).

## Interactive challenges

Each challenge is self-contained. The CSV files provide the example inputs.

| Challenge | What it explores | Streamlit entry point |
| --- | --- | --- |
| [Frugal deployment](challenges/01-frugal-deployment/app.py) | Compare models for the same task by accuracy, energy, carbon, and water use. | `python -m streamlit run challenges/01-frugal-deployment/app.py` |
| [Counterfactual explorer](challenges/02-counterfactual-explorer/app.py) | Vary adoption, efficiency, rebound, and AI emissions, then inspect outcome ranges and sensitivity. | `python -m streamlit run challenges/02-counterfactual-explorer/app.py` |
| [Rebound-loop simulator](challenges/03-rebound-loop/app.py) | Test whether efficiency gains survive demand growth and infrastructure lock-in. | `python -m streamlit run challenges/03-rebound-loop/app.py` |

The counterfactual explorer also has a browser-only version: [explorer.html](challenges/02-counterfactual-explorer/explorer.html). The rebound-loop simulator has a Gradio entry point:

```text
python challenges/03-rebound-loop/gradio_app.py
```

## Run the apps

From the repository root, use a Python environment and install the packages used by the examples:

```text
python -m pip install streamlit pandas numpy gradio
```

Then run one of the entry points above. Streamlit prints a local URL in the terminal.

## Use the exercises critically

For any scenario, record:

- the system boundary;
- the baseline or counterfactual;
- the lifecycle stage involved;
- one measurable indicator;
- one missing effect or uncertainty; and
- the source for the claim.

Keep withdrawal, consumption, and discharge separate when discussing water. Treat a modeled potential reduction as different from a realized, additional, or net reduction.

## Reference material

The notes draw on the local [lecture PDF](CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf) and the readings listed in [Pre-readings-lecture.md](Pre-readings-lecture.md).