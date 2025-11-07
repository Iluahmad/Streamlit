# nigeria_fiscal_simulator_with_mechanics.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ======================
# ENHANCED ECONOMIC MODEL FOR COMMODITY-DEPENDENT ECONOMIES
# ======================
class NigeriaFiscalModel:
    def __init__(self):
        # Nigeria-specific initial values (billions of USD)
        self.initial_gdp = 450  # ~$450B GDP
        self.initial_debt = 140  # ~31% debt-to-GDP
        self.initial_deficit = 12  # ~2.7% of GDP
        
        # Revenue structure (typical for Nigeria)
        self.oil_revenue = 25    # ~$25B from oil
        self.non_oil_revenue = 35 # ~$35B from other sources
        self.total_revenue = self.oil_revenue + self.non_oil_revenue
        
        # Spending
        self.total_spending = self.total_revenue + self.initial_deficit
        
        # Oil parameters
        self.oil_price = 75  # USD per barrel
        self.oil_production = 1.4  # million barrels per day
        self.oil_revenue_per_dollar = 0.33  # $0.33B revenue per $1 oil price
        
    def calculate_impact(self, tax_change, spending_change, growth_assumption, 
                        oil_price_shock, years=5):
        """
        Enhanced model with oil dependency and debt feedback
        """
        
        # Initialize results
        results = []
        gdp = self.initial_gdp
        debt = self.initial_debt
        non_oil_revenue = self.non_oil_revenue
        oil_revenue = self.oil_revenue
        spending = self.total_spending
        
        # Dynamic multipliers based on economic conditions
        economic_condition = self.assess_economic_condition(gdp, debt/gdp)
        spending_multiplier, tax_multiplier = self.get_multipliers(economic_condition)
        
        # Initial interest rate (sovereign borrowing cost)
        interest_rate = 12.0  # Base interest rate in %
        
        for year in range(years):
            # ======================
            # OIL REVENUE CALCULATION
            # ======================
            current_oil_price = self.oil_price * (1 + oil_price_shock/100)
            oil_revenue = current_oil_price * self.oil_revenue_per_dollar
            
            # ======================
            # NON-OIL REVENUE (with growth feedback)
            # ======================
            non_oil_revenue = non_oil_revenue * (1 + tax_change/100) * (1 + growth_assumption/100)
            
            total_revenue = oil_revenue + non_oil_revenue
            
            # ======================
            # SPENDING
            # ======================
            spending = spending * (1 + spending_change/100)
            
            # ======================
            # DEBT-DRIVEN INTEREST RATE (Critical enhancement!)
            # ======================
            debt_to_gdp = (debt / gdp) * 100
            
            # Higher debt leads to higher risk premium
            if debt_to_gdp > 50:
                risk_premium = (debt_to_gdp - 50) * 0.15  # 0.15% increase per 1% debt/GDP above 50%
            elif debt_to_gdp < 30:
                risk_premium = (30 - debt_to_gdp) * -0.1  # Lower rates for good fiscal position
            else:
                risk_premium = 0
                
            effective_interest_rate = interest_rate + risk_premium
            
            # ======================
            # DEBT SERVICE COSTS
            # ======================
            debt_service = debt * (effective_interest_rate/100)
            
            # ======================
            # FISCAL IMPACT ON GDP (with crowding-out effect)
            # ======================
            fiscal_impact = (spending_change * (spending - debt_service) * spending_multiplier + 
                           tax_change * non_oil_revenue * tax_multiplier) / gdp
            
            # ======================
            # CROWDING-OUT EFFECT: Higher debt service reduces productive spending
            # ======================
            crowding_out_effect = max(0, (debt_service - (debt_service * (debt/gdp))) / gdp) * 100
            
            effective_growth = growth_assumption + fiscal_impact - crowding_out_effect
            
            # ======================
            # UPDATE ECONOMIC VARIABLES
            # ======================
            gdp = gdp * (1 + effective_growth/100)
            deficit = spending + debt_service - total_revenue  # Now includes debt service
            debt = debt + deficit
            debt_to_gdp = (debt / gdp) * 100
            
            # Update economic condition for next year's multipliers
            economic_condition = self.assess_economic_condition(gdp, debt_to_gdp)
            spending_multiplier, tax_multiplier = self.get_multipliers(economic_condition)
            
            results.append({
                'Year': year + 1,
                'GDP': gdp,
                'Oil_Revenue': oil_revenue,
                'Non_Oil_Revenue': non_oil_revenue,
                'Total_Revenue': total_revenue,
                'Spending': spending,
                'Debt_Service': debt_service,
                'Deficit': deficit,
                'Debt': debt,
                'Debt_to_GDP': debt_to_gdp,
                'GDP_Growth': effective_growth,
                'Interest_Rate': effective_interest_rate,
                'Oil_Price': current_oil_price,
                'Economic_Condition': economic_condition,
                'Crowding_Out_Effect': crowding_out_effect
            })
            
        return pd.DataFrame(results)
    
    def assess_economic_condition(self, gdp, debt_to_gdp):
        """Determine if economy is in recession, normal, or boom"""
        if debt_to_gdp > 60:
            return "high_debt"
        elif gdp < self.initial_gdp * 0.98:  # Contraction
            return "recession"
        elif gdp > self.initial_gdp * 1.05:  # Strong growth
            return "boom"
        else:
            return "normal"
    
    def get_multipliers(self, economic_condition):
        """Time-varying multipliers based on economic conditions"""
        if economic_condition == "recession":
            return 0.8, 0.5  # Higher multipliers in recession
        elif economic_condition == "boom":
            return 0.4, 0.2  # Lower multipliers in boom (crowding out)
        elif economic_condition == "high_debt":
            return 0.3, 0.1  # Very low multipliers with high debt (confidence effect)
        else:  # normal
            return 0.6, 0.3

