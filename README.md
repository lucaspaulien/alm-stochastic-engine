# 🏦 Advanced ALM Stochastic Engine & Macro-Hedging Framework

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Financial Standards](https://img.shields.io/badge/Standards-EBA_IRRBB-red.svg)](https://www.eba.europa.eu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Quant: Stochastic](https://img.shields.io/badge/Quant-Monte_Carlo-purple.svg)]()

## 🎯 Overview
This high-performance **Asset Liability Management (ALM)** engine is a quantitative framework designed to simulate a commercial bank's balance sheet under complex market conditions. Going beyond static gap analysis, this engine integrates **Stochastic Calculus**, **Behavioral Modeling**, and **Automated Macro-Hedging** to provide a production-ready environment for monitoring **Interest Rate Risk in the Banking Book (IRRBB)**.

The framework quantifies the dual impact of interest rate movements on:
1.  **Economic Value of Equity (EVE):** Long-term value sensitivity (Stock view).
2.  **Net Interest Income (NII):** Short-term margin stability (Flow view).
3.  **Value at Risk (VaR 95%):** Stochastic tail-risk metric via Monte Carlo simulations.

---

## 🔥 Key Quantitative Features (V4.0)

### 1. Stochastic Interest Rate Modeling (Monte Carlo)
* **Vasicek Model:** Implementation of a mean-reverting stochastic differential equation to generate realistic interest rate trajectories.
* **Stochastic VaR:** Monte Carlo simulation engine computing the 95% Value at Risk (VaR) of the EVE across thousands of market scenarios.

### 2. Automated Macro-Hedging Engine (DV01)
* **Dollar-Duration Immunization:** Automated calculation of the exact sensitivity (DV01) of the entire balance sheet.
* **Derivatives Integration:** Dynamic injection of **Interest Rate Swaps (IRS)** (Pay/Receive Fixed) to perfectly neutralize linear interest rate exposure, driving post-hedge portfolio duration to $0.0000$.

### 3. Dynamic Behavioral Embedded Options
* **Convexity Risk in Deposits:** Non-Maturing Deposits (NMDs) feature dynamic exponential decay laws. Outflow velocity is mathematically correlated to market rates (e.g., higher market rates accelerate liquidity flight), replicating real-world retail optionality.

---

## 📈 Quantitative & Financial Core

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

## 🛠 Mathematical Foundations

The engine ensures absolute mathematical consistency across all valuation metrics:

**1. EVE Taylor Series Expansion (Sensitivities):**
$$\Delta EVE \approx -D_{mod} \cdot \Delta y \cdot EVE + \frac{1}{2} \cdot C \cdot (\Delta y)^2 \cdot EVE$$

**2. Vasicek Stochastic Differential Equation (SDE):**
$$dr_t = \kappa(\theta - r_t)dt + \sigma dW_t$$
*(Where $\kappa$ is the speed of mean reversion, $\theta$ the long-term mean, and $dW_t$ a Wiener process).*

**3. DV01 Hedging Formula:**
$$Nominal_{Swap} = -\frac{DV01_{BalanceSheet}}{DV01_{Unit\_Swap}}$$

---

## 📂 Project Architecture
```bash
alm-stochastic-engine/
├── src/
│   ├── yield_curve.py   # Spline interpolation & EBA shock logic
│   ├── contracts.py     # OO-Modeling (Fixed, Floating, NMD, IRS)
│   ├── stochastic.py    # Vasicek Monte Carlo Simulator
│   ├── engine.py        # Portfolio Aggregator, DV01 Hedging & VaR
│   ├── stress_test.py   # Regulatory reporting automation
│   └── viz.py           # Plotly interactive dashboards
├── reports/             # Dynamic HTML Risk Reports
├── tests/               # Unit tests for valuation accuracy
└── requirements.txt     # NumPy, SciPy, Pandas, Plotly, Matplotlib
