import numpy as np

class Contract:
    """Classe mère enrichie pour tous les instruments ALM."""
    def __init__(self, contract_id, nominal, maturity, side="Asset"):
        self.contract_id = contract_id
        self.nominal = nominal
        self.maturity = maturity 
        self.direction = 1 if side == "Asset" else -1

    def calculate_npv(self, yield_curve):
        """Calcule la Net Present Value (NPV)."""
        cashflows = self.get_cashflows(yield_curve)
        npv = 0
        for t, cf in cashflows.items():
            df = yield_curve.get_discount_factor(t)
            npv += cf * df
        return npv

    def calculate_duration(self, yield_curve):
        """Duration de Macaulay : centre de gravité temporel des flux."""
        cashflows = self.get_cashflows(yield_curve)
        npv = self.calculate_npv(yield_curve)
        if abs(npv) < 1e-6: return 0
        
        weighted_time = sum(t * (cf * yield_curve.get_discount_factor(t)) 
                            for t, cf in cashflows.items())
        return weighted_time / npv

    def calculate_modified_duration(self, yield_curve):
        """Duration Modifiée : Sensibilité directe dV/dy."""
        # Pour une courbe continue : D_mod = D_mac / (1 + r)
        # Ici on simplifie en utilisant le taux à la maturité
        r = yield_curve.get_rate(self.maturity)
        return self.calculate_duration(yield_curve) / (1 + r)

    def calculate_convexity(self, yield_curve):
        """Calcule la Convexité (ajustement de second ordre pour les gros chocs)."""
        cashflows = self.get_cashflows(yield_curve)
        npv = self.calculate_npv(yield_curve)
        if abs(npv) < 1e-6: return 0
        
        weighted_time_sq = sum((t**2 + t) * (cf * yield_curve.get_discount_factor(t)) 
                               for t, cf in cashflows.items())
        return weighted_time_sq / (npv * (1 + yield_curve.get_rate(self.maturity))**2)

class FixedRateLoan(Contract):
    """Prêt à taux fixe (ex: Crédit Immo)."""
    def __init__(self, contract_id, nominal, maturity, rate):
        super().__init__(contract_id, nominal, maturity, side="Asset")
        self.rate = rate

    def get_cashflows(self, yield_curve=None):
        cfs = {}
        for t in range(1, int(self.maturity) + 1):
            interest = self.nominal * self.rate
            cfs[t] = self.direction * (interest if t < int(self.maturity) else (interest + self.nominal))
        return cfs

class FloatingRateLoan(Contract):
    """Prêt à taux variable (ex: Euribor 3M + Spread)."""
    def __init__(self, contract_id, nominal, maturity, spread=0.01):
        super().__init__(contract_id, nominal, maturity, side="Asset")
        self.spread = spread

    def get_cashflows(self, yield_curve):
        """Les flux dépendent des taux forward de la courbe."""
        cfs = {}
        for t in range(1, int(self.maturity) + 1):
            # On utilise le taux spot comme proxy du forward pour l'exercice
            variable_rate = yield_curve.get_rate(t) + self.spread
            interest = self.nominal * variable_rate
            cfs[t] = self.direction * (interest if t < int(self.maturity) else (interest + self.nominal))
        return cfs

class NonMaturingDeposit(Contract):
    """Dépôts à vue avec loi d'écoulement exponentielle (NMD)."""
    def __init__(self, contract_id, nominal, decay_rate=0.15):
        # Maturité conventionnelle de 20 ans pour les dépôts stables
        super().__init__(contract_id, nominal, maturity=20, side="Liability")
        self.decay_rate = decay_rate

    def get_cashflows(self, yield_curve=None):
        cfs = {}
        balance = self.nominal
        for t in range(1, 21):
            outflow = balance * self.decay_rate
            cfs[t] = self.direction * outflow
            balance -= outflow
        return cfs