# ======================
# STREAMLIT INTERFACE
# ======================

st.set_page_config(
    page_title=" Nigeria Fiscal Simulator",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #008751;
        text-align: center;
        margin-bottom: 2rem;
    }
    .nigeria-green {
        background-color: #008751;
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #008751;
        margin-bottom: 1rem;
    }
    .equation {
        background-color: #f8f9fa;
        padding: 15px;
        border-left: 4px solid #008751;
        font-family: "Courier New", monospace;
        margin: 10px 0;
    }
    .mechanic-box {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Fictional Nigeria Fiscal Policy Simulator</div>', unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("🎛️ Policy Controls")

# Oil market assumptions
st.sidebar.subheader("🛢️ Oil Market Assumptions")
oil_price_shock = st.sidebar.slider(
    "Oil Price Shock (%)", 
    min_value=-50.0, max_value=100.0, value=0.0, step=5.0,
    help="Percentage change in oil prices from current levels"
)

# Economic assumptions
st.sidebar.subheader("📈 Economic Assumptions")
baseline_growth = st.sidebar.slider(
    "Non-Oil GDP Growth (%)", 
    min_value=0.0, max_value=8.0, value=3.0, step=0.5
)

# Fiscal policy levers
st.sidebar.subheader("🏛️ Fiscal Policy Levers")

tax_change = st.sidebar.slider(
    "Non-Oil Revenue Change (%)", 
    min_value=-20.0, max_value=50.0, value=0.0, step=2.0,
    help="Change in tax collection efficiency and non-oil revenue"
)

spending_change = st.sidebar.slider(
    "Government Spending Change (%)", 
    min_value=-30.0, max_value=40.0, value=0.0, step=2.0,
    help="Change in total government expenditure"
)

# Model execution
@st.cache_data
def run_enhanced_model(tax_change, spending_change, growth_rate, oil_shock):
    model = NigeriaFiscalModel()
    return model.calculate_impact(tax_change, spending_change, growth_rate, oil_shock)

results_df = run_enhanced_model(tax_change, spending_change, baseline_growth, oil_price_shock)

# Key Metrics Dashboard - Enhanced with 5 Columns including Nominal GDP
st.subheader("📊 Key Fiscal Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    debt_change = results_df['Debt_to_GDP'].iloc[-1] - results_df['Debt_to_GDP'].iloc[0]
    st.metric(
        "Debt-to-GDP (5Y)", 
        f"{results_df['Debt_to_GDP'].iloc[-1]:.1f}%",
        f"{debt_change:+.1f}%"
    )

with col2:
    avg_growth = results_df['GDP_Growth'].mean()
    st.metric(
        "Avg GDP Growth", 
        f"{avg_growth:.1f}%",
        f"{(avg_growth - baseline_growth):+.1f}% vs baseline"
    )

with col3:
    oil_reliance = (results_df['Oil_Revenue'].iloc[-1] / results_df['Total_Revenue'].iloc[-1]) * 100
    st.metric(
        "Oil Revenue Share", 
        f"{oil_reliance:.1f}%",
        "of total revenue"
    )

with col4:
    interest_rate_change = results_df['Interest_Rate'].iloc[-1] - results_df['Interest_Rate'].iloc[0]
    st.metric(
        "Sovereign Interest Rate", 
        f"{results_df['Interest_Rate'].iloc[-1]:.1f}%",
        f"{interest_rate_change:+.1f}%"
    )

with col5:
    # Enhanced Nominal GDP Analysis
    initial_gdp = results_df['GDP'].iloc[0]
    final_gdp = results_df['GDP'].iloc[-1]
    total_gdp_growth = ((final_gdp - initial_gdp) / initial_gdp) * 100
    
    # Calculate baseline scenario (no policy changes)
    baseline_gdp = initial_gdp
    baseline_path = [initial_gdp]
    for year in range(4):  # 5 years total (0-4)
        baseline_gdp = baseline_gdp * (1 + baseline_growth/100)
        baseline_path.append(baseline_gdp)
    
    baseline_final_gdp = baseline_path[-1]
    
    # Policy impact in absolute terms
    policy_impact_abs = final_gdp - baseline_final_gdp
    policy_impact_percent = (policy_impact_abs / baseline_final_gdp) * 100
    
    # Determine if policy is growth-enhancing or contractionary
    if policy_impact_abs > 5:  # More than $5B positive impact
        delta_color = "normal"
        impact_label = "growth-added"
    elif policy_impact_abs < -5:  # More than $5B negative impact  
        delta_color = "inverse"
        impact_label = "growth-lost"
    else:
        delta_color = "off"
        impact_label = "neutral"
    
    st.metric(
        "Economy Size (Year 5)", 
        f"${final_gdp:,.0f}B",
        f"${policy_impact_abs:+,.0f}B {impact_label}",
        delta_color=delta_color
    )
    
    # Rich context below the metric
    st.progress(min(100, max(0, int((final_gdp / (initial_gdp * 1.5)) * 100))), 
                text=f"↑{total_gdp_growth:.1f}% from ${initial_gdp:,.0f}B")

# Enhanced Visualizations
st.subheader("📈 Comprehensive Fiscal Analysis")

# Create tabs for different aspects - ADDED TAB5 FOR TECHNICAL MECHANICS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Debt Dynamics", "Revenue Composition", "Growth Drivers", "Fiscal Sustainability", "Technical Mechanics"])

with tab1:
    fig_debt = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Debt-to-GDP Ratio', 'Sovereign Borrowing Cost', 
                       'Debt Service Burden', 'Primary Balance'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Debt-to-GDP
    fig_debt.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Debt_to_GDP'], 
                   name="Debt/GDP", line=dict(color='red', width=3)),
        row=1, col=1
    )
    
    # Interest rate
    fig_debt.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Interest_Rate'], 
                   name="Interest Rate", line=dict(color='orange', width=3)),
        row=1, col=2
    )
    
    # Debt service
    fig_debt.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Debt_Service'], 
               name="Debt Service", marker_color='purple'),
        row=2, col=1
    )
    
    # Primary balance (revenue - spending excluding interest)
    results_df['Primary_Balance'] = results_df['Total_Revenue'] - results_df['Spending']
    fig_debt.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Primary_Balance'], 
               name="Primary Balance", marker_color='green'),
        row=2, col=2
    )
    
    fig_debt.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_debt, use_container_width=True)

