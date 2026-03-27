import plotly.graph_objects as go
import numpy as np
from src.yield_curve import YieldCurve

def plot_yield_curves(base_curve, shocked_curves=None):
    """
    Génère un graphique interactif comparant la courbe de base et les scénarios de stress.
    :param base_curve: Objet YieldCurve initial
    :param shocked_curves: Liste d'objets YieldCurve (optionnel)
    """
    # 1. Création de l'axe des abscisses (maturités de 0 à 30 ans avec un pas fin)
    t_range = np.linspace(0.25, 30, 200)
    
    fig = go.Figure()

    # 2. Ajout de la courbe de base
    fig.add_trace(go.Scatter(
        x=t_range, 
        y=base_curve.get_rate(t_range) * 100,
        mode='lines',
        name=base_curve.label,
        line=dict(color='black', width=3)
    ))

    # 3. Ajout des courbes de stress si présentes
    if shocked_curves:
        for curve in shocked_curves:
            fig.add_trace(go.Scatter(
                x=t_range, 
                y=curve.get_rate(t_range) * 100,
                mode='lines',
                name=curve.label,
                line=dict(dash='dash')
            ))

    # 4. Mise en forme "Banque d'Investissement"
    fig.update_layout(
        title=f"ALM Analysis: Interest Rate Term Structure & Shocks",
        xaxis_title="Maturity (Years)",
        yaxis_title="Zero-Coupon Rate (%)",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    # 5. Sauvegarde et affichage
    fig.write_html("reports/yield_curve_analysis.html")
    print("✅ Graphique généré dans : reports/yield_curve_analysis.html")
    fig.show()

def plot_balance_sheet_gap(balance_sheet):
    """
    Génère un histogramme comparant le stock d'Actifs et de Passifs par année.
    """
    # 1. On agrège les flux par année (Gap de liquidité)
    years = list(range(1, 21))
    asset_flows = np.zeros(20)
    liab_flows = np.zeros(20)

    for asset in balance_sheet.assets:
        cfs = asset.get_cashflows()
        for t, val in cfs.items():
            if 0 < t <= 20: asset_flows[t-1] += val

    for liab in balance_sheet.liabilities:
        cfs = liab.get_cashflows()
        for t, val in cfs.items():
            if 0 < t <= 20: liab_flows[t-1] += abs(val) # On prend la valeur absolue pour comparer

    # 2. Création du graphique à barres
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years, y=asset_flows, name='Assets (Inflows)', marker_color='green'
    ))
    
    fig.add_trace(go.Bar(
        x=years, y=liab_flows, name='Liabilities (Outflows)', marker_color='red'
    ))

    # 3. Mise en forme
    fig.update_layout(
        title="Liquidity Gap Analysis: Annual Cash Flow Projection",
        xaxis_title="Time to Maturity (Years)",
        yaxis_title="Nominal Amount (€)",
        barmode='group',
        template="plotly_white"
    )

    fig.write_html("reports/liquidity_gap.html")
    print("✅ Graphique de Gap généré : reports/liquidity_gap.html")
    fig.show()

def plot_stress_test_results(stress_results_df):
    """
    Crée un bar chart horizontal montrant l'impact des chocs sur la valeur (Delta EVE).
    :param stress_results_df: Le DataFrame retourné par ton module stress_test
    """
    # 1. On trie par impact pour le visuel
    df = stress_results_df.sort_values(by="Delta")
    
    # 2. On définit les couleurs (Rouge pour perte, Vert pour gain)
    colors = ['red' if x < 0 else 'green' for x in df['Delta']]

    fig = go.Figure(go.Bar(
        x=df['Delta'],
        y=df['Scenario'],
        orientation='h',
        marker_color=colors,
        text=df['Pct'].apply(lambda x: f"{x:.2f}%"),
        textposition='auto'
    ))

    # 3. Mise en forme pro
    fig.update_layout(
        title="<b>ALM Stress-Test Impact on EVE</b>",
        xaxis_title="Delta Economic Value of Equity (€)",
        yaxis_title="EBA Regulatory Scenarios",
        template="plotly_white",
        margin=dict(l=150) # Pour laisser de la place aux noms des scénarios
    )

    fig.write_html("reports/stress_test_dashboard.html")
    print("✅ Dashboard de stress généré : reports/stress_test_dashboard.html")
    fig.show()

if __name__ == "__main__":
    from src.stress_test import run_eba_stress_tests
    from src.engine import BalanceSheet
    from src.yield_curve import YieldCurve

    # 1. On lance les tests réglementaires et on récupère les données
    print("🚀 Lancement du moteur de stress-test...")
    df_results = run_eba_stress_tests()
    
    # 2. On génère le Dashboard de Sensibilité
    plot_stress_test_results(df_results)

    # 3. On génère le Gap de Liquidité avec un bilan frais
    bank = BalanceSheet()
    bank.generate_random_portfolio(n_loans=600, n_deposits=300)
    plot_balance_sheet_gap(bank)

    # 4. On génère la comparaison des courbes
    mats = [0.25, 1, 5, 10, 30]
    rates = [0.038, 0.035, 0.030, 0.031, 0.034]
    base = YieldCurve(mats, rates, label="Market_Base")
    up = base.apply_shock("parallel", 200)
    plot_yield_curves(base, [up])