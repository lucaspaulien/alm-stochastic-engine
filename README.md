# Advanced ALM Stochastic Engine & Macro-Hedging Framework

## Overview
This high-performance **Asset Liability Management (ALM)** engine is a quantitative framework designed to simulate a commercial bank's balance sheet under complex market conditions. Going beyond static gap analysis, this engine integrates **Stochastic Calculus**, **Behavioral Modeling**, and **Automated Macro-Hedging** to provide a production-ready environment for monitoring **Interest Rate Risk in the Banking Book (IRRBB)**.

The framework quantifies the dual impact of interest rate movements on:
1.  **Economic Value of Equity (EVE):** Long-term value sensitivity (Stock view).
2.  **Net Interest Income (NII):** Short-term margin stability (Flow view).
3.  **Value at Risk (VaR 95%):** Stochastic tail-risk metric via Monte Carlo simulations.

---

## Key Features 
* **Multi-Product Banking Engine:** Handles Amortizing Fixed-Rate Loans, Floating-Rate Loans (Spread-based), and Non-Maturing Deposits (NMDs).
* **Regulatory Sensitivity (EVE):** Calculation of Economic Value of Equity (EVE) via parallel and non-parallel shocks (DV01, Duration, Convexity).
* **NII Projection (Margin Analysis):** Dynamic Net Interest Income (NII) projection over a 36-month horizon with amortizing capital (Run-off profile) and Earnings at Risk (EaR) metrics.
* **Macro-Calibration & Behavioral Modeling:** OLS-based calibration of the **Vasicek SDE** and estimation of **Deposit Beta** (Pass-through rate) on historical market data.
* **Stochastic Monte Carlo:** Vasicek-driven interest rate simulations for Value-at-Risk (VaR) estimation.
* **Automated Hedging:** Portfolio immunization using Interest Rate Swaps (IRS) via Dollar-Duration matching.
* **Industrial Reporting:** Automated generation of interactive HTML Dashboards using **Plotly** for ALM committees.

---

## Key Quantitative Features

### 1. Stochastic Interest Rate Modeling (Monte Carlo)
* **Vasicek Model:** Implementation of a mean-reverting stochastic differential equation to generate realistic interest rate trajectories.
* **Stochastic VaR:** Monte Carlo simulation engine computing the 95% Value at Risk (VaR) of the EVE across thousands of market scenarios.

### 2. Automated Macro-Hedging Engine (DV01)
* **Dollar-Duration Immunization:** Automated calculation of the exact sensitivity (DV01) of the entire balance sheet.
* **Derivatives Integration:** Dynamic injection of **Interest Rate Swaps (IRS)** (Pay/Receive Fixed) to perfectly neutralize linear interest rate exposure, driving post-hedge portfolio duration to $0.0000$.

### 3. Dynamic Behavioral Embedded Options
* **Convexity Risk in Deposits:** Non-Maturing Deposits (NMDs) feature dynamic exponential decay laws. Outflow velocity is mathematically correlated to market rates (e.g., higher market rates accelerate liquidity flight), replicating real-world retail optionality.

---

## Quantitative & Financial Core

### 1. Term Structure Modeling
* **Yield Curve Bootstrapping:** Construction of zero-coupon curves using **Cubic Spline Interpolation** ($S$) for continuous and smooth discount factors.
* **Shock Engine:** Implementation of the **6 EBA (European Banking Authority) scenarios**: Parallel Up/Down, Steepener, Flattener, Short Rates Up/Down.

### 2. Risk Sensitivity & Greeks
* **Modified Duration ($D_{mod}$):** First-order linear sensitivity of EVE to parallel shifts.
* **Convexity ($C$):** Second-order adjustment to capture non-linear price behavior during large shocks ($\pm 200$ bps).
* **Gap Analysis:** Mismatch identification between interest-rate-sensitive assets and liabilities across the maturity ladder.

### 3. Financial Instrument Library (Object-Oriented)
* **Fixed-Rate Loans:** Bullet and amortizing structures with precise NPV and Duration mapping.
* **Floating-Rate Loans (FRN):** Indexed on market forwards (Euribor proxies) to simulate repricing risk.
* **Non-Maturing Deposits (NMD):** Advanced behavioral modeling using **Exponential Decay Laws** to simulate stable vs. volatile liquidity outflows.

---

## Mathematical Foundations

The engine ensures absolute mathematical consistency across all valuation metrics:

**1. EVE Taylor Series Expansion (Sensitivities):**
$$\Delta EVE \approx -D_{mod} \cdot \Delta y \cdot EVE + \frac{1}{2} \cdot C \cdot (\Delta y)^2 \cdot EVE$$

**2. Vasicek Stochastic Differential Equation (SDE):**
$$dr_t = \kappa(\theta - r_t)dt + \sigma dW_t$$
(Where `κ` is the speed of mean reversion, `θ` the long-term mean, and `dW_t` a Wiener process).

**3. Net Interest Income (NII) Projection**
$$NII_{m} = \sum_{i \in Assets} \left( CRD_{i,m} \cdot \frac{r_{i,m}}{12} \right) - \sum_{j \in Liabilities} \left( Nominal_{j,m} \cdot \frac{r_{j,m}}{12} \right)$$
*Where $CRD_{i,m}$ represents the amortized Capital Remaining Due for asset $i$ at month $m$.*

**4. DV01 Hedging Formula:**
$$Nominal_{Swap} = -\frac{DV01_{BalanceSheet}}{DV01_{Unit\_Swap}}$$

---

## Unit Testing & Validation
The engine includes a robust `unittest` suite to continuously validate the financial mathematics and pricing accuracy:
* **Par Pricing Validation:** Ensures that fixed-rate instruments issued at market rates hold a Net Present Value (NPV) exactly equal to their nominal.
* **Derivative Valuation:** Validates that Interest Rate Swaps (IRS) exhibit a strict zero NPV at inception.

---


## Project Architecture
```bash
alm-stochastic-engine/
├── notebooks/
│   └── ALM_Showcase.ipynb      # Interactive Full-Scale Quant Demonstration
├── reports/                    # Automated HTML Risk Dashboards (Plotly)
├── src/
│   ├── __init__.py
│   ├── yield_curve.py          # Spline interpolation & EBA shock logic
│   ├── contracts.py            # OO-Modeling (Fixed, Floating, NMD, IRS)
│   ├── stochastic.py           # Vasicek Monte Carlo Simulator
│   ├── engine.py               # Portfolio Aggregator & EVE Analytics
│   ├── nii_engine.py           # NII Projection & Earnings at Risk (EaR)
│   ├── macro_calibration.py    # Econometric OLS Calibration (Vasicek & Beta)
│   ├── reporting.py            # Automated Plotly Dashboard Generator
│   ├── stress_test.py          # Regulatory scenario orchestration
│   └── viz.py                  # Static plotting utilities
├── tests/                      # Unit testing suite
│   ├── __init__.py
│   └── test_pricing.py         # Financial validation (NPV & Par Pricing)
├── .gitignore
├── README.md
└── requirements.txt            # NumPy, SciPy, Pandas, Plotly, Statsmodels