with tab2:
    # Revenue composition over time
    revenue_data = []
    for idx, row in results_df.iterrows():
        revenue_data.extend([
            {'Year': row['Year'], 'Source': 'Oil', 'Revenue': row['Oil_Revenue']},
            {'Year': row['Year'], 'Source': 'Non-Oil', 'Revenue': row['Non_Oil_Revenue']}
        ])
    
    revenue_df = pd.DataFrame(revenue_data)
    fig_revenue = px.area(revenue_df, x='Year', y='Revenue', color='Source',
                         title='Revenue Composition Over Time',
                         color_discrete_map={'Oil': '#FFA500', 'Non-Oil': '#008751'})
    st.plotly_chart(fig_revenue, use_container_width=True)

with tab3:
    fig_growth = go.Figure()
    
    fig_growth.add_trace(go.Bar(name='Baseline Growth', x=results_df['Year'], 
                               y=[baseline_growth]*len(results_df),
                               marker_color='lightgray'))
    
    fig_growth.add_trace(go.Bar(name='Fiscal Impact', x=results_df['Year'], 
                               y=results_df['GDP_Growth'] - baseline_growth,
                               marker_color='blue'))
    
    fig_growth.add_trace(go.Bar(name='- Crowding Out', x=results_df['Year'], 
                               y=-results_df['Crowding_Out_Effect'],
                               marker_color='red'))
    
    fig_growth.add_trace(go.Scatter(name='Actual Growth', x=results_df['Year'], 
                                   y=results_df['GDP_Growth'],
                                   line=dict(color='black', width=3)))
    
    fig_growth.update_layout(barmode='relative', title='GDP Growth Decomposition',
                           yaxis_title='Percentage Points')
    st.plotly_chart(fig_growth, use_container_width=True)

