import pandas as pd
import numpy as np
from src.contracts import FixedRateLoan, NonMaturingDeposit

class BalanceSheet:
    """Simulateur de Bilan Bancaire ALM."""
    
    def __init__(self):
        self.assets = []
        self.liabilities = []

    def add_contract(self, contract):
        """Ajoute un contrat au bon côté du bilan."""
        if contract.direction == 1:
            self.assets.append(contract)
        else:
            self.liabilities.append(contract)

    def generate_random_portfolio(self, n_loans=500, n_deposits=200):
        """Génère un portefeuille fictif massif pour simuler une vraie banque."""
        # 1. Génération de crédits immo aléatoires
        for i in range(n_loans):
            nominal = np.random.uniform(50000, 300000)
            mat = np.random.choice([5, 10, 15, 20])
            rate = np.random.uniform(0.035, 0.055)
            self.add_contract(FixedRateLoan(f"LOAN_{i}", nominal, mat, rate))
        
        # 2. Génération de dépôts aléatoires
        for j in range(n_deposits):
            nominal = np.random.uniform(100000, 500000)
            decay = np.random.uniform(0.10, 0.25)
            self.add_contract(NonMaturingDeposit(f"DEP_{j}", nominal, decay))

    def calculate_eve(self, yield_curve):
        """Calcule la Valeur Nette Économique (EVE = Assets - Liabilities)."""
        total_assets_npv = sum([c.calculate_npv(yield_curve) for c in self.assets])
        total_liabilities_npv = sum([c.calculate_npv(yield_curve) for c in self.liabilities])
        # Note : total_liabilities_npv est déjà négatif dans notre modèle
        return total_assets_npv + total_liabilities_npv

# --- Test de l'agrégateur ---
if __name__ == "__main__":
    from src.yield_curve import YieldCurve
    
    # On initialise la banque et le marché
    my_bank = BalanceSheet()
    market_curve = YieldCurve([1, 5, 10, 30], [0.035, 0.038, 0.04, 0.042])
    
    # On crée 1000 contrats d'un coup
    my_bank.generate_random_portfolio(n_loans=700, n_deposits=300)
    
    # Calcul de la santé financière
    eve_initial = my_bank.calculate_eve(market_curve)
    print(f"--- Bilan Initial ---")
    print(f"Nombre d'actifs  : {len(my_bank.assets)}")
    print(f"Nombre de passifs : {len(my_bank.liabilities)}")
    print(f"Valeur Nette Économique (EVE) : {eve_initial:,.2f} €")
    
    # Simulation d'un choc EBA (+200 bps)
    stressed_curve = market_curve.apply_shock("parallel", 200)
    eve_shocked = my_bank.calculate_eve(stressed_curve)
    
    print(f"\n--- Simulation de Stress (+200 bps) ---")
    print(f"EVE après choc : {eve_shocked:,.2f} €")
    print(f"Perte de valeur : {eve_shocked - eve_initial:,.2f} €")