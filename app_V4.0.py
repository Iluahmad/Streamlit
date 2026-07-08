# Nigeria Fiscal-Monetary Policy Simulator v4.0
# Ahmad Ilu | Bayero University Kano
# Global Standard Edition
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
import json

st.set_page_config(
    page_title="Nigeria Fiscal-Monetary Simulator",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_YEAR = datetime.now().year
SIM_YEARS = [BASE_YEAR + i for i in range(5)]
YEAR_LABELS = [str(y) for y in SIM_YEARS]
DSA_DEBT_CAP = 50.0
FRA_DEFICIT_CAP = 3.0

G = {
    "green": "#008751", "green_lt": "#00A562", "green_pale": "#E8F5EE",
    "gold": "#C8922A", "gold_pale": "#FDF6E9",
    "red": "#C0392B", "red_pale": "#FDEDEC",
    "amber": "#D68910", "amber_pale": "#FEF9E7",
    "info": "#1A5276", "info_pale": "#EAF2FB",
    "surf": "#F7F9FC", "border": "#E2E8F0",
    "txt": "#1A202C", "txt2": "#4A5568", "txtm": "#718096",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;color:{G['txt']};}}
#MainMenu,footer,header{{visibility:hidden;}}
.block-container{{padding-top:1.5rem;padding-bottom:2rem;}}

