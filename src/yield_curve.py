import numpy as np
from scipy.interpolate import CubicSpline

class YieldCurve:
    """
    Moteur de courbe des taux zéro-coupon.
    Supporte l'interpolation par Spline Cubique et les chocs de structure.
    """

    def __init__(self, maturities, rates, label="Base Curve"):
        self.maturities = np.sort(np.array(maturities))
        self.rates = np.array(rates)
        self.label = label
        
        if len(self.maturities) != len(self.rates):
            raise ValueError("Maturities and Rates must have the same length.")

        # Interpolation Spline Cubique
        self._spline = CubicSpline(self.maturities, self.rates, bc_type='natural')

    def get_rate(self, t):
        """Retourne le taux zéro-coupon interpolé pour une maturité t."""
        t = np.atleast_1d(t)
        t_clipped = np.clip(t, self.maturities.min(), self.maturities.max())
        rates = self._spline(t_clipped)
        return rates[0] if rates.size == 1 else rates

    def get_discount_factor(self, t):
        """Calcule le facteur d'actualisation : DF(t) = exp(-r(t) * t)"""
        r = self.get_rate(t)
        return np.exp(-r * t)

    def apply_shock(self, shock_type="parallel", bps=0):
        """Génère une NOUVELLE YieldCurve stressée (Standard EBA)."""
        shock_decimal = bps / 10000
        new_rates = self.rates.copy()

        if shock_type == "parallel":
            new_rates += shock_decimal
        elif shock_type == "steepener":
            new_rates = self.rates + (self.maturities - 5) / 10 * shock_decimal
        elif shock_type == "flattener":
            new_rates = self.rates - (self.maturities - 5) / 10 * shock_decimal
        
        return YieldCurve(self.maturities, new_rates, label=f"{self.label}_{shock_type}_{bps}bps")

    def __repr__(self):
        return f"<YieldCurve '{self.label}' | Range: {self.maturities.min()}Y-{self.maturities.max()}Y>"

# --- BLOC DE TEST UNIQUE ---
if __name__ == "__main__":
    # Points de marché (Exemple Euribor)
    mats = [0.25, 0.5, 1, 2, 5, 10, 20, 30]
    rates = [0.038, 0.037, 0.035, 0.032, 0.030, 0.031, 0.033, 0.034]

    curve = YieldCurve(mats, rates, label="EUR_MARKET")
    
    print(f"--- {curve.label} ---")
    print(f"Taux 3 ans : {curve.get_rate(3.0)*100:.4f}%")
    print(f"DF 5 ans   : {curve.get_discount_factor(5.0):.6f}")

    # Test du choc parallèle de +200bps
    shocked = curve.apply_shock("parallel", 200)
    print(f"\n--- {shocked.label} ---")
    print(f"Taux 3 ans après choc : {shocked.get_rate(3.0)*100:.4f}%")