import numpy as np

class Contract:
    """Classe mère (Template) pour tous les instruments financiers du bilan."""
    def __init__(self, contract_id, nominal, maturity, side="Asset"):
        self.contract_id = contract_id
        self.nominal = nominal
        self.maturity = maturity  # En années
        # Side : 'Asset' (on reçoit du cash) ou 'Liability' (on doit du cash)
        self.direction = 1 if side == "Asset" else -1

    def calculate_npv(self, yield_curve):
        """Calcule la Net Present Value (NPV) en actualisant les cash flows."""
        cashflows = self.get_cashflows()
        npv = 0
        for t, cf in cashflows.items():
            df = yield_curve.get_discount_factor(t)
            npv += cf * df
        return npv

class FixedRateLoan(Contract):
    """Modèle de crédit à taux fixe (Amortissement In Fine pour simplifier)."""
    def __init__(self, contract_id, nominal, maturity, rate):
        # Un prêt accordé est un Actif (Asset)
        super().__init__(contract_id, nominal, maturity, side="Asset")
        self.rate = rate

    def get_cashflows(self):
        """Génère les intérêts annuels + le remboursement du capital à la fin."""
        cfs = {}
        for t in range(1, int(self.maturity) + 1):
            interest = self.nominal * self.rate
            # On multiplie par self.direction (1 pour Actif)
            cfs[t] = self.direction * (interest if t < int(self.maturity) else (interest + self.nominal))
        return cfs

class NonMaturingDeposit(Contract):
    """Modèle de Dépôt à Vue (Passif). Modélisé par une loi d'écoulement."""
    def __init__(self, contract_id, nominal, decay_rate=0.15):
        # Un dépôt est un Passif (Liability) - Maturité conventionnelle de 20 ans
        super().__init__(contract_id, nominal, maturity=20, side="Liability")
        self.decay_rate = decay_rate

    def get_cashflows(self):
        """Modélise la sortie progressive du cash (Loi exponentielle)."""
        cfs = {}
        balance = self.nominal
        for t in range(1, 21):
            outflow = balance * self.decay_rate
            cfs[t] = self.direction * outflow # Négatif car direction = -1
            balance -= outflow
        return cfs

# --- Script de Test Interne ---
if __name__ == "__main__":
    from yield_curve import YieldCurve
    # On crée une courbe simple pour le test
    test_curve = YieldCurve([1, 5, 10], [0.03, 0.035, 0.04])
    
    # Test 1 : Un crédit immo de 100k€ à 4% sur 5 ans
    loan = FixedRateLoan("LOAN_1", 100000, 5, 0.04)
    print(f"NPV du Crédit (Actif) : {loan.calculate_npv(test_curve):,.2f} €")
    
    # Test 2 : Un dépôt de 100k€ qui s'écoule de 15% par an
    deposit = NonMaturingDeposit("DEP_1", 100000, 0.15)
    print(f"NPV du Dépôt (Passif) : {deposit.calculate_npv(test_curve):,.2f} €")