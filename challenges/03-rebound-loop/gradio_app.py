import gradio as gr
import pandas as pd

import model

LEVEL_KEYS = ["baseline", "low", "medium", "high"]


def compute(demand, efficiency, adoption, rebound, lock_in, intensity):
    baseline = model.annual_impact_tco2e(demand, intensity)
    levels = model.rebound_levels(rebound)
    impacts = {
        "baseline": baseline,
        "low": model.impact_with_ai(demand, intensity, efficiency, adoption, levels["low"]),
        "medium": model.impact_with_ai(demand, intensity, efficiency, adoption, levels["medium"]),
        "high": model.impact_with_ai(demand, intensity, efficiency, adoption, levels["high"]),
    }
    chart_df = pd.DataFrame(
        {
            "scenario": [
                "baseline (no AI)",
                f"low rebound (0%)",
                f"medium rebound ({levels['medium']:.0f}%)",
                f"high rebound ({levels['high']:.0f}%)",
            ],
            "annual_tco2e": [impacts[k] for k in LEVEL_KEYS],
        }
    )
    cum_df = pd.DataFrame(
        {
            "scenario": ["baseline", "low", "medium", "high"],
            "annual_tco2e": [f"{impacts[k]:,.0f}" for k in LEVEL_KEYS],
            "cumulative_tco2e": [f"{impacts[k] * lock_in:,.0f}" for k in LEVEL_KEYS],
        }
    )
    verdict = model.verdict_text(demand, intensity, efficiency, adoption, rebound)
    per_unit = model.intensity_after(intensity, efficiency, adoption)
    caption = (
        f"Assumes each rebound level persists for the whole {lock_in:.0f} year lock-in period; "
        f"per-unit intensity after AI: {per_unit:.3f} kg CO2e/unit "
        f"({(1 - per_unit / intensity) * 100:.1f}% lower than baseline). All values are toy assumptions."
    )
    return chart_df, cum_df, verdict, caption


def build():
    with gr.Blocks(title="Rebound-Loop Simulator") as demo:
        gr.Markdown(
            "## Rebound-loop simulator\n"
            "Challenge from lecture 03: an AI service gets more resource-efficient, but the "
            "rebound loop can make total impact rise anyway. Watch the label switch between "
            "'efficiency scenario' and 'rebound scenario'."
        )
        with gr.Row():
            with gr.Column(scale=1):
                demand = gr.Slider(0, 10_000_000, value=model.DEFAULT_DEMAND, step=50_000,
                                   label="Baseline demand (units of activity per year)")
                efficiency = gr.Slider(0, 50, value=model.DEFAULT_EFFICIENCY, step=1,
                                       label="Efficiency improvement after AI (%)")
                adoption = gr.Slider(0, 100, value=model.DEFAULT_ADOPTION, step=1,
                                     label="Adoption rate (%)")
                rebound = gr.Slider(0, 100, value=model.DEFAULT_REBOUND, step=1,
                                    label="Rebound demand increase (%)")
                lock_in = gr.Slider(1, 30, value=model.DEFAULT_LOCK_IN, step=1,
                                    label="Infrastructure lock-in period (years)")
                intensity = gr.Slider(0, 10, value=model.DEFAULT_INTENSITY, step=0.1,
                                      label="Resource intensity (kg CO2e per unit of activity)")
            with gr.Column(scale=2):
                gr.Markdown("### Causal diagram")
                diagram = gr.HTML(model.causal_diagram_html())
                gr.Markdown("### Total annual impact under low, medium, and high rebound")
                chart = gr.BarPlot(
                    x="scenario",
                    y="annual_tco2e",
                    title=None,
                    color="#1f6feb",
                    height=320,
                )
                verdict = gr.Markdown()
                gr.Markdown("### Cumulative impact over the lock-in period")
                table = gr.Dataframe(headers=["scenario", "annual_tco2e", "cumulative_tco2e"],
                                     datatype=["str", "str", "str"], interactive=False)
                caption = gr.Markdown()
                gr.Markdown("### Social and governance effects the numeric model does not capture")
                for effect in model.SOCIAL_EFFECTS:
                    gr.Markdown(f"- {effect}")
                gr.Markdown(
                    "> Reflection: which system-level effect is most likely to be ignored in "
                    "your use case, and which stakeholder could provide evidence about it?"
                )

        inputs = [demand, efficiency, adoption, rebound, lock_in, intensity]
        outputs = [chart, table, verdict, caption]
        for control in inputs:
            control.change(fn=compute, inputs=inputs, outputs=outputs)
        demo.load(fn=compute, inputs=inputs, outputs=outputs)
    return demo


if __name__ == "__main__":
    build().launch()