with tab4:
    # Fiscal space analysis
    fig_sustainability = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Fiscal Space Analysis', 'Debt Service vs Revenue'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Fiscal space (revenue minus mandatory spending)
    results_df['Fiscal_Space'] = results_df['Total_Revenue'] - results_df['Debt_Service'] - (results_df['Spending'] * 0.7)  # Assume 70% is mandatory
    
    fig_sustainability.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Fiscal_Space'], 
                   name="Fiscal Space", line=dict(color='green', width=3),
                   fill='tozeroy'),
        row=1, col=1
    )
    
    # Debt service as % of revenue
    results_df['Debt_Service_Ratio'] = (results_df['Debt_Service'] / results_df['Total_Revenue']) * 100
    
    fig_sustainability.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Debt_Service_Ratio'], 
                   name="Debt Service/Revenue", line=dict(color='red', width=3)),
        row=2, col=1
    )
    
    # Add threshold lines
    fig_sustainability.add_hline(y=30, line_dash="dash", line_color="red", 
                                annotation_text="Danger Zone (30%)", row=2, col=1)
    
    fig_sustainability.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_sustainability, use_container_width=True)

with tab5:
    st.header("🔬 Complete Model Mechanics")
    st.markdown("""
    ## 🏗️ Core Economic Architecture
    
    ### **1. Initial State Setup (Nigeria-Specific Baseline)**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Macroeconomic Baseline:**
        - Initial GDP: $450 billion
        - Initial Debt: $140 billion (31% debt-to-GDP)
        - Initial Deficit: $12 billion (2.7% of GDP)
        
        **Revenue Structure:**
        - Oil Revenue: $25 billion (55% of total)
        - Non-Oil Revenue: $35 billion
        - Total Revenue: $60 billion
        """)
    
    with col2:
        st.markdown("""
        **Spending & Oil Parameters:**
        - Total Spending: $72 billion
        - Oil Price: $75/barrel
        - Oil Production: 1.4 million bpd
        - Oil Revenue Sensitivity: $0.33B per $1 oil price
        """)
    
    st.markdown("""
    ---
    
    ## 🔄 Annual Simulation Engine
    
    ### **Step 1: Oil Revenue Calculation**
    """)
    
    st.markdown('<div class="equation">Oil Revenue<sub>t</sub> = Oil Price × (1 + Oil Price Shock) × Oil Revenue per Dollar</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Mechanic**: 
    - Oil price shocks directly impact government revenue
    - ±20% oil price → ±$4.7B revenue impact
    - ±30% oil price → ±$7.7B revenue impact
    
    **Economic Impact**: Direct fiscal shock affecting spending capacity
    """)
    
    st.markdown("""
    ### **Step 2: Non-Oil Revenue with Growth Feedback**
    """)
    
    st.markdown('<div class="equation">Non-Oil Revenue<sub>t</sub> = Non-Oil Revenue<sub>t-1</sub> × (1 + Tax Change) × (1 + Growth Rate)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Dual Effects**:
    1. **Policy Effect**: Tax change (e.g., +10% better collection)
    2. **Economic Effect**: Growth assumption (e.g., +3% expansion)
    
    **Economic Rationale**: Tax revenues are endogenous - they grow with the economy
    """)
    
    st.markdown("""
    ### **Step 3: Dynamic Multiplier System**
    """)
    
    multiplier_data = {
        'Economic Condition': ['Recession', 'Normal', 'Boom', 'High Debt'],
        'Spending Multiplier': [0.8, 0.6, 0.4, 0.3],
        'Tax Multiplier': [0.5, 0.3, 0.2, 0.1],
        'Economic Reason': [
            'Slack resources, low crowding-out',
            'Standard Keynesian multipliers', 
            'Resource constraints, high crowding-out',
            'Confidence effects, high interest rates'
        ]
    }
    multiplier_df = pd.DataFrame(multiplier_data)
    st.dataframe(multiplier_df, use_container_width=True)
    
    st.markdown("""
    **Empirical Basis**: IMF research shows multipliers vary by economic cycle
    """)
    
    st.markdown("""
    ### **Step 4: Debt-Driven Interest Rate Mechanism**
    """)
    
    st.markdown('<div class="equation">Effective Interest Rate = Base Rate + Risk Premium</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Risk Premium Calculation**:
    - Debt/GDP < 30%: Negative premium (fiscal virtue rewarded)
    - Debt/GDP 30-50%: Zero premium (neutral zone)
    - Debt/GDP > 50%: +0.15% per 1% above 50% (rising risk)
    
    **Economic Rationale**: Sovereign bond markets charge higher rates as debt sustainability concerns increase
    """)
    
    st.markdown("""
    ### **Step 5: Debt Service Calculation**
    """)
    
    st.markdown('<div class="equation">Debt Service = Debt × (Effective Interest Rate / 100)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Example**: 
    - $140B debt at 13.5% → $18.9B debt service
    - This is **31.5% of total revenue** - crowding out productive spending
    
    **Fiscal Impact**: Debt service is non-discretionary - must be paid before other spending
    """)
    
    st.markdown("""
    ### **Step 6: Fiscal Impact on GDP**
    """)
    
    st.markdown("""
    <div class="equation">
    Fiscal Impact = [Spending Change × (Spending - Debt Service) × Spending Multiplier +<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Tax Change × Non-Oil Revenue × Tax Multiplier] ÷ GDP
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **Decomposition**:
    1. **Spending Impact**: Only discretionary spending (total spending - debt service) stimulates economy
    2. **Tax Impact**: Tax cuts stimulate, tax hikes contract (smaller multiplier than spending)
    
    **Example Calculation**:
    - Spending increase: +10% on $53.1B → $5.31B × 0.6 multiplier = $3.19B GDP impact
    - Tax cut: -5% on $39.66B → -$1.98B × 0.3 multiplier = -$0.59B GDP impact  
    - Net fiscal impact = ($3.19B - $0.59B) / $450B = **0.58% of GDP**
    """)
    
    st.markdown("""
    ### **Step 7: Crowding-Out Effect**
    """)
    
    st.markdown('<div class="equation">Crowding Out Effect = max(0, (Debt Service - Baseline Service) ÷ GDP) × 100</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Mechanic**: 
    - Rising debt service reduces funds for productive investment
    - Higher interest rates discourage private investment
    - Creates a **drag on economic growth**
    
    **Example**: 
    - Debt service increases from $16.8B to $18.9B
    - Crowding out = ($18.9B - $16.8B) / $450B = **0.47% GDP drag**
    """)
    
    st.markdown("""
    ### **Step 8: Final Growth Calculation**
    """)
    
    st.markdown('<div class="equation">Effective Growth = Baseline Growth + Fiscal Impact - Crowding Out Effect</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Complete Growth Decomposition**:
    ```
    Effective Growth = 3.0%   [Baseline]
                     + 0.58%  [Fiscal stimulus]  
                     - 0.47%  [Crowding out]
                     = 3.11%  [Final growth]
    ```
    """)
    
    st.markdown("""
    ### **Step 9: Update Economic Variables**
    """)
    
    st.markdown("""
    <div class="equation">
    GDP<sub>t</sub> = GDP<sub>t-1</sub> × (1 + Effective Growth ÷ 100)<br>
    Deficit<sub>t</sub> = Spending + Debt Service - Total Revenue<br>
    Debt<sub>t</sub> = Debt<sub>t-1</sub> + Deficit<sub>t</sub><br>
    Debt/GDP<sub>t</sub> = (Debt<sub>t</sub> ÷ GDP<sub>t</sub>) × 100
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **Stock-Flow Consistency**: 
    - GDP grows based on effective growth rate
    - Deficit = Spending + Interest - Revenue
    - Debt accumulates year-to-year
    - Debt/GDP ratio changes based on both numerator (debt) and denominator (GDP)
    """)
    
    st.markdown("""
    ---
    
    ## 🎯 Key Economic Mechanisms
    
    ### **1. Oil Dependency Feedback Loop**
    ```
    Oil Price Shock → Revenue Change → Fiscal Space Change → Spending Capacity → Economic Growth
    ```
    
    **Vulnerability**: -30% oil price shock → -$7.7B revenue → Either cut spending or increase deficit → Both reduce growth
    
    ### **2. Debt-Growth Vicious/Virtuous Cycle**
    
    **Vicious Cycle**:
    ```
    Higher Debt → Higher Interest Rates → More Debt Service → Less Productive Spending → Lower Growth → Higher Debt/GDP
    ```
    
    **Virtuous Cycle**:
    ```
    Lower Debt → Lower Interest Rates → Less Debt Service → More Productive Spending → Higher Growth → Lower Debt/GDP
    ```
    """)
    
    st.markdown("""
    ### **3. Critical Thresholds & Non-Linearities**
    """)
    
    threshold_data = {
        'Indicator': ['Debt/GDP Ratio', 'Oil Revenue Share', 'Debt Service/Revenue'],
        'Safe Zone': ['< 30%', '< 30%', '< 15%'],
        'Caution Zone': ['30-50%', '30-60%', '15-30%'],
        'Danger Zone': ['> 50%', '> 60%', '> 30%']
    }
    threshold_df = pd.DataFrame(threshold_data)
    st.dataframe(threshold_df, use_container_width=True)
    
    st.markdown("""
    ---
    
    ## 📈 Policy Transmission Channels
    
    ### **Channel 1: Direct Fiscal Stimulus**
    ```
    Government Spending → Aggregate Demand → GDP Growth
    ```
    - Most effective in recessions
    - Weakened by import leakage in open economies
    
    ### **Channel 2: Tax Policy Incentives**
    ```
    Tax Cuts → Disposable Income → Consumption → GDP Growth
    ```
    - Smaller impact than direct spending
    - Depends on marginal propensity to consume
    
    ### **Channel 3: Debt Sustainability**
    ```
    Debt Levels → Investor Confidence → Interest Rates → Investment → Growth
    ```
    - Non-linear: small effects until thresholds, then rapid deterioration
    
    ### **Channel 4: Oil Revenue Volatility**
    ```
    Oil Prices → Fiscal Revenues → Spending Consistency → Economic Stability
    ```
    - Pro-cyclicality risk: spend in booms, austerity in busts
    """)
    
    st.markdown("""
    ---
    
    ## ⚠️ Model Limitations & Real-World Complexities
    
    ### **Simplifications in Current Model**:
    1. **Constant Elasticities**: Multipliers and risk premiums are simplified
    2. **No Monetary Policy**: Central bank reaction function not included  
    3. **No Exchange Rates**: Currency valuation effects not modeled
    4. **No Distributional Effects**: Aggregate analysis only
    5. **No Time Lags**: Immediate effects rather than delayed impacts
    
    ### **Real-World Additions Needed**:
    1. **Sectoral Detail**: Oil vs. agriculture vs. services
    2. **Regional Distribution**: Federal vs. state dynamics
    3. **External Sector**: Current account, capital flows
    4. **Institutional Quality**: Corruption, efficiency factors
    5. **Demographics**: Population growth, youth bulge effects
    """)

