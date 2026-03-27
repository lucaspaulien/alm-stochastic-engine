import pandas as pd
import numpy as np
from src.contracts import FixedRateLoan, FloatingRateLoan, NonMaturingDeposit

class BalanceSheet:
    """Simulateur de Bilan Bancaire ALM Haute Fidélité."""
    
    def __init__(self):
        self.assets = []
        self.liabilities = []

    def add_contract(self, contract):
        if contract.direction == 1:
            self.assets.append(contract)
        else:
            self.liabilities.append(contract)

    def generate_random_portfolio(self, n_loans=800, n_deposits=400):
        """Génère un mix réaliste Taux Fixe / Taux Variable."""
        for i in range(n_loans):
            nominal = np.random.uniform(50000, 300000)
            mat = np.random.choice([5, 10, 15, 20])
            
            # 70% Taux Fixe, 30% Taux Variable (Euribor + Spread)
            if np.random.rand() < 0.7:
                rate = np.random.uniform(0.035, 0.055)
                self.add_contract(FixedRateLoan(f"FIX_LOAN_{i}", nominal, mat, rate))
            else:
                spread = np.random.uniform(0.008, 0.015)
                self.add_contract(FloatingRateLoan(f"VAR_LOAN_{i}", nominal, mat, spread))
        
        for j in range(n_deposits):
            nominal = np.random.uniform(100, 500) * 1000
            decay = np.random.uniform(0.10, 0.20)
            self.add_contract(NonMaturingDeposit(f"DEP_{j}", nominal, decay))

    # --- MÉTRIQUES DE VALEUR (EVE & CONVEXITÉ) ---
    def calculate_eve(self, yield_curve):
        a_npv = sum([c.calculate_npv(yield_curve) for c in self.assets])
        l_npv = sum([c.calculate_npv(yield_curve) for c in self.liabilities])
        return a_npv + l_npv

    def get_equity_duration(self, yield_curve):
        """Sensibilité de 1er ordre (Linéaire)."""
        a_npv = sum([c.calculate_npv(yield_curve) for c in self.assets])
        l_npv = sum([c.calculate_npv(yield_curve) for c in self.liabilities])
        eve = a_npv + l_npv
        
        # Duration pondérée
        d_a = sum([(c.calculate_npv(yield_curve)/a_npv) * c.calculate_duration(yield_curve) for c in self.assets])
        d_l = sum([(c.calculate_npv(yield_curve)/l_npv) * c.calculate_duration(yield_curve) for c in self.liabilities])
        
        return (d_a * a_npv + d_l * l_npv) / eve

    def get_equity_convexity(self, yield_curve):
        """Sensibilité de 2nd ordre (Courbure)."""
        a_npv = sum([c.calculate_npv(yield_curve) for c in self.assets])
        l_npv = sum([c.calculate_npv(yield_curve) for c in self.liabilities])
        eve = a_npv + l_npv
        
        c_a = sum([(c.calculate_npv(yield_curve)/a_npv) * c.calculate_convexity(yield_curve) for c in self.assets])
        c_l = sum([(c.calculate_npv(yield_curve)/l_npv) * c.calculate_convexity(yield_curve) for c in self.liabilities])
        
        return (c_a * a_npv + c_l * l_npv) / eve

    # --- MÉTRIQUE DE MARGE (NII) ---
    def calculate_nii(self, yield_curve, horizon=1.0):
        total_income = 0
        total_expense = 0

        for asset in self.assets:
            effective_time = min(asset.maturity, horizon)
            # Le FloatingRateLoan utilisera le taux de la courbe, le Fixed utilisera son taux fixe
            cfs = asset.get_cashflows(yield_curve)
            total_income += abs(cfs.get(1, asset.nominal * 0.04)) # Estimation simplifiée sur Y1

        dep_rate = yield_curve.get_rate(horizon) * 0.4
        for liab in self.liabilities:
            total_expense += abs(liab.nominal) * dep_rate * horizon

        return total_income - total_expense

if __name__ == "__main__":
    from src.yield_curve import YieldCurve
    
    bank = BalanceSheet()
    curve = YieldCurve([0.5, 1, 10], [0.03, 0.032, 0.038])
    bank.generate_random_portfolio()
    
    eve0 = bank.calculate_eve(curve)
    dur = bank.get_equity_duration(curve)
    conv = bank.get_equity_convexity(curve)
    
    # Choc violent de +300 bps pour tester la convexité
    shock_bps = 300
    dy = shock_bps / 10000
    shock_curve = curve.apply_shock("parallel", shock_bps)
    
    eve_real = bank.calculate_eve(shock_curve)
    # Formule Taylor : dEVE = -Dur * dy * EVE + 0.5 * Conv * dy^2 * EVE
    eve_pred = eve0 * (1 - dur * dy + 0.5 * conv * (dy**2))
    
    print(f"--- ANALYSE QUANTITATIVE AVANCÉE ---")
    print(f"Duration de l'Equity  : {dur:.2f} ans")
    print(f"Convexité de l'Equity : {conv:.2f}")
    print("-" * 40)
    print(f"Choc de +{shock_bps} bps :")
    print(f"Variation Réelle      : {eve_real - eve0:+,.0f} €")
    print(f"Variation Prédite     : {eve_pred - eve0:+,.0f} €")
    print(f"Précision du modèle   : {100 - abs((eve_real-eve_pred)/eve_real)*100:.4f}%")