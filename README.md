# 🏦 ALM Stochastic Engine & Regulatory Stress-Testing Framework

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Financial Standards](https://img.shields.io/badge/Standards-EBA_IRRBB-red.svg)](https://www.eba.europa.eu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview
This high-performance **Asset Liability Management (ALM)** engine is a quantitative framework designed to simulate a commercial bank's balance sheet under complex market conditions. It provides a robust environment for monitoring **Interest Rate Risk in the Banking Book (IRRBB)** through advanced valuation metrics and regulatory stress-testing.

The engine quantifies the dual impact of interest rate movements on:
1.  **Economic Value of Equity (EVE):** Long-term value sensitivity (Stock view).
2.  **Net Interest Income (NII):** Short-term margin stability (Flow view).

---

## 📈 Quantitative & Financial Core

### 1. Term Structure Modeling
* **Yield Curve Bootstrapping:** Construction of zero-coupon curves using **Cubic Spline Interpolation** ($S$) for continuous and smooth discount factors.
* **Shock Engine:** Implementation of the **6 EBA (European Banking Authority) scenarios**:
    * *Parallel Up/Down, Steepener, Flattener, Short Rates Up/Down.*

### 2. Risk Sensitivity & Greeks
* **Modified Duration ($D_{mod}$):** First-order linear sensitivity of EVE to parallel shifts.
* **Convexity ($C$):** Second-order adjustment to capture non-linear price behavior during large shocks ($\pm 200$ bps).
* **Gap Analysis:** Mismatch identification between interest-rate-sensitive assets and liabilities across the maturity ladder.

### 3. Financial Instrument Library (Object-Oriented)
* **Fixed-Rate Loans:** Bullet and amortizing structures with precise NPV and Duration mapping.
* **Floating-Rate Loans (FRN):** Indexed on market forwards (Euribor proxies) to simulate repricing risk.
* **Non-Maturing Deposits (NMD):** Advanced behavioral modeling using **Exponential Decay Laws** to simulate stable vs. volatile liquidity outflows.

---

## 🛠 Mathematical Validation
The engine computes value variations using the **Taylor Series Expansion**, ensuring the mathematical consistency of the risk metrics:

$$\Delta EVE \approx -D_{mod} \cdot \Delta y \cdot EVE + \frac{1}{2} \cdot C \cdot (\Delta y)^2 \cdot EVE$$

| Metric | Business Usage | Method |
| :--- | :--- | :--- |
| **NPV** | Present Value | $PV = \sum \frac{CF_t}{(1+r_t)^t}$ |
| **Duration** | Interest Rate Sensitivity | Macaulay & Modified |
| **NII** | Earnings at Risk | Projected Cash Flows (12m) |

---

## 📂 Project Architecture
```bash
alm-stochastic-engine/
├── src/
│   ├── yield_curve.py   # Spline interpolation & EBA shock logic
│   ├── contracts.py     # OO-Modeling (Fixed, Floating, NMD)
│   ├── engine.py        # Portfolio Aggregator (EVE/NII/Duration)
│   ├── stress_test.py   # Regulatory reporting automation
│   └── viz.py           # Plotly interactive dashboards
├── reports/             # Dynamic HTML Risk Reports
├── tests/               # Unit tests for valuation accuracy
└── requirements.txt     # NumPy, SciPy, Pandas, Plotly