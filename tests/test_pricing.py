import unittest
from src.yield_curve import YieldCurve
from src.contracts import FixedRateLoan, InterestRateSwap

class TestPricing(unittest.TestCase):
    def setUp(self):
        """Initialisation d'une courbe de taux plate à 4% pour les tests."""
        self.curve = YieldCurve([1, 10, 20], [0.04, 0.04, 0.04])

    def test_fixed_rate_loan_npv(self):
        """
        Vérifie que la NPV calculée par le moteur correspond exactement 
        à la somme des flux actualisés (Validation du Pricing).
        """
        nominal = 1_000_000
        loan = FixedRateLoan("TEST_LOAN", nominal, maturity=5, rate=0.04)
        
        # NPV calculée par notre classe
        npv_engine = loan.calculate_npv(self.curve)
        
        # NPV théorique attendue avec les mêmes facteurs d'escompte
        expected_npv = 0
        cfs = loan.get_cashflows(self.curve)
        for t, cf in cfs.items():
            expected_npv += cf * self.curve.get_discount_factor(t)
            
        # Les deux doivent correspondre au centime près
        self.assertAlmostEqual(npv_engine, expected_npv, places=2)

    def test_swap_par_pricing(self):
        """
        À la signature, un Swap émis au taux du marché doit valoir 0.
        """
        swap = InterestRateSwap("TEST_SWAP", 1_000_000, maturity=10, fixed_rate=0.04, pay_fixed=True)
        npv = swap.calculate_npv(self.curve)
        
        # La NPV doit être strictement 0
        self.assertAlmostEqual(npv, 0.0, places=2)

if __name__ == '__main__':
    unittest.main()