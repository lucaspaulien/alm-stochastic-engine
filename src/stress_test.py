import pandas as pd
from src.yield_curve import YieldCurve
from src.engine import BalanceSheet

def run_eba_stress_tests():
    # 1. Initialisation du marché et de la banque
    mats = [0.25, 0.5, 1, 2, 5, 10, 20, 30]
    rates = [0.038, 0.037, 0.035, 0.032, 0.030, 0.031, 0.033, 0.034]
    base_curve = YieldCurve(mats, rates, label="Market_Base")

    my_bank = BalanceSheet()
    my_bank.generate_random_portfolio(n_loans=800, n_deposits=400)
    
    initial_eve = my_bank.calculate_eve(base_curve)
    
    # 2. Définition des scénarios réglementaires (EBA Guidelines)
    scenarios = [
        {"name": "Parallel Up", "type": "parallel", "bps": 200},
        {"name": "Parallel Down", "type": "parallel", "bps": -200},
        {"name": "Steepener", "type": "steepener", "bps": 100},
        {"name": "Flattener", "type": "flattener", "bps": 100},
    ]

    results = []

    print(f"{'Scenario':<20} | {'EVE (€)':<15} | {'Delta EVE (€)':<15} | {'% Impact'}")
    print("-" * 70)
    print(f"{'Base Case':<20} | {initial_eve:15,.0f} | {'-':<15} | 0.00%")

    for sc in scenarios:
        # On génère la courbe choquée
        shocked_curve = base_curve.apply_shock(sc['type'], sc['bps'])
        
        # On recalcule l'EVE
        new_eve = my_bank.calculate_eve(shocked_curve)
        delta = new_eve - initial_eve
        pct_impact = (delta / initial_eve) * 100
        
        results.append({
            "Scenario": sc['name'],
            "EVE": new_eve,
            "Delta": delta,
            "Pct": pct_impact
        })
        
        print(f"{sc['name']:<20} | {new_eve:15,.0f} | {delta:15,.0f} | {pct_impact:.2f}%")

    return pd.DataFrame(results)

if __name__ == "__main__":
    run_eba_stress_tests()