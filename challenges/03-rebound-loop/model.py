DEFAULT_DEMAND = 1_000_000
DEFAULT_EFFICIENCY = 20.0
DEFAULT_ADOPTION = 80.0
DEFAULT_REBOUND = 30.0
DEFAULT_LOCK_IN = 10
DEFAULT_INTENSITY = 1.0

SOCIAL_EFFECTS = [
    "Who can opt out of the service, appeal an automated decision, or benefit from it?",
    "Who controls the models, data, and compute, and who is represented in the data?",
    "Misinformation, polarization, and trust effects that shape climate action even when computing footprint is small.",
    "Long-lived infrastructure, habits, and business models beyond the modeled lock-in period.",
    "Which community carries the environmental or social cost of the demand growth?",
]


def intensity_after(intensity_kg, efficiency_pct, adoption_pct):
    return intensity_kg * (1 - efficiency_pct / 100.0 * adoption_pct / 100.0)


def demand_after(demand, rebound_pct):
    return demand * (1 + rebound_pct / 100.0)


def annual_impact_tco2e(demand, intensity_kg):
    return demand * intensity_kg / 1000.0


def impact_with_ai(demand, intensity_kg, efficiency_pct, adoption_pct, rebound_pct):
    return annual_impact_tco2e(
        demand_after(demand, rebound_pct), intensity_after(intensity_kg, efficiency_pct, adoption_pct)
    )


def rebound_levels(rebound_pct):
    return {
        "low": 0.0,
        "medium": rebound_pct,
        "high": min(2.0 * rebound_pct, 100.0),
    }


def is_rebound_scenario(demand, intensity_kg, efficiency_pct, adoption_pct, rebound_pct):
    baseline = annual_impact_tco2e(demand, intensity_kg)
    return impact_with_ai(demand, intensity_kg, efficiency_pct, adoption_pct, rebound_pct) > baseline


def cumulative_tco2e(annual_impact, lock_in_years):
    return annual_impact * lock_in_years


def verdict_text(demand, intensity_kg, efficiency_pct, adoption_pct, rebound_pct):
    baseline = annual_impact_tco2e(demand, intensity_kg)
    after = impact_with_ai(demand, intensity_kg, efficiency_pct, adoption_pct, rebound_pct)
    per_unit = intensity_after(intensity_kg, efficiency_pct, adoption_pct)
    per_unit_pct = (1 - per_unit / intensity_kg) * 100 if intensity_kg else 0.0
    total_pct = (after / baseline - 1) * 100 if baseline else 0.0
    if after > baseline:
        return (
            f"REBOUND SCENARIO: per-unit resource use fell {per_unit_pct:.1f}%, but total annual "
            f"impact rose {total_pct:+.1f}% ({(after - baseline):,.0f} tCO2e/yr more). "
            "This is a rebound effect, not an efficiency success."
        )
    return (
        f"EFFICIENCY SCENARIO: per-unit resource use fell {per_unit_pct:.1f}% and total annual "
        f"impact fell {abs(total_pct):.1f}%. The rebound loop did not overtake the efficiency gain."
    )


def causal_diagram_html():
    box = ("display:inline-block;background:#1a2230;color:#fff;padding:10px 14px;"
           "border-radius:6px;font-size:0.85rem;vertical-align:middle;margin:4px 2px;")
    arrow = "display:inline-block;color:#1a2230;font-size:1.2rem;padding:0 4px;vertical-align:middle;"
    arrow_down = "&#8595;"
    arrow_up = "&#8593;"
    arrow_right = "&#8594;"
    return (
        "<div style='text-align:center;line-height:2.4;'>"
        f"<span style='{box}'>AI capability</span><span style='{arrow}'>{arrow_right}</span>"
        f"<span style='{box}'>per-unit efficiency {arrow_down}</span><span style='{arrow}'>{arrow_right}</span>"
        f"<span style='{box}'>service cost {arrow_down}</span><span style='{arrow}'>{arrow_right}</span>"
        f"<span style='{box}'>demand {arrow_up}</span><span style='{arrow}'>{arrow_right}</span>"
        f"<span style='{box}'>lock-in of infrastructure</span><span style='{arrow}'>{arrow_right}</span>"
        f"<span style='{box}'>total annual impact ?</span>"
        "<div style='color:#8a4b12;font-size:0.8rem;margin-top:6px;'>"
        "&#8635; rebound loop: demand growth feeds back through the system and can overtake the efficiency gain"
        "</div></div>"
    )
