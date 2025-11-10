# nigeria_fiscal_monetary_simulator_enhanced.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ======================
# STREAMLIT PAGE CONFIG
# ======================

st.set_page_config(
    page_title="Nigeria Fiscal-Monetary Simulator",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for custom parameters
if 'use_custom_params' not in st.session_state:
    st.session_state.use_custom_params = False
if 'custom_params' not in st.session_state:
    st.session_state.custom_params = {}

# ======================
# CUSTOM PARAMETERS INTERFACE
# ======================

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
        border-radius: 5px;
        white-space: pre-wrap;
    }
    .mechanic-box {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .step-header {
        color: #008751;
        font-weight: bold;
        margin-top: 20px;
        border-bottom: 2px solid #008751;
        padding-bottom: 5px;
    }
    .reform-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .distribution-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .impulse-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .equation-box {
        background-color: #f8f9fa;
        border-left: 4px solid #008751;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: "Courier New", monospace;
    }
    .technical-section {
        background-color: #e8f4fd;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 4px solid #1f77b4;
    }
    .parameter-table {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .custom-params-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .param-group {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #008751;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Nigeria Integrated Fiscal-Monetary Policy Simulator</div>', unsafe_allow_html=True)

# Custom Parameters Expander
with st.expander("⚙️ Custom Model Parameters (Click to customize initial conditions)", expanded=False):
    
    st.markdown("""
    **Customize the model's initial conditions and parameters. Leave as default for Nigeria 2024 scenario.**
    """)
    
    use_custom = st.checkbox("Use Custom Parameters", value=st.session_state.use_custom_params,
                           help="Enable to override default Nigeria-specific parameters")
    
    if use_custom:
        st.session_state.use_custom_params = True
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Macroeconomic Base")
            st.session_state.custom_params['initial_gdp'] = st.number_input(
                "Initial GDP (Billions USD)", 
                min_value=10.0, max_value=5000.0, value=450.0, step=10.0,
                help="Initial size of the economy"
            )
            st.session_state.custom_params['initial_debt'] = st.number_input(
                "Initial Debt (Billions USD)", 
                min_value=0.0, max_value=3000.0, value=140.0, step=10.0,
                help="Total government debt"
            )
            st.session_state.custom_params['initial_deficit'] = st.number_input(
                "Initial Deficit (Billions USD)", 
                min_value=0.0, max_value=500.0, value=12.0, step=1.0,
                help="Annual fiscal deficit"
            )
            
        with col2:
            st.subheader("🛢️ Oil & Revenue Structure")
            st.session_state.custom_params['oil_revenue'] = st.number_input(
                "Oil Revenue (Billions USD)", 
                min_value=0.0, max_value=500.0, value=25.0, step=1.0,
                help="Annual oil revenue"
            )
            st.session_state.custom_params['non_oil_revenue'] = st.number_input(
                "Non-Oil Revenue (Billions USD)", 
                min_value=0.0, max_value=500.0, value=35.0, step=1.0,
                help="Annual non-oil revenue"
            )
            st.session_state.custom_params['oil_price'] = st.number_input(
                "Oil Price (USD/barrel)", 
                min_value=10.0, max_value=200.0, value=75.0, step=5.0,
                help="Current oil price"
            )
            st.session_state.custom_params['oil_revenue_per_dollar'] = st.number_input(
                "Oil Revenue Sensitivity", 
                min_value=0.1, max_value=1.0, value=0.33, step=0.01,
                help="Revenue change per $1 oil price change ($B)"
            )
            
        with col3:
            st.subheader("🏦 Monetary & External")
            st.session_state.custom_params['policy_rate'] = st.number_input(
                "Policy Rate (%)", 
                min_value=0.0, max_value=50.0, value=18.75, step=0.25,
                help="Central bank policy rate"
            )
            st.session_state.custom_params['inflation_target'] = st.number_input(
                "Inflation Target (%)", 
                min_value=1.0, max_value=20.0, value=9.0, step=0.5,
                help="Central bank inflation target"
            )
            st.session_state.custom_params['current_inflation'] = st.number_input(
                "Current Inflation (%)", 
                min_value=0.0, max_value=100.0, value=28.0, step=1.0,
                help="Current inflation rate"
            )
            st.session_state.custom_params['exchange_rate'] = st.number_input(
                "Exchange Rate (NGN/USD)", 
                min_value=1.0, max_value=3000.0, value=1500.0, step=50.0,
                help="Current exchange rate"
            )
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.subheader("📈 Structural Parameters")
            st.session_state.custom_params['poverty_rate'] = st.number_input(
                "Poverty Rate (%)", 
                min_value=0.0, max_value=100.0, value=40.0, step=1.0,
                help="Population below poverty line"
            )
            st.session_state.custom_params['unemployment_rate'] = st.number_input(
                "Unemployment Rate (%)", 
                min_value=0.0, max_value=50.0, value=4.0, step=0.5,
                help="Official unemployment rate"
            )
            st.session_state.custom_params['informal_sector_share'] = st.number_input(
                "Informal Sector Share (%)", 
                min_value=0.0, max_value=100.0, value=55.0, step=1.0,
                help="Size of informal economy"
            )
            
        with col5:
            st.subheader("📊 Distributional Parameters")
            st.session_state.custom_params['gini_coefficient'] = st.number_input(
                "Gini Coefficient", 
                min_value=20.0, max_value=70.0, value=35.1, step=0.1,
                help="Income inequality (0=perfect equality, 100=perfect inequality)"
            )
            st.session_state.custom_params['poor_consumption_share'] = st.number_input(
                "Bottom 40% Consumption Share (%)", 
                min_value=5.0, max_value=50.0, value=15.0, step=0.5,
                help="Consumption share of bottom 40% population"
            )
            st.session_state.custom_params['rich_consumption_share'] = st.number_input(
                "Top 20% Consumption Share (%)", 
                min_value=20.0, max_value=80.0, value=55.0, step=0.5,
                help="Consumption share of top 20% population"
            )
            
        with col6:
            st.subheader("🌍 Trade & Elasticities")
            st.session_state.custom_params['imports_gdp_ratio'] = st.number_input(
                "Imports/GDP Ratio", 
                min_value=0.01, max_value=1.0, value=0.14, step=0.01,
                help="Imports as percentage of GDP"
            )
            st.session_state.custom_params['exports_gdp_ratio'] = st.number_input(
                "Exports/GDP Ratio", 
                min_value=0.01, max_value=1.0, value=0.11, step=0.01,
                help="Exports as percentage of GDP"
            )
            st.session_state.custom_params['import_elasticity'] = st.number_input(
                "Import Elasticity", 
                min_value=0.1, max_value=2.0, value=0.8, step=0.1,
                help="Responsiveness of imports to income changes"
            )
            st.session_state.custom_params['export_elasticity'] = st.number_input(
                "Export Elasticity", 
                min_value=0.1, max_value=2.0, value=0.6, step=0.1,
                help="Responsiveness of exports to exchange rate changes"
            )
        
        # Advanced parameters
        with st.expander("🔧 Advanced Parameters"):
            col7, col8 = st.columns(2)
            
            with col7:
                st.session_state.custom_params['automatic_stabilizers'] = st.number_input(
                    "Automatic Stabilizers Sensitivity", 
                    min_value=0.0, max_value=1.0, value=0.2, step=0.05,
                    help="Sensitivity of fiscal balance to output gap"
                )
                st.session_state.custom_params['cyclically_adjusted_balance'] = st.number_input(
                    "Structural Balance (% of GDP)", 
                    min_value=-20.0, max_value=5.0, value=-8.0, step=0.5,
                    help="Cyclically-adjusted fiscal balance"
                )
                
            with col8:
                st.session_state.custom_params['foreign_reserves'] = st.number_input(
                    "Foreign Reserves (Billions USD)", 
                    min_value=0.0, max_value=500.0, value=33.0, step=1.0,
                    help="Central bank foreign reserves"
                )
                st.session_state.custom_params['oil_production'] = st.number_input(
                    "Oil Production (Million barrels/day)", 
                    min_value=0.1, max_value=10.0, value=1.4, step=0.1,
                    help="Daily oil production"
                )
        
        # Display summary
        st.markdown("---")
        st.subheader("📋 Custom Parameters Summary")
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            debt_to_gdp = (st.session_state.custom_params['initial_debt'] / st.session_state.custom_params['initial_gdp']) * 100
            deficit_to_gdp = (st.session_state.custom_params['initial_deficit'] / st.session_state.custom_params['initial_gdp']) * 100
            oil_dependency = (st.session_state.custom_params['oil_revenue'] / 
                            (st.session_state.custom_params['oil_revenue'] + st.session_state.custom_params['non_oil_revenue'])) * 100
            
            st.metric("Debt/GDP Ratio", f"{debt_to_gdp:.1f}%")
            st.metric("Deficit/GDP Ratio", f"{deficit_to_gdp:.1f}%")
            st.metric("Oil Dependency", f"{oil_dependency:.1f}%")
            
        with summary_col2:
            total_revenue = st.session_state.custom_params['oil_revenue'] + st.session_state.custom_params['non_oil_revenue']
            total_spending = total_revenue + st.session_state.custom_params['initial_deficit']
            reserve_cover = (st.session_state.custom_params['foreign_reserves'] / 
                           (st.session_state.custom_params['initial_gdp'] * st.session_state.custom_params['imports_gdp_ratio'] / 12))
            
            st.metric("Total Revenue", f"${total_revenue:.1f}B")
            st.metric("Total Spending", f"${total_spending:.1f}B")
            st.metric("Import Cover", f"{reserve_cover:.1f} months")
            
        with summary_col3:
            real_interest_rate = st.session_state.custom_params['policy_rate'] - st.session_state.custom_params['current_inflation']
            inequality_ratio = st.session_state.custom_params['rich_consumption_share'] / st.session_state.custom_params['poor_consumption_share']
            
            st.metric("Real Interest Rate", f"{real_interest_rate:.1f}%")
            st.metric("Inequality Ratio", f"{inequality_ratio:.1f}x")
            st.metric("Informal Economy", f"{st.session_state.custom_params['informal_sector_share']:.1f}%")
            
    else:
        st.session_state.use_custom_params = False
        st.info("Using default Nigeria 2024 parameters. Check the box above to customize.")

# ======================
# ENHANCED FISCAL-MONETARY MODEL FOR NIGERIA
# ======================
class NigeriaFiscalMonetaryModel:
    def __init__(self, custom_params=None):
        if custom_params and st.session_state.use_custom_params:
            # Use custom parameters
            self.initial_gdp = custom_params.get('initial_gdp', 450)
            self.initial_debt = custom_params.get('initial_debt', 140)
            self.initial_deficit = custom_params.get('initial_deficit', 12)
            
            self.oil_revenue = custom_params.get('oil_revenue', 25)
            self.non_oil_revenue = custom_params.get('non_oil_revenue', 35)
            self.total_revenue = self.oil_revenue + self.non_oil_revenue
            
            self.total_spending = self.total_revenue + self.initial_deficit
            
            self.oil_price = custom_params.get('oil_price', 75)
            self.oil_production = custom_params.get('oil_production', 1.4)
            self.oil_revenue_per_dollar = custom_params.get('oil_revenue_per_dollar', 0.33)
            
            self.policy_rate = custom_params.get('policy_rate', 18.75)
            self.inflation_target = custom_params.get('inflation_target', 9.0)
            self.current_inflation = custom_params.get('current_inflation', 28.0)
            self.exchange_rate = custom_params.get('exchange_rate', 1500)
            self.foreign_reserves = custom_params.get('foreign_reserves', 33)
            
            self.imports_gdp_ratio = custom_params.get('imports_gdp_ratio', 0.14)
            self.exports_gdp_ratio = custom_params.get('exports_gdp_ratio', 0.11)
            self.import_elasticity = custom_params.get('import_elasticity', 0.8)
            self.export_elasticity = custom_params.get('export_elasticity', 0.6)
            
            self.poverty_rate = custom_params.get('poverty_rate', 40.0)
            self.unemployment_rate = custom_params.get('unemployment_rate', 4.0)
            self.informal_sector_share = custom_params.get('informal_sector_share', 55.0)
            
            self.income_inequality_gini = custom_params.get('gini_coefficient', 35.1)
            self.poor_consumption_share = custom_params.get('poor_consumption_share', 15.0)
            self.rich_consumption_share = custom_params.get('rich_consumption_share', 55.0)
            
            self.cyclically_adjusted_balance = custom_params.get('cyclically_adjusted_balance', -8.0)
            self.automatic_stabilizers = custom_params.get('automatic_stabilizers', 0.2)
            
        else:
            # Use default Nigeria parameters
            self.initial_gdp = 450
            self.initial_debt = 140
            self.initial_deficit = 12
            
            self.oil_revenue = 25
            self.non_oil_revenue = 35
            self.total_revenue = self.oil_revenue + self.non_oil_revenue
            
            self.total_spending = self.total_revenue + self.initial_deficit
            
            self.oil_price = 75
            self.oil_production = 1.4
            self.oil_revenue_per_dollar = 0.33
            
            self.policy_rate = 18.75
            self.inflation_target = 9.0
            self.current_inflation = 28.0
            self.exchange_rate = 1500
            self.foreign_reserves = 33
            
            self.imports_gdp_ratio = 0.14
            self.exports_gdp_ratio = 0.11
            self.import_elasticity = 0.8
            self.export_elasticity = 0.6
            
            self.poverty_rate = 40.0
            self.unemployment_rate = 4.0
            self.informal_sector_share = 55.0
            
            self.income_inequality_gini = 35.1
            self.poor_consumption_share = 15.0
            self.rich_consumption_share = 55.0
            
            self.cyclically_adjusted_balance = -8.0
            self.automatic_stabilizers = 0.2

    def calculate_impact(self, tax_change, spending_change, growth_assumption, 
                        oil_price_shock, monetary_response="automatic", 
                        structural_reform=False, progressive_tax=False,
                        pro_poor_spending=False, years=5):
        """
        Consolidated model with fiscal, monetary, structural, and distributional components
        """
        
        # Initialize results
        results = []
        gdp = self.initial_gdp
        debt = self.initial_debt
        non_oil_revenue = self.non_oil_revenue
        oil_revenue = self.oil_revenue
        spending = self.total_spending
        
        # Monetary variables
        policy_rate = self.policy_rate
        inflation = self.current_inflation
        exchange_rate = self.exchange_rate
        foreign_reserves = self.foreign_reserves
        
        # Structural variables
        poverty_rate = self.poverty_rate
        unemployment_rate = self.unemployment_rate
        informal_share = self.informal_sector_share
        
        # Fiscal incidence variables
        gini_coefficient = self.income_inequality_gini
        poor_share = self.poor_consumption_share
        rich_share = self.rich_consumption_share
        
        # Fiscal impulse variables
        output_gap = 0.0  # Initial output gap
        fiscal_impulse = 0.0
        structural_balance = self.cyclically_adjusted_balance
        
        # Trade variables
        imports = gdp * self.imports_gdp_ratio
        exports = gdp * self.exports_gdp_ratio
        current_account = exports - imports
        
        # Dynamic multipliers
        economic_condition = self.assess_economic_condition(gdp, debt/gdp, inflation)
        spending_multiplier, tax_multiplier = self.get_multipliers(economic_condition)
        
        for year in range(years):
            # ======================
            # STRUCTURAL REFORM EFFECTS
            # ======================
            reform_boost = 0
            if structural_reform:
                reform_boost = self.calculate_reform_boost(year, poverty_rate, informal_share)
                effective_tax_change = tax_change + reform_boost * 2
                poverty_rate = max(20, poverty_rate - reform_boost * 3)
                informal_share = max(30, informal_share - reform_boost * 2)
            else:
                effective_tax_change = tax_change
            
            # ======================
            # FISCAL INCIDENCE EFFECTS
            # ======================
            distribution_impact, new_gini, new_poor_share, new_rich_share = self.calculate_fiscal_incidence(
                tax_change, spending_change, progressive_tax, pro_poor_spending, gini_coefficient,
                poor_share, rich_share, economic_condition
            )
            
            # ======================
            # FISCAL IMPULSE CALCULATION
            # ======================
            fiscal_impulse, structural_balance, discretionary_stimulus = self.calculate_fiscal_impulse(
                spending_change, tax_change, output_gap, structural_balance, economic_condition
            )
            
            # ======================
            # OIL REVENUE CALCULATION
            # ======================
            current_oil_price = self.oil_price * (1 + oil_price_shock/100)
            oil_revenue = current_oil_price * self.oil_revenue_per_dollar
            
            # ======================
            # NON-OIL REVENUE (with growth and reform feedback)
            # ======================
            non_oil_revenue = non_oil_revenue * (1 + effective_tax_change/100) * (1 + growth_assumption/100)
            total_revenue = oil_revenue + non_oil_revenue
            
            # ======================
            # SPENDING (with reform efficiency gains)
            # ======================
            spending_efficiency = 1.0
            if structural_reform:
                spending_efficiency = 1.1
            spending = spending * (1 + spending_change/100) * spending_efficiency
            
            # ======================
            # DEBT-DRIVEN INTEREST RATE
            # ======================
            debt_to_gdp = (debt / gdp) * 100
            risk_premium = self.calculate_risk_premium(debt_to_gdp, foreign_reserves, structural_reform)
            effective_interest_rate = policy_rate + risk_premium
            
            # ======================
            # DEBT SERVICE COSTS
            # ======================
            debt_service = debt * (effective_interest_rate/100)
            
            # ======================
            # FISCAL IMPACT ON GDP
            # ======================
            fiscal_impact = (spending_change * (spending - debt_service) * spending_multiplier + 
                           effective_tax_change * non_oil_revenue * tax_multiplier) / gdp
            
            # ======================
            # CROWDING-OUT EFFECT
            # ======================
            crowding_out_effect = max(0, (debt_service - (debt_service * (debt/gdp))) / gdp) * 100
            
            # ======================
            # MONETARY POLICY REACTION
            # ======================
            monetary_impact, new_policy_rate, new_inflation = self.monetary_policy_reaction(
                fiscal_impact, inflation, economic_condition, monetary_response, structural_reform
            )
            
            # ======================
            # EXCHANGE RATE & TRADE EFFECTS
            # ======================
            exchange_rate_impact, new_exchange_rate, new_reserves, trade_balance_impact = self.exchange_rate_dynamics(
                fiscal_impact, current_account, oil_revenue, foreign_reserves, policy_rate, structural_reform
            )
            
            # ======================
            # NET TRADE EFFECT
            # ======================
            import_effect = - (growth_assumption/100) * self.import_elasticity * (imports/gdp) * 100
            export_effect = max(0, (new_exchange_rate - exchange_rate)/exchange_rate) * self.export_elasticity * (exports/gdp) * 100
            net_trade_effect = import_effect + export_effect
            
            # ======================
            # STRUCTURAL REFORM GROWTH BOOST
            # ======================
            structural_impact = reform_boost
            
            # ======================
            # DISTRIBUTIONAL GROWTH EFFECT (reduced inequality can boost growth)
            # ======================
            equality_boost = distribution_impact * 0.1  # Reduced inequality can boost growth
            
            # ======================
            # FINAL GROWTH CALCULATION
            # ======================
            effective_growth = (growth_assumption + fiscal_impact + monetary_impact + 
                              exchange_rate_impact + net_trade_effect + structural_impact + 
                              equality_boost - crowding_out_effect)
            
            # ======================
            # UPDATE OUTPUT GAP
            # ======================
            output_gap = (effective_growth - growth_assumption) * 0.8  # Simple output gap calculation
            
            # ======================
            # UNEMPLOYMENT DYNAMICS (Okun's Law)
            # ======================
            unemployment_change = -0.5 * (effective_growth - growth_assumption)
            new_unemployment = max(2.0, unemployment_rate + unemployment_change)
            
            # ======================
            # UPDATE ECONOMIC VARIABLES
            # ======================
            gdp = gdp * (1 + effective_growth/100)
            deficit = spending + debt_service - total_revenue
            debt = debt + deficit
            debt_to_gdp = (debt / gdp) * 100
            
            # Update trade variables
            imports = gdp * self.imports_gdp_ratio * (1 + effective_growth/100 * self.import_elasticity)
            exports = gdp * self.exports_gdp_ratio * (1 + export_effect/100)
            current_account = exports - imports
            
            # Update monetary variables
            policy_rate = new_policy_rate
            inflation = new_inflation
            exchange_rate = new_exchange_rate
            foreign_reserves = new_reserves
            
            # Update structural variables
            unemployment_rate = new_unemployment
            
            # Update distributional variables
            gini_coefficient = new_gini
            poor_share = new_poor_share
            rich_share = new_rich_share
            
            # Update economic condition
            economic_condition = self.assess_economic_condition(gdp, debt_to_gdp, inflation)
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
                'Policy_Rate': policy_rate,
                'Inflation': inflation,
                'Exchange_Rate': exchange_rate,
                'Foreign_Reserves': foreign_reserves,
                'Imports': imports,
                'Exports': exports,
                'Current_Account': current_account,
                'Oil_Price': current_oil_price,
                'Economic_Condition': economic_condition,
                'Crowding_Out_Effect': crowding_out_effect,
                'Monetary_Impact': monetary_impact,
                'Trade_Impact': net_trade_effect,
                'Fiscal_Impact': fiscal_impact,
                'Structural_Impact': structural_impact,
                'Poverty_Rate': poverty_rate,
                'Unemployment_Rate': unemployment_rate,
                'Informal_Sector_Share': informal_share,
                'Reform_Boost': reform_boost,
                # NEW FISCAL INCIDENCE VARIABLES
                'Gini_Coefficient': gini_coefficient,
                'Poor_Consumption_Share': poor_share,
                'Rich_Consumption_Share': rich_share,
                'Distribution_Impact': distribution_impact,
                'Equality_Boost': equality_boost,
                # NEW FISCAL IMPULSE VARIABLES
                'Fiscal_Impulse': fiscal_impulse,
                'Structural_Balance': structural_balance,
                'Output_Gap': output_gap,
                'Discretionary_Stimulus': discretionary_stimulus
            })
            
        return pd.DataFrame(results)
    
    def calculate_fiscal_incidence(self, tax_change, spending_change, progressive_tax, 
                                 pro_poor_spending, gini, poor_share, rich_share, economic_condition):
        """
        Calculate distributional impact of fiscal policy
        """
        # Base distributional impact
        distribution_impact = 0
        
        # Tax progressivity effect
        if progressive_tax and tax_change > 0:
            # Progressive taxes reduce inequality
            distribution_impact -= 0.5 * (tax_change / 10)  # Negative = more equal
        elif not progressive_tax and tax_change > 0:
            # Regressive taxes increase inequality
            distribution_impact += 0.3 * (tax_change / 10)  # Positive = less equal
        
        # Spending progressivity effect
        if pro_poor_spending and spending_change > 0:
            # Pro-poor spending reduces inequality
            distribution_impact -= 0.8 * (spending_change / 10)
        elif not pro_poor_spending and spending_change > 0:
            # General spending has modest equalizing effect
            distribution_impact -= 0.2 * (spending_change / 10)
        
        # Update Gini coefficient (lower = more equal)
        new_gini = max(20, min(60, gini + distribution_impact * 2))
        
        # Update consumption shares
        if distribution_impact < 0:  # More equal distribution
            equality_gain = abs(distribution_impact) * 0.5
            new_poor_share = min(30, poor_share + equality_gain)
            new_rich_share = max(40, rich_share - equality_gain)
        else:  # Less equal distribution
            inequality_gain = distribution_impact * 0.3
            new_poor_share = max(10, poor_share - inequality_gain)
            new_rich_share = min(70, rich_share + inequality_gain)
        
        return distribution_impact, new_gini, new_poor_share, new_rich_share
    
    def calculate_fiscal_impulse(self, spending_change, tax_change, output_gap, 
                               structural_balance, economic_condition):
        """
        Calculate fiscal impulse - measure of discretionary fiscal stimulus
        """
        # Discretionary fiscal stimulus
        discretionary_stimulus = spending_change - (tax_change * 0.7)  # Spending has larger impact
        
        # Cyclical component (automatic stabilizers)
        cyclical_component = -output_gap * self.automatic_stabilizers
        
        # Fiscal impulse (change in structural balance)
        if economic_condition == "recession":
            # Counter-cyclical impulse in recessions
            fiscal_impulse = max(-5, min(5, discretionary_stimulus / 5 + cyclical_component))
        elif economic_condition == "boom":
            # Pro-cyclical restraint in booms
            fiscal_impulse = max(-5, min(5, discretionary_stimulus / 8 + cyclical_component))
        else:
            fiscal_impulse = max(-5, min(5, discretionary_stimulus / 6 + cyclical_component))
        
        # Update structural balance
        new_structural_balance = structural_balance - fiscal_impulse
        
        return fiscal_impulse, new_structural_balance, discretionary_stimulus
    
    def calculate_reform_boost(self, year, poverty_rate, informal_share):
        """Calculate growth boost from structural reforms"""
        base_boost = 0.2
        time_multiplier = min(2.0, 1 + year * 0.3)
        poverty_effect = max(0, (poverty_rate - 20) / 100)
        informal_effect = max(0, (informal_share - 30) / 100)
        
        return base_boost * time_multiplier * (1 + poverty_effect + informal_effect)
    
    def monetary_policy_reaction(self, fiscal_impact, inflation, economic_condition, response_type, structural_reform):
        """Enhanced CBN monetary policy reaction function"""
        inflation_gap = inflation - self.inflation_target
        reform_effect = 0.2 if structural_reform else 0
        
        if response_type == "hawkish":
            if inflation_gap > 5:
                rate_change = min(4.0, inflation_gap * 0.5) - reform_effect
            elif inflation_gap > 2:
                rate_change = inflation_gap * 0.3 - reform_effect
            else:
                rate_change = 0
                
        elif response_type == "dovish":
            if inflation_gap > 10:
                rate_change = inflation_gap * 0.2 - reform_effect
            elif inflation_gap > 5:
                rate_change = inflation_gap * 0.1 - reform_effect
            else:
                rate_change = 0
                
        else:  # automatic
            if inflation_gap > 8:
                rate_change = inflation_gap * 0.4 - reform_effect
            elif inflation_gap > 4:
                rate_change = inflation_gap * 0.25 - reform_effect
            elif economic_condition == "recession" and inflation_gap < 2:
                rate_change = -1.0 - reform_effect
            else:
                rate_change = 0
        
        new_policy_rate = max(12.0, self.policy_rate + rate_change)
        new_inflation = inflation - (rate_change * (0.3 + reform_effect))
        monetary_impact = -rate_change * (0.2 + reform_effect)
        
        return monetary_impact, new_policy_rate, new_inflation
    
    def exchange_rate_dynamics(self, fiscal_impact, current_account, oil_revenue, reserves, policy_rate, structural_reform):
        """Enhanced exchange rate determination"""
        current_account_gap = current_account / (self.initial_gdp * 0.1)
        exchange_pressure = -current_account_gap * 50
        oil_effect = (oil_revenue - self.oil_revenue) / self.oil_revenue * (-100)
        interest_effect = (policy_rate - 6.0) * (-2)
        
        reserve_adequacy = reserves / (self.initial_gdp * 0.1)
        if reserve_adequacy < 3:
            reserve_effect = 50
        elif reserve_adequacy < 6:
            reserve_effect = 20
        else:
            reserve_effect = 0
        
        reform_effect = -20 if structural_reform else 0
        total_pressure = exchange_pressure + oil_effect + interest_effect + reserve_effect + reform_effect
        
        exchange_rate_change = max(-20, min(20, total_pressure / 10))
        new_exchange_rate = self.exchange_rate * (1 + exchange_rate_change/100)
        
        intervention_intensity = min(1.0, abs(exchange_rate_change) / 10)
        reserves_change = -intervention_intensity * reserves * 0.1
        new_reserves = max(5, reserves + reserves_change)
        
        if exchange_rate_change > 5:
            exchange_impact = -1.0
        elif exchange_rate_change < -5:
            exchange_impact = 0.5
        else:
            exchange_impact = 0
        
        if exchange_rate_change > 0:
            trade_balance_effect = 0.3
        else:
            trade_balance_effect = -0.2
        
        return exchange_impact, new_exchange_rate, new_reserves, trade_balance_effect
    
    def calculate_risk_premium(self, debt_to_gdp, reserves, structural_reform):
        """Enhanced risk premium with reforms"""
        debt_premium = 0
        if debt_to_gdp > 50:
            debt_premium = (debt_to_gdp - 50) * 0.15
        
        reserve_premium = 0
        reserve_cover = reserves / (self.initial_gdp * self.imports_gdp_ratio / 12)
        if reserve_cover < 3:
            reserve_premium = 3.0
        elif reserve_cover < 6:
            reserve_premium = 1.5
        
        reform_discount = -2.0 if structural_reform else 0
        return max(0, debt_premium + reserve_premium + reform_discount)
    
    def assess_economic_condition(self, gdp, debt_to_gdp, inflation):
        """Enhanced economic condition assessment"""
        if debt_to_gdp > 60:
            return "high_debt"
        elif inflation > 25:
            return "high_inflation"
        elif gdp < self.initial_gdp * 0.98:
            return "recession"
        elif gdp > self.initial_gdp * 1.05:
            return "boom"
        else:
            return "normal"
    
    def get_multipliers(self, economic_condition):
        """Time-varying multipliers"""
        if economic_condition == "recession":
            return 0.8, 0.5
        elif economic_condition == "boom":
            return 0.4, 0.2
        elif economic_condition == "high_debt":
            return 0.3, 0.1
        elif economic_condition == "high_inflation":
            return 0.2, 0.1
        else:
            return 0.6, 0.3

# ======================
# SIDEBAR CONTROLS
# ======================

st.sidebar.header("🎛️ Consolidated Policy Controls")

# Oil market assumptions
st.sidebar.subheader("🛢️ Oil Market Assumptions")
oil_price_shock = st.sidebar.slider("Oil Price Shock (%)", -50.0, 100.0, 0.0, 5.0)

# Economic assumptions
st.sidebar.subheader("📈 Economic Assumptions")
baseline_growth = st.sidebar.slider("Non-Oil GDP Growth (%)", 0.0, 8.0, 3.0, 0.5)

# Structural Reforms
st.sidebar.subheader("🏗️ Structural Reforms")
structural_reform = st.sidebar.checkbox("Implement Structural Reforms")

# NEW: Fiscal Incidence Controls
st.sidebar.subheader("📊 Fiscal Incidence (Distribution)")
progressive_tax = st.sidebar.checkbox("Progressive Tax System", 
                                    help="Tax burden increases with income")
pro_poor_spending = st.sidebar.checkbox("Pro-Poor Spending", 
                                      help="Target spending to lower-income groups")

# Monetary Policy Stance
st.sidebar.subheader("🏦 Central Bank Reaction")
monetary_response = st.sidebar.selectbox("Monetary Policy Stance", ["automatic", "hawkish", "dovish"])

# Fiscal policy levers
st.sidebar.subheader("🏛️ Fiscal Policy Levers")
tax_change = st.sidebar.slider("Non-Oil Revenue Change (%)", -20.0, 50.0, 0.0, 2.0)
spending_change = st.sidebar.slider("Government Spending Change (%)", -30.0, 40.0, 0.0, 2.0)

# ======================
# MODEL EXECUTION
# ======================

@st.cache_data
def run_enhanced_model(tax_change, spending_change, growth_rate, oil_shock, monetary_stance, 
                      structural_reform, progressive_tax, pro_poor_spending, custom_params=None):
    model = NigeriaFiscalMonetaryModel(custom_params)
    return model.calculate_impact(tax_change, spending_change, growth_rate, oil_shock, 
                                monetary_stance, structural_reform, progressive_tax, pro_poor_spending)

# Run model with custom parameters if enabled
results_df = run_enhanced_model(tax_change, spending_change, baseline_growth, oil_price_shock, 
                              monetary_response, structural_reform, progressive_tax, pro_poor_spending,
                              custom_params=st.session_state.custom_params if st.session_state.use_custom_params else None)

# ======================
# STATUS INDICATOR
# ======================

if st.session_state.use_custom_params:
    st.success("🎯 **Using Custom Parameters** - Model running with user-defined initial conditions")
else:
    st.info(" **Using Nigeria 2024 Default Parameters** - Toggle custom parameters above for other scenarios")

# ======================
# MAIN DASHBOARD
# ======================

# Enhanced Key Metrics Dashboard
st.subheader("📊 Comprehensive Economic Indicators")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    debt_change = results_df['Debt_to_GDP'].iloc[-1] - results_df['Debt_to_GDP'].iloc[0]
    st.metric("Debt-to-GDP", f"{results_df['Debt_to_GDP'].iloc[-1]:.1f}%", f"{debt_change:+.1f}%")

with col2:
    avg_growth = results_df['GDP_Growth'].mean()
    st.metric("Avg Growth", f"{avg_growth:.1f}%", f"{(avg_growth - baseline_growth):+.1f}%")

with col3:
    st.metric("Inflation", f"{results_df['Inflation'].iloc[-1]:.1f}%", 
              f"{(results_df['Inflation'].iloc[-1] - results_df['Inflation'].iloc[0]):+.1f}%")

with col4:
    # NEW: Fiscal Impulse Indicator
    avg_impulse = results_df['Fiscal_Impulse'].mean()
    impulse_color = "normal" if avg_impulse > 0.5 else "inverse" if avg_impulse < -0.5 else "off"
    st.metric("Fiscal Impulse", f"{avg_impulse:+.1f}%", "Avg discretionary stimulus", delta_color=impulse_color)

with col5:
    # NEW: Inequality Indicator
    gini_change = results_df['Gini_Coefficient'].iloc[-1] - results_df['Gini_Coefficient'].iloc[0]
    gini_color = "inverse" if gini_change > 1 else "normal" if gini_change < -1 else "off"
    st.metric("Inequality", f"{results_df['Gini_Coefficient'].iloc[-1]:.1f}", 
              f"{gini_change:+.1f} Gini", delta_color=gini_color)

with col6:
    # Economic Value Creation
    final_gdp = results_df['GDP'].iloc[-1]
    policy_impact_abs = final_gdp - (results_df['GDP'].iloc[0] * (1 + baseline_growth/100)**5)
    delta_color = "normal" if policy_impact_abs > 5 else "inverse" if policy_impact_abs < -5 else "off"
    st.metric("Economy Size", f"${final_gdp:,.0f}B", f"${policy_impact_abs:+,.0f}B", delta_color=delta_color)

# Comprehensive Analysis Tabs
st.subheader("📈 Integrated Economic Analysis")

tabs = st.tabs([
    "Macro Dashboard", "Fiscal Analysis", "Fiscal Stance", "Distribution Impact", 
    "Monetary & Prices", "External Sector", "Structural Indicators", "Technical Mechanics"
])

with tabs[0]:
    st.subheader("🏠 Macroeconomic Dashboard")
    
    fig_macro = make_subplots(
        rows=2, cols=2,
        subplot_titles=('GDP Growth Decomposition', 'Inflation & Interest Rates', 
                       'Fiscal Impulse & Output Gap', 'Debt Dynamics'),
        specs=[[{"secondary_y": False}, {"secondary_y": True}],
               [{"secondary_y": True}, {"secondary_y": False}]]
    )
    
    # GDP Growth Decomposition
    components = ['Fiscal_Impact', 'Monetary_Impact', 'Trade_Impact', 
                 'Structural_Impact', 'Equality_Boost', 'Crowding_Out_Effect']
    colors = ['blue', 'orange', 'green', 'purple', 'pink', 'red']
    
    for i, component in enumerate(components):
        fig_macro.add_trace(
            go.Bar(name=component.replace('_', ' '), x=results_df['Year'], 
                   y=results_df[component], marker_color=colors[i]),
            row=1, col=1
        )
    
    fig_macro.add_trace(
        go.Scatter(name='Actual Growth', x=results_df['Year'], 
                  y=results_df['GDP_Growth'], line=dict(color='black', width=3)),
        row=1, col=1
    )
    
    # Inflation & Interest Rates
    fig_macro.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Inflation'], 
                   name="Inflation", line=dict(color='red', width=3)),
        row=1, col=2, secondary_y=False
    )
    fig_macro.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Policy_Rate'], 
                   name="Policy Rate", line=dict(color='blue', width=3)),
        row=1, col=2, secondary_y=True
    )
    
    # Fiscal Impulse & Output Gap
    fig_macro.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Fiscal_Impulse'], 
               name="Fiscal Impulse", marker_color='orange'),
        row=2, col=1, secondary_y=False
    )
    fig_macro.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Output_Gap'], 
                   name="Output Gap", line=dict(color='green', width=3)),
        row=2, col=1, secondary_y=True
    )
    
    # Debt Dynamics
    fig_macro.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Debt_to_GDP'], 
                   name="Debt/GDP", line=dict(color='orange', width=3)),
        row=2, col=2
    )
    
    fig_macro.update_layout(height=600, barmode='relative', showlegend=True)
    st.plotly_chart(fig_macro, use_container_width=True)