# Policy Insights
st.subheader("💡 Nigeria-Specific Policy Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛢️ Oil Dependency Analysis")
    
    final_oil_share = (results_df['Oil_Revenue'].iloc[-1] / results_df['Total_Revenue'].iloc[-1]) * 100
    initial_oil_share = (results_df['Oil_Revenue'].iloc[0] / results_df['Total_Revenue'].iloc[0]) * 100
    
    if final_oil_share > 60:
        st.error(f"**High Oil Dependency**: {final_oil_share:.1f}% of revenue from oil. Vulnerable to price shocks.")
    elif final_oil_share < 30:
        st.success(f"**Diversified Revenue**: {final_oil_share:.1f}% of revenue from oil. More resilient economy.")
    else:
        st.warning(f"**Moderate Oil Dependency**: {final_oil_share:.1f}% of revenue from oil.")
    
    # Debt sustainability
    if results_df['Debt_to_GDP'].iloc[-1] > 70:
        st.error("**Debt Sustainability Concern**: Debt levels may trigger IMF program requirements")
    elif results_df['Debt_to_GDP'].iloc[-1] > 50:
        st.warning("**Moderate Debt Risk**: Approaching prudent debt limits")

with col2:
    st.markdown("### 📊 Multiplier Analysis")
    
    current_condition = results_df['Economic_Condition'].iloc[-1]
    spending_mult, tax_mult = NigeriaFiscalModel().get_multipliers(current_condition)
    
    st.info(f"**Current Economic Condition**: {current_condition.replace('_', ' ').title()}")
    st.metric("Spending Multiplier", f"{spending_mult:.2f}")
    st.metric("Tax Multiplier", f"{tax_mult:.2f}")
    
    if current_condition == "recession":
        st.success("**Recommendation**: Counter-cyclical spending has high impact now")
    elif current_condition == "high_debt":
        st.warning("**Recommendation**: Fiscal consolidation needed to restore confidence")

