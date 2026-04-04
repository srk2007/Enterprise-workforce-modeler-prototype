import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    layout="wide",
    page_title="Enterprise Cost & Workforce Navigator | Standard Chartered"
)

# -----------------------------
# PAGE STYLING
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #F7F9FC;
    color: #111827;
}

.stApp, .main {
    background-color: #F7F9FC;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Banner */
.banner {
    background: linear-gradient(90deg, #0072CE, #18A0E1);
    padding: 22px 24px;
    border-radius: 16px;
    margin-bottom: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    text-align: center;
}
.banner-title {
    font-size: 34px;
    font-weight: 800;
    color: white;
    line-height: 1.2;
    margin-bottom: 4px;
}
.banner-sub {
    font-size: 14px;
    color: #EAF6FF;
    letter-spacing: 0.3px;
}

/* Text */
.section-title {
    font-size: 20px;
    font-weight: 800;
    margin-top: 12px;
    margin-bottom: 10px;
    color: #111827;
}
.soft-caption {
    color: #6B7280;
    font-size: 13px;
    margin-bottom: 18px;
}
.table-note {
    color: #6B7280;
    font-size: 12px;
    margin-top: -2px;
    margin-bottom: 10px;
}

/* KPI Cards */
.kpi-card {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 14px 16px;
    min-height: 118px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
.kpi-title {
    font-size: 12px;
    color: #6B7280;
    font-weight: 600;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
    margin-bottom: 10px;
}
.kpi-chip {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    border-radius: 999px;
    padding: 4px 10px;
}
.kpi-chip-green {
    background-color: #DCFCE7;
    color: #166534;
}
.kpi-chip-red {
    background-color: #FEE2E2;
    color: #991B1B;
}
.kpi-chip-gray {
    background-color: #F3F4F6;
    color: #4B5563;
}

/* Panels */
.panel-card {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
.panel-title {
    font-size: 18px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 4px;
}
.panel-sub {
    font-size: 12px;
    color: #6B7280;
    margin-bottom: 12px;
}

/* Chart wrapper */
.chart-card {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 10px 10px 2px 10px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}

/* Table wrapper */
.table-card {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    overflow-x: auto;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F3F6FA;
    border-right: 1px solid #E5E7EB;
}
.sidebar-title {
    font-size: 20px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 4px;
}
.sidebar-sub {
    font-size: 12px;
    color: #6B7280;
    margin-bottom: 12px;
}
.sidebar-section {
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #4B5563;
    margin-top: 14px;
    margin-bottom: 8px;
}

/* Force select controls readable */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border-radius: 10px !important;
    border-color: #D1D5DB !important;
}
div[data-baseweb="select"] * {
    color: #111827 !important;
    fill: #111827 !important;
}
div[role="listbox"] * {
    color: #111827 !important;
    background-color: #FFFFFF !important;
}
input, textarea {
    color: #111827 !important;
}

/* General control labels */
.stMultiSelect label,
.stSelectbox label,
.stSlider label,
.stNumberInput label,
.stCheckbox label,
.stRadio label,
.stRadio div[role="radiogroup"] label,
.stRadio div[role="radiogroup"] label p {
    color: #111827 !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

.stCaption {
    color: #6B7280 !important;
}

/* -----------------------------
   FIX RADIO BUTTON LABEL VISIBILITY
----------------------------- */
div[data-testid="stRadio"] {
    color: #111827 !important;
}

div[data-testid="stRadio"] > div {
    color: #111827 !important;
}

div[role="radiogroup"] {
    color: #111827 !important;
}

div[role="radiogroup"] label {
    color: #111827 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

div[role="radiogroup"] label p,
div[role="radiogroup"] p {
    color: #111827 !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

div[role="radiogroup"] > label {
    background-color: transparent !important;
}

div[data-testid="stRadio"] label {
    color: #111827 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

div[data-testid="stRadio"] label p {
    color: #111827 !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-weight: 600 !important;
}

/* metric fallback */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    padding: 12px 14px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
[data-testid="stMetricLabel"] { color: #4B5563; }
[data-testid="stMetricValue"] { color: #111827; }

/* Tables */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS - UI
# -----------------------------
def fmt_money(val: float, unit_mode: str = "$") -> str:
    if unit_mode == "$m":
        return f"${val/1_000_000:,.1f}m"
    return f"${val:,.0f}"

def fmt_num(val: float) -> str:
    return f"{val:,.0f}"

def variance_chip_html(val: float, base_for_pct: float | None = None, kind: str = "money", unit_mode: str = "$") -> str:
    arrow = "↓" if val < 0 else "↑"
    css = "kpi-chip-green" if val < 0 else "kpi-chip-red"

    pct_txt = ""
    if base_for_pct is not None and base_for_pct != 0:
        pct = abs(val) / base_for_pct * 100
        pct_txt = f" ({pct:.1f}%)"

    if kind == "money":
        txt = f"{arrow} {fmt_money(abs(val), unit_mode)}{pct_txt} vs Bud"
    else:
        txt = f"{arrow} {abs(val):,.0f}{pct_txt} vs Bud"

    return f'<span class="kpi-chip {css}">{txt}</span>'

def neutral_chip_html(text: str) -> str:
    return f'<span class="kpi-chip kpi-chip-gray">{text}</span>'

def kpi_card(title: str, value: str, delta_html: str | None = None):
    html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html if delta_html else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_styled_table(styler):
    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.markdown(styler.to_html(), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def get_ordered_dimension_values(df_in: pd.DataFrame, row_dim: str):
    values = (
        df_in[row_dim]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )
    unique_values = list(dict.fromkeys(values))

    if row_dim != "Grade":
        return sorted(unique_values)

    seniority_order = (
        ["MD", "ED", "D", "C"] +
        [f"B{i}" for i in range(1, 11)] +
        [f"A{i}" for i in range(1, 11)]
    )

    ordered = [g for g in seniority_order if g in unique_values]
    remaining = sorted([g for g in unique_values if g not in seniority_order])
    return ordered + remaining

# -----------------------------
# BANNER
# -----------------------------
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
    df = pd.read_csv("Cleansed_SCB_HC_2026_4Apr.csv")
    rates = pd.read_csv("SCB_Rate_Card_2026_4Apr.csv")
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
    st.stop()

if "Monthly_Rate_USD" in rates_df.columns:
    rate_col = "Monthly_Rate_USD"
elif "Annual_Rate_USD" in rates_df.columns:
    rate_col = "Annual_Rate_USD"
else:
    st.error("Rate card must contain either Monthly_Rate_USD or Annual_Rate_USD")
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
df["Grade"] = df["Grade"].astype(str).str.strip().str.upper()

rates_df["Grade"] = rates_df["Grade"].astype(str).str.strip().str.upper()

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
    st.markdown('<div class="sidebar-title">Scenario Builder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Define scope and apply workforce/cost levers. KPIs and charts are driven by this pane.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Display</div>', unsafe_allow_html=True)
    unit_mode = st.radio(
        "Financial display",
        options=["$", "$m"],
        index=0,
        horizontal=True
    )

    st.markdown('<div class="sidebar-section">Scope</div>', unsafe_allow_html=True)
    mt = st.selectbox("Management Team", ["All"] + sorted(df["MT"].dropna().unique().tolist()))

    country_options = sorted(df["Country"].dropna().unique().tolist())
    select_all_countries = st.checkbox("Select All Countries", value=True)

    if select_all_countries:
        selected_countries = st.multiselect(
            "Country Scope",
            country_options,
            default=country_options,
            key="country_scope_all"
        )
    else:
        selected_countries = st.multiselect(
            "Country Scope",
            country_options,
            default=[],
            key="country_scope_custom"
        )

    location_type = st.selectbox("Location Type", ["All"] + sorted(df["Location_Type"].dropna().unique().tolist()))

    st.markdown('<div class="sidebar-section">Snapshot</div>', unsafe_allow_html=True)
    kpi_month = st.selectbox("Select month for workforce snapshot", months, index=11)

    st.markdown('<div class="sidebar-section">Levers</div>', unsafe_allow_html=True)
    salary_inflation = st.slider("Salary Inflation %", -20, 30, 0, 1)
    hiring_change = st.slider("Hiring Rate %", -50, 50, 0, 1)
    attrition = st.slider("Attrition %", 0, 50, 10, 1)
    offshore_shift = st.slider("Shift Onshore to Offshore %", 0, 100, 0, 5)

    st.markdown('<div class="sidebar-section">Workforce Actions</div>', unsafe_allow_html=True)
    grade_options = get_ordered_dimension_values(df, "Grade")
    eliminate_grade = st.multiselect("Eliminate Grades", grade_options)
    elim_month = st.selectbox("Elimination Start Month", months)
    optimise_from = st.selectbox("Optimise From Grade", ["None"] + grade_options)
    optimise_to = st.selectbox("Optimise To Grade", ["None"] + grade_options)
    optimise_pct = st.slider("Optimisation % of HC shifted", 0, 100, 0, 5)

# -----------------------------
# FILTER DATA
# -----------------------------
df_sim = df.copy()
if mt != "All":
    df_sim = df_sim[df_sim["MT"] == mt]

if selected_countries:
    df_sim = df_sim[df_sim["Country"].isin(selected_countries)]
else:
    st.warning("Please select at least one country in Country Scope.")
    st.stop()

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
    scenario["Adj_Rate"] = scenario["Base_Rate_Monthly"] * (1 + salary_inflation_pct / 100)

    scenario["Attrition_HC"] = scenario["HC"] * (attrition_pct / 100)
    scenario["Hiring_HC"] = scenario["HC"] * (hiring_change_pct / 100)
    scenario["Adj_HC"] = scenario["HC"] - scenario["Attrition_HC"] + scenario["Hiring_HC"]
    scenario["Adj_HC"] = scenario["Adj_HC"].clip(lower=0)

    scenario["Grade"] = scenario["Grade"].astype(str).str.strip().str.upper()
    eliminate_grades_clean = [g.strip().upper() for g in eliminate_grades] if eliminate_grades else []

    if eliminate_grades_clean:
        elim_num = month_order[elimination_month]
        elim_mask = scenario["Grade"].isin(eliminate_grades_clean) & (scenario["Month_Num"] >= elim_num)
        scenario.loc[elim_mask, "Adj_HC"] = 0

    if (
        optimise_from_grade != "None"
        and optimise_to_grade != "None"
        and optimise_from_grade != optimise_to_grade
        and optimise_pct_val > 0
    ):
        optimise_from_grade_clean = optimise_from_grade.strip().upper()
        optimise_to_grade_clean = optimise_to_grade.strip().upper()

        shift_df = (
            scenario[scenario["Grade"] == optimise_from_grade_clean]
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
                (scenario["Grade"] == optimise_from_grade_clean)
            )
            scenario.loc[mask_from, "Adj_HC"] -= r["Shift_HC"]

            mask_to = (
                (scenario["MT"] == r["MT"]) &
                (scenario["Country"] == r["Country"]) &
                (scenario["Location_Type"] == r["Location_Type"]) &
                (scenario["Cost_Centre"] == r["Cost_Centre"]) &
                (scenario["Month"] == r["Month"]) &
                (scenario["Grade"] == optimise_to_grade_clean)
            )
            if mask_to.any():
                scenario.loc[mask_to, "Adj_HC"] += r["Shift_HC"]

        scenario["Adj_HC"] = scenario["Adj_HC"].clip(lower=0)

    onshore_mask = scenario["Location_Type"].astype(str).str.lower() == "onshore"
    offshore_discount = 0.30
    scenario.loc[onshore_mask, "Adj_Rate"] = scenario.loc[onshore_mask, "Adj_Rate"] * (
        1 - (offshore_shift_pct / 100) * offshore_discount
    )

    scenario["Scenario_Cost"] = scenario["Adj_HC"] * scenario["Adj_Rate"]
    return scenario

# -----------------------------
# BRIDGE
# -----------------------------
def scenario_total_only(salary, hiring, attr, offshore, elim, elim_start, opt_from, opt_to, opt_pct):
    temp = run_scenario(
        df_sim,
        salary_inflation_pct=salary,
        hiring_change_pct=hiring,
        attrition_pct=attr,
        offshore_shift_pct=offshore,
        eliminate_grades=elim,
        elimination_month=elim_start,
        optimise_from_grade=opt_from,
        optimise_to_grade=opt_to,
        optimise_pct_val=opt_pct
    )
    return temp["Scenario_Cost"].sum()

baseline_total_bridge = scenario_total_only(0, 0, 0, 0, [], "Dec", "None", "None", 0)
after_salary = scenario_total_only(salary_inflation, 0, 0, 0, [], "Dec", "None", "None", 0)
after_hiring = scenario_total_only(salary_inflation, hiring_change, 0, 0, [], "Dec", "None", "None", 0)
after_attrition = scenario_total_only(salary_inflation, hiring_change, attrition, 0, [], "Dec", "None", "None", 0)
after_offshore = scenario_total_only(salary_inflation, hiring_change, attrition, offshore_shift, [], "Dec", "None", "None", 0)
after_elimination = scenario_total_only(salary_inflation, hiring_change, attrition, offshore_shift, eliminate_grade, elim_month, "None", "None", 0)
after_optimisation = scenario_total_only(salary_inflation, hiring_change, attrition, offshore_shift, eliminate_grade, elim_month, optimise_from, optimise_to, optimise_pct)

bridge_steps = [
    ("Baseline YE Cost", baseline_total_bridge),
    ("Salary Inflation", after_salary - baseline_total_bridge),
    ("Hiring", after_hiring - after_salary),
    ("Attrition", after_attrition - after_hiring),
    ("Offshore Shift", after_offshore - after_attrition),
    ("Role Elimination", after_elimination - after_offshore),
    ("Grade Optimisation", after_optimisation - after_elimination),
    ("Scenario YE Cost", after_optimisation),
]

# -----------------------------
# CURRENT SCENARIO
# -----------------------------
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

base_var_vs_budget = base_total - budget_total
scenario_var_vs_budget = scenario_total - budget_total
budget_gap_pct = (scenario_var_vs_budget / budget_total * 100) if budget_total != 0 else 0

base_snap = df_basecase[df_basecase["Month"] == kpi_month].copy()
scn_snap = df_scn[df_scn["Month"] == kpi_month].copy()

base_hc = base_snap["HC"].sum()
budget_hc = base_snap["Budget_HC"].sum()
scenario_hc = scn_snap["Adj_HC"].sum()

base_hc_var_vs_budget = base_hc - budget_hc
scenario_hc_var_vs_budget = scenario_hc - budget_hc

monthly_base_hc = df_basecase.groupby("Month", as_index=False)["HC"].sum()
monthly_budget_hc = df_basecase.groupby("Month", as_index=False)["Budget_HC"].sum()
monthly_scn_hc = df_scn.groupby("Month", as_index=False)["Adj_HC"].sum()

avg_annual_base_hc = monthly_base_hc["HC"].mean()
avg_annual_budget_hc = monthly_budget_hc["Budget_HC"].mean()
avg_annual_scn_hc = monthly_scn_hc["Adj_HC"].mean()

base_annual_cost_per_hc = base_total / avg_annual_base_hc if avg_annual_base_hc != 0 else 0
budget_annual_cost_per_hc = budget_total / avg_annual_budget_hc if avg_annual_budget_hc != 0 else 0
scenario_annual_cost_per_hc = scenario_total / avg_annual_scn_hc if avg_annual_scn_hc != 0 else 0

# -----------------------------
# MONTHLY VIEW HELPERS
# -----------------------------
def build_monthly_view_table(value_type: str, row_dim: str):
    row_order = get_ordered_dimension_values(df_sim, row_dim)

    if value_type == "HC":
        baseline_col = "HC"
        scenario_col = "Adj_HC"
        budget_col = "Budget_HC"
    else:
        baseline_col = "Base_Cost"
        scenario_col = "Scenario_Cost"
        budget_col = "Budget_Cost"

    base_pivot = (
        df_basecase.groupby([row_dim, "Month"], as_index=False)[baseline_col]
        .sum()
        .pivot(index=row_dim, columns="Month", values=baseline_col)
        .reindex(index=row_order, columns=months)
        .fillna(0)
    )

    scn_pivot = (
        df_scn.groupby([row_dim, "Month"], as_index=False)[scenario_col]
        .sum()
        .pivot(index=row_dim, columns="Month", values=scenario_col)
        .reindex(index=row_order, columns=months)
        .fillna(0)
    )

    bud_pivot = (
        df_basecase.groupby([row_dim, "Month"], as_index=False)[budget_col]
        .sum()
        .pivot(index=row_dim, columns="Month", values=budget_col)
        .reindex(index=row_order, columns=months)
        .fillna(0)
    )

    if value_type == "Cost" and unit_mode == "$m":
        base_pivot = base_pivot / 1_000_000
        scn_pivot = scn_pivot / 1_000_000
        bud_pivot = bud_pivot / 1_000_000

    base_pivot.loc["Total"] = base_pivot.sum(axis=0)
    scn_pivot.loc["Total"] = scn_pivot.sum(axis=0)
    bud_pivot.loc["Total"] = bud_pivot.sum(axis=0)

    ordered_parts = []
    ordered_cols = []
    for m in months:
        ordered_parts.append(base_pivot[[m]].rename(columns={m: (m, "Baseline")}))
        ordered_parts.append(scn_pivot[[m]].rename(columns={m: (m, "Scenario")}))
        ordered_parts.append(bud_pivot[[m]].rename(columns={m: (m, "Budget")}))
        ordered_cols.extend([(m, "Baseline"), (m, "Scenario"), (m, "Budget")])

    table = pd.concat(ordered_parts, axis=1)
    table.columns = pd.MultiIndex.from_tuples(ordered_cols)
    table.index.name = row_dim

    return table

def style_monthly_view_table(table: pd.DataFrame, value_type: str):
    styles = pd.DataFrame("", index=table.index, columns=table.columns)

    for m in months:
        base_col = (m, "Baseline")
        scn_col = (m, "Scenario")
        bud_col = (m, "Budget")

        styles.loc[:, bud_col] = "background-color: #F3F4F6; color: #111827; font-weight: 600;"

        styles.loc[table[base_col] > table[bud_col], base_col] = "background-color: #FEE2E2; color: #991B1B;"
        styles.loc[table[base_col] < table[bud_col], base_col] = "background-color: #DCFCE7; color: #166534;"

        styles.loc[table[scn_col] > table[bud_col], scn_col] = "background-color: #FEE2E2; color: #991B1B;"
        styles.loc[table[scn_col] < table[bud_col], scn_col] = "background-color: #DCFCE7; color: #166534;"

    if "Total" in table.index:
        for col in table.columns:
            styles.loc["Total", col] = styles.loc["Total", col] + " font-weight: 700; border-top: 2px solid #9CA3AF;"

    if value_type == "HC":
        formatter = {col: "{:,.0f}" for col in table.columns}
    else:
        if unit_mode == "$m":
            formatter = {col: "${:,.1f}m" for col in table.columns}
        else:
            formatter = {col: "${:,.0f}" for col in table.columns}

    styler = (
        table.style
        .apply(lambda _: styles, axis=None)
        .format(formatter)
        .set_table_styles([
            {"selector": "table", "props": [("border-collapse", "collapse"), ("font-size", "12px"), ("width", "100%")]},
            {"selector": "th", "props": [("background-color", "#F9FAFB"), ("color", "#111827"), ("border", "1px solid #E5E7EB"), ("padding", "6px 8px"), ("text-align", "center")]},
            {"selector": "td", "props": [("border", "1px solid #E5E7EB"), ("padding", "6px 8px"), ("text-align", "right")]},
            {"selector": ".row_heading", "props": [("background-color", "#FFFFFF"), ("color", "#111827"), ("font-weight", "600"), ("text-align", "left")]},
            {"selector": ".index_name", "props": [("background-color", "#F9FAFB"), ("color", "#111827"), ("font-weight", "700")]},
        ])
    )

    return styler

# -----------------------------
# KPI SECTIONS
# -----------------------------
st.markdown('<div class="section-title">💰 YE Cost Overview</div>', unsafe_allow_html=True)
cost_cols = st.columns(5)
with cost_cols[0]:
    kpi_card("Baseline Cost Outlook", fmt_money(base_total, unit_mode), variance_chip_html(base_var_vs_budget, budget_total, "money", unit_mode))
with cost_cols[1]:
    kpi_card("Scenario Cost Outlook", fmt_money(scenario_total, unit_mode), variance_chip_html(scenario_var_vs_budget, budget_total, "money", unit_mode))
with cost_cols[2]:
    kpi_card("Budget Cost", fmt_money(budget_total, unit_mode), neutral_chip_html("Reference"))
with cost_cols[3]:
    gap_chip = '<span class="kpi-chip kpi-chip-green">Under Budget</span>' if budget_gap_pct < 0 else '<span class="kpi-chip kpi-chip-red">Over Budget</span>'
    kpi_card("Budget Gap %", f"{budget_gap_pct:.1f}%", gap_chip)
with cost_cols[4]:
    kpi_card(
        "Annual Cost / HC (Base / Scn / Bud)",
        f"{fmt_money(base_annual_cost_per_hc, '$')} / {fmt_money(scenario_annual_cost_per_hc, '$')} / {fmt_money(budget_annual_cost_per_hc, '$')}",
        neutral_chip_html("Annualised")
    )

st.markdown('<div class="section-title">👥 YE HC Overview</div>', unsafe_allow_html=True)
hc_cols = st.columns(5)
with hc_cols[0]:
    kpi_card("Baseline HC Outlook", fmt_num(base_hc), variance_chip_html(base_hc_var_vs_budget, budget_hc, "hc"))
with hc_cols[1]:
    kpi_card("Scenario HC Outlook", fmt_num(scenario_hc), variance_chip_html(scenario_hc_var_vs_budget, budget_hc, "hc"))
with hc_cols[2]:
    kpi_card("Budget HC", fmt_num(budget_hc), neutral_chip_html("Reference"))
with hc_cols[3]:
    kpi_card("Scenario HC vs Budget", fmt_num(scenario_hc_var_vs_budget), variance_chip_html(scenario_hc_var_vs_budget, budget_hc, "hc"))
with hc_cols[4]:
    kpi_card(
        "Avg Annual HC (Base/Bud/Scn)",
        f"{avg_annual_base_hc:,.0f} / {avg_annual_budget_hc:,.0f} / {avg_annual_scn_hc:,.0f}",
        neutral_chip_html("Annual average")
    )

# -----------------------------
# WATERFALL CHART
# -----------------------------
bridge_labels = [x[0] for x in bridge_steps]
bridge_values = [x[1] for x in bridge_steps]
measure = ["absolute"] + ["relative"] * (len(bridge_steps) - 2) + ["total"]
waterfall_text = [fmt_money(v, unit_mode) for v in bridge_values]

waterfall_fig = go.Figure(go.Waterfall(
    name="YE Cost Bridge",
    orientation="v",
    measure=measure,
    x=bridge_labels,
    y=bridge_values,
    text=waterfall_text,
    textposition="outside",
    textfont=dict(color="#111827", size=12),
    connector={"line": {"color": "#9CA3AF"}},
    increasing={"marker": {"color": "#EF4444"}},
    decreasing={"marker": {"color": "#22C55E"}},
    totals={"marker": {"color": "#2563EB"}},
    cliponaxis=False
))

waterfall_fig.update_layout(
    title="YE Cost Bridge: Baseline to Scenario",
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#111827"),
    yaxis=dict(
        title=f"YE Cost Impact ({unit_mode} USD)",
        gridcolor="#E5E7EB",
        tickfont=dict(color="#111827")
    ),
    xaxis=dict(
        title="Drivers",
        tickfont=dict(color="#111827", size=11)
    ),
    height=440,
    margin=dict(l=20, r=10, t=70, b=95)
)

# -----------------------------
# CUMULATIVE COST TREND
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

baseline_trend["Cumulative_Base_Cost"] = baseline_trend["Base_Cost"].cumsum()
budget_trend["Cumulative_Budget_Cost"] = budget_trend["Budget_Cost"].cumsum()
scenario_trend["Cumulative_Scenario_Cost"] = scenario_trend["Scenario_Cost"].cumsum()

scale = 1_000_000 if unit_mode == "$m" else 1

trend_fig = go.Figure()
trend_fig.add_trace(go.Scatter(
    x=baseline_trend["Month"], y=baseline_trend["Cumulative_Base_Cost"] / scale,
    mode="lines+markers", line=dict(width=3, color="#2563EB"), name="Cumulative Baseline Cost"
))
trend_fig.add_trace(go.Scatter(
    x=budget_trend["Month"], y=budget_trend["Cumulative_Budget_Cost"] / scale,
    mode="lines+markers", line=dict(width=3, color="#FB7185"), name="Cumulative Budget Cost"
))
trend_fig.add_trace(go.Scatter(
    x=scenario_trend["Month"], y=scenario_trend["Cumulative_Scenario_Cost"] / scale,
    mode="lines+markers", line=dict(width=3, color="#14B8A6"), name="Cumulative Scenario Cost"
))
trend_fig.update_layout(
    title="Cumulative Cost Trend to Year-End",
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#111827"),
    xaxis=dict(title="Month", showgrid=False, tickfont=dict(color="#111827")),
    yaxis=dict(title=f"Cumulative Cost ({unit_mode} USD)", gridcolor="#E5E7EB", tickfont=dict(color="#111827")),
    hovermode="x unified",
    height=420,
    margin=dict(l=20, r=10, t=50, b=20),
    legend=dict(orientation="h", y=1.1, font=dict(color="#111827"))
)

# -----------------------------
# TARGET NAVIGATOR
# -----------------------------
def goal_seek(solve_for, target_variance_vs_budget, base_df):
    if solve_for == "Attrition %":
        candidates = [x / 2 for x in range(0, 61)]
    elif solve_for == "Hiring Rate %":
        candidates = [x / 2 for x in range(-40, 41)]
    elif solve_for == "Offshore Shift %":
        candidates = list(range(0, 101, 5))
    else:
        candidates = [x / 2 for x in range(-20, 41)]

    best_value = None
    best_gap = None
    best_scn_total = None
    best_df = None

    for candidate in candidates:
        if solve_for == "Attrition %":
            temp = run_scenario(base_df, salary_inflation, hiring_change, candidate, offshore_shift,
                                eliminate_grade, elim_month, optimise_from, optimise_to, optimise_pct)
        elif solve_for == "Hiring Rate %":
            temp = run_scenario(base_df, salary_inflation, candidate, attrition, offshore_shift,
                                eliminate_grade, elim_month, optimise_from, optimise_to, optimise_pct)
        elif solve_for == "Offshore Shift %":
            temp = run_scenario(base_df, salary_inflation, hiring_change, attrition, candidate,
                                eliminate_grade, elim_month, optimise_from, optimise_to, optimise_pct)
        else:
            temp = run_scenario(base_df, candidate, hiring_change, attrition, offshore_shift,
                                eliminate_grade, elim_month, optimise_from, optimise_to, optimise_pct)

        temp_total = temp["Scenario_Cost"].sum()
        temp_var_vs_budget = temp_total - budget_total
        gap = abs(temp_var_vs_budget - target_variance_vs_budget)

        if best_gap is None or gap < best_gap:
            best_gap = gap
            best_value = candidate
            best_scn_total = temp_total
            best_df = temp

    best_var_vs_budget = best_scn_total - budget_total
    best_snap = best_df[best_df["Month"] == kpi_month].copy()
    best_scn_hc = best_snap["Adj_HC"].sum()
    monthly_goal_trend = (
        best_df.groupby(["Month_Num", "Month"], as_index=False)
        .agg(Scenario_HC=("Adj_HC", "sum"))
        .sort_values("Month_Num")
    )
    best_avg_cost_per_hc = best_scn_total / monthly_goal_trend["Scenario_HC"].mean() if monthly_goal_trend["Scenario_HC"].mean() != 0 else 0

    return {
        "recommended_value": best_value,
        "annual_cost": best_scn_total,
        "var_vs_budget": best_var_vs_budget,
        "scenario_hc": best_scn_hc,
        "annual_cost_per_hc": best_avg_cost_per_hc
    }

chart_left, chart_mid, chart_right = st.columns([1.05, 1.2, 0.85])

with chart_left:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(waterfall_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chart_mid:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(trend_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chart_right:
    st.markdown("""
    <div class="panel-card">
        <div class="panel-title">🎯 Target Navigator</div>
        <div class="panel-sub">Set a target landing position and solve for one lever at a time. This pane is advisory and does not automatically change the charts.</div>
    """, unsafe_allow_html=True)

    target_mode = st.selectbox("Target Definition", ["At Budget", "Custom Variance vs Budget (USD)"], key="target_mode")
    if target_mode == "At Budget":
        target_variance_vs_budget = 0.0
    else:
        target_variance_vs_budget = st.number_input(
            "Target Variance vs Budget (USD)",
            value=0.0,
            step=1000000.0,
            help="Negative means under budget. Positive means over budget."
        )

    solve_for = st.selectbox(
        "Solve For",
        ["Attrition %", "Hiring Rate %", "Offshore Shift %", "Salary Inflation %"],
        key="solve_for"
    )

    nav_result = goal_seek(
        solve_for=solve_for,
        target_variance_vs_budget=target_variance_vs_budget,
        base_df=df_sim
    )

    st.metric("Recommended Lever", f"{nav_result['recommended_value']:.1f}%" if solve_for != "Offshore Shift %" else f"{nav_result['recommended_value']:.0f}%")
    st.metric("Target Gap", fmt_money(nav_result['var_vs_budget'] - target_variance_vs_budget, unit_mode))
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# RECOMMENDED ACTIONS
# -----------------------------
st.markdown('<div class="section-title">🧭 Recommended Actions</div>', unsafe_allow_html=True)

rec1, rec2, rec3, rec4, rec5, rec6 = st.columns(6)
with rec1:
    kpi_card("Recommended Lever", f"{nav_result['recommended_value']:.1f}%" if solve_for != "Offshore Shift %" else f"{nav_result['recommended_value']:.0f}%", neutral_chip_html(solve_for))
with rec2:
    kpi_card("Projected Landing", fmt_money(nav_result['annual_cost'], unit_mode), variance_chip_html(nav_result['var_vs_budget'], budget_total, "money", unit_mode))
with rec3:
    kpi_card("Budget Gap", fmt_money(nav_result['var_vs_budget'], unit_mode), variance_chip_html(nav_result['var_vs_budget'], budget_total, "money", unit_mode))
with rec4:
    kpi_card(f"{kpi_month} HC", fmt_num(nav_result['scenario_hc']), neutral_chip_html("Snapshot"))
with rec5:
    kpi_card("Annual Cost / HC", fmt_money(nav_result['annual_cost_per_hc'], '$'), neutral_chip_html("Annualised"))
with rec6:
    target_gap = nav_result['var_vs_budget'] - target_variance_vs_budget
    kpi_card("Gap to Target", fmt_money(target_gap, unit_mode), variance_chip_html(target_gap, budget_total, "money", unit_mode))

# -----------------------------
# IMPACT SUMMARY
# -----------------------------
st.markdown('<div class="section-title">📊 Impact Summary</div>', unsafe_allow_html=True)
sum_cols = st.columns(3)
with sum_cols[0]:
    kpi_card("Baseline vs Budget", fmt_money(base_var_vs_budget, unit_mode), variance_chip_html(base_var_vs_budget, budget_total, "money", unit_mode))
with sum_cols[1]:
    kpi_card("Scenario vs Budget", fmt_money(scenario_var_vs_budget, unit_mode), variance_chip_html(scenario_var_vs_budget, budget_total, "money", unit_mode))
with sum_cols[2]:
    scen_vs_base = scenario_total - base_total
    chip = '<span class="kpi-chip kpi-chip-green">Improvement</span>' if scen_vs_base < 0 else '<span class="kpi-chip kpi-chip-red">Deterioration</span>'
    kpi_card("Scenario vs Baseline", fmt_money(scen_vs_base, unit_mode), chip)

# -----------------------------
# MONTHLY VIEW SELECTOR
# -----------------------------
st.markdown('<div class="section-title">📘 Monthly Views</div>', unsafe_allow_html=True)

row_dimension_map = {
    "Grade": "Grade",
    "Country": "Country",
    "Location Type": "Location_Type",
    "Cost Centre": "Cost_Centre"
}

row_dimension_label = st.selectbox(
    "Monthly view by",
    options=list(row_dimension_map.keys()),
    index=0
)
row_dimension_col = row_dimension_map[row_dimension_label]

# -----------------------------
# MONTHLY VIEW HC
# -----------------------------
st.markdown(f'<div class="section-title">📅 Monthly View HC — by {row_dimension_label}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="table-note">Baseline and Scenario are shaded against Budget for each month. Red = above budget, Green = below budget, Budget = reference.</div>',
    unsafe_allow_html=True
)

hc_monthly_table = build_monthly_view_table("HC", row_dimension_col)
hc_monthly_styler = style_monthly_view_table(hc_monthly_table, "HC")
render_styled_table(hc_monthly_styler)

# -----------------------------
# MONTHLY VIEW COST
# -----------------------------
st.markdown(f'<div class="section-title">💵 Monthly View Cost — by {row_dimension_label}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="table-note">Baseline and Scenario are shaded against Budget for each month. Red = above budget, Green = below budget, Budget = reference. Cost view reflects both workforce volume and rate changes, so lower HC can still result in higher cost where scenario rates are above budget/base rates.</div>',
    unsafe_allow_html=True
)

cost_monthly_table = build_monthly_view_table("Cost", row_dimension_col)
cost_monthly_styler = style_monthly_view_table(cost_monthly_table, "Cost")
render_styled_table(cost_monthly_styler)

# -----------------------------
# RAW DETAIL TABLE
# -----------------------------
with st.expander("Show raw detailed monthly data"):
    detail = df_scn[[
        "MT", "Country", "Location_Type", "Cost_Centre", "Grade", "Month",
        "HC", "Budget_HC", "Attrition_HC", "Hiring_HC", "Adj_HC",
        "Base_Rate_Monthly", "Adj_Rate",
        "Base_Cost", "Budget_Cost", "Scenario_Cost"
    ]].copy()

    if unit_mode == "$m":
        for col in ["Base_Rate_Monthly", "Adj_Rate", "Base_Cost", "Budget_Cost", "Scenario_Cost"]:
            detail[col] = detail[col] / 1_000_000

    st.dataframe(detail, use_container_width=True)