with tabs[1]:
    st.subheader("💰 Fiscal Sustainability Analysis")
    
    fig_fiscal = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Revenue Composition', 'Spending Breakdown', 
                       'Debt Service Burden', 'Fiscal Space'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Revenue composition
    revenue_data = []
    for idx, row in results_df.iterrows():
        revenue_data.extend([
            {'Year': row['Year'], 'Source': 'Oil', 'Revenue': row['Oil_Revenue']},
            {'Year': row['Year'], 'Source': 'Non-Oil', 'Revenue': row['Non_Oil_Revenue']}
        ])
    revenue_df = pd.DataFrame(revenue_data)
    
    for source in ['Oil', 'Non-Oil']:
        source_data = revenue_df[revenue_df['Source'] == source]
        fig_fiscal.add_trace(
            go.Scatter(x=source_data['Year'], y=source_data['Revenue'], 
                       name=source, stackgroup='one'),
            row=1, col=1
        )
    
    # Spending breakdown
    fig_fiscal.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Spending'] - results_df['Debt_Service'], 
               name="Discretionary Spending", marker_color='blue'),
        row=1, col=2
    )
    fig_fiscal.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Debt_Service'], 
               name="Debt Service", marker_color='red'),
        row=1, col=2
    )
    
    # Debt service ratio
    results_df['Debt_Service_Ratio'] = (results_df['Debt_Service'] / results_df['Total_Revenue']) * 100
    fig_fiscal.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Debt_Service_Ratio'], 
                   name="Debt Service/Revenue", line=dict(color='red', width=3)),
        row=2, col=1
    )
    fig_fiscal.add_hline(y=30, line_dash="dash", line_color="red", row=2, col=1)
    
    # Fiscal space
    results_df['Fiscal_Space'] = results_df['Total_Revenue'] - results_df['Debt_Service'] - (results_df['Spending'] * 0.7)
    fig_fiscal.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Fiscal_Space'], 
                   name="Fiscal Space", line=dict(color='green', width=3), fill='tozeroy'),
        row=2, col=2
    )
    
    fig_fiscal.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_fiscal, use_container_width=True)

