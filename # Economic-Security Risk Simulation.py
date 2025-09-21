# Economic-Security Risk Simulation: Activist → (Indirect) Tech Leakage → Competitiveness → Rating Downgrade
#
# What this script does
# - Simulates a Monte Carlo model of a firm where a leakage event (via indirect channels like accounting-footprint inference) 
#   can degrade revenue growth and margins.
# - Tracks EBITDA, interest coverage, and leverage. Triggers a "downgrade" if coverage falls below a threshold OR leverage rises above a threshold.
# - Provides scenario toggles (industry capital intensity, mitigation strength, severity, detection lag, etc.).
# - Outputs: headline metrics + plots + a CSV of the run distribution for your documentation.
#
# Notes
# - This is a stylized policy/strategy model, not a valuation. Calibrate to firm/sector data if available.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass

# ----------------------------
# PARAMETERS (edit here)
# ----------------------------
np.random.seed(42)

N_SIM = 3000           # number of Monte Carlo paths
T_YEARS = 5            # horizon in years (discrete annual steps for readability)

# Baseline business
REVENUE_0 = 1000.0     # initial revenue (arbitrary units)
BASE_GROWTH = 0.05     # baseline annual revenue growth
GROWTH_VOL = 0.06      # volatility of revenue growth (one-sigma shock)
EBITDA_MARGIN_0 = 0.18 # starting EBITDA margin
MARGIN_VOL = 0.02      # annual random drift on margin (small)

# Capital structure
DEBT_0 = 600.0         # total debt (constant for simplicity)
INT_RATE = 0.05        # average interest rate
INTEREST = DEBT_0 * INT_RATE

# Industry capital intensity: fixed-cost burden proxy (amplifies operating deleverage)
FIXED_COST_INTENSITY = 0.6  # 0.3=low capital intensity, 0.6=semi/battery-like, 0.8=very high

# Leakage mechanism
P_LEAK = 0.15          # probability that leakage event occurs at t=1 (one-off hazard at start)
SEVERITY = 0.20        # fractional impact when "active": reduces growth and margin (20% severity)
DETECTION_LAG = 2      # years before mitigation kicks in (e.g., internal controls, legal response)
MITIGATION = 0.5       # fraction of severity removed after detection (0=no mitigation, 1=full mitigation)

# Rating trigger rules
COVERAGE_THRESHOLD = 2.5              # Downgrade if EBITDA/Interest < 2.5
LEVERAGE_THRESHOLD = 4.0              # OR if Debt/EBITDA > 4.0
CONSECUTIVE_YEARS_BELOW = 2           # must breach for this many consecutive years to count as downgrade
DOWNGRADE_WINDOW = 3                  # compute probability of downgrade within first 3 years (headline metric)

# Sensitivity grid (optional sweep on severity)
SEVERITY_SWEEP = np.linspace(0.05, 0.35, 7)  # 5% → 35%

# ----------------------------
# MODEL FUNCTIONS
# ----------------------------
@dataclass
class PathResult:
    downgraded: bool
    downgrade_year: int
    coverage_path: list
    leverage_path: list
    revenue_path: list
    ebitda_path: list
    leak_active_years: list

def simulate_one(severity=SEVERITY):
    revenue = REVENUE_0
    ebitda_margin = EBITDA_MARGIN_0

    # draw if leakage event happens at t=1 (stylized)
    leak_occurs = (np.random.rand() < P_LEAK)
    leak_active_years = [False]*T_YEARS
    # if occurs, it's active from year 1 and reduced after detection lag
    # severity_effect(t) = severity (full) before mitigation, severity*(1-MITIGATION) after lag
    downgraded = False
    downgrade_year = None

    coverage_breach_streak = 0
    leverage_breach_streak = 0

    coverage_path = []
    leverage_path = []
    revenue_path = []
    ebitda_path = []

    for t in range(T_YEARS):
        # stochastic growth and margin drift
        g_shock = np.random.normal(0, GROWTH_VOL)
        m_shock = np.random.normal(0, MARGIN_VOL)

        # leakage impact
        eff_sev = 0.0
        if leak_occurs:
            leak_active_years[t] = True
            if t < DETECTION_LAG:
                eff_sev = severity
            else:
                eff_sev = max(0.0, severity * (1.0 - MITIGATION))

        # effect on growth and margin
        # growth reduced and margin compressed, amplified by fixed-cost intensity (operating leverage)
        effective_growth = BASE_GROWTH + g_shock - eff_sev * 0.6   # 60% of severity hits growth
        ebitda_margin = max(0.01, ebitda_margin + m_shock - eff_sev * 0.4 * (1 + FIXED_COST_INTENSITY))

        # update revenue and EBITDA
        revenue = max(1.0, revenue * (1.0 + effective_growth))
        ebitda = revenue * ebitda_margin

        # coverage & leverage
        coverage = ebitda / max(1e-6, INTEREST)
        leverage = DEBT_0 / max(1e-6, ebitda)

        coverage_path.append(coverage)
        leverage_path.append(leverage)
        revenue_path.append(revenue)
        ebitda_path.append(ebitda)

        coverage_breach = coverage < COVERAGE_THRESHOLD
        leverage_breach = leverage > LEVERAGE_THRESHOLD

        coverage_breach_streak = coverage_breach_streak + 1 if coverage_breach else 0
        leverage_breach_streak = leverage_breach_streak + 1 if leverage_breach else 0

        # downgrade if any streak meets rule
        if (coverage_breach_streak >= CONSECUTIVE_YEARS_BELOW) or (leverage_breach_streak >= CONSECUTIVE_YEARS_BELOW):
            downgraded = True
            downgrade_year = t + 1  # 1-based year
            # continue to record the path for completeness

    return PathResult(downgraded, downgrade_year, coverage_path, leverage_path, revenue_path, ebitda_path, leak_active_years)

