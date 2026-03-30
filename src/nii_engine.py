import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class NIIEngine:
    """
    Moteur de projection de la Marge Nette d'Intérêt (MNI / NII).
    Analyse l'évolution des revenus d'intérêts mensuels face aux chocs de taux.
    """
    def __init__(self, balance_sheet):
        self.bs = balance_sheet

    def project_monthly_nii(self, yield_curve, horizon_months=36):
        """
        Projette la MNI mois par mois avec Amortissement Dynamique (Bilan en run-off).
        """
        nii_profile = []
        
        for m in range(1, horizon_months + 1):
            t_years = m / 12.0
            monthly_interest = 0
            
            for contract in self.bs.assets + self.bs.liabilities:
                rate = 0.0
                
                # --- NOUVEAUTÉ : Amortissement Linéaire Dynamique ---
                # On vérifie si le contrat est arrivé à maturité
                total_months = contract.maturity * 12
                if m > total_months:
                    continue # Le contrat est terminé, il ne génère plus d'intérêts
                
                # Calcul du Capital Restant Dû (CRD) au mois m
                remaining_ratio = max(0.0, 1.0 - (m / total_months))
                current_nominal = contract.nominal * remaining_ratio
                
                # --- REPRICING GAP ---
                if contract.__class__.__name__ == "FixedRateLoan":
                    rate = contract.rate
                    
                elif contract.__class__.__name__ == "FloatingRateLoan":
                    rate = yield_curve.get_rate(t_years) + contract.spread
                    
                elif contract.__class__.__name__ == "NonMaturingDeposit":
                    market_rate = yield_curve.get_rate(t_years)
                    # Les dépôts à vue ne s'amortissent pas comme des prêts (comportement stable)
                    current_nominal = contract.nominal 
                    pass_through = 0.5 * max(0, market_rate - 0.02)
                    rate = 0.005 + pass_through
                    
                elif contract.__class__.__name__ == "InterestRateSwap":
                    market_rate = yield_curve.get_rate(t_years)
                    # Un swap a un nominal constant
                    current_nominal = contract.nominal
                    if contract.pay_fixed:
                        rate = market_rate - contract.fixed_rate
                    else:
                        rate = contract.fixed_rate - market_rate
                
                # Flux mensuel basé sur le CAPITAL RESTANT DÛ
                monthly_flow = contract.direction * (current_nominal * rate) / 12.0
                monthly_interest += monthly_flow
                
            nii_profile.append(monthly_interest)
            
        return pd.Series(nii_profile, index=range(1, horizon_months + 1))

    def generate_stress_report(self, base_curve, shock_bps=200, horizon=36):
        """
        Génère les projections Baseline vs Scénario Stresse (+X bps) 
        et affiche le graphique professionnel attendu en comité ALM.
        """
        print(f"--- ANALYSE DE SENSIBILITÉ MNI ({horizon} MOIS) ---")
        
        # 1. Projection Baseline
        nii_base = self.project_monthly_nii(base_curve, horizon)
        total_base = nii_base.sum()
        print(f"MNI Cumulée (Baseline) : {total_base:,.0f} €")
        
        # 2. Projection Choc Parallèle EBA (+200 bps)
        shocked_curve = base_curve.apply_shock("parallel", shock_bps)
        nii_shock = self.project_monthly_nii(shocked_curve, horizon)
        total_shock = nii_shock.sum()
        print(f"MNI Cumulée (+{shock_bps} bps) : {total_shock:,.0f} €")
        
        # 3. Earnings at Risk (EaR)
        ear = total_shock - total_base
        print(f"Sensibilité (Earnings at Risk) : {ear:+,.0f} €")
        
        # 4. Visualisation
        self._plot_nii_comparison(nii_base, nii_shock, shock_bps)
        
        return nii_base, nii_shock

    def _plot_nii_comparison(self, nii_base, nii_shock, shock_bps):
        plt.figure(figsize=(12, 6))
        
        plt.plot(nii_base.index, nii_base.values, label="Baseline (Courbe Actuelle)", color="#2c3e50", linewidth=2.5)
        plt.plot(nii_shock.index, nii_shock.values, label=f"Choc EBA (+{shock_bps} bps)", color="#e74c3c", linewidth=2.5, linestyle="--")
        
        # Remplissage de la zone de différence (Earnings at Risk)
        plt.fill_between(nii_base.index, nii_base.values, nii_shock.values, 
                         where=(nii_shock.values > nii_base.values), interpolate=True, color="#2ecc71", alpha=0.2, label="Gain MNI")
        plt.fill_between(nii_base.index, nii_base.values, nii_shock.values, 
                         where=(nii_shock.values < nii_base.values), interpolate=True, color="#e74c3c", alpha=0.2, label="Perte MNI")
        
        plt.title("Projection de la Marge Nette d'Intérêt (MNI) - Repricing Gap", fontsize=14, fontweight="bold")
        plt.xlabel("Mois de projection", fontsize=12)
        plt.ylabel("Revenu Net Mensuel (€)", fontsize=12)
        plt.legend(loc="best")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

# Bloc de test rapide si on lance ce fichier directement
if __name__ == "__main__":
    from src.engine import BalanceSheet
    from src.yield_curve import YieldCurve
    
    bank = BalanceSheet()
    bank.generate_random_portfolio(n_loans=800, n_deposits=400)
    
    curve = YieldCurve([1, 10, 20], [0.03, 0.035, 0.04])
    
    nii_engine = NIIEngine(bank)
    nii_engine.generate_stress_report(curve, shock_bps=200, horizon=36)