with tabs[2]:
    st.subheader("🎯 Fiscal Stance & Impulse Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="impulse-box">', unsafe_allow_html=True)
        st.markdown("### 📈 Fiscal Impulse Definition")
        st.markdown("""
        **Fiscal Impulse** measures discretionary fiscal stimulus:
        - **Positive**: Expansionary policy (stimulus)
        - **Negative**: Contractionary policy (austerity)
        - **> 1%**: Strong stimulus
        - **< -1%**: Strong consolidation
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Fiscal impulse insights
        avg_impulse = results_df['Fiscal_Impulse'].mean()
        max_impulse = results_df['Fiscal_Impulse'].max()
        min_impulse = results_df['Fiscal_Impulse'].min()
        
        if avg_impulse > 1.0:
            st.success(f"**Strong Expansionary Stance**: Average impulse of {avg_impulse:.1f}% GDP")
        elif avg_impulse > 0.5:
            st.info(f"**Moderate Expansionary Stance**: Average impulse of {avg_impulse:.1f}% GDP")
        elif avg_impulse < -1.0:
            st.warning(f"**Strong Contractionary Stance**: Average impulse of {avg_impulse:.1f}% GDP")
        elif avg_impulse < -0.5:
            st.info(f"**Moderate Contractionary Stance**: Average impulse of {avg_impulse:.1f}% GDP")
        else:
            st.success(f"**Neutral Stance**: Average impulse of {avg_impulse:.1f}% GDP")
    
    fig_impulse = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Fiscal Impulse Evolution', 'Structural Balance', 
                       'Discretionary vs Automatic', 'Output Gap Response'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": True}]]
    )
    
    # Fiscal impulse evolution
    fig_impulse.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Fiscal_Impulse'], 
               name="Fiscal Impulse", marker_color='coral'),
        row=1, col=1
    )
    fig_impulse.add_hline(y=0, line_dash="dash", line_color="black", row=1, col=1)
    
    # Structural balance
    fig_impulse.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Structural_Balance'], 
                   name="Structural Balance", line=dict(color='purple', width=3)),
        row=1, col=2
    )
    
    # Discretionary vs automatic
    results_df['Automatic_Stabilizers'] = -results_df['Output_Gap'] * 0.2
    fig_impulse.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Discretionary_Stimulus'], 
               name="Discretionary", marker_color='blue'),
        row=2, col=1
    )
    fig_impulse.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Automatic_Stabilizers'], 
               name="Automatic", marker_color='green'),
        row=2, col=1
    )
    
    # Output gap response
    fig_impulse.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Output_Gap'], 
                   name="Output Gap", line=dict(color='red', width=3)),
        row=2, col=2, secondary_y=False
    )
    fig_impulse.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['GDP_Growth'], 
                   name="GDP Growth", line=dict(color='orange', width=3)),
        row=2, col=2, secondary_y=True
    )
    
    fig_impulse.update_layout(height=600, barmode='stack', showlegend=True)
    st.plotly_chart(fig_impulse, use_container_width=True)

with tabs[3]:
    st.subheader("📊 Fiscal Incidence & Distributional Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="distribution-box">', unsafe_allow_html=True)
        st.markdown("### 🎯 Fiscal Incidence Analysis")
        st.markdown("""
        **Measures who bears tax burden & benefits from spending:**
        - **Progressive**: Rich pay more, poor benefit more
        - **Regressive**: Poor pay more, rich benefit more  
        - **Gini Coefficient**: 0 = perfect equality, 100 = perfect inequality
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Distributional insights
        gini_change = results_df['Gini_Coefficient'].iloc[-1] - results_df['Gini_Coefficient'].iloc[0]
        poor_share_change = results_df['Poor_Consumption_Share'].iloc[-1] - results_df['Poor_Consumption_Share'].iloc[0]
        
        if gini_change < -2:
            st.success(f"**Significant Inequality Reduction**: Gini decreased by {abs(gini_change):.1f} points")
        elif gini_change < -0.5:
            st.info(f"**Moderate Inequality Reduction**: Gini decreased by {abs(gini_change):.1f} points")
        elif gini_change > 2:
            st.error(f"**Significant Inequality Increase**: Gini increased by {gini_change:.1f} points")
        elif gini_change > 0.5:
            st.warning(f"**Moderate Inequality Increase**: Gini increased by {gini_change:.1f} points")
        else:
            st.success(f"**Stable Inequality**: Gini changed by {gini_change:+.1f} points")
    
    fig_distribution = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Income Inequality (Gini)', 'Consumption Shares', 
                       'Distributional Impact', 'Poverty & Inequality Link'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": True}]]
    )
    
    # Gini coefficient
    fig_distribution.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Gini_Coefficient'], 
                   name="Gini Coefficient", line=dict(color='red', width=3)),
        row=1, col=1
    )
    fig_distribution.add_hline(y=30, line_dash="dash", line_color="green", 
                              annotation_text="Good", row=1, col=1)
    fig_distribution.add_hline(y=40, line_dash="dash", line_color="orange", 
                              annotation_text="High", row=1, col=1)
    
    # Consumption shares
    fig_distribution.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Poor_Consumption_Share'], 
                   name="Bottom 40% Share", line=dict(color='blue', width=3)),
        row=1, col=2
    )
    fig_distribution.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Rich_Consumption_Share'], 
                   name="Top 20% Share", line=dict(color='orange', width=3)),
        row=1, col=2
    )
    
    # Distributional impact
    fig_distribution.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Distribution_Impact'], 
               name="Distribution Impact", marker_color='purple'),
        row=2, col=1
    )
    fig_distribution.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)
    
    # Poverty-inequality link
    fig_distribution.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Poverty_Rate'], 
                   name="Poverty Rate", line=dict(color='red', width=3)),
        row=2, col=2, secondary_y=False
    )
    fig_distribution.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Gini_Coefficient'], 
                   name="Gini Coefficient", line=dict(color='blue', width=3)),
        row=2, col=2, secondary_y=True
    )
    
    fig_distribution.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_distribution, use_container_width=True)
    
    # Distributional policy assessment
    st.subheader("🎯 Distributional Policy Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tax_progressivity = "Progressive" if progressive_tax else "Neutral/Regressive"
        st.metric("Tax Progressivity", tax_progressivity)
    
    with col2:
        spending_progressivity = "Pro-Poor" if pro_poor_spending else "General"
        st.metric("Spending Progressivity", spending_progressivity)
    
    with col3:
        overall_incidence = "Pro-Poor" if (progressive_tax and pro_poor_spending) else "Mixed" if (progressive_tax or pro_poor_spending) else "Regressive"
        st.metric("Overall Incidence", overall_incidence)

with tabs[4]:
    st.subheader("🏦 Monetary Policy & Price Stability")
    
    fig_monetary = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Policy Rate vs Inflation Gap', 'Real Interest Rate', 
                       'Inflation Convergence', 'Monetary Policy Impact'),
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Policy rate vs inflation gap
    results_df['Inflation_Gap'] = results_df['Inflation'] - 9.0
    fig_monetary.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Policy_Rate'], 
                   name="Policy Rate", line=dict(color='blue', width=3)),
        row=1, col=1, secondary_y=False
    )
    fig_monetary.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Inflation_Gap'],  # FIXED: Changed Scater to Scatter
                   name="Inflation Gap", line=dict(color='red', width=3)),
        row=1, col=1, secondary_y=True
    )
    
    # Real interest rate
    results_df['Real_Rate'] = results_df['Policy_Rate'] - results_df['Inflation']
    fig_monetary.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Real_Rate'], 
                   name="Real Interest Rate", line=dict(color='purple', width=3)),
        row=1, col=2
    )
    
    # Inflation convergence
    fig_monetary.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Inflation'], 
                   name="Actual Inflation", line=dict(color='red', width=3)),
        row=2, col=1
    )
    fig_monetary.add_hline(y=9.0, line_dash="dash", line_color="green", 
                          annotation_text="Target", row=2, col=1)
    
    # Monetary policy impact
    fig_monetary.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Monetary_Impact'], 
               name="Monetary Impact", marker_color='orange'),
        row=2, col=2
    )
    
    fig_monetary.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_monetary, use_container_width=True)

