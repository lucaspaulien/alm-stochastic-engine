import numpy as np
import matplotlib.pyplot as plt

class VasicekSimulator:
    """Modèle de taux d'intérêt stochastique (Vasicek)."""
    def __init__(self, r0, kappa, theta, sigma):
        self.r0 = r0         # Taux initial
        self.kappa = kappa   # Vitesse de retour à la moyenne
        self.theta = theta   # Moyenne de long terme
        self.sigma = sigma   # Volatilité

    def simulate_paths(self, n_paths, n_years, dt=1/12):
        """Simule n_paths trajectoires sur n_years avec un pas de temps dt."""
        n_steps = int(n_years / dt)
        paths = np.zeros((n_steps + 1, n_paths))
        paths[0, :] = self.r0
        
        for t in range(1, n_steps + 1):
            # Formule de Vasicek : dr_t = kappa * (theta - r_t) * dt + sigma * dW_t
            dr = self.kappa * (self.theta - paths[t-1, :]) * dt + \
                 self.sigma * np.sqrt(dt) * np.random.normal(size=n_paths)
            paths[t, :] = paths[t-1, :] + dr
            
        return paths

if __name__ == "__main__":
    # Test visuel
    sim = VasicekSimulator(r0=0.035, kappa=0.15, theta=0.04, sigma=0.01)
    trajectories = sim.simulate_paths(n_paths=50, n_years=10)
    
    plt.plot(trajectories)
    plt.title("Simulation Monte-Carlo des Taux (Vasicek)")
    plt.xlabel("Mois")
    plt.ylabel("Taux")
    plt.show()