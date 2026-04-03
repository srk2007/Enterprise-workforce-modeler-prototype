import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    layout="wide",
    page_title="Enterprise Workforce Scenario Modeler | Standard Chartered"
)

# -----------------------------
# PAGE STYLING
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.main {
    background-color: #0b1220;
}

.banner {
    background: linear-gradient(90deg, #0072CE, #00A3E0);
    padding: 18px 24px;
    border-radius: 14px;
    margin-bottom: 10px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

.banner-title {
    font-size: 32px;
    font-weight: 700;
    color: white;
    line-height: 1.2;
}

.banner-sub {
    font-size: 14px;
    color: #EAF6FF;
    margin-top: 4px;
    letter-spacing: 0.3px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 4px;
}

.soft-caption {
    color: #a8b3c7;
    font-size: 13px;
    margin-bottom: 18px;
}

[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #1f2937;
    padding: 14px 16px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18);
}

[data-testid="stSidebar"] {
    background-color: #121826;
}

.block-container {
    padding-top: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
    <div class="banner-title">Enterprise Workforce Scenario Modeler</div>
    <div class="banner-sub">Standard Chartered</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="soft-caption">Interactive simulation of workforce, cost drivers and strategic levers across the enterprise</div>',
    unsafe_allow_html=True
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Cleansed_SCB_HC_2026.csv")
    rates = pd.read_csv("SCB_Rate_Card_2026.csv")

    df.columns = df.columns.str.strip()
    rates.columns = rates.columns.str.strip()
    return df, rates


df_base, rates_df = load_data()

# -----------------------------
# SETUP
# -----------------------------
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_order = {m: i + 1 for i, m in enumerate(months)}

required_workforce_cols = ["Country", "Location_Type", "MT", "Cost Centre", "Grade"]
missing_workforce = [c for c in required_workforce_cols if c not in df_base.columns]
if missing_workforce:
    st.error(f"Missing required columns in workforce file: {missing_workforce}")
    st.write("Available workforce columns:", df_base.columns.tolist())
    st.stop()

if "Monthly_Rate_USD" in rates_df.columns:
    rate_col = "Monthly_Rate_USD"
elif "Annual_Rate_USD" in rates_df.columns:
    rate_col = "Annual_Rate_USD"
else:
    st.error("Rate card must contain either Monthly_Rate_USD or Annual_Rate_USD")
    st.write("Available rate columns:", rates_df.columns.tolist())
    st.stop()

# -----------------------------
# TRANSFORM TO LONG FORMAT
# -----------------------------
records = []
for _, row in df_base.iterrows():
    for m in months:
        records.append({
            "MT": row["MT"],
            "Country": row["Country"],
            "Location_Type": row["Location_Type"],
            "Cost_Centre": row["Cost Centre"],
            "Grade": row["Grade"],
            "Month": m,
            "Month_Num": month_order[m],
            "HC": pd.to_numeric(row.get(f"{m}_HC", 0), errors="coerce"),
            "Budget_HC": pd.to_numeric(row.get(f"{m}_Budget", 0), errors="coerce")
        })

df = pd.DataFrame(records)
df["HC"] = df["HC"].fillna(0)
df["Budget_HC"] = df["Budget_HC"].fillna(0)

df = df.merge(
    rates_df[["Country", "Grade", rate_col]],
    on=["Country", "Grade"],
    how="left"
)

if rate_col == "Annual_Rate_USD":
    df["Base_Rate_Monthly"] = pd.to_numeric(df[rate_col], errors="coerce").fillna(0) / 12
else:
    df["Base_Rate_Monthly"] = pd.to_numeric(df[rate_col], errors="coerce").fillna(0)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("## Scenario Controls")

    mt = st.selectbox("Management Team", ["All"] + sorted(df["MT"].dropna().unique().tolist()))
    country = st.selectbox("Country", ["All"] + sorted(df["Country"].dropna().unique().tolist()))
    location_type = st.selectbox("Location Type", ["All"] + sorted(df["Location_Type"].dropna().unique().tolist()))

    st.markdown("---")
    st.markdown("### KPI Month")
    kpi_month = st.selectbox("Select month for HC / cost-per-HC view", months, index=11)

    st.markdown("---")
    st.markdown("### Variable Adjustments")
    salary_inflation = st.slider("Salary Inflation %", -20, 30, 0, 1)
    hiring_change = st.slider("Hiring Change %", -50, 50, 0, 1)
    attrition = st.slider("Attrition %", 0, 50, 10, 1)
    offshore_shift = st.slider("Shift Onshore to Offshore %", 0, 100, 0, 5)

    st.markdown("---")
    st.markdown("### Grade Actions")
    grade_options = sorted(df["Grade"].dropna().unique().tolist())

    eliminate_grade = st.multiselect("Eliminate Grades", grade_options)
    elim_month = st.selectbox("Elimination Start Month", months)

    optimise_from = st.selectbox("Optimise From Grade", ["None"] + grade_options)
    optimise_to = st.selectbox("Optimise To Grade", ["None"] + grade_options)
    optimise_pct = st.slider("Optimisation % of HC shifted", 0, 100, 0, 5)

    st.markdown("---")
    payoff_driver = st.selectbox(
        "Payoff Graph Driver",
        ["Salary Inflation %", "Hiring Change %", "Attrition %", "Offshore Shift %"]
    )

# -----------------------------
# FILTER DATA
# -----------------------------
df_sim = df.copy()

if mt != "All":
    df_sim = df_sim[df_sim["MT"] == mt]
if country != "All":
    df_sim = df_sim[df_sim["Country"] == country]
if location_type != "All":
    df_sim = df_sim[df_sim["Location_Type"] == location_type]

if df_sim.empty:
    st.warning("No data after applying filters.")
    st.stop()

# -----------------------------
# BASE CASE
# -----------------------------
df_basecase = df_sim.copy()
df_basecase["Base_Cost"] = df_basecase["HC"] * df_basecase["Base_Rate_Monthly"]
df_basecase["Budget_Cost"] = df_basecase["Budget_HC"] * df_basecase["Base_Rate_Monthly"]

# -----------------------------
# SCENARIO ENGINE
# -----------------------------
def run_scenario(
    input_df,
    salary_inflation_pct=0,
    hiring_change_pct=0,
    attrition_pct=10,
    offshore_shift_pct=0,
    eliminate_grades=None,
    elimination_month="Dec",
    optimise_from_grade="None",
    optimise_to_grade="None",
    optimise_pct_val=0
):
    scenario = input_df.copy()

    # Rate adjustment
    scenario["Adj_Rate"] = scenario["Base_Rate_Monthly"] * (1 + salary_inflation_pct / 100)

    # Proper workforce flow:
    # Adjusted HC = Baseline HC - Attrition HC + Hiring HC
    scenario["Attrition_HC"] = scenario["HC"] * (attrition_pct / 100)
    scenario["Hiring_HC"] = scenario["HC"] * (hiring_change_pct / 100)
    scenario["Adj_HC"] = scenario["HC"] - scenario["Attrition_HC"] + scenario["Hiring_HC"]

    # Prevent negative HC
    scenario["Adj_HC"] = scenario["Adj_HC"].clip(lower=0)

    # Grade elimination from selected month onward
    if eliminate_grades:
        elim_num = month_order[elimination_month]
        scenario.loc[
            (scenario["Grade"].isin(eliminate_grades)) &
            (scenario["Month_Num"] >= elim_num),
            "Adj_HC"
        ] = 0

    # Grade optimisation
    if (
        optimise_from_grade != "None"
        and optimise_to_grade != "None"
        and optimise_from_grade != optimise_to_grade
        and optimise_pct_val > 0
    ):
        shift_df = (
            scenario[scenario["Grade"] == optimise_from_grade]
            .groupby(["MT", "Country", "Location_Type", "Cost_Centre", "Month", "Month_Num"], as_index=False)["Adj_HC"]
            .sum()
        )
        shift_df["Shift_HC"] = shift_df["Adj_HC"] * (optimise_pct_val / 100)

        for _, r in shift_df.iterrows():
            mask_from = (
                (scenario["MT"] == r["MT"]) &
                (scenario["Country"] == r["Country"]) &
                (scenario["Location_Type"] == r["Location_Type"]) &
                (scenario["Cost_Centre"] == r["Cost_Centre"]) &
                (scenario["Month"] == r["Month"]) &
                (scenario["Grade"] == optimise_from_grade)
            )
            scenario.loc[mask_from, "Adj_HC"] -= r["Shift_HC"]

            mask_to = (
                (scenario["MT"] == r["MT"]) &
                (scenario["Country"] == r["Country"]) &
                (scenario["Location_Type"] == r["Location_Type"]) &
                (scenario["Cost_Centre"] == r["Cost_Centre"]) &
                (scenario["Month"] == r["Month"]) &
                (scenario["Grade"] == optimise_to_grade)
            )
            if mask_to.any():
                scenario.loc[mask_to, "Adj_HC"] += r["Shift_HC"]

        scenario["Adj_HC"] = scenario["Adj_HC"].clip(lower=0)

    # Prototype offshore rate discount assumption
    onshore_mask = scenario["Location_Type"].astype(str).str.lower() == "onshore"
    offshore_discount = 0.30
    scenario.loc[onshore_mask, "Adj_Rate"] = scenario.loc[onshore_mask, "Adj_Rate"] * (
        1 - (offshore_shift_pct / 100) * offshore_discount
    )

    scenario["Scenario_Cost"] = scenario["Adj_HC"] * scenario["Adj_Rate"]
    return scenario


df_scn = run_scenario(
    df_sim,
    salary_inflation_pct=salary_inflation,
    hiring_change_pct=hiring_change,
    attrition_pct=attrition,
    offshore_shift_pct=offshore_shift,
    eliminate_grades=eliminate_grade,
    elimination_month=elim_month,
    optimise_from_grade=optimise_from,
    optimise_to_grade=optimise_to,
    optimise_pct_val=optimise_pct
)

df_scn["Base_Cost"] = df_basecase["Base_Cost"].values
df_scn["Budget_Cost"] = df_basecase["Budget_Cost"].values

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
base_total = df_basecase["Base_Cost"].sum()
budget_total = df_basecase["Budget_Cost"].sum()
scenario_total = df_scn["Scenario_Cost"].sum()

var_budget_vs_base = budget_total - base_total
var_scenario_vs_base = scenario_total - base_total
var_scenario_vs_budget = scenario_total - budget_total

base_snap = df_basecase[df_basecase["Month"] == kpi_month].copy()
scn_snap = df_scn[df_scn["Month"] == kpi_month].copy()

base_hc = base_snap["HC"].sum()
budget_hc = base_snap["Budget_HC"].sum()
scenario_hc = scn_snap["Adj_HC"].sum()

base_month_cost = base_snap["Base_Cost"].sum()
budget_month_cost = base_snap["Budget_Cost"].sum()
scenario_month_cost = scn_snap["Scenario_Cost"].sum()

hc_var_budget_vs_base = budget_hc - base_hc
hc_var_scenario_vs_base = scenario_hc - base_hc
hc_var_scenario_vs_budget = scenario_hc - budget_hc

base_cost_per_hc = base_month_cost / base_hc if base_hc != 0 else 0
budget_cost_per_hc = budget_month_cost / budget_hc if budget_hc != 0 else 0
scenario_cost_per_hc = scenario_month_cost / scenario_hc if scenario_hc != 0 else 0

# -----------------------------
# HELPERS
# -----------------------------
def cost_delta_text(val):
    arrow = "↓" if val < 0 else "↑"
    return f"{arrow} ${abs(val):,.0f} vs Base"

def hc_delta_text(val):
    arrow = "↓" if val < 0 else "↑"
    return f"{arrow} {abs(val):,.1f} vs Base"

# -----------------------------
# COST OVERVIEW
# -----------------------------
st.markdown('<div class="section-title">💰 Cost Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Baseline Annual Cost", f"${base_total:,.0f}")
c2.metric("Budget Annual Cost", f"${budget_total:,.0f}", delta=cost_delta_text(var_budget_vs_base), delta_color="inverse")
c3.metric("Scenario Annual Cost", f"${scenario_total:,.0f}", delta=cost_delta_text(var_scenario_vs_base), delta_color="inverse")
c4.metric("Scenario vs Budget", f"${var_scenario_vs_budget:,.0f}")
c5.metric(f"{kpi_month} Avg Cost / HC", f"${scenario_cost_per_hc:,.0f}")

# -----------------------------
# HC OVERVIEW
# -----------------------------
st.markdown('<div class="section-title">👥 Workforce Snapshot</div>', unsafe_allow_html=True)

h1, h2, h3, h4, h5 = st.columns(5)
h1.metric("Baseline HC", f"{base_hc:,.1f}")
h2.metric("Budget HC", f"{budget_hc:,.1f}", delta=hc_delta_text(hc_var_budget_vs_base))
h3.metric("Scenario HC", f"{scenario_hc:,.1f}", delta=hc_delta_text(hc_var_scenario_vs_base))
h4.metric("Scenario HC vs Budget", f"{hc_var_scenario_vs_budget:,.1f}")
h5.metric("Avg Cost / HC (Base/Bud/Scn)", f"${base_cost_per_hc:,.0f} / ${budget_cost_per_hc:,.0f} / ${scenario_cost_per_hc:,.0f}")

# -----------------------------
# PAYOFF GRAPH
# -----------------------------
def payoff_series(driver_name):
    if driver_name == "Salary Inflation %":
        x_vals = list(range(-20, 31, 5))
    elif driver_name == "Hiring Change %":
        x_vals = list(range(-30, 31, 5))
    elif driver_name == "Attrition %":
        x_vals = list(range(0, 41, 5))
    else:
        x_vals = list(range(0, 101, 10))

    y_vals = []

    for x in x_vals:
        if driver_name == "Salary Inflation %":
            temp = run_scenario(
                df_sim,
                salary_inflation_pct=x,
                hiring_change_pct=hiring_change,
                attrition_pct=attrition,
                offshore_shift_pct=offshore_shift,
                eliminate_grades=eliminate_grade,
                elimination_month=elim_month,
                optimise_from_grade=optimise_from,
                optimise_to_grade=optimise_to,
                optimise_pct_val=optimise_pct
            )
        elif driver_name == "Hiring Change %":
            temp = run_scenario(
                df_sim,
                salary_inflation_pct=salary_inflation,
                hiring_change_pct=x,
                attrition_pct=attrition,
                offshore_shift_pct=offshore_shift,
                eliminate_grades=eliminate_grade,
                elimination_month=elim_month,
                optimise_from_grade=optimise_from,
                optimise_to_grade=optimise_to,
                optimise_pct_val=optimise_pct
            )
        elif driver_name == "Attrition %":
            temp = run_scenario(
                df_sim,
                salary_inflation_pct=salary_inflation,
                hiring_change_pct=hiring_change,
                attrition_pct=x,
                offshore_shift_pct=offshore_shift,
                eliminate_grades=eliminate_grade,
                elimination_month=elim_month,
                optimise_from_grade=optimise_from,
                optimise_to_grade=optimise_to,
                optimise_pct_val=optimise_pct
            )
        else:
            temp = run_scenario(
                df_sim,
                salary_inflation_pct=salary_inflation,
                hiring_change_pct=hiring_change,
                attrition_pct=attrition,
                offshore_shift_pct=x,
                eliminate_grades=eliminate_grade,
                elimination_month=elim_month,
                optimise_from_grade=optimise_from,
                optimise_to_grade=optimise_to,
                optimise_pct_val=optimise_pct
            )

        y_vals.append(temp["Scenario_Cost"].sum() - budget_total)

    return x_vals, y_vals


x_vals, y_vals = payoff_series(payoff_driver)

payoff_fig = go.Figure()

payoff_fig.add_trace(go.Scatter(
    x=x_vals,
    y=[y if y > 0 else 0 for y in y_vals],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(255, 80, 80, 0.35)",
    line=dict(color="rgba(255, 80, 80, 1)", width=2),
    name="Over Budget",
    hovertemplate="Driver: %{x}<br>Over Budget: $%{y:,.0f}<extra></extra>"
))

payoff_fig.add_trace(go.Scatter(
    x=x_vals,
    y=[y if y < 0 else 0 for y in y_vals],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(0, 180, 90, 0.35)",
    line=dict(color="rgba(0, 180, 90, 1)", width=2),
    name="Under Budget",
    hovertemplate="Driver: %{x}<br>Under Budget: $%{y:,.0f}<extra></extra>"
))

payoff_fig.add_trace(go.Scatter(
    x=x_vals,
    y=y_vals,
    mode="lines+markers",
    line=dict(color="white", width=3),
    marker=dict(size=6),
    name="Net Outcome",
    hovertemplate="Driver: %{x}<br>Variance vs Budget: $%{y:,.0f}<extra></extra>"
))

current_x = (
    salary_inflation if payoff_driver == "Salary Inflation %"
    else hiring_change if payoff_driver == "Hiring Change %"
    else attrition if payoff_driver == "Attrition %"
    else offshore_shift
)

payoff_fig.add_trace(go.Scatter(
    x=[current_x],
    y=[var_scenario_vs_budget],
    mode="markers+text",
    marker=dict(size=14, color="yellow", symbol="diamond"),
    text=[f"${var_scenario_vs_budget:,.0f}"],
    textposition="top center",
    name="Current Selection"
))

payoff_fig.add_hline(y=0, line_dash="dash", line_color="gray")

payoff_fig.update_layout(
    title=f"Payoff Curve: {payoff_driver}",
    template="plotly_dark",
    plot_bgcolor="#0b1220",
    paper_bgcolor="#0b1220",
    font=dict(color="white"),
    xaxis=dict(title=payoff_driver, showgrid=False),
    yaxis=dict(title="Annual Variance vs Budget (USD)", gridcolor="#1f2937"),
    hovermode="x unified",
    height=500,
    legend=dict(orientation="v")
)

# -----------------------------
# MONTHLY TREND
# -----------------------------
baseline_trend = (
    df_basecase.groupby(["Month_Num", "Month"], as_index=False)["Base_Cost"]
    .sum().sort_values("Month_Num")
)

budget_trend = (
    df_basecase.groupby(["Month_Num", "Month"], as_index=False)["Budget_Cost"]
    .sum().sort_values("Month_Num")
)

scenario_trend = (
    df_scn.groupby(["Month_Num", "Month"], as_index=False)["Scenario_Cost"]
    .sum().sort_values("Month_Num")
)

trend_fig = go.Figure()
trend_fig.add_trace(go.Scatter(
    x=baseline_trend["Month"],
    y=baseline_trend["Base_Cost"],
    mode="lines+markers",
    line=dict(width=3),
    name="Baseline Cost"
))
trend_fig.add_trace(go.Scatter(
    x=budget_trend["Month"],
    y=budget_trend["Budget_Cost"],
    mode="lines+markers",
    line=dict(width=3),
    name="Budget Cost"
))
trend_fig.add_trace(go.Scatter(
    x=scenario_trend["Month"],
    y=scenario_trend["Scenario_Cost"],
    mode="lines+markers",
    line=dict(width=3),
    name="Scenario Cost"
))

trend_fig.update_layout(
    title="Monthly Cost Trend",
    template="plotly_dark",
    plot_bgcolor="#0b1220",
    paper_bgcolor="#0b1220",
    font=dict(color="white"),
    xaxis=dict(title="Month", showgrid=False),
    yaxis=dict(title="Monthly Cost (USD)", gridcolor="#1f2937"),
    hovermode="x unified",
    height=500,
    legend=dict(orientation="h", y=1.1)
)

# -----------------------------
# CHART LAYOUT
# -----------------------------
left, right = st.columns([1, 2])
with left:
    st.plotly_chart(payoff_fig, use_container_width=True)
with right:
    st.plotly_chart(trend_fig, use_container_width=True)

# -----------------------------
# IMPACT SUMMARY
# -----------------------------
st.markdown('<div class="section-title">📊 Impact Summary</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
s1.metric("Budget vs Base", f"${var_budget_vs_base:,.0f}", delta=cost_delta_text(var_budget_vs_base), delta_color="inverse")
s2.metric("Scenario vs Base", f"${var_scenario_vs_base:,.0f}", delta=cost_delta_text(var_scenario_vs_base), delta_color="inverse")
s3.metric("Scenario vs Budget", f"${var_scenario_vs_budget:,.0f}", delta=cost_delta_text(var_scenario_vs_budget), delta_color="inverse")

# -----------------------------
# SEGMENT VIEW
# -----------------------------
st.markdown('<div class="section-title">🧩 Segment View</div>', unsafe_allow_html=True)

base_seg_snap = df_basecase[df_basecase["Month"] == kpi_month].copy()
scn_seg_snap = df_scn[df_scn["Month"] == kpi_month].copy()

hc_summary = (
    scn_seg_snap.groupby(["MT", "Country", "Location_Type"], as_index=False)
    .agg(
        Baseline_HC=("HC", "sum"),
        Budget_HC=("Budget_HC", "sum"),
        Scenario_HC=("Adj_HC", "sum")
    )
)

base_cost_summary = (
    df_basecase.groupby(["MT", "Country", "Location_Type"], as_index=False)
    .agg(
        Baseline_Cost=("Base_Cost", "sum"),
        Budget_Cost=("Budget_Cost", "sum")
    )
)

scn_cost_summary = (
    df_scn.groupby(["MT", "Country", "Location_Type"], as_index=False)
    .agg(
        Scenario_Cost=("Scenario_Cost", "sum")
    )
)

summary = hc_summary.merge(base_cost_summary, on=["MT", "Country", "Location_Type"], how="outer")
summary = summary.merge(scn_cost_summary, on=["MT", "Country", "Location_Type"], how="outer")

summary["Scenario_vs_Budget"] = summary["Scenario_Cost"] - summary["Budget_Cost"]
summary["Scenario_vs_Base"] = summary["Scenario_Cost"] - summary["Baseline_Cost"]
summary["Avg_Cost_per_HC_Scenario"] = summary["Scenario_Cost"] / summary["Scenario_HC"].replace(0, pd.NA)

st.dataframe(summary, use_container_width=True)

# -----------------------------
# DETAIL TABLE
# -----------------------------
with st.expander("Show detailed monthly data"):
    detail = df_scn[[
        "MT", "Country", "Location_Type", "Cost_Centre", "Grade", "Month",
        "HC", "Budget_HC", "Attrition_HC", "Hiring_HC", "Adj_HC",
        "Base_Rate_Monthly", "Adj_Rate",
        "Base_Cost", "Budget_Cost", "Scenario_Cost"
    ]].copy()
    st.dataframe(detail, use_container_width=True)