.hero{{background:linear-gradient(135deg,{G['green']} 0%,#005a36 100%);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden;}}
.hero::before{{content:'';position:absolute;top:-40px;right:-40px;width:200px;height:200px;border-radius:50%;background:rgba(255,255,255,0.05);}}
.hero-title{{font-size:1.85rem;font-weight:700;color:#fff;margin:0 0 0.3rem;letter-spacing:-0.5px;}}
.hero-sub{{font-size:0.88rem;color:rgba(255,255,255,0.75);margin:0 0 1rem;}}
.hero-badge{{display:inline-block;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff;font-size:0.7rem;font-weight:600;letter-spacing:0.5px;padding:3px 10px;border-radius:20px;margin-right:6px;text-transform:uppercase;}}

.kpi-card{{background:#fff;border:1px solid {G['border']};border-radius:12px;padding:14px 16px;transition:box-shadow 0.2s;}}
.kpi-card:hover{{box-shadow:0 4px 12px rgba(0,0,0,0.08);}}
.kpi-card.red{{border-left:4px solid {G['red']};}}
.kpi-card.amber{{border-left:4px solid {G['amber']};}}
.kpi-card.grn{{border-left:4px solid {G['green']};}}
.kpi-label{{font-size:0.66rem;font-weight:700;color:{G['txtm']};text-transform:uppercase;letter-spacing:0.6px;margin-bottom:4px;}}
.kpi-value{{font-size:1.5rem;font-weight:700;color:{G['txt']};line-height:1.1;}}
.kpi-delta{{font-size:0.71rem;font-weight:500;margin-top:3px;}}
.du{{color:{G['red']};}} .dd{{color:{G['green']};}} .dn{{color:{G['txtm']};}}

.ic{{border-radius:10px;padding:12px 16px;margin-bottom:10px;border-left:4px solid;}}
.ic.green{{background:{G['green_pale']};border-color:{G['green']};color:#1a4731;}}
.ic.amber{{background:{G['amber_pale']};border-color:{G['amber']};color:#5a3d00;}}
.ic.red{{background:{G['red_pale']};border-color:{G['red']};color:#6b1a16;}}
.ic.blue{{background:{G['info_pale']};border-color:{G['info']};color:#1a3a5c;}}
.ic-title{{font-size:0.76rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;}}
.ic-text{{font-size:0.86rem;line-height:1.5;}}

.sh{{font-size:1.05rem;font-weight:700;color:{G['txt']};border-bottom:2px solid {G['green']};padding-bottom:6px;margin:1.5rem 0 1rem;}}

.eq{{background:{G['surf']};border:1px solid {G['border']};border-left:4px solid {G['green']};border-radius:8px;padding:14px 18px;font-family:'JetBrains Mono',monospace;font-size:0.77rem;line-height:1.7;color:{G['txt']};margin:10px 0;white-space:pre-wrap;overflow-x:auto;}}

.disc{{background:{G['amber_pale']};border:1px solid {G['amber']};border-radius:8px;padding:10px 16px;font-size:0.78rem;color:#5a3d00;margin-bottom:1rem;}}

.stDownloadButton>button{{background:{G['green']};color:white;border:none;border-radius:8px;font-weight:600;padding:8px 20px;}}
.stDownloadButton>button:hover{{background:{G['green_lt']};color:white;}}

.sim-footer{{background:{G['surf']};border:1px solid {G['border']};border-radius:12px;padding:20px 24px;margin-top:2rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;}}
.fb{{font-size:0.88rem;font-weight:700;color:{G['txt']};}}
.fm{{font-size:0.74rem;color:{G['txtm']};margin-top:2px;}}
.fv{{font-size:0.72rem;font-weight:600;color:{G['green']};background:{G['green_pale']};padding:4px 12px;border-radius:20px;}}
</style>
""", unsafe_allow_html=True)

# ---- SESSION STATE ----
for k, v in [('use_custom_params', False), ('custom_params', {}), ('scenario_a', None), ('scenario_b', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ---- CHART THEME ----
def style_fig(fig, height=440):
    fig.update_layout(
        height=height, paper_bgcolor="white", plot_bgcolor=G["surf"],
        font=dict(family="Inter", size=11, color=G["txt2"]),
        legend=dict(bgcolor="white", bordercolor=G["border"], borderwidth=1, font=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig.update_xaxes(showgrid=True, gridcolor=G["border"], gridwidth=1, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor=G["border"], gridwidth=1, zeroline=True, zerolinecolor=G["border"], zerolinewidth=1, tickfont=dict(size=10))
    return fig

def ic(cls, title, text):
    return f'<div class="ic {cls}"><div class="ic-title">{title}</div><div class="ic-text">{text}</div></div>'

# ---- MODEL ----
class NigeriaFiscalMonetaryModel:
    def __init__(self, cp=None):
        p = cp if (cp and st.session_state.use_custom_params) else {}
        self.initial_gdp = p.get('initial_gdp', 450)
        self.initial_debt = p.get('initial_debt', 140)
        self.initial_deficit = p.get('initial_deficit', 12)
        self.oil_revenue = p.get('oil_revenue', 25)
        self.non_oil_revenue = p.get('non_oil_revenue', 35)
        self.total_revenue = self.oil_revenue + self.non_oil_revenue
        self.total_spending = self.total_revenue + self.initial_deficit
        self.oil_price = p.get('oil_price', 75)
        self.oil_production = p.get('oil_production', 1.4)
        self.oil_revenue_per_dollar = p.get('oil_revenue_per_dollar', 0.33)
        self.policy_rate = p.get('policy_rate', 18.75)
        self.inflation_target = p.get('inflation_target', 9.0)
        self.current_inflation = p.get('current_inflation', 28.0)
        self.exchange_rate = p.get('exchange_rate', 1500)
        self.foreign_reserves = p.get('foreign_reserves', 33)
        self.imports_gdp_ratio = p.get('imports_gdp_ratio', 0.14)
        self.exports_gdp_ratio = p.get('exports_gdp_ratio', 0.11)
        self.import_elasticity = p.get('import_elasticity', 0.8)
        self.export_elasticity = p.get('export_elasticity', 0.6)
        self.poverty_rate = p.get('poverty_rate', 40.0)
        self.unemployment_rate = p.get('unemployment_rate', 4.0)
        self.informal_sector_share = p.get('informal_sector_share', 55.0)
        self.income_inequality_gini = p.get('gini_coefficient', 35.1)
        self.poor_consumption_share = p.get('poor_consumption_share', 15.0)
        self.rich_consumption_share = p.get('rich_consumption_share', 55.0)
        self.cyclically_adjusted_balance = p.get('cyclically_adjusted_balance', -8.0)
        self.automatic_stabilizers = p.get('automatic_stabilizers', 0.2)

    def run(self, tax_change, spending_change, growth_assumption, oil_price_shock,
            monetary_response="automatic", structural_reform=False,
            progressive_tax=False, pro_poor_spending=False, years=5):
        results = []
        gdp = self.initial_gdp; debt = self.initial_debt
        non_oil_revenue = self.non_oil_revenue; oil_revenue = self.oil_revenue
        spending = self.total_spending; policy_rate = self.policy_rate
        inflation = self.current_inflation; exchange_rate = self.exchange_rate
        foreign_reserves = self.foreign_reserves; poverty_rate = self.poverty_rate
        unemployment_rate = self.unemployment_rate; informal_share = self.informal_sector_share
        gini = self.income_inequality_gini; poor_share = self.poor_consumption_share
        rich_share = self.rich_consumption_share; output_gap = 0.0
        structural_balance = self.cyclically_adjusted_balance
        imports = gdp * self.imports_gdp_ratio; exports = gdp * self.exports_gdp_ratio
        current_account = exports - imports
        ec = self.assess_ec(gdp, debt/gdp, inflation)
        sm, tm = self.multipliers(ec)

        for yr in range(years):
            rb = 0
            if structural_reform:
                rb = self.reform_boost(yr, poverty_rate, informal_share)
                eff_tax = tax_change + rb * 2
                poverty_rate = max(20, poverty_rate - rb * 3)
                informal_share = max(30, informal_share - rb * 2)
            else:
                eff_tax = tax_change

            di, new_gini, new_poor, new_rich = self.fiscal_incidence(
                tax_change, spending_change, progressive_tax, pro_poor_spending, gini, poor_share, rich_share, ec)
            fi, sb, ds_stim = self.fiscal_impulse(spending_change, tax_change, output_gap, structural_balance, ec)

            cop = self.oil_price * (1 + oil_price_shock/100)
            oil_revenue = cop * self.oil_revenue_per_dollar
            non_oil_revenue = non_oil_revenue * (1 + eff_tax/100) * (1 + growth_assumption/100)
            total_revenue = oil_revenue + non_oil_revenue
            eff = 1.1 if structural_reform else 1.0
            spending = spending * (1 + spending_change/100) * eff
            dtg = (debt/gdp)*100
            rp = self.risk_premium(dtg, foreign_reserves, structural_reform)
            eff_ir = policy_rate + rp
            debt_svc = debt * (eff_ir/100)
            fiscal_impact = (spending_change*(spending-debt_svc)*sm + eff_tax*non_oil_revenue*tm)/gdp
            co = max(0, (debt_svc - (debt_svc*(debt/gdp)))/gdp)*100
            mi, npr, ni = self.monetary(fiscal_impact, inflation, ec, monetary_response, structural_reform)
            eri, ne, nfx, tbe = self.exchange(fiscal_impact, current_account, oil_revenue, foreign_reserves, policy_rate, structural_reform)
            imp_eff = -(growth_assumption/100)*self.import_elasticity*(imports/gdp)*100
            exp_eff = max(0,(ne-exchange_rate)/exchange_rate)*self.export_elasticity*(exports/gdp)*100
            nte = imp_eff + exp_eff
            eq_boost = di * 0.1
            eg = growth_assumption + fiscal_impact + mi + eri + nte + rb + eq_boost - co
            output_gap = (eg - growth_assumption)*0.8
            new_unemp = max(2.0, unemployment_rate - 0.5*(eg - growth_assumption))
            gdp = gdp*(1+eg/100)
            deficit = spending + debt_svc - total_revenue
            debt = debt + deficit
            dtg = (debt/gdp)*100
            imports = gdp*self.imports_gdp_ratio*(1+eg/100*self.import_elasticity)
            exports = gdp*self.exports_gdp_ratio*(1+exp_eff/100)
            current_account = exports - imports
            policy_rate = npr; inflation = ni; exchange_rate = ne; foreign_reserves = nfx
            unemployment_rate = new_unemp; gini = new_gini; poor_share = new_poor; rich_share = new_rich
            structural_balance = sb
            ec = self.assess_ec(gdp, dtg, inflation); sm, tm = self.multipliers(ec)
            results.append({
                'Year': SIM_YEARS[yr], 'Year_Label': YEAR_LABELS[yr],
                'GDP': gdp, 'GDP_Growth': eg,
                'Oil_Revenue': oil_revenue, 'Non_Oil_Revenue': non_oil_revenue,
                'Total_Revenue': total_revenue, 'Spending': spending,
                'Debt_Service': debt_svc, 'Deficit': deficit, 'Debt': debt,
                'Debt_to_GDP': dtg, 'Deficit_to_GDP': (deficit/gdp)*100,
                'Interest_Rate': eff_ir, 'Policy_Rate': policy_rate, 'Inflation': inflation,
                'Exchange_Rate': exchange_rate, 'Foreign_Reserves': foreign_reserves,
                'Imports': imports, 'Exports': exports, 'Current_Account': current_account,
                'Oil_Price': cop, 'Economic_Condition': ec,
                'Crowding_Out_Effect': co, 'Monetary_Impact': mi,
                'Trade_Impact': nte, 'Fiscal_Impact': fiscal_impact,
                'Structural_Impact': rb, 'Poverty_Rate': poverty_rate,
                'Unemployment_Rate': unemployment_rate, 'Informal_Sector_Share': informal_share,
                'Gini_Coefficient': gini, 'Poor_Consumption_Share': poor_share,
                'Rich_Consumption_Share': rich_share, 'Distribution_Impact': di,
                'Equality_Boost': eq_boost, 'Fiscal_Impulse': fi,
                'Structural_Balance': structural_balance, 'Output_Gap': output_gap,
                'Discretionary_Stimulus': ds_stim,
            })
        return pd.DataFrame(results)

    def fiscal_incidence(self, tc, sc, pt, pp, gini, poor, rich, ec):
        di = 0
        if pt and tc > 0: di -= 0.5*(tc/10)
        elif not pt and tc > 0: di += 0.3*(tc/10)
        if pp and sc > 0: di -= 0.8*(sc/10)
        elif not pp and sc > 0: di -= 0.2*(sc/10)
        ng = max(20, min(60, gini + di*2))
        if di < 0:
            eg = abs(di)*0.5; np_ = min(30, poor+eg); nr = max(40, rich-eg)
        else:
            ig = di*0.3; np_ = max(10, poor-ig); nr = min(70, rich+ig)
        return di, ng, np_, nr

    def fiscal_impulse(self, sc, tc, og, sb, ec):
        ds = sc - tc*0.7; cc = -og*self.automatic_stabilizers
        div = 5 if ec=="recession" else 8 if ec=="boom" else 6
        fi = max(-5, min(5, ds/div + cc))
        return fi, sb - fi, ds

    def reform_boost(self, yr, pov, inf):
        return 0.2*min(2.0,1+yr*0.3)*(1+max(0,(pov-20)/100)+max(0,(inf-30)/100))

    def monetary(self, fi, inf, ec, stance, reform):
        gap = inf - self.inflation_target; re = 0.2 if reform else 0
        if stance=="hawkish":
            rc = (min(4.0,gap*0.5)-re if gap>5 else gap*0.3-re if gap>2 else 0)
        elif stance=="dovish":
            rc = (gap*0.2-re if gap>10 else gap*0.1-re if gap>5 else 0)
        else:
            rc = (gap*0.4-re if gap>8 else gap*0.25-re if gap>4 else -1.0-re if ec=="recession" and gap<2 else 0)
        npr = max(12.0, self.policy_rate + rc)
        return -rc*(0.2+re), npr, inf - rc*(0.3+re)

    def exchange(self, fi, ca, oil_rev, res, pr, reform):
        cag = ca/(self.initial_gdp*0.1)
        p = (-cag*50 + (oil_rev-self.oil_revenue)/max(self.oil_revenue,0.001)*(-100)
             + (pr-6.0)*(-2) + (50 if res/(self.initial_gdp*0.1)<3 else 20 if res/(self.initial_gdp*0.1)<6 else 0)
             + (-20 if reform else 0))
        ec = max(-20, min(20, p/10))
        ne = self.exchange_rate*(1+ec/100)
        nfx = max(5, res - min(1.0, abs(ec)/10)*res*0.1)
        ei = -1.0 if ec>5 else 0.5 if ec<-5 else 0
        return ei, ne, nfx, 0.3 if ec>0 else -0.2

    def risk_premium(self, dtg, res, reform):
        dp = max(0,(dtg-50)*0.15) if dtg>50 else 0
        rc = res/(self.initial_gdp*self.imports_gdp_ratio/12)
        rp = 3.0 if rc<3 else 1.5 if rc<6 else 0
        return max(0, dp + rp + (-2.0 if reform else 0))

    def assess_ec(self, gdp, dtg, inf):
        if dtg > 60: return "high_debt"
        if inf > 25: return "high_inflation"
        if gdp < self.initial_gdp*0.98: return "recession"
        if gdp > self.initial_gdp*1.05: return "boom"
        return "normal"

    def multipliers(self, ec):
        return {"recession":(0.8,0.5),"boom":(0.4,0.2),"high_debt":(0.3,0.1),"high_inflation":(0.2,0.1)}.get(ec,(0.6,0.3))

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown(f'<div style="text-align:center;padding:12px 0 8px;"><div style="font-size:1.5rem;">🇳🇬</div><div style="font-size:0.85rem;font-weight:700;">Policy Simulator</div><div style="font-size:0.68rem;color:{G["txtm"]};">v4.0 · Calibrated Structural Model</div></div><hr style="border-color:{G["border"]};margin:8px 0 12px;">', unsafe_allow_html=True)
    with st.expander("🛢️ Oil Market", expanded=True):
        oil_price_shock = st.slider("Oil Price Shock (%)", -50.0, 100.0, 0.0, 5.0)
    with st.expander("📈 Growth & Structure", expanded=True):
        baseline_growth = st.slider("Non-Oil GDP Growth (%)", 0.0, 8.0, 3.0, 0.5)
        structural_reform = st.checkbox("Implement Structural Reforms")
    with st.expander("🏛️ Fiscal Policy", expanded=True):
        tax_change = st.slider("Non-Oil Revenue Change (%)", -20.0, 50.0, 0.0, 2.0)
        spending_change = st.slider("Govt Spending Change (%)", -30.0, 40.0, 0.0, 2.0)
        progressive_tax = st.checkbox("Progressive Tax System")
        pro_poor_spending = st.checkbox("Pro-Poor Spending")
    with st.expander("🏦 Monetary Policy", expanded=True):
        monetary_response = st.selectbox("CBN Reaction Function", ["automatic", "hawkish", "dovish"])
    st.markdown(f'<div style="font-size:0.7rem;color:{G["txtm"]};padding:8px 4px;">Calibrated to Nigeria 2024 · Horizon: {SIM_YEARS[0]}–{SIM_YEARS[-1]}<br><a href="mailto:aii2400012.pec@buk.edu.ng" style="color:{G["green"]};">aii2400012.pec@buk.edu.ng</a></div>', unsafe_allow_html=True)

# ---- CUSTOM PARAMS ----
with st.expander("⚙️ Custom Model Parameters — override Nigeria 2024 defaults", expanded=False):
    use_custom = st.checkbox("Enable custom parameters", value=st.session_state.use_custom_params)
    if use_custom:
        st.session_state.use_custom_params = True
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.custom_params['initial_gdp'] = st.number_input("Initial GDP ($B)", 10.0, 5000.0, 450.0, 10.0)
            st.session_state.custom_params['initial_debt'] = st.number_input("Initial Debt ($B)", 0.0, 3000.0, 140.0, 10.0)
            st.session_state.custom_params['initial_deficit'] = st.number_input("Initial Deficit ($B)", 0.0, 500.0, 12.0, 1.0)
        with c2:
            st.session_state.custom_params['oil_revenue'] = st.number_input("Oil Revenue ($B)", 0.0, 500.0, 25.0, 1.0)
            st.session_state.custom_params['non_oil_revenue'] = st.number_input("Non-Oil Revenue ($B)", 0.0, 500.0, 35.0, 1.0)
            st.session_state.custom_params['oil_price'] = st.number_input("Oil Price ($/bbl)", 10.0, 200.0, 75.0, 5.0)
        with c3:
            st.session_state.custom_params['policy_rate'] = st.number_input("Policy Rate (%)", 0.0, 50.0, 18.75, 0.25)
            st.session_state.custom_params['current_inflation'] = st.number_input("Inflation (%)", 0.0, 100.0, 28.0, 1.0)
            st.session_state.custom_params['exchange_rate'] = st.number_input("NGN/USD", 1.0, 3000.0, 1500.0, 50.0)
        with st.expander("More parameters"):
            a1, a2, a3 = st.columns(3)
            with a1:
                st.session_state.custom_params['poverty_rate'] = st.number_input("Poverty Rate (%)", 0.0, 100.0, 40.0, 1.0)
                st.session_state.custom_params['unemployment_rate'] = st.number_input("Unemployment (%)", 0.0, 50.0, 4.0, 0.5)
                st.session_state.custom_params['informal_sector_share'] = st.number_input("Informal Sector (%)", 0.0, 100.0, 55.0, 1.0)
            with a2:
                st.session_state.custom_params['gini_coefficient'] = st.number_input("Gini Coefficient", 20.0, 70.0, 35.1, 0.1)
                st.session_state.custom_params['poor_consumption_share'] = st.number_input("Bottom 40% Share (%)", 5.0, 50.0, 15.0, 0.5)
                st.session_state.custom_params['rich_consumption_share'] = st.number_input("Top 20% Share (%)", 20.0, 80.0, 55.0, 0.5)
            with a3:
                st.session_state.custom_params['foreign_reserves'] = st.number_input("FX Reserves ($B)", 0.0, 500.0, 33.0, 1.0)
                st.session_state.custom_params['imports_gdp_ratio'] = st.number_input("Imports/GDP", 0.01, 1.0, 0.14, 0.01)
                st.session_state.custom_params['exports_gdp_ratio'] = st.number_input("Exports/GDP", 0.01, 1.0, 0.11, 0.01)
    else:
        st.session_state.use_custom_params = False
        st.info("Using calibrated Nigeria 2024 parameters. Enable above to run alternative-country scenarios.")

# ---- MODEL RUN ----
@st.cache_data
def run_model(tc, sc, gr, os_, ms, sr, pt, pp, cpk):
    cp = st.session_state.custom_params if st.session_state.use_custom_params else None
    m = NigeriaFiscalMonetaryModel(cp)
    df = m.run(tc, sc, gr, os_, ms, sr, pt, pp)
    df['Real_Interest_Rate'] = df['Policy_Rate'] - df['Inflation']
    df['Debt_Service_Ratio'] = (df['Debt_Service']/df['Total_Revenue'])*100
    df['Fiscal_Space'] = df['Total_Revenue'] - df['Debt_Service'] - df['Spending']*0.7
    df['Oil_Dependency'] = (df['Oil_Revenue']/df['Total_Revenue'])*100
    df['Import_Cover'] = df['Foreign_Reserves']/(df['Imports']/12)
    df['Social_Progress'] = (100-df['Poverty_Rate']) + (100-df['Informal_Sector_Share'])/2
    df['Inflation_Gap'] = df['Inflation'] - 9.0
    df['Automatic_Stabilizers'] = -df['Output_Gap']*0.2
    return df

cpk = str(st.session_state.custom_params) if st.session_state.use_custom_params else "default"
df = run_model(tax_change, spending_change, baseline_growth, oil_price_shock,
               monetary_response, structural_reform, progressive_tax, pro_poor_spending, cpk)

# ---- HERO ----
param_label = "Custom Parameters" if st.session_state.use_custom_params else "Nigeria 2024 Calibration"
st.markdown(f"""
<div class="hero">
  <div class="hero-title">Nigeria Fiscal-Monetary Policy Simulator</div>
  <div class="hero-sub">Calibrated Structural Model · Integrated Fiscal–Monetary–Distributional Framework · {SIM_YEARS[0]}–{SIM_YEARS[-1]} Projection Horizon</div>
  <span class="hero-badge">{param_label}</span>
  <span class="hero-badge">CBN {monetary_response.title()}</span>
  {'<span class="hero-badge">Reforms Active</span>' if structural_reform else ''}
  {'<span class="hero-badge">Progressive Mix</span>' if progressive_tax or pro_poor_spending else ''}
</div>
<div class="disc">ℹ️ <b>Research Instrument.</b> This is a calibrated structural policy simulator for scenario analysis and pedagogical use — not a forecasting system. Parameters calibrated to Nigeria 2024 data (CBN · NBS · DMO · FMFBNP).</div>
""", unsafe_allow_html=True)

# ---- KPI CARDS ----
debt_end = df['Debt_to_GDP'].iloc[-1]; debt_delta = debt_end - df['Debt_to_GDP'].iloc[0]
avg_growth = df['GDP_Growth'].mean(); inf_end = df['Inflation'].iloc[-1]
avg_impulse = df['Fiscal_Impulse'].mean(); gini_end = df['Gini_Coefficient'].iloc[-1]
gini_delta = gini_end - df['Gini_Coefficient'].iloc[0]; gdp_end = df['GDP'].iloc[-1]
gdp_pi = gdp_end - (df['GDP'].iloc[0]*(1+baseline_growth/100)**5)
dsr_end = df['Debt_Service_Ratio'].iloc[-1]

def kpi(col, label, val, delta_txt, d_cls, card_cls):
    col.markdown(f'<div class="kpi-card {card_cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div><div class="kpi-delta {d_cls}">{delta_txt}</div></div>', unsafe_allow_html=True)

cols = st.columns(6)
kpi(cols[0],"Debt-to-GDP",f"{debt_end:.1f}%",f"{debt_delta:+.1f}pp","du" if debt_delta>0 else "dd","red" if debt_end>80 else "amber" if debt_end>50 else "grn")
kpi(cols[1],"Avg GDP Growth",f"{avg_growth:.1f}%",f"{avg_growth-baseline_growth:+.1f}pp vs base","dd" if avg_growth>=3 else "du","grn" if avg_growth>=3 else "amber")
kpi(cols[2],"End Inflation",f"{inf_end:.1f}%","Target: 9.0%","du" if inf_end>9 else "dd","red" if inf_end>25 else "amber" if inf_end>15 else "grn")
kpi(cols[3],"Avg Fiscal Impulse",f"{avg_impulse:+.1f}%","% of GDP","dd" if avg_impulse>0 else "du","grn" if avg_impulse>0 else "amber")
kpi(cols[4],"Gini (End-Period)",f"{gini_end:.1f}",f"{gini_delta:+.1f} pts","du" if gini_delta>0 else "dd","red" if gini_end>45 else "amber" if gini_end>35 else "grn")
kpi(cols[5],"Economy Size",f"${gdp_end:.0f}B",f"Policy Δ: ${gdp_pi:+.0f}B","dd" if gdp_pi>=0 else "du","grn" if gdp_pi>=0 else "amber")

# ---- POLICY INTELLIGENCE ----
st.markdown('<div class="sh">🧠 Policy Intelligence Summary</div>', unsafe_allow_html=True)
ca, cb, cc = st.columns(3)

with ca:
    if debt_end > 80: st.markdown(ic("red","⚠ Debt Sustainability Risk",f"Debt-to-GDP reaches {debt_end:.1f}% by {SIM_YEARS[-1]} — IMF High-Risk threshold (>80%). Urgent consolidation signalled."), unsafe_allow_html=True)
    elif debt_end > DSA_DEBT_CAP: st.markdown(ic("amber","⚡ Debt Watch",f"Debt-to-GDP of {debt_end:.1f}% exceeds DSA prudent threshold of {DSA_DEBT_CAP:.0f}%. Monitor trajectory."), unsafe_allow_html=True)
    else: st.markdown(ic("green","✓ Debt Sustainable",f"Debt-to-GDP of {debt_end:.1f}% is within DSA prudent threshold of {DSA_DEBT_CAP:.0f}%."), unsafe_allow_html=True)
    avg_def = df['Deficit_to_GDP'].mean()
    if avg_def > FRA_DEFICIT_CAP: st.markdown(ic("amber","📋 FRA Deficit Cap Breached",f"Average deficit of {avg_def:.1f}% GDP exceeds the FRA cap of {FRA_DEFICIT_CAP:.0f}% GDP. Revenue mobilisation needed."), unsafe_allow_html=True)
    else: st.markdown(ic("green","✓ FRA Compliant",f"Average deficit of {avg_def:.1f}% GDP is within the FRA cap of {FRA_DEFICIT_CAP:.0f}% GDP."), unsafe_allow_html=True)

with cb:
    y2t = next((r['Year'] for _, r in df.iterrows() if r['Inflation'] <= 15), None)
    if y2t: st.markdown(ic("green","📉 Disinflation On Track",f"Inflation projected below 15% by {y2t}. CBN {monetary_response} stance {'effective' if inf_end < 20 else 'partially effective'}."), unsafe_allow_html=True)
    else: st.markdown(ic("amber","🔥 Persistent Inflation",f"Inflation remains at {inf_end:.1f}% through {SIM_YEARS[-1]}. Stronger tightening or fiscal consolidation needed."), unsafe_allow_html=True)
    exp_f = avg_impulse > 0.5; con_m = df['Policy_Rate'].iloc[-1] > df['Policy_Rate'].iloc[0]+1
    if exp_f and con_m: st.markdown(ic("amber","⚠ Policy Mix Tension","Expansionary fiscal + contractionary monetary. Growth gains may be offset by higher real rates."), unsafe_allow_html=True)
    elif not exp_f and not con_m: st.markdown(ic("green","✓ Policy Coordination","Fiscal and monetary policies aligned. Potential for synergistic stabilisation."), unsafe_allow_html=True)
    else: st.markdown(ic("blue","ℹ Mixed Policy Stance","Fiscal and monetary pursuing different objectives — context-dependent outcome."), unsafe_allow_html=True)

with cc:
    if gini_delta < -2: st.markdown(ic("green","✓ Inequality Reduced",f"Gini declines by {abs(gini_delta):.1f} points — progressive fiscal architecture effective."), unsafe_allow_html=True)
    elif gini_delta > 2: st.markdown(ic("red","↑ Inequality Rising",f"Gini increases by {gini_delta:.1f} points — regressive incidence. Consider progressive reform."), unsafe_allow_html=True)
    else: st.markdown(ic("blue","→ Stable Distribution",f"Gini changes by {gini_delta:+.1f} points — distributional neutrality maintained."), unsafe_allow_html=True)
    if dsr_end > 80: st.markdown(ic("red","🚨 Debt Service Crisis Risk",f"Debt service consumes {dsr_end:.0f}% of revenue by {SIM_YEARS[-1]} — far beyond the 30% benchmark. Fiscal space severely compressed."), unsafe_allow_html=True)
    elif dsr_end > 30: st.markdown(ic("amber","⚡ Debt Service Pressure",f"DSR of {dsr_end:.0f}% exceeds the 30% IMF benchmark. Limited space for development spending."), unsafe_allow_html=True)
    else: st.markdown(ic("green","✓ Manageable Debt Service",f"DSR of {dsr_end:.0f}% is below the 30% benchmark. Adequate fiscal space maintained."), unsafe_allow_html=True)

# ---- ANALYTICAL TABS ----
st.markdown('<div class="sh">📊 Economic Analysis</div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 Macro Dashboard","💰 Fiscal Sustainability","🎯 Fiscal Stance",
                "📉 Distribution","🏦 Monetary & Prices","🌍 External Sector",
                "🏗️ Structural","⚖️ Scenario Comparison","🧠 Model Mechanics"])

# TAB 0 - MACRO
with tabs[0]:
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["GDP Growth Decomposition (pp)","Inflation & Policy Rate (%)","Fiscal Impulse & Output Gap","Debt-to-GDP Trajectory (%)"],
        specs=[[{"secondary_y":False},{"secondary_y":True}],[{"secondary_y":True},{"secondary_y":False}]],
        vertical_spacing=0.14, horizontal_spacing=0.1)
    comp_map = [("Fiscal",G['green'],"Fiscal_Impact"),("Monetary",G['gold'],"Monetary_Impact"),
                ("Trade",G['info'],"Trade_Impact"),("Structural",G['chart_structural'] if 'chart_structural' in G else "#8E44AD","Structural_Impact"),
                ("Equality",G['green_lt'],"Equality_Boost"),("Crowding-Out",G['red'],"Crowding_Out_Effect")]
    for nm, col, fld in comp_map:
        fig.add_trace(go.Bar(name=nm, x=df['Year_Label'], y=df[fld], marker_color=col, opacity=0.82), row=1, col=1)
    fig.add_trace(go.Scatter(name='Actual Growth', x=df['Year_Label'], y=df['GDP_Growth'],
                             line=dict(color='#1A202C',width=2.5), mode='lines+markers', marker=dict(size=6)), row=1, col=1)
    fig.add_trace(go.Scatter(name='Inflation', x=df['Year_Label'], y=df['Inflation'], line=dict(color=G['red'],width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(name='Policy Rate', x=df['Year_Label'], y=df['Policy_Rate'], line=dict(color=G['info'],width=2.5,dash='dot')), row=1, col=2, secondary_y=True)
    fig.add_hline(y=9, line_dash="dash", line_color=G['green'], annotation_text="CBN Target 9%", row=1, col=2)
    fi_colors = [G['green'] if v>=0 else G['red'] for v in df['Fiscal_Impulse']]
    fig.add_trace(go.Bar(name='Fiscal Impulse', x=df['Year_Label'], y=df['Fiscal_Impulse'], marker_color=fi_colors, opacity=0.82), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=2, col=1)
    fig.add_trace(go.Scatter(name='Output Gap', x=df['Year_Label'], y=df['Output_Gap'], line=dict(color='#8E44AD',width=2.5)), row=2, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(name='Debt/GDP', x=df['Year_Label'], y=df['Debt_to_GDP'],
                             line=dict(color=G['red'],width=2.5), fill='tozeroy', fillcolor='rgba(192,57,43,0.07)'), row=2, col=2)
    fig.add_hline(y=DSA_DEBT_CAP, line_dash="dash", line_color=G['amber'], annotation_text=f"DSA {DSA_DEBT_CAP:.0f}%", row=2, col=2)
    fig.add_hline(y=80, line_dash="dot", line_color=G['red'], annotation_text="IMF High-Risk 80%", row=2, col=2)
    fig.update_layout(barmode='relative')
    style_fig(fig, 480)
    st.plotly_chart(fig, use_container_width=True)

# TAB 1 - FISCAL
with tabs[1]:
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["Revenue Composition ($B)","Spending Structure ($B)","Debt Service Burden (% Revenue)","Fiscal Space ($B)"],
        vertical_spacing=0.14, horizontal_spacing=0.1)
    fig.add_trace(go.Scatter(name='Oil Revenue', x=df['Year_Label'], y=df['Oil_Revenue'],
        stackgroup='rv', fillcolor='rgba(200,146,42,0.55)', line=dict(color=G['gold'])), row=1, col=1)
    fig.add_trace(go.Scatter(name='Non-Oil Revenue', x=df['Year_Label'], y=df['Non_Oil_Revenue'],
        stackgroup='rv', fillcolor='rgba(0,135,81,0.55)', line=dict(color=G['green'])), row=1, col=1)
    fig.add_trace(go.Bar(name='Discretionary', x=df['Year_Label'], y=df['Spending']-df['Debt_Service'], marker_color=G['info'], opacity=0.82), row=1, col=2)
    fig.add_trace(go.Bar(name='Debt Service', x=df['Year_Label'], y=df['Debt_Service'], marker_color=G['red'], opacity=0.82), row=1, col=2)
    fig.add_trace(go.Scatter(name='DSR', x=df['Year_Label'], y=df['Debt_Service_Ratio'],
        line=dict(color=G['red'],width=2.5), fill='tozeroy', fillcolor='rgba(192,57,43,0.07)'), row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color=G['amber'], annotation_text="IMF Benchmark 30%", row=2, col=1)
    fig.add_trace(go.Scatter(name='Fiscal Space', x=df['Year_Label'], y=df['Fiscal_Space'],
        line=dict(color=G['green'],width=2.5), fill='tozeroy', fillcolor='rgba(0,135,81,0.08)'), row=2, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=2, col=2)
    fig.update_layout(barmode='stack')
    style_fig(fig, 480)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**FRA Compliance Table**")
    fra = df[['Year_Label','Deficit_to_GDP','Debt_to_GDP','Debt_Service_Ratio']].copy()
    fra.columns = ['Year','Deficit/GDP (%)','Debt/GDP (%)','Debt Service/Revenue (%)']
    for c in fra.columns[1:]: fra[c] = fra[c].round(1)
    st.dataframe(fra, use_container_width=True, hide_index=True)

# TAB 2 - FISCAL STANCE
with tabs[2]:
    avg_imp = df['Fiscal_Impulse'].mean()
    if avg_imp > 1.0: st.markdown(ic("green","Strong Expansionary Stance",f"Average fiscal impulse of {avg_imp:.1f}% GDP. Monitor debt sustainability."), unsafe_allow_html=True)
    elif avg_imp > 0: st.markdown(ic("blue","Moderate Expansionary Stance",f"Average fiscal impulse of {avg_imp:.1f}% GDP. Mild net stimulus."), unsafe_allow_html=True)
    elif avg_imp < -1.0: st.markdown(ic("amber","Contractionary — Fiscal Consolidation",f"Average impulse of {avg_imp:.1f}% GDP. Near-term growth drag likely."), unsafe_allow_html=True)
    else: st.markdown(ic("blue","Broadly Neutral Stance",f"Average fiscal impulse of {avg_imp:.1f}% GDP."), unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["Fiscal Impulse (% GDP)","Structural Balance (% GDP)","Discretionary vs Automatic","Output Gap & Growth"],
        specs=[[{"secondary_y":False},{"secondary_y":False}],[{"secondary_y":False},{"secondary_y":True}]],
        vertical_spacing=0.14, horizontal_spacing=0.1)
    fi_c = [G['green'] if v>=0 else G['red'] for v in df['Fiscal_Impulse']]
    fig.add_trace(go.Bar(name='Fiscal Impulse', x=df['Year_Label'], y=df['Fiscal_Impulse'], marker_color=fi_c, opacity=0.82), row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=1, col=1)
    fig.add_trace(go.Scatter(name='Structural Balance', x=df['Year_Label'], y=df['Structural_Balance'],
        line=dict(color='#8E44AD',width=2.5), fill='tozeroy', fillcolor='rgba(142,68,173,0.08)'), row=1, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=1, col=2)
    fig.add_trace(go.Bar(name='Discretionary', x=df['Year_Label'], y=df['Discretionary_Stimulus'], marker_color=G['info'], opacity=0.8), row=2, col=1)
    fig.add_trace(go.Bar(name='Automatic', x=df['Year_Label'], y=df['Automatic_Stabilizers'], marker_color=G['green'], opacity=0.8), row=2, col=1)
    fig.add_trace(go.Scatter(name='GDP Growth', x=df['Year_Label'], y=df['GDP_Growth'], line=dict(color=G['gold'],width=2.5)), row=2, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(name='Output Gap', x=df['Year_Label'], y=df['Output_Gap'], line=dict(color=G['red'],width=2,dash='dot')), row=2, col=2, secondary_y=True)
    fig.update_layout(barmode='stack')
    style_fig(fig, 480)
    st.plotly_chart(fig, use_container_width=True)

# TAB 3 - DISTRIBUTION
with tabs[3]:
    d1, d2, d3 = st.columns(3)
    for col, lbl, val, cls in [
        (d1,"Tax Progressivity",("Progressive" if progressive_tax else "Neutral/Regressive"),"green" if progressive_tax else "amber"),
        (d2,"Spending Progressivity",("Pro-Poor" if pro_poor_spending else "General"),"green" if pro_poor_spending else "blue"),
        (d3,"Overall Incidence",("Pro-Poor" if (progressive_tax and pro_poor_spending) else "Mixed" if (progressive_tax or pro_poor_spending) else "Regressive"),"green" if (progressive_tax and pro_poor_spending) else "blue" if (progressive_tax or pro_poor_spending) else "red"),
    ]:
        col.markdown(f'<div class="ic {cls}"><div class="ic-title">{lbl}</div><div class="ic-text" style="font-weight:700;font-size:1rem;">{val}</div></div>', unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["Gini Coefficient","Consumption Shares (%)","Distributional Impact per Year","Poverty Rate & Gini"],
        specs=[[{"secondary_y":False},{"secondary_y":False}],[{"secondary_y":False},{"secondary_y":True}]],
        vertical_spacing=0.14, horizontal_spacing=0.1)
    fig.add_trace(go.Scatter(name='Gini', x=df['Year_Label'], y=df['Gini_Coefficient'],
        line=dict(color=G['red'],width=2.5), fill='tozeroy', fillcolor='rgba(192,57,43,0.06)'), row=1, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color=G['green'], annotation_text="Low ≤30", row=1, col=1)
    fig.add_hline(y=45, line_dash="dot", line_color=G['amber'], annotation_text="High ≥45", row=1, col=1)
    fig.add_trace(go.Scatter(name='Bottom 40%', x=df['Year_Label'], y=df['Poor_Consumption_Share'], line=dict(color=G['green'],width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(name='Top 20%', x=df['Year_Label'], y=df['Rich_Consumption_Share'], line=dict(color=G['red'],width=2.5,dash='dot')), row=1, col=2)
    dc = [G['green'] if v<=0 else G['red'] for v in df['Distribution_Impact']]
    fig.add_trace(go.Bar(name='Distribution Impact', x=df['Year_Label'], y=df['Distribution_Impact'], marker_color=dc, opacity=0.82), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=2, col=1)
    fig.add_trace(go.Scatter(name='Poverty Rate', x=df['Year_Label'], y=df['Poverty_Rate'], line=dict(color=G['amber'],width=2.5)), row=2, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(name='Gini', x=df['Year_Label'], y=df['Gini_Coefficient'], line=dict(color=G['red'],width=2,dash='dot')), row=2, col=2, secondary_y=True)
    style_fig(fig, 480)
    st.plotly_chart(fig, use_container_width=True)

# TAB 4 - MONETARY
with tabs[4]:
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["Policy Rate vs Inflation Gap","Real Interest Rate (%)","Inflation Convergence Path","Monetary Impact on Growth (pp)"],
        specs=[[{"secondary_y":True},{"secondary_y":False}],[{"secondary_y":False},{"secondary_y":False}]],
        vertical_spacing=0.14, horizontal_spacing=0.1)
    fig.add_trace(go.Scatter(name='Policy Rate', x=df['Year_Label'], y=df['Policy_Rate'], line=dict(color=G['info'],width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(name='Inflation Gap', x=df['Year_Label'], y=df['Inflation_Gap'], line=dict(color=G['red'],width=2.5,dash='dot')), row=1, col=1, secondary_y=True)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(name='Real Rate', x=df['Year_Label'], y=df['Real_Interest_Rate'],
        line=dict(color='#8E44AD',width=2.5), fill='tozeroy', fillcolor='rgba(142,68,173,0.08)'), row=1, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=1, col=2)
    fig.add_trace(go.Scatter(name='Inflation', x=df['Year_Label'], y=df['Inflation'], line=dict(color=G['red'],width=2.5)), row=2, col=1)
    fig.add_hline(y=9.0, line_dash="dash", line_color=G['green'], annotation_text="CBN Target 9%", row=2, col=1)
    fig.add_hline(y=15.0, line_dash="dot", line_color=G['amber'], annotation_text="15%", row=2, col=1)
    mc = [G['green'] if v>=0 else G['red'] for v in df['Monetary_Impact']]
    fig.add_trace(go.Bar(name='Monetary Impact', x=df['Year_Label'], y=df['Monetary_Impact'], marker_color=mc, opacity=0.82), row=2, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=2, col=2)
    style_fig(fig, 480)
    st.plotly_chart(fig, use_container_width=True)

# TAB 5 - EXTERNAL
with tabs[5]:
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["Current Account Balance ($B)","Trade Composition ($B)","FX Reserve Adequacy (months)","Oil Revenue Dependency (%)"],
        vertical_spacing=0.14, horizontal_spacing=0.1)
    ca_c = [G['green'] if v>=0 else G['red'] for v in df['Current_Account']]
    fig.add_trace(go.Bar(name='Current Account', x=df['Year_Label'], y=df['Current_Account'], marker_color=ca_c, opacity=0.82), row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=1, col=1)
    fig.add_trace(go.Scatter(name='Exports', x=df['Year_Label'], y=df['Exports'], line=dict(color=G['green'],width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(name='Imports', x=df['Year_Label'], y=df['Imports'], line=dict(color=G['red'],width=2.5,dash='dot')), row=1, col=2)
    fig.add_trace(go.Scatter(name='Import Cover', x=df['Year_Label'], y=df['Import_Cover'],
        line=dict(color=G['info'],width=2.5), fill='tozeroy', fillcolor='rgba(26,82,118,0.07)'), row=2, col=1)
    fig.add_hline(y=3, line_dash="dash", line_color=G['red'], annotation_text="Min 3 months", row=2, col=1)
    fig.add_hline(y=6, line_dash="dot", line_color=G['green'], annotation_text="Comfortable 6m", row=2, col=1)
    fig.add_trace(go.Scatter(name='Oil Dependency', x=df['Year_Label'], y=df['Oil_Dependency'],
        line=dict(color=G['gold'],width=2.5), fill='tozeroy', fillcolor='rgba(200,146,42,0.08)'), row=2, col=2)
    fig.add_hline(y=50, line_dash="dash", line_color=G['amber'], annotation_text="Diversification 50%", row=2, col=2)
    style_fig(fig, 480)
    st.plotly_chart(fig, use_container_width=True)

# TAB 6 - STRUCTURAL
with tabs[6]:
    if structural_reform:
        st.markdown(ic("green","✓ Structural Reforms Active","Tax reform, business climate improvements, anti-corruption measures modelled. Reform dividend builds over the simulation horizon."), unsafe_allow_html=True)
    else:
        st.markdown(ic("amber","⚠ Structural Reforms Not Implemented","Growth dividend from structural reform not captured. Activate in the sidebar to model reform scenarios."), unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["Poverty Rate & Unemployment (%)","Informal Sector Share (%)","Reform Growth Dividend (pp)","Social Progress Index"],
        specs=[[{"secondary_y":True},{"secondary_y":False}],[{"secondary_y":False},{"secondary_y":False}]],
        vertical_spacing=0.14, horizontal_spacing=0.1)
    fig.add_trace(go.Scatter(name='Poverty Rate', x=df['Year_Label'], y=df['Poverty_Rate'], line=dict(color=G['red'],width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(name='Unemployment', x=df['Year_Label'], y=df['Unemployment_Rate'], line=dict(color=G['info'],width=2.5,dash='dot')), row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(name='Informal Sector', x=df['Year_Label'], y=df['Informal_Sector_Share'],
        line=dict(color=G['gold'],width=2.5), fill='tozeroy', fillcolor='rgba(200,146,42,0.08)'), row=1, col=2)
    fig.add_hline(y=30, line_dash="dash", line_color=G['green'], annotation_text="Target 30%", row=1, col=2)
    rc = [G['green'] if v>0 else G['border'] for v in df['Structural_Impact']]
    fig.add_trace(go.Bar(name='Reform Dividend', x=df['Year_Label'], y=df['Structural_Impact'], marker_color=rc, opacity=0.82), row=2, col=1)
    fig.add_trace(go.Scatter(name='Social Progress', x=df['Year_Label'], y=df['Social_Progress'],
        line=dict(color='#8E44AD',width=2.5), fill='tozeroy', fillcolor='rgba(142,68,173,0.07)'), row=2, col=2)
    style_fig(fig, 480)
    st.plotly_chart(fig, use_container_width=True)

# TAB 7 - SCENARIO COMPARISON
with tabs[7]:
    st.markdown("Save the current simulation as Scenario A or B, then compare side-by-side.")
    s1, s2 = st.columns(2)
    with s1:
        if st.button("💾 Save as Scenario A", use_container_width=True):
            st.session_state.scenario_a = {"df": df.copy(), "label": f"A: g={baseline_growth}%, Spend={spending_change:+.0f}%, Tax={tax_change:+.0f}%, Oil={oil_price_shock:+.0f}%"}
            st.success("Scenario A saved.")
    with s2:
        if st.button("💾 Save as Scenario B", use_container_width=True):
            st.session_state.scenario_b = {"df": df.copy(), "label": f"B: g={baseline_growth}%, Spend={spending_change:+.0f}%, Tax={tax_change:+.0f}%, Oil={oil_price_shock:+.0f}%"}
            st.success("Scenario B saved.")
    if st.session_state.scenario_a and st.session_state.scenario_b:
        da = st.session_state.scenario_a["df"]; db = st.session_state.scenario_b["df"]
        la = st.session_state.scenario_a["label"]; lb = st.session_state.scenario_b["label"]
        metrics = ['GDP_Growth','Inflation','Debt_to_GDP','Fiscal_Impulse','Gini_Coefficient','Poverty_Rate']
        titles = ['GDP Growth (%)','Inflation (%)','Debt/GDP (%)','Fiscal Impulse (%)','Gini Coefficient','Poverty Rate (%)']
        fig = make_subplots(rows=2, cols=3, subplot_titles=titles, vertical_spacing=0.16, horizontal_spacing=0.1)
        pos = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3)]
        for m, t, (r,c) in zip(metrics, titles, pos):
            fig.add_trace(go.Scatter(name=la[:25], x=da['Year_Label'], y=da[m], line=dict(color=G['green'],width=2.5),
                legendgroup="A", showlegend=(r==1 and c==1)), row=r, col=c)
            fig.add_trace(go.Scatter(name=lb[:25], x=db['Year_Label'], y=db[m], line=dict(color=G['red'],width=2.5,dash='dot'),
                legendgroup="B", showlegend=(r==1 and c==1)), row=r, col=c)
        style_fig(fig, 520)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**End-Period Comparison (Scenario B − A)**")
        names = ['GDP Growth','Inflation','Debt/GDP','Fiscal Impulse','Gini','Poverty Rate','Unemployment']
        flds = ['GDP_Growth','Inflation','Debt_to_GDP','Fiscal_Impulse','Gini_Coefficient','Poverty_Rate','Unemployment_Rate']
        rows = [{"Indicator":n,"Scenario A":f"{da[f].iloc[-1]:.1f}","Scenario B":f"{db[f].iloc[-1]:.1f}","Δ (B−A)":f"{db[f].iloc[-1]-da[f].iloc[-1]:+.1f}"} for n, f in zip(names, flds)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Set sliders to Scenario A, save it, then change parameters and save Scenario B to compare.")

# TAB 8 - MODEL MECHANICS
with tabs[8]:
    with st.expander("Model Architecture Overview", expanded=True):
        st.markdown(f"""
This simulator implements a **DSGE-inspired calibrated structural framework**, running annual simulations 
over a {SIM_YEARS[0]}–{SIM_YEARS[-1]} horizon with four integrated policy channels:

- **Fiscal Channel** — revenue composition, expenditure, debt dynamics, fiscal impulse, fiscal incidence  
- **Monetary Channel** — CBN reaction function (hawkish/dovish/automatic), inflation targeting, real rate determination  
- **External Channel** — exchange rate determination, FX reserve dynamics, trade balance  
- **Structural Channel** — reform dividend, poverty/informality dynamics, inequality-growth nexus  

Calibrated to Nigeria 2024 (CBN Statistical Bulletin · NBS GDP releases · DMO Debt Reports · FMFBNP MTEF/FSP).
Policy thresholds: DSA Prudent Debt Cap **{DSA_DEBT_CAP:.0f}% GDP** · FRA Deficit Cap **{FRA_DEFICIT_CAP:.0f}% GDP** · CBN Inflation Target **9.0%**
        """)
    with st.expander("National Income & Growth"):
        st.markdown('<div class="eq">GDPₜ = GDPₜ₋₁ × (1 + gₜ/100)\n\ngₜ = gᴮ + Δᴹ + Δᶠ + Δˣ + Δˢ + Δᴰ − Ω\n\n  gᴮ = Baseline growth (exogenous input)\n  Δᴹ = Monetary policy impact on growth\n  Δᶠ = Fiscal multiplier effect\n  Δˣ = Net trade effect (Marshall-Lerner)\n  Δˢ = Structural reform dividend\n  Δᴰ = Inequality-growth nexus (−ΔGini × 0.1)\n  Ω   = Crowding-out effect</div>', unsafe_allow_html=True)
    with st.expander("Fiscal Block"):
        st.markdown('<div class="eq">Revenue:\n  Rᴼᶦˡ  = Pᴼᶦˡ × κ         κ = 0.33 $/bbl sensitivity\n  Rᴺᴼ   = Rᴺᴼₜ₋₁ × (1+τ/100) × (1+gᴮ/100)\n  Rᵀᵒᵗ  = Rᴼᶦˡ + Rᴺᴼ\n\nSpending:\n  Gₜ = Gₜ₋₁ × (1+γ/100) × η       η=1.0 base | 1.1 with reforms\n\nDebt:\n  Dₜ = Dₜ₋₁ + (Gₜ + Sᴰᵉᵇᵗ − Rᵀᵒᵗ)\n  Sᴰᵉᵇᵗ = Dₜ₋₁ × (rˢᵒᵛ/100)    rˢᵒᵛ = rᴾᵒˡ + ρᴿᶦˢᵏ</div>', unsafe_allow_html=True)
    with st.expander("Risk Premium & DSA Thresholds"):
        st.markdown(f'<div class="eq">ρᴿᶦˢᵏ = ρᴰᵉᵇᵗ + ρᴿᵉˢᵉʳᵛᵉ + ρᴿᵉᶠᵒʳᵐ\n\nρᴰᵉᵇᵗ   = max(0, (D/GDP − 50) × 0.15)\nρᴿᵉˢᵉʳᵛᵉ = 3.0% if cover<3m | 1.5% if cover<6m | 0 otherwise\nρᴿᵉᶠᵒʳᵐ = −2.0% if structural reforms active\n\nPolicy Anchors:\n  DSA Prudent Threshold: {DSA_DEBT_CAP:.0f}% of GDP\n  FRA 2007 Deficit Cap:   {FRA_DEFICIT_CAP:.0f}% of GDP\n  IMF High-Debt Ceiling: 80% of GDP\n  IMF DSR Benchmark:     30% of Revenue</div>', unsafe_allow_html=True)
    with st.expander("CBN Monetary Policy Reaction Function"):
        st.markdown('<div class="eq">Δrᴾᵒˡ = f(π − π*, economic_condition, stance)\n\nHAWKISH:   (π−π*)>5 → Δr = min(4.0, (π−π*)×0.5)\n           (π−π*)>2 → Δr = (π−π*)×0.3\nDOVISH:    (π−π*)>10→ Δr = (π−π*)×0.2\n           (π−π*)>5 → Δr = (π−π*)×0.1\nAUTOMATIC: (π−π*)>8 → Δr = (π−π*)×0.4\n           (π−π*)>4 → Δr = (π−π*)×0.25\n           recession & low π → Δr = −1.0\n\nπ* = 9.0%  |  Policy rate floor: 12.0%\nMonetary growth impact: Δᴹ = −Δrᴾᵒˡ × (0.2 + reform_effect)</div>', unsafe_allow_html=True)
    with st.expander("Exchange Rate & Trade"):
        st.markdown('<div class="eq">ΔEₜ = [θᴬ + θᴼᶦˡ + θᴿ + θᴮ + θᴿᵉᶠ] / 10\n\nθᴬ  = −(CA/GDP₀)×50              Current account pressure\nθᴼᶦˡ = (Rᴼᶦˡ − R₀ᴼᶦˡ)/R₀ᴼᶦˡ×(−100) Oil revenue effect\nθᴿ  = (rᴾᵒˡ − 6.0)×(−2)          Interest rate differential\nθᴿᵉᶠ = −20 if reforms              Confidence premium\n\nMₜ = GDPₜ × 0.14 × (1 + gₜ/100 × 0.8)    Imports\nXₜ = GDPₜ × 0.11 × (1 + εₜᵉˣᵖ/100)       Exports\nεₜᵉˣᵖ = max(0, ΔEₜ) × 0.6                 Export response</div>', unsafe_allow_html=True)
    with st.expander("Fiscal Incidence & Inequality"):
        st.markdown('<div class="eq">ΔGini = f(τ, γ, progressive_tax, pro_poor)\n\nProgressive tax & τ>0:   ΔGini −= 0.5×(τ/10)\nRegressive  tax & τ>0:   ΔGini += 0.3×(τ/10)\nPro-poor spending & γ>0: ΔGini −= 0.8×(γ/10)\nGeneral spending & γ>0:  ΔGini −= 0.2×(γ/10)\n\nGiniₜ = max(20, min(60, Giniₜ₋₁ + ΔGini×2))\nInequality-growth nexus: Δᴰ = ΔGini × 0.1</div>', unsafe_allow_html=True)
    with st.expander("Policy Transmission Channels"):
        td = pd.DataFrame({
            'Instrument':['Fiscal Expansion','Tax Reform','Monetary Tightening','Structural Reforms'],
            'Primary Channel':['Demand stimulus','Incentive effects','Interest rate','Efficiency gains'],
            'Multiplier (normal)':['0.6×','0.3×','−0.2pp/pp','0.2pp + time dividend'],
            'Horizon':['Short-term','Medium-term','Short-medium','Long-term'],
            'Nigeria Context':['Oil dep. limits space','Narrow tax base','High inflation premium','Informality & governance'],
        })
        st.dataframe(td, use_container_width=True, hide_index=True)
    with st.expander("Model Limitations & Boundary Conditions"):
        lc, rc = st.columns(2)
        with lc:
            st.markdown("**Simplifications**\n- Annual (not quarterly) frequency\n- Constant elasticities within periods\n- No explicit financial/credit channel\n- Simplified expectations formation\n- No regional/sectoral disaggregation\n- No demographic dynamics")
        with rc:
            st.markdown("**Hard Bounds**\n- Policy rate floor: 12.0%\n- Max annual FX change: ±20%\n- Min FX reserves: $5B\n- Min poverty rate: 20%\n- Min informal sector: 30%\n- Gini bounds: [20, 60]\n- Max inflation: 50%")

# ---- DATA EXPORT ----
st.markdown('<div class="sh">📥 Data Export</div>', unsafe_allow_html=True)
ec1, ec2, ec3 = st.columns([3, 1, 1])
with ec1:
    with st.expander("📋 Full Projection Data Table"):
        disp_cols = {
            'Year_Label':'Year','GDP':'GDP ($B)','GDP_Growth':'Growth (%)','Inflation':'Inflation (%)',
            'Policy_Rate':'Policy Rate (%)','Debt_to_GDP':'Debt/GDP (%)','Deficit_to_GDP':'Deficit/GDP (%)',
            'Debt_Service_Ratio':'DSR (%)','Total_Revenue':'Revenue ($B)','Oil_Revenue':'Oil Rev ($B)',
            'Non_Oil_Revenue':'Non-Oil Rev ($B)','Spending':'Spending ($B)','Debt_Service':'Debt Svc ($B)',
            'Fiscal_Impulse':'FI (%)','Structural_Balance':'Struct Bal (%)','Gini_Coefficient':'Gini',
            'Poverty_Rate':'Poverty (%)','Unemployment_Rate':'Unemp (%)','Foreign_Reserves':'FX Res ($B)',
            'Import_Cover':'Import Cover (mo)','Exchange_Rate':'NGN/USD',
        }
        disp = df[list(disp_cols.keys())].copy()
        disp.columns = list(disp_cols.values())
        for c in disp.columns[1:]: disp[c] = disp[c].round(2)
        st.dataframe(disp, use_container_width=True, hide_index=True)
with ec2:
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    st.download_button("⬇️ Download CSV", csv_buf.getvalue(),
        f"nigeria_sim_v4_{SIM_YEARS[0]}-{SIM_YEARS[-1]}.csv", "text/csv", use_container_width=True)
with ec3:
    summary = {
        "simulation_date": datetime.now().strftime("%Y-%m-%d"),
        "horizon": f"{SIM_YEARS[0]}-{SIM_YEARS[-1]}",
        "parameters": {"growth": baseline_growth, "tax": tax_change, "spending": spending_change,
                       "oil_shock": oil_price_shock, "monetary": monetary_response,
                       "reform": structural_reform, "progressive_tax": progressive_tax, "pro_poor": pro_poor_spending},
        "outcomes": {"streamlit run app.pyavg_growth": round(avg_growth,2), "end_debt_gdp": round(debt_end,2),
                     "end_inflation": round(inf_end,2), "avg_fiscal_impulse": round(avg_impulse,2),
                     "end_gini": round(gini_end,2), "dsr_end": round(dsr_end,2)},
    }
    st.download_button("⬇️ Download JSON", json.dumps(summary, indent=2),
        f"nigeria_sim_summary_{SIM_YEARS[0]}.json", "application/json", use_container_width=True)

# ---- FOOTER ----
st.markdown(f"""
<div class="sim-footer">
  <div>
    <div class="fb">Nigeria Integrated Fiscal-Monetary-Structural Simulator</div>
    <div class="fm">Ahmad Ilu · Bayero University Kano · <a href="mailto:aii2400012.pec@buk.edu.ng" style="color:{G['green']};">aii2400012.pec@buk.edu.ng</a> · <a href="https://twitter.com/Iluahmad_" style="color:{G['green']};">@Iluahmad_</a></div>
    <div class="fm">Calibrated to Nigeria 2024 data (CBN · NBS · DMO · FMFBNP) · © Ahmad Ilu {datetime.now().year} · All rights reserved</div>
  </div>
  <div><span class="fv">v4.0 — Global Standard Edition</span></div>
</div>
""", unsafe_allow_html=True)