def run_simulation(severity=SEVERITY, n_sim=N_SIM):
    results = [simulate_one(severity=severity) for _ in range(n_sim)]
    # metrics
    downgraded_any = np.array([r.downgraded for r in results])
    downgrade_years = np.array([r.downgrade_year if r.downgraded else np.nan for r in results])

    prob_within_window = np.mean([
        (r.downgraded and (r.downgrade_year is not None) and (r.downgrade_year <= DOWNGRADE_WINDOW))
        for r in results
    ])

    avg_time_to_dg = np.nanmean(downgrade_years)  # conditional on downgrade
    leak_share = np.mean([any(r.leak_active_years) for r in results])

    summary = {
        "severity": severity,
        "prob_downgraded_any": float(np.mean(downgraded_any)),
        "prob_downgraded_within_window": float(prob_within_window),
        "avg_time_to_downgrade_if_dg": float(avg_time_to_dg),
        "share_paths_with_leak": float(leak_share),
    }
    return results, summary

# ----------------------------
# RUN BASE CASE + SWEEP
# ----------------------------
base_results, base_summary = run_simulation(severity=SEVERITY, n_sim=N_SIM)

sweep_summaries = []
for sev in SEVERITY_SWEEP:
    _, s = run_simulation(severity=sev, n_sim=N_SIM//2)  # fewer sims for speed on sweep
    sweep_summaries.append(s)

summary_df = pd.DataFrame(sweep_summaries).sort_values("severity").reset_index(drop=True)

# Save a CSV for documentation
csv_path = "risk_simulation_summary.csv"
summary_df.to_csv(csv_path, index=False)

# ----------------------------
# DISPLAY HEADLINES
# ----------------------------
print("Base summary:", base_summary)
print("CSV saved to:", csv_path)
print(summary_df.round(4))

# ----------------------------
# PLOTS
# ----------------------------
# 1) Probability of downgrade (anytime & within window) vs severity
plt.figure()
plt.plot(summary_df["severity"], summary_df["prob_downgraded_any"], marker="o", label="Any time")
plt.plot(summary_df["severity"], summary_df["prob_downgraded_within_window"], marker="s", label=f"Within {DOWNGRADE_WINDOW}y")
plt.xlabel("Leakage severity")
plt.ylabel("Probability of downgrade")
plt.title("Downgrade probability vs leakage severity")
plt.legend()
plt.show()

# 2) Example path visualization (one random path from base case)
example_idx = np.random.randint(len(base_results))
example = base_results[example_idx]
years = np.arange(1, T_YEARS+1)

plt.figure()
plt.plot(years, example.coverage_path, marker="o")
plt.axhline(COVERAGE_THRESHOLD)
plt.xlabel("Year")
plt.ylabel("Interest coverage (EBITDA / Interest)")
plt.title("Example path: coverage and threshold")
plt.show()

plt.figure()
plt.plot(years, example.leverage_path, marker="o")
plt.axhline(LEVERAGE_THRESHOLD)
plt.xlabel("Year")
plt.ylabel("Leverage (Debt / EBITDA)")
plt.title("Example path: leverage and threshold")
plt.show()

# 3) Distribution of downgrade year (base case)
dg_years = [r.downgrade_year for r in base_results if r.downgraded and r.downgrade_year is not None]
if len(dg_years) > 0:
    plt.figure()
    plt.hist(dg_years, bins=np.arange(1, T_YEARS+2)-0.5, rwidth=0.8)
    plt.xlabel("Downgrade year")
    plt.ylabel("Frequency")
    plt.title("Distribution of downgrade timing (base case)")
    plt.show()
