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
        """Génération des flux fixes : Intérêts + Capital in fine."""
        cfs = {}
        for t in range(1, int(self.maturity) + 1):
            interest = self.nominal * self.rate
            # Flux = Intérêt simple, et au dernier terme on ajoute le Capital
            payment = interest if t < int(self.maturity) else (interest + self.nominal)
            cfs[t] = self.direction * payment
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
            variable_rate = yield_curve.get_rate(t) + self.spread
            interest = self.nominal * variable_rate
            cfs[t] = self.direction * (interest if t < int(self.maturity) else (interest + self.nominal))
        return cfs

class NonMaturingDeposit(Contract):
    def __init__(self, contract_id, nominal, decay_rate=0.15):
        super().__init__(contract_id, nominal, maturity=20, side="Liability")
        self.base_decay = decay_rate

    def get_cashflows(self, yield_curve=None):
        """Loi d'écoulement dynamique liée aux taux."""
        cfs = {}
        balance = self.nominal
        dynamic_decay = self.base_decay
        if yield_curve:
            market_rate = yield_curve.get_rate(1.0)
            dynamic_decay = self.base_decay * (1 + max(0, market_rate - 0.03) * 5)
            dynamic_decay = min(0.40, dynamic_decay)

        for t in range(1, 21):
            outflow = balance * dynamic_decay
            cfs[t] = self.direction * outflow
            balance -= outflow
        return cfs
    
class InterestRateSwap(Contract):
    """Swap de Taux (IRS) pour Hedging."""
    def __init__(self, contract_id, nominal, maturity, fixed_rate, pay_fixed=True):
        super().__init__(contract_id, nominal, maturity, side="Asset")
        self.fixed_rate = fixed_rate
        self.pay_fixed = pay_fixed

    def get_cashflows(self, yield_curve):
        """Différentiel entre taux fixe et taux variable."""
        cfs = {}
        for t in range(1, int(self.maturity) + 1):
            variable_rate = yield_curve.get_rate(t)
            if self.pay_fixed:
                net_rate = variable_rate - self.fixed_rate
            else:
                net_rate = self.fixed_rate - variable_rate
            cfs[t] = self.direction * (self.nominal * net_rate)
        return cfs