# Economic Value Creation Summary
st.subheader("💰 Economic Value Creation Summary")

# Calculate comprehensive economic impact
initial_gdp = results_df['GDP'].iloc[0]
final_gdp = results_df['GDP'].iloc[-1]
cumulative_gdp = results_df['GDP'].sum()
baseline_cumulative = sum([initial_gdp * (1 + baseline_growth/100)**i for i in range(5)])

total_value_added = cumulative_gdp - baseline_cumulative
value_per_capita = total_value_added / 200  # Nigeria population ~200M

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Economic Value Added", f"${total_value_added:+,.0f}B", 
              "5-year cumulative vs baseline")

with col2:
    st.metric("Per Capita Impact", f"${value_per_capita:+,.0f}", 
              "Per Nigerian citizen")

with col3:
    final_debt_service_ratio = (results_df['Debt_Service'].iloc[-1] / results_df['Total_Revenue'].iloc[-1]) * 100
    st.metric("Debt Service Burden", f"{final_debt_service_ratio:.1f}%", 
              "of revenue")

with col4:
    fiscal_space_ratio = (results_df['Fiscal_Space'].iloc[-1] / results_df['Total_Revenue'].iloc[-1]) * 100
    st.metric("Available Fiscal Space", f"{fiscal_space_ratio:.1f}%", 
              "for new initiatives")

