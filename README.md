# 🏦 ALM Stochastic Engine & Stress-Testing

## 🎯 Overview
This project is an **Object-Oriented Asset Liability Management (ALM) engine** built in Python. It simulates a bank's balance sheet, computes the Net Present Value (NPV) of various financial instruments, and executes regulatory stress tests (EBA standards) to monitor interest rate risk.

## 📈 Financial Features
- **Yield Curve Modeling:** Zero-coupon curve construction using Cubic Spline interpolation ($).
- **Instrument Valuation:** NPV calculation for Fixed-Rate Loans, Floating-Rate Loans, and Non-Maturing Deposits (NMDs).
- **Risk Metrics:** Implementation of $\Delta EVE$ (Economic Value of Equity) and $\Delta NII$ (Net Interest Income).
- **Stress Testing:** Support for the 6 EBA standard interest rate shocks (Parallel, Steepener, Flattener, etc.).

## 🛠 Tech Stack
- **Data:** $, $ (Vectorized calculations).
- **Math:** $ (Interpolation & Optimization).
- **Visualization:** $ (Interactive risk dashboards).

## 🚀 Getting Started
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

## 📂 Architecture
- `src/yield_curve.py`: Yield curve construction & shocks.
- `src/contracts.py`: OO-modeling of banking contracts.
- `src/engine.py`: Balance sheet aggregator.
