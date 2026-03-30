import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

class MacroCalibrator:
    """
    Calibrateur de modèles macroéconomiques pour l'ALM.
    1. Calibration du modèle stochastique de Vasicek via OLS.
    2. Estimation du Beta de Dépôt (Pass-through rate) via régression linéaire.
    """
    def __init__(self, dt=1/252): 
        # dt = 1 jour ouvré par défaut (252 jours de trading par an)
        self.dt = dt

    def calibrate_vasicek(self, historical_rates):
        """
        Calibre les paramètres (kappa, theta, sigma) du modèle de Vasicek
        sur une série temporelle historique de taux via un modèle AR(1).
        """
        # r_{t} = a + b * r_{t-1} + e
        y = historical_rates[1:]
        x = historical_rates[:-1]
        
        # Ajout de la constante pour la régression (le 'a' de l'équation)
        x_with_const = sm.add_constant(x)
        model = sm.OLS(y, x_with_const).fit()
        
        a, b = model.params[0], model.params[1]
        residuals = model.resid
        
        # Transformation des paramètres AR(1) vers Vasicek (SDE continue)
        kappa = -np.log(b) / self.dt
        theta = a / (1 - b)
        
        # Volatilité implicite basée sur la variance des résidus
        var_epsilon = np.var(residuals)
        sigma = np.sqrt((var_epsilon * 2 * kappa) / (1 - b**2))
        
        print(f"✅ Calibration Vasicek réussie (R2 = {model.rsquared:.4f}) :")
        print(f"   - Kappa (Vitesse de rappel)  : {kappa:.4f}")
        print(f"   - Theta (Moyenne long terme) : {theta:.4f} ({theta*100:.2f}%)")
        print(f"   - Sigma (Volatilité)         : {sigma:.4f} ({sigma*100:.2f}%)")
        
        return kappa, theta, sigma

    def calibrate_deposit_beta(self, market_rates, deposit_rates):
        """
        Calibre le "Deposit Beta", c'est-à-dire la sensibilité des taux de dépôts
        aux variations des taux de marché (ex: BCE / Euribor).
        """
        # Régression : Taux_Depot = alpha + Beta * Taux_Marche
        x_with_const = sm.add_constant(market_rates)
        model = sm.OLS(deposit_rates, x_with_const).fit()
        
        alpha = model.params[0]
        beta = model.params[1]
        
        print(f"\n✅ Calibration Beta de Dépôt réussie (R2 = {model.rsquared:.4f}) :")
        print(f"   - Taux Plancher (Alpha) : {alpha:.4f} ({alpha*100:.2f}%)")
        print(f"   - Deposit Beta          : {beta:.4f} (La banque répercute {beta*100:.1f}% de la hausse)")
        
        return alpha, beta

# --- Bloc de test rapide si on lance ce script ---
if __name__ == "__main__":
    # Simulation d'un historique de taux sur 5 ans (1250 jours) pour la démo
    np.random.seed(42)
    n_days = 1250
    
    # 1. Faux historique Euribor 3M (Market Rate)
    market_history = np.zeros(n_days)
    market_history[0] = 0.02 # Démarre à 2%
    for i in range(1, n_days):
        # On simule la vraie vie avec un peu de bruit
        dr = 0.15 * (0.035 - market_history[i-1]) * (1/252) + 0.008 * np.sqrt(1/252) * np.random.normal()
        market_history[i] = market_history[i-1] + dr
        
    # 2. Faux historique de Taux de Dépôts (La banque lisse les taux)
    # La banque répercute ~40% (Beta) avec un taux plancher de 0.5% et un léger bruit
    deposit_history = 0.005 + 0.40 * market_history + np.random.normal(0, 0.0005, n_days)

    calibrator = MacroCalibrator()
    
    # Test 1 : L'algorithme retrouve-t-il les paramètres cachés ?
    print("--- 1. ANALYSE STOCHASTIQUE (VASICEK) ---")
    k, t, s = calibrator.calibrate_vasicek(market_history)
    
    # Test 2 : L'algorithme calcule-t-il le bon Deposit Beta ?
    print("\n--- 2. ANALYSE COMPORTEMENTALE (ALM) ---")
    alpha, beta = calibrator.calibrate_deposit_beta(market_history, deposit_history)
    
    # Visualisation Quant
    plt.figure(figsize=(10, 5))
    plt.plot(market_history * 100, label="Taux de Marché (ex: Euribor)", color="#e74c3c", alpha=0.9)
    plt.plot(deposit_history * 100, label="Taux de Dépôts (Clients)", color="#3498db", linewidth=2)
    
    plt.title(f"Historique des Taux & Deposit Beta (β = {beta:.2f})", fontweight='bold', fontsize=14)
    plt.ylabel("Taux d'intérêt (%)", fontsize=12)
    plt.xlabel("Jours (Historique sur 5 ans)", fontsize=12)
    plt.legend(loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()