with tabs[5]:
    st.subheader("🌍 External Sector Vulnerability")
    
    fig_external = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Current Account Balance', 'Trade Composition', 
                       'External Resilience', 'Oil Dependency'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Current account
    fig_external.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Current_Account'], 
               name="Current Account", marker_color='purple'),
        row=1, col=1
    )
    
    # Trade composition
    fig_external.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Exports'], 
                   name="Exports", line=dict(color='green', width=3)),
        row=1, col=2
    )
    fig_external.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Imports'], 
                   name="Imports", line=dict(color='red', width=3)),
        row=1, col=2
    )
    
    # External resilience
    results_df['Import_Cover'] = (results_df['Foreign_Reserves'] / (results_df['Imports'] / 12))
    fig_external.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Import_Cover'], 
                   name="Months of Import Cover", line=dict(color='blue', width=3)),
        row=2, col=1
    )
    fig_external.add_hline(y=3, line_dash="dash", line_color="red", 
                          annotation_text="Min Adequate", row=2, col=1)
    
    # Oil dependency
    results_df['Oil_Dependency'] = (results_df['Oil_Revenue'] / results_df['Total_Revenue']) * 100
    fig_external.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Oil_Dependency'], 
                   name="Oil % of Revenue", line=dict(color='orange', width=3)),
        row=2, col=2
    )
    
    fig_external.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_external, use_container_width=True)