# Enhanced data table
with st.expander("📋 Detailed Projection Data"):
    display_df = results_df.copy()
    numeric_cols = ['GDP', 'Oil_Revenue', 'Non_Oil_Revenue', 'Total_Revenue', 
                   'Spending', 'Debt_Service', 'Deficit', 'Debt']
    
    for col in numeric_cols:
        display_df[col] = display_df[col].round(1)
    
    display_df['Debt_to_GDP'] = display_df['Debt_to_GDP'].round(1)
    display_df['GDP_Growth'] = display_df['GDP_Growth'].round(1)
    display_df['Interest_Rate'] = display_df['Interest_Rate'].round(1)
    display_df['Oil_Price'] = display_df['Oil_Price'].round(1)
    display_df['Crowding_Out_Effect'] = display_df['Crowding_Out_Effect'].round(2)
    
    st.dataframe(display_df)

# Methodology
with st.expander("🔬 Enhanced Methodology"):
    st.markdown("""
    **Nigeria-Specific Model Enhancements:**
    
    🛢️ **Oil Revenue Module:**
    - Explicit modeling of oil revenue based on price and production
    - Oil price shocks directly impact fiscal space
    - Tracks revenue diversification away from oil
    
    📈 **Debt-Growth Feedback Loop:**
    - Higher debt → Higher risk premium → Higher interest rates
    - Debt service costs crowd out productive spending
    - Non-linear effects: severe crowding out at high debt levels
    
    🔄 **Time-Varying Multipliers:**
    - **Recession**: Higher multipliers (0.8 spending, 0.5 tax)
    - **Boom**: Lower multipliers (0.4 spending, 0.2 tax)  
    - **High Debt**: Very low multipliers due to confidence effects
    
    ⚠️ **Crowding-Out Effects:**
    - Rising debt service reduces funds for productive investment
    - Higher interest rates discourage private investment
    - Model captures both direct and indirect crowding out
    
    💰 **Economic Value Measurement:**
    - Tracks nominal GDP growth and policy impact in absolute terms
    - Calculates cumulative economic value added vs baseline
    - Estimates per-capita impact on citizens
    
    **Key Policy Variables:**
    - Debt sustainability thresholds (50%, 70% of GDP)
    - Oil revenue dependency (target < 30%)
    - Interest rate risk premium dynamics
    - Fiscal space for development spending
    """)

st.markdown("---")
st.markdown("*Nigeria Fiscal Simulator v2.0 - Complete with Technical Mechanics Documentation*")
st.markdown("*Ahmad Ilu | @Iluahmad_*")
st.markdown("---")
st.markdown(" Toy Model © ® ™ 2025. All rights reserved. ")