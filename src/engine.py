import pandas as pd
import numpy as np
from src.contracts import FixedRateLoan, FloatingRateLoan, NonMaturingDeposit, InterestRateSwap
from src.stochastic import VasicekSimulator

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
        for i in range(n_loans):
            nominal = np.random.uniform(50000, 300000)
            mat = np.random.choice([5, 10, 15, 20])
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

    def calculate_eve(self, yield_curve):
        """EVE = Somme de toutes les NPV."""
        a_npv = sum([c.calculate_npv(yield_curve) for c in self.assets])
        l_npv = sum([c.calculate_npv(yield_curve) for c in self.liabilities])
        return a_npv + l_npv
    
    # ==========================================
    # L'APPROCHE PROFESSIONNELLE (BUMP & REVALUE)
    # ==========================================
    def get_dv01(self, yield_curve):
        """Calcule combien d'Euros on gagne/perd pour +1 bps de hausse des taux."""
        eve_base = self.calculate_eve(yield_curve)
        shocked_curve = yield_curve.apply_shock("parallel", 1) # Choc +1 bps (0.01%)
        eve_shock = self.calculate_eve(shocked_curve)
        return eve_shock - eve_base

    def get_equity_duration(self, yield_curve):
        """Déduit la Duration exacte à partir de la perte réelle en Euros."""
        eve = self.calculate_eve(yield_curve)
        if abs(eve) < 1e-6: return 0
        dv01 = self.get_dv01(yield_curve)
        # Formule mathématique pure : Duration = - dEVE / (EVE * dy)
        return -dv01 / (eve * 0.0001)

    def optimize_hedging(self, yield_curve, target_duration=0.0):
        """Immunise le bilan basé sur les sensibilités directes en Euros."""
        bs_dv01 = self.get_dv01(yield_curve)
        
        # On teste un Swap Receveur de 1M€ pour mesurer son "Pouvoir de Couverture" (DV01)
        fixed_rate = yield_curve.get_rate(10)
        test_swap = InterestRateSwap("TEST", 1_000_000, 10, fixed_rate, pay_fixed=False)
        test_swap.direction = 1
        
        npv_base = test_swap.calculate_npv(yield_curve)
        npv_shock = test_swap.calculate_npv(yield_curve.apply_shock("parallel", 1))
        swap_dv01 = npv_shock - npv_base
        
        # Combien de Swap de 1M€ faut-il pour annuler le risque de la banque ?
        required_nominal = - bs_dv01 / (swap_dv01 / 1_000_000)
        
        print(f"--- OPTIMISATION DU HEDGING ---")
        print(f"Sensibilité (DV01) Bilan : {bs_dv01:,.0f} € par point de base")
        print(f"Nominal de Swap requis   : {required_nominal:,.0f} €")
        return required_nominal, fixed_rate

    def apply_hedge(self, nominal, fixed_rate, maturity=10):
        """Injecte le swap dans le bilan."""
        hedge_swap = InterestRateSwap("STRATEGIC_HEDGE", nominal, maturity, fixed_rate, pay_fixed=False)
        hedge_swap.direction = 1 
        self.assets.append(hedge_swap)
        
        type_swap = "Payeur de Fixe" if nominal < 0 else "Receveur de Fixe"
        print(f"✅ Couverture appliquée : Swap {type_swap} de {abs(nominal):,.0f} €")

    def calculate_stochastic_var(self, simulator, n_scenarios=30):
        """Calcul allégé (30 scénarios au lieu de 100 pour la vitesse)."""
        from src.yield_curve import YieldCurve
        paths = simulator.simulate_paths(n_paths=n_scenarios, n_years=1)
        final_rates = paths[-1, :]
        eve_base = self.calculate_eve(YieldCurve([1, 10], [simulator.r0, simulator.r0 + 0.01]))
        
        diffs = []
        for r in final_rates:
            scen_curve = YieldCurve([1, 10, 20], [r, r + 0.005, r + 0.01])
            diffs.append(self.calculate_eve(scen_curve) - eve_base)
        
        var_95 = np.percentile(diffs, 5)
        print(f"--- ANALYSE STOCHASTIQUE ---")
        print(f"EVE VaR (95%) : {var_95:+,.0f} €")
        return var_95

if __name__ == "__main__":
    from src.yield_curve import YieldCurve
    bank = BalanceSheet()
    curve = YieldCurve([1, 10], [0.035, 0.04])
    bank.generate_random_portfolio()
    
    # 1. Avant Hedge
    print(f"Duration avant : {bank.get_equity_duration(curve):.4f}")
    
    # 2. Application Hedge
    nom, rate = bank.optimize_hedging(curve)
    bank.apply_hedge(nom, rate)
    
    # 3. Après Hedge
    print(f"Duration après : {bank.get_equity_duration(curve):.4f}")
    
    # 4. Monte-Carlo (30 scenarios)
    sim = VasicekSimulator(r0=0.035, kappa=0.1, theta=0.04, sigma=0.01)
    bank.calculate_stochastic_var(sim, n_scenarios=30)