with tabs[6]:
    st.subheader("🏗️ Structural Transformation")
    
    if structural_reform:
        st.markdown('<div style="background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 10px 0; border-radius: 5px;">', unsafe_allow_html=True)
        st.markdown('🔄 **Structural Reforms Active**: Tax reform, business climate improvements, anti-corruption measures implemented')
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Structural reforms not implemented - missing potential growth benefits")
    
    fig_structural = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Poverty & Unemployment', 'Informal Sector Share', 
                       'Structural Reform Impact', 'Social Progress'),
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Poverty & Unemployment
    fig_structural.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Poverty_Rate'], 
                   name="Poverty Rate", line=dict(color='red', width=3)),
        row=1, col=1, secondary_y=False
    )
    fig_structural.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Unemployment_Rate'], 
                   name="Unemployment", line=dict(color='blue', width=3)),
        row=1, col=1, secondary_y=True
    )
    
    # Informal sector
    fig_structural.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Informal_Sector_Share'], 
                   name="Informal Sector %", line=dict(color='orange', width=3)),
        row=1, col=2
    )
    
    # Reform impact
    fig_structural.add_trace(
        go.Bar(x=results_df['Year'], y=results_df['Structural_Impact'], 
               name="Reform Growth Boost", marker_color='green'),
        row=2, col=1
    )
    
    # Social progress
    results_df['Social_Progress'] = (100 - results_df['Poverty_Rate']) + (100 - results_df['Informal_Sector_Share']) / 2
    fig_structural.add_trace(
        go.Scatter(x=results_df['Year'], y=results_df['Social_Progress'], 
                   name="Social Progress Index", line=dict(color='purple', width=3)),
        row=2, col=2
    )
    
    fig_structural.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_structural, use_container_width=True)

