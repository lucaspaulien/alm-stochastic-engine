import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ReportGenerator:
    """
    Moteur de reporting automatisé pour le Stress-Testing ALM.
    Génère un tableau de bord interactif HTML des sensibilités du bilan.
    """
    def __init__(self, balance_sheet, base_curve):
        self.bs = balance_sheet
        self.base_curve = base_curve
        
        # Le dossier de sortie des rapports
        self.report_dir = "reports"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def run_eba_scenarios(self):
        """
        Simule une batterie de chocs réglementaires (Stress Tests).
        """
        print("⏳ Exécution des stress-tests réglementaires...")
        
        # Valeur de référence (Baseline)
        eve_base = self.bs.calculate_eve(self.base_curve)
        
        # Définition des scénarios (Simulés ici par des chocs parallèles pour la compatibilité)
        scenarios = {
            "Baseline (0 bps)": 0,
            "Parallel UP (+200 bps)": 200,
            "Parallel UP (+100 bps)": 100,
            "Parallel DOWN (-100 bps)": -100,
            "Parallel DOWN (-200 bps)": -200
        }
        
        results = []
        for name, bps in scenarios.items():
            shocked_curve = self.base_curve.apply_shock("parallel", bps)
            eve_shock = self.bs.calculate_eve(shocked_curve)
            
            # Calcul de la variation (Δ EVE)
            delta_eve = eve_shock - eve_base
            delta_eve_pct = (delta_eve / eve_base) * 100 if eve_base != 0 else 0
            
            results.append({
                "Scénario": name,
                "EVE (€)": eve_shock,
                "Impact (€)": delta_eve,
                "Impact (%)": delta_eve_pct
            })
            
        return pd.DataFrame(results)

    def generate_html_dashboard(self):
        """
        Génère un dashboard interactif Plotly et le sauvegarde en HTML.
        """
        df = self.run_eba_scenarios()
        
        # Création de la figure avec 2 graphiques
        fig = make_subplots(
            rows=1, cols=2, 
            subplot_titles=("Valeur Économique (EVE) par Scénario", "Sensibilité (Impact en €)"),
            specs=[[{"type": "bar"}, {"type": "waterfall"}]]
        )

        # Graphique 1 : EVE Absolue (Bar Chart)
        fig.add_trace(
            go.Bar(
                x=df["Scénario"], 
                y=df["EVE (€)"], 
                marker_color='#3498db',
                text=df["EVE (€)"].apply(lambda x: f"{x/1e6:.1f}M€"),
                textposition='auto',
                name="EVE"
            ),
            row=1, col=1
        )

        # Graphique 2 : Impact en € (Waterfall Chart)
        fig.add_trace(
            go.Waterfall(
                x=df["Scénario"], 
                y=df["Impact (€)"],
                measure=["relative"] * len(df),
                text=df["Impact (€)"].apply(lambda x: f"{x/1e6:+.2f}M€"),
                textposition="outside",
                decreasing={"marker": {"color": "#e74c3c"}},
                increasing={"marker": {"color": "#2ecc71"}},
                totals={"marker": {"color": "#2c3e50"}},
                name="Δ EVE"
            ),
            row=1, col=2
        )

        # Mise en forme du Dashboard
        fig.update_layout(
            title_text="<b>ALM Regulatory Stress-Testing Dashboard</b>",
            title_font_size=20,
            height=600,
            template="plotly_white",
            showlegend=False
        )

        # Sauvegarde du fichier HTML
        filepath = os.path.join(self.report_dir, "ALM_Risk_Dashboard.html")
        fig.write_html(filepath)
        print(f"✅ Dashboard généré avec succès : {filepath}")
        
        # Ouvre automatiquement le rapport dans ton navigateur (sur Mac)
        os.system(f"open {filepath}")


# --- Bloc d'exécution principal ---
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from src.engine import BalanceSheet
    from src.yield_curve import YieldCurve
    
    # 1. Création de l'environnement
    bank = BalanceSheet()
    bank.generate_random_portfolio(n_loans=1500, n_deposits=800)
    curve = YieldCurve([1, 10, 20], [0.03, 0.035, 0.04])
    
    # 2. Lancement du Reporting
    reporter = ReportGenerator(bank, curve)
    reporter.generate_html_dashboard()