with tabs[7]:
    st.header("🧠 Complete Model Mechanics & Equations")
    
    # Model Architecture Overview
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🏗️ Model Architecture Overview")
    st.markdown("""
    The simulator implements a **dynamic stochastic general equilibrium (DSGE)**-inspired framework with Nigeria-specific structural features, 
    running annual simulations over a 5-year horizon with integrated fiscal, monetary, and structural policy channels.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Core Model Equations
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("📐 Core Model Equations")
    
    st.markdown("### National Income Identity (Enhanced)")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    GDPₜ = GDPₜ₋₁ × (1 + gₜ/100)
    
    WHERE:
    gₜ = gᴮ + Δᴹ + Δᶠ + Δˣ + Δˢ + Δᴰ - Ω
    
    COMPONENTS:
    gᴮ  = Baseline growth assumption (exogenous)
    Δᴹ  = Monetary policy impact
    Δᶠ  = Fiscal policy impact  
    Δˣ  = Net trade effect
    Δˢ  = Structural reform boost
    Δᴰ  = Distributional equality effect
    Ω   = Crowding-out effect
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Fiscal Block Equations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Revenue Composition:**")
        st.markdown('<div class="equation-box">', unsafe_allow_html=True)
        st.markdown(r"""
        ```
        Rₜᴼᶦˡ = Pₜᴼᶦˡ × κᴼᶦˡ
        Rₜᴺᵒⁿ⁻ᴼᶦˡ = Rₜ₋₁ᴺᵒⁿ⁻ᴼᶦˡ × (1 + τ/100) 
                  × (1 + gᴮ/100)
        Rₜᵀᵒᵗᵃˡ = Rₜᴼᶦˡ + Rₜᴺᵒⁿ⁻ᴼᶦˡ
        
        WHERE:
        Pₜᴼᶦˡ = P₀ᴼᶦˡ × (1 + εᴼᶦˡ/100)
        κᴼᶦˡ = 0.33
        τ = Tax policy change (%)
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Government Spending:**")
        st.markdown('<div class="equation-box">', unsafe_allow_html=True)
        st.markdown(r"""
        ```
        Gₜ = Gₜ₋₁ × (1 + γ/100) × η
        
        WHERE:
        γ = Spending change (%)
        η = Spending efficiency 
            (1.0 base, 1.1 with reforms)
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Debt Dynamics")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Dₜ = Dₜ₋₁ + (Gₜ + Sₜᴰᵉᵇᵗ - Rₜᵀᵒᵗᵃˡ)
    
    WHERE:
    Sₜᴰᵉᵇᵗ = Dₜ₋₁ × (rₜˢᵒᵛ/100)
    rₜˢᵒᵛ = rₜᴾᵒˡᶦᶜʸ + ρₜᴿᶦˢᵏ
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Risk Premium Mechanism")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    ρₜᴿᶦˢᵏ = ρᴰᵉᵇᵗ + ρᴿᵉˢᵉʳᵛᵉ + ρᴿᵉᶠᵒʳᵐ
    
    WHERE:
    ρᴰᵉᵇᵗ = max(0, (Debt/GDP - 50) × 0.15)
    ρᴿᵉˢᵉʳᵛᵉ = { 3.0 if ReserveCover < 3 months
                 1.5 if ReserveCover < 6 months
                 0.0 otherwise }
    ρᴿᵉᶠᵒʳᵐ = -2.0 if structural reforms else 0
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Monetary Policy Block
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🏦 Monetary Policy Block")
    
    st.markdown("### Central Bank Reaction Function")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Δrₜᴾᵒˡᶦᶜʸ = f(πₜ₋₁ - π*, economic_condition, monetary_stance)
    
    HAWKISH REACTION:
    IF (π - π*) > 5: Δr = min(4.0, (π - π*) × 0.5) - reform_effect
    IF (π - π*) > 2: Δr = (π - π*) × 0.3 - reform_effect
    
    DOVISH REACTION:  
    IF (π - π*) > 10: Δr = (π - π*) × 0.2 - reform_effect
    IF (π - π*) > 5: Δr = (π - π*) × 0.1 - reform_effect
    
    AUTOMATIC REACTION:
    IF (π - π*) > 8: Δr = (π - π*) × 0.4 - reform_effect
    IF (π - π*) > 4: Δr = (π - π*) × 0.25 - reform_effect
    IF recession AND (π - π*) < 2: Δr = -1.0 - reform_effect
    
    WHERE:
    π* = 9.0% (CBN inflation target)
    πₜ = πₜ₋₁ - (Δrₜᴾᵒˡᶦᶜʸ × transmission_effect)
    reform_effect = 0.2 if structural reforms else 0
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Monetary Impact on Growth")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Δᴹ = -Δrₜᴾᵒˡᶦᶜʸ × (0.2 + reform_effect)
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Exchange Rate & External Sector
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🌍 Exchange Rate & External Sector")
    
    st.markdown("### Exchange Rate Determination")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    ΔEₜ = [θᴬ + θᴼᶦˡ + θᴿ + θᴮ + θᴿᵉᶠᵒʳᵐ] / 10
    
    COMPONENTS:
    θᴬ = -CAₜ₋₁/GDP₀ × 50          # Current account
    θᴼᶦˡ = (Rₜᴼᶦˡ - R₀ᴼᶦˡ)/R₀ᴼᶦˡ × (-100)  # Oil effect
    θᴿ = (rₜᴾᵒˡᶦᶜʸ - 6.0) × (-2)        # Interest diff
    θᴮ = Reserve adequacy effect
    θᴿᵉᶠᵒʳᵐ = -20 if reforms else 0   # Reform confidence
    
    WHERE:
    Eₜ = Eₜ₋₁ × (1 + ΔEₜ/100)
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Reserve Dynamics")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    FXRₜ = FXRₜ₋₁ - (intervention_intensity × FXRₜ₋₁ × 0.1)
    intervention_intensity = min(1.0, |ΔEₜ|/10)
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Trade Balance Effects")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Mₜ = GDPₜ × 0.14 × (1 + gₜ/100 × 0.8)    # Imports
    Xₜ = GDPₜ × 0.11 × (1 + εₜᵉˣᵖ/100)       # Exports
    
    WHERE:
    εₜᵉˣᵖ = max(0, ΔEₜ) × 0.6  # Export response
    Current_Accountₜ = Xₜ - Mₜ
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Structural Reforms Block
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🏗️ Structural Reforms Block")
    
    st.markdown("### Reform Growth Boost")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Δˢ = 0.2 × μₜ × (1 + φᴾ + φᴵ)
    
    WHERE:
    μₜ = min(2.0, 1 + t × 0.3)              # Time multiplier
    φᴾ = max(0, (PovertyRate - 20)/100)     # Poverty potential
    φᴵ = max(0, (InformalShare - 30)/100)   # Formalization
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Structural Transformation")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    PovertyRateₜ = max(20, PovertyRateₜ₋₁ - Δˢ × 3)
    InformalShareₜ = max(30, InformalShareₜ₋₁ - Δˢ × 2)
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fiscal Incidence & Distribution
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("📊 Fiscal Incidence & Distribution")
    
    st.markdown("### Inequality Dynamics")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    ΔGiniₜ = f(τ, γ, progressivity_flags)
    
    PROGRESSIVE TAX EFFECT:
    IF progressive_tax AND τ > 0: ΔGini -= 0.5 × (τ/10)
    
    PRO-POOR SPENDING EFFECT:  
    IF pro_poor_spending AND γ > 0: ΔGini -= 0.8 × (γ/10)
    
    GENERAL SPENDING EFFECT:
    IF NOT pro_poor_spending AND γ > 0: ΔGini -= 0.2 × (γ/10)
    
    WHERE:
    Giniₜ = max(20, min(60, Giniₜ₋₁ + ΔGini × 2))
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Consumption Share Redistribution")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    IF ΔGini < 0:  # More equal distribution
      PoorShareₜ = min(30, PoorShareₜ₋₁ + |ΔGini| × 0.5)
      RichShareₜ = max(40, RichShareₜ₋₁ - |ΔGini| × 0.5)
    ELSE:          # Less equal distribution
      PoorShareₜ = max(10, PoorShareₜ₋₁ - ΔGini × 0.3)  
      RichShareₜ = min(70, RichShareₜ₋₁ + ΔGini × 0.3)
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Equality-Growth Link")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Δᴰ = ΔGini × 0.1    # Reduced inequality boosts growth
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fiscal Impulse & Stance
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🎯 Fiscal Impulse & Stance")
    
    st.markdown("### Fiscal Impulse Calculation")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    FIₜ = (γ - τ × 0.7)/divisor + cyclical_component
    
    WHERE:
    divisor = { 5 in recession, 8 in boom, 6 otherwise }
    cyclical_component = -OutputGapₜ₋₁ × 0.2
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Output Gap Dynamics")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    OutputGapₜ = (gₜ - gᴮ) × 0.8
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Structural Balance")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    StructuralBalanceₜ = StructuralBalanceₜ₋₁ - FIₜ
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Multiplier System
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("📈 Multiplier System (State-Dependent)")
    
    st.markdown("### Time-Varying Multipliers")
    multiplier_data = {
        'Economic Condition': ['Recession', 'Normal', 'Boom', 'High Debt', 'High Inflation'],
        'Spending Multiplier': [0.8, 0.6, 0.4, 0.3, 0.2],
        'Tax Multiplier': [0.5, 0.3, 0.2, 0.1, 0.1],
        'Economic Rationale': [
            'Slack resources, low crowding-out',
            'Standard Keynesian multipliers',
            'Resource constraints, high crowding-out', 
            'Confidence effects, high interest rates',
            'Inflation concerns limit effectiveness'
        ]
    }
    st.dataframe(pd.DataFrame(multiplier_data), use_container_width=True)
    
    st.markdown("### Fiscal Impact Calculation")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Δᶠ = [γ × (Gₜ - Sₜᴰᵉᵇᵗ) × Multiplierˢ + τ × Rₜᴺᵒⁿ⁻ᴼᶦˡ × Multiplierᵀ] / GDPₜ₋₁
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Crowding-Out Effect
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("⚡ Crowding-Out Effect")
    
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    Ω = max(0, [Sₜᴰᵉᵇᵗ - (Sₜᴰᵉᵇᵗ × (Dₜ₋₁/GDPₜ₋₁))] / GDPₜ₋₁) × 100
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Mechanism**: Rising debt service costs reduce funds available for productive government spending and 
    higher interest rates discourage private investment, creating a drag on economic growth.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Labor Market & Social Indicators
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("👥 Labor Market & Social Indicators")
    
    st.markdown("### Okun's Law Implementation")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    ΔUnemploymentₜ = -0.5 × (gₜ - gᴮ)
    Unemploymentₜ = max(2.0, Unemploymentₜ₋₁ + ΔUnemploymentₜ)
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Social Progress Index")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    SPIₜ = (100 - PovertyRateₜ) + (100 - InformalShareₜ)/2
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Economic Condition Assessment
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🔍 Economic Condition Assessment")
    
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    FUNCTION assess_economic_condition(GDP, Debt/GDP, Inflation):
      IF Debt/GDP > 60: RETURN "high_debt"
      IF Inflation > 25: RETURN "high_inflation" 
      IF GDP < GDP₀ × 0.98: RETURN "recession"
      IF GDP > GDP₀ × 1.05: RETURN "boom"
      ELSE: RETURN "normal"
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Model Calibration
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🎚️ Model Calibration Parameters")
    
    st.markdown("### Nigeria-Specific Initial Conditions")
    calibration_data = {
        'Parameter': ['GDP₀', 'Debt/GDP₀', 'Oil Revenue Share', 'Inflation₀', 'Policy Rate₀', 
                     'Gini₀', 'Poverty Rate₀', 'Informal Share₀'],
        'Value': ['$450B', '31%', '55%', '28%', '18.75%', '35.1', '40%', '55%'],
        'Description': [
            'Initial GDP',
            'Initial debt ratio', 
            'Oil dependency',
            'Current inflation',
            'CBN MPC rate',
            'Income inequality',
            'Population below poverty line',
            'Informal economy size'
        ]
    }
    st.dataframe(pd.DataFrame(calibration_data), use_container_width=True)
    
    st.markdown("### Elasticity Parameters")
    elasticity_data = {
        'Parameter': ['Oil Revenue Sensitivity', 'Import Elasticity', 'Export Elasticity', 
                     'Automatic Stabilizers', 'Okun\'s Coefficient'],
        'Value': ['0.33', '0.8', '0.6', '0.2', '0.5'],
        'Description': [
            '$0.33B per $1 oil price',
            'Responsiveness to income',
            'Responsiveness to exchange rate',
            'Cyclical sensitivity', 
            'Unemployment-growth relationship'
        ]
    }
    st.dataframe(pd.DataFrame(elasticity_data), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Non-linearities & Thresholds
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("⚠️ Non-linearities & Critical Thresholds")
    
    st.markdown("### Critical Thresholds")
    threshold_data = {
        'Indicator': ['Debt/GDP', 'Debt Service/Revenue', 'Reserve Cover', 'Oil Dependency', 'Gini Coefficient'],
        'Safe Zone': ['< 30%', '< 15%', '> 6 months', '< 30%', '< 30'],
        'Caution Zone': ['30-50%', '15-30%', '3-6 months', '30-60%', '30-40'],
        'Danger Zone': ['> 50%', '> 30%', '< 3 months', '> 60%', '> 40']
    }
    st.dataframe(pd.DataFrame(threshold_data), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feedback Loops & System Dynamics
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🔄 Feedback Loops & System Dynamics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Primary Feedback Mechanisms")
        st.markdown("""
        **1. Debt-Growth Vicious Cycle:**
        ```
        Higher Debt → Higher Risk Premium → Higher Interest Rates → 
        More Debt Service → Less Productive Spending → Lower Growth → 
        Higher Debt/GDP Ratio
        ```
        
        **2. Reform-Confidence Virtuous Cycle:**
        ```
        Structural Reforms → Improved Institutions → Higher Confidence → 
        Lower Risk Premium → More Investment → Higher Growth → 
        More Reform Capacity
        ```
        """)
    
    with col2:
        st.markdown("### Additional Feedback Loops")
        st.markdown("""
        **3. Oil Revenue Volatility Cycle:**
        ```
        Oil Price Shock → Revenue Change → Fiscal Space Change → 
        Spending Consistency → Economic Stability → Investor Confidence
        ```
        
        **4. Inequality-Growth Nexus:**
        ```
        Progressive Policies → Reduced Inequality → Higher Consumption → 
        Stronger Domestic Demand → More Inclusive Growth → Poverty Reduction
        ```
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Policy Transmission Channels
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("📡 Policy Transmission Channels")
    
    transmission_data = {
        'Policy Instrument': ['Fiscal Expansion', 'Tax Reform', 'Monetary Tightening', 'Structural Reforms'],
        'Primary Channel': ['Direct Demand Stimulus', 'Incentive Effects', 'Interest Rate Channel', 'Efficiency Gains'],
        'Secondary Effects': ['Multiplier Effects', 'Behavioral Responses', 'Exchange Rate Impact', 'Institutional Quality'],
        'Time Horizon': ['Short-term', 'Medium-term', 'Short-medium term', 'Long-term'],
        'Effectiveness Condition': ['Economic Slack', 'Tax Base Structure', 'Inflation Expectations', 'Implementation Capacity']
    }
    st.dataframe(pd.DataFrame(transmission_data), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Model Limitations
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🔬 Model Limitations & Boundary Conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Simplifications")
        st.markdown("""
        - Constant elasticities within simulation periods
        - Immediate rather than delayed policy impacts  
        - No explicit monetary policy reaction to fiscal stance
        - Simplified expectations formation
        - No regional or sectoral disaggregation
        - No explicit financial sector
        - No demographic dynamics
        """)
    
    with col2:
        st.markdown("### Boundary Conditions")
        st.markdown("""
        - Minimum policy rate: 12.0%
        - Maximum annual exchange rate change: ±20%
        - Minimum foreign reserves: $5B
        - Minimum poverty rate: 20%
        - Minimum informal sector share: 30%
        - Maximum debt/GDP ratio: 100%
        - Maximum inflation: 50%
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Complete Simulation Algorithm
    st.markdown('<div class="technical-section">', unsafe_allow_html=True)
    st.subheader("🔄 Complete Simulation Algorithm")
    
    st.markdown("### Annual Simulation Steps")
    st.markdown('<div class="equation-box">', unsafe_allow_html=True)
    st.markdown(r"""
    ```
    FOR each year t from 1 to 5:
      1. Calculate structural reform boost Δˢ
      2. Calculate fiscal incidence effects
      3. Calculate fiscal impulse FIₜ
      4. Update oil revenue Rₜᴼᶦˡ
      5. Update non-oil revenue Rₜᴺᵒⁿ⁻ᴼᶦˡ
      6. Update government spending Gₜ
      7. Calculate risk premium ρₜᴿᶦˢᵏ
      8. Calculate debt service Sₜᴰᵉᵇᵗ
      9. Calculate fiscal impact Δᶠ
      10. Calculate crowding-out effect Ω
      11. Execute monetary policy reaction
      12. Calculate monetary impact Δᴹ
      13. Update exchange rate Eₜ
      14. Calculate trade effects Δˣ
      15. Calculate equality boost Δᴰ
      16. Compute final growth gₜ
      17. Update all economic variables
      18. Assess new economic condition
    ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
# Enhanced Policy Insights with New Features
st.subheader("💡 Enhanced Policy Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎯 Fiscal Stance Assessment")
    avg_impulse = results_df['Fiscal_Impulse'].mean()
    if avg_impulse > 1.0:
        st.success(f"**Strong Expansionary**: {avg_impulse:.1f}% GDP impulse")
        st.info("Consider debt sustainability if sustained")
    elif avg_impulse > 0:
        st.info(f"**Moderate Expansionary**: {avg_impulse:.1f}% GDP impulse")
    elif avg_impulse < -1.0:
        st.warning(f"**Strong Contractionary**: {avg_impulse:.1f}% GDP impulse")
        st.info("May dampen growth in short term")
    else:
        st.success(f"**Neutral Stance**: {avg_impulse:.1f}% GDP impulse")

with col2:
    st.markdown("### 📊 Distributional Impact")
    gini_change = results_df['Gini_Coefficient'].iloc[-1] - results_df['Gini_Coefficient'].iloc[0]
    if gini_change < -1:
        st.success(f"**Inequality Reduced**: Gini ↓ {abs(gini_change):.1f} points")
        st.info("Pro-poor policies effective")
    elif gini_change > 1:
        st.error(f"**Inequality Increased**: Gini ↑ {gini_change:.1f} points")
        st.warning("Consider more progressive policies")
    else:
        st.info(f"**Stable Distribution**: Gini changed {gini_change:+.1f} points")

with col3:
    st.markdown("### 🏛️ Policy Coherence")
    expansionary_fiscal = avg_impulse > 0.5
    contractionary_monetary = results_df['Policy_Rate'].iloc[-1] > results_df['Policy_Rate'].iloc[0] + 1
    
    if expansionary_fiscal and contractionary_monetary:
        st.warning("**Policy Mix Conflict**: Expansionary fiscal + contractionary monetary")
        st.info("May reduce policy effectiveness")
    elif not expansionary_fiscal and not contractionary_monetary:
        st.success("**Coordinated Policy**: Both policies aligned")
    else:
        st.info("**Mixed Policy Stance**: Different objectives")

# Enhanced data table with new variables
with st.expander("📋 Detailed Projection Data with Fiscal Incidence & Impulse"):
    display_df = results_df.copy()
    
    # Format numeric columns
    numeric_cols = ['GDP', 'Oil_Revenue', 'Non_Oil_Revenue', 'Total_Revenue', 
                   'Spending', 'Debt_Service', 'Deficit', 'Debt', 'Imports', 'Exports', 'Foreign_Reserves']
    
    for col in numeric_cols:
        display_df[col] = display_df[col].round(1)
    
    # Format percentage columns
    percent_cols = ['Debt_to_GDP', 'GDP_Growth', 'Interest_Rate', 'Policy_Rate', 
                   'Inflation', 'Poverty_Rate', 'Unemployment_Rate', 'Informal_Sector_Share',
                   'Gini_Coefficient', 'Poor_Consumption_Share', 'Rich_Consumption_Share',
                   'Fiscal_Impulse', 'Structural_Balance', 'Output_Gap']
    
    for col in percent_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(1)
    
    st.dataframe(display_df.style.format({
        'GDP': '${:,.1f}B',
        'Oil_Revenue': '${:,.1f}B', 
        'Non_Oil_Revenue': '${:,.1f}B',
        'Total_Revenue': '${:,.1f}B',
        'Spending': '${:,.1f}B',
        'Debt_Service': '${:,.1f}B',
        'Deficit': '${:,.1f}B',
        'Debt': '${:,.1f}B',
        'Imports': '${:,.1f}B',
        'Exports': '${:,.1f}B',
        'Foreign_Reserves': '${:,.1f}B',
        'Debt_to_GDP': '{:.1f}%',
        'GDP_Growth': '{:.1f}%',
        'Interest_Rate': '{:.1f}%',
        'Policy_Rate': '{:.1f}%',
        'Inflation': '{:.1f}%',
        'Poverty_Rate': '{:.1f}%',
        'Unemployment_Rate': '{:.1f}%',
        'Informal_Sector_Share': '{:.1f}%',
        'Gini_Coefficient': '{:.1f}',
        'Poor_Consumption_Share': '{:.1f}%',
        'Rich_Consumption_Share': '{:.1f}%',
        'Fiscal_Impulse': '{:.1f}%',
        'Structural_Balance': '{:.1f}%',
        'Output_Gap': '{:.1f}%'
    }))

st.markdown("---")
st.markdown("**Nigeria Integrated Fiscal-Monetary-Structural Simulator v3.0**")
st.markdown("*Now with Custom Parameters & Global Adaptability*")
st.markdown("---")
st.markdown("*Ahmad Ilu | @Iluahmad_*")
st.markdown("*aii2400012.pec@buk.edu.ng*")
st.markdown(" Toy Model © ® ™ 2025. All rights reserved. ")