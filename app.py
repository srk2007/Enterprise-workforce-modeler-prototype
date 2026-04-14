import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import base64

st.set_page_config(
    layout="wide",
    page_title="Workforce Intelligence Navigator | Standard Chartered"
)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def plotly_font() -> str:
    return "SC Prosper Sans, Prosper Sans, Arial, sans-serif"

def fmt_money(val: float, unit_mode: str = "$000s") -> str:
    if unit_mode == "$m":
        return f"${val/1_000_000:,.1f}m"
    elif unit_mode == "$000s":
        return f"${val/1_000:,.0f}k"
    return f"${val:,.0f}"

def fmt_num(val: float) -> str:
    return f"{val:,.0f}"

def chip_html(text: str, kind: str = "grey") -> str:
    return f'<span class="kpi-chip kpi-chip-{kind}">{text}</span>'

def kpi_card(title: str, value: str, sub_html: str = "", footnote: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
            <div class="kpi-sub">{footnote}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def budget_variance_chip(actual_val: float, budget_val: float, unit_mode: str = "$", is_hc: bool = False) -> str:
    var = actual_val - budget_val
    pct = (var / budget_val * 100) if budget_val else 0
    kind = "green" if var < 0 else "red"
    display_var = fmt_num(abs(var)) if is_hc else fmt_money(abs(var), unit_mode)
    sign = "-" if var < 0 else "+"
    return chip_html(f"Vs Budget ({sign}{display_var}, {pct:.1f}%)", kind)

def sum_cols(df_in: pd.DataFrame, cols: list[str]) -> pd.Series:
    present = [c for c in cols if c in df_in.columns]
    if not present:
        return pd.Series([0] * len(df_in), index=df_in.index, dtype=float)
    return df_in[present].sum(axis=1)

def get_driver_cost_columns(prefix: str) -> tuple[str, str]:
    return (f"{prefix}_Committed_Cost", f"{prefix}_NonCommitted_Cost")

def get_driver_hc_columns(prefix: str) -> tuple[str, str]:
    return (f"{prefix}_Committed_HC", f"{prefix}_NonCommitted_HC")

def build_bridge_range(start_val, step_vals, end_val):
    levels = [start_val]
    running = start_val
    for val in step_vals:
        running += val
        levels.append(running)
    levels.append(end_val)
    y_min = min(levels)
    y_max = max(levels)
    span = max(y_max - y_min, 1)
    return y_min - span * 0.25, y_max + span * 0.25

def load_logo_html(path: str = "sc_logo.png") -> str:
    logo_path = Path(path)
    if logo_path.exists():
        encoded = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        return f'<img src="data:image/png;base64,{encoded}" class="sc-logo-img" alt="Standard Chartered Logo" />'
    return '<div class="sc-logo-fallback">Standard Chartered</div>'

# -------------------------------------------------
# STYLING
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --sc-navy: #04145f;
    --sc-blue: #1369e2;
    --sc-green: #22c55e;
    --sc-red: #ef4444;
    --sc-amber: #f59e0b;
    --sc-grey-bg: #f3f3f3;
    --sc-panel: #ffffff;
    --sc-text: #4f4f4f;
    --sc-dark-text: #1f2b4d;
}

html, body, [class*="css"] {
    font-family: "SC Prosper Sans", "Prosper Sans", Arial, sans-serif;
    background-color: var(--sc-grey-bg);
    color: var(--sc-text);
}

.stApp, .main {
    background-color: var(--sc-grey-bg);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.25rem;
    max-width: 1920px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

.banner-wrap {
    background: linear-gradient(95deg, var(--sc-navy) 0%, #0a1d89 42%, #1239d0 100%);
    border-radius: 18px;
    padding: 30px 28px 20px 28px;
    margin-bottom: 14px;
    box-shadow: 0 10px 28px rgba(4,20,95,0.16);
    position: relative;
    overflow: hidden;
}

.banner-wrap:after {
    content: "";
    position: absolute;
    right: -70px;
    top: -20px;
    width: 55%;
    height: 180%;
    background: radial-gradient(circle at 10% 40%, rgba(71,215,245,0.55), rgba(71,215,245,0.05) 35%, transparent 55%);
    transform: rotate(-8deg);
    pointer-events: none;
    filter: blur(12px);
}

.banner-inner {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 220px 1fr 220px;
    align-items: center;
    gap: 12px;
}

.banner-center {
    text-align: center;
    padding-top: 2px;
}

.banner-title {
    color: white;
    font-weight: 600;
    font-size: 34px;
    line-height: 1.15;
    margin-bottom: 6px;
}

.banner-sub {
    color: rgba(255,255,255,0.88);
    font-size: 13px;
    letter-spacing: 0.2px;
}

.sc-logo-slot {
    display: flex;
    align-items: center;
    justify-content: flex-start;
}

.sc-logo-img {
    max-height: 72px;
    width: auto;
    object-fit: contain;
    background: rgba(255,255,255,0.96);
    padding: 8px 14px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.10);
}

.sc-logo-fallback {
    color: white;
    font-size: 14px;
    font-weight: 700;
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 10px;
    padding: 8px 10px;
    display: inline-block;
    background: rgba(255,255,255,0.08);
}

.section-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--sc-dark-text);
    margin-top: 10px;
    margin-bottom: 10px;
}

.kpi-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 18px;
    padding: 14px 16px;
    min-height: 112px;
    box-shadow: 0 4px 14px rgba(20,20,20,0.04);
}
.kpi-title {
    font-size: 12px;
    font-weight: 600;
    color: #7d7d7d;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 20px;
    font-weight: 700;
    color: #0e214f;
    line-height: 1.2;
    margin-bottom: 10px;
}
.kpi-sub {
    font-size: 11px;
    color: #7d7d7d;
}

.kpi-chip {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
}
.kpi-chip-blue {
    background: rgba(19,105,226,0.10);
    color: #0c54ba;
}
.kpi-chip-green {
    background: rgba(34,197,94,0.14);
    color: #15803d;
}
.kpi-chip-grey {
    background: #efefef;
    color: #666666;
}
.kpi-chip-red {
    background: rgba(239,68,68,0.14);
    color: #b91c1c;
}
.kpi-chip-amber {
    background: rgba(245,158,11,0.14);
    color: #b45309;
}

.chart-wrap {
    background: white;
    border: 1px solid #e3e3e3;
    border-radius: 16px;
    padding: 10px 10px 4px 10px;
    box-shadow: 0 4px 14px rgba(20,20,20,0.03);
    height: 100%;
}

[data-testid="stSidebar"] {
    background-color: #eef1f5;
    border-right: 1px solid #dfe3ea;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 700;
    color: #0e214f;
    margin-bottom: 6px;
}
.sidebar-sub {
    font-size: 12px;
    color: #5f6878;
    margin-bottom: 16px;
}
.sidebar-section {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #5f6878;
    margin-top: 12px;
    margin-bottom: 8px;
}

.insight-card {
    background: white;
    border: 1px solid #dbe1ea;
    border-radius: 16px;
    padding: 14px 14px 12px 14px;
    box-shadow: 0 4px 14px rgba(20,20,20,0.03);
    margin-top: 10px;
}
.insight-title {
    font-size: 14px;
    font-weight: 700;
    color: #0e214f;
    margin-bottom: 8px;
}
.insight-bullet {
    font-size: 12px;
    line-height: 1.45;
    color: #334155;
    margin-bottom: 8px;
}
.insight-pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 10px;
}
.insight-pill-green {
    background: rgba(34,197,94,0.14);
    color: #15803d;
}
.insight-pill-red {
    background: rgba(239,68,68,0.14);
    color: #b91c1c;
}
.insight-pill-amber {
    background: rgba(245,158,11,0.14);
    color: #b45309;
}
.insight-pill-blue {
    background: rgba(19,105,226,0.10);
    color: #0c54ba;
}

.stSelectbox label,
.stRadio label,
label,
p {
    color: #334155 !important;
}

div[data-testid="stRadio"] label,
div[data-testid="stRadio"] p,
div[role="radiogroup"] label,
div[role="radiogroup"] p {
    color: #334155 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 10px !important;
    border: 1px solid #cbd5e1 !important;
}
div[data-baseweb="select"] * {
    color: #111827 !important;
}

hr.sc-divider {
    border: none;
    border-top: 1px solid #d4d4d4;
    margin-top: 14px;
    margin-bottom: 12px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 2px solid #e0e3ea;
}
.stTabs [data-baseweb="tab"] {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #5f6878 !important;
    padding: 10px 22px !important;
    border-radius: 8px 8px 0 0 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #04145f !important;
    border-bottom: 3px solid #04145f !important;
    background: rgba(4,20,95,0.04) !important;
}

.lever-tile {
    background: white;
    border: 1px solid #e0e3ea;
    border-left: 4px solid #1369e2;
    border-radius: 0 12px 12px 0;
    padding: 14px 16px 12px 14px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(20,20,20,0.04);
}
.lever-tile-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #1369e2;
    margin-bottom: 4px;
}
.lever-tile-title {
    font-size: 13px;
    font-weight: 700;
    color: #0e214f;
    margin-bottom: 10px;
}
.lever-preview {
    font-size: 11px;
    color: #15803d;
    font-weight: 600;
    margin-top: 4px;
    background: rgba(34,197,94,0.08);
    border-radius: 6px;
    padding: 4px 8px;
    display: inline-block;
}

[data-testid="stDownloadButton"] button,
.stDownloadButton button,
.stDownloadButton > button {
    background-color: #04145f !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] button p,
.stDownloadButton button p,
[data-testid="stDownloadButton"] button span,
.stDownloadButton button span {
    color: white !important;
}
[data-testid="stDownloadButton"] button:hover,
.stDownloadButton button:hover {
    background-color: #0a1d89 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_ORDER = {m: i + 1 for i, m in enumerate(MONTHS)}

POSITIVE_DRIVERS = [
    ("Growth Hires", "Growth_Hires"),
    ("Regulatory Hires", "Regulatory_Hires"),
    ("Replacements", "Replacements"),
    ("Transfers In", "Transfers_In"),
    ("Offshoring In", "Offshoring_In"),
]

NEGATIVE_DRIVERS = [
    ("Transformation Exits", "Transformation_Exits"),
    ("Other Exits", "Other_Exits"),
    ("Attrition", "Attrition"),
    ("Transfers Out", "Transfers_Out"),
    ("Offshoring Out", "Offshoring_Out"),
]

SENIOR_GRADES = {"MD", "ED", "D", "C"}

MT_COLOUR_PALETTE = [
    "#1369e2", "#1D9E75", "#D85A30", "#7F77DD", "#BA7517",
    "#E24B4A", "#D4537E", "#639922", "#888780", "#04145f",
]

def get_scale(unit_mode_local: str) -> int:
    if unit_mode_local == "$m":
        return 1_000_000
    elif unit_mode_local == "$000s":
        return 1_000
    return 1

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data(path: str = "WFP_Data.csv") -> pd.DataFrame:
    df_load = pd.read_csv(path)
    df_load.columns = [c.strip() for c in df_load.columns]
    df_load["Month"] = df_load["Month"].astype(str).str.strip()
    df_load["Month_Num"] = df_load["Month"].map(MONTH_ORDER).fillna(df_load.get("Month_Num", 0))
    df_load["Month_Num"] = df_load["Month_Num"].astype(int)
    df_load["Month_Type"] = df_load["Month_Type"].astype(str).str.strip()

    numeric_cols = [
        c for c in df_load.columns
        if c.endswith("_HC") or c.endswith("_Cost") or c in ["Opening_HC", "Closing_HC", "Budget_HC", "Monthly_Rate_USD", "Actual_Cost"]
    ]
    for c in numeric_cols:
        df_load[c] = pd.to_numeric(df_load[c], errors="coerce").fillna(0).astype(float)

    return df_load

df = load_data("WFP_Data.csv")

@st.cache_data
def load_snapshot(file_bytes: bytes) -> pd.DataFrame:
    import io
    df_s = pd.read_csv(io.BytesIO(file_bytes))
    df_s.columns = [c.strip() for c in df_s.columns]
    df_s["Month"] = df_s["Month"].astype(str).str.strip()
    df_s["Month_Num"] = df_s["Month"].map(MONTH_ORDER).fillna(0).astype(int)
    df_s["Month_Type"] = df_s["Month_Type"].astype(str).str.strip()
    for c in [c for c in df_s.columns if c.endswith("_HC") or c.endswith("_Cost")
              or c in ["Opening_HC","Closing_HC","Budget_HC","Monthly_Rate_USD","Actual_Cost"]]:
        df_s[c] = pd.to_numeric(df_s[c], errors="coerce").fillna(0).astype(float)
    df_s["Derived_WFP_Monthly_Cost"] = df_s.apply(
        lambda r: r["Actual_Cost"] if str(r["Month_Type"]).lower() == "actual"
        else r["Closing_HC"] * r["Monthly_Rate_USD"], axis=1)
    df_s["Derived_Budget_Monthly_Cost"] = df_s["Budget_HC"] * df_s["Monthly_Rate_USD"]
    return df_s


@st.cache_data
def scan_wfp_snapshots() -> list:
    """Auto-detect WFP_Data_MMMYY.csv files and return list of (close_month_num, label, df).
    Always includes WFP_Data.csv as the current snapshot."""
    import glob, re
    month_map = {m: i+1 for i,m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}
    results = []

    # Scan for dated snapshots
    for f in sorted(glob.glob("WFP_Data_????.csv") + glob.glob("WFP_Data_?????.csv")):
        m = re.match(r"WFP_Data_([A-Za-z]{3})(\d{2})\.csv$", f)
        if not m:
            continue
        mon_name, yr = m.group(1).capitalize(), m.group(2)
        mon_num = month_map.get(mon_name, 0)
        if mon_num == 0:
            continue
        try:
            df_s = load_snapshot(open(f, "rb").read())
            results.append((mon_num, f"{mon_name} 20{yr} Close", df_s))
        except Exception:
            pass

    # Always append WFP_Data.csv as the current snapshot
    # Derive label from latest actual month in the data
    try:
        df_curr = load_snapshot(open("WFP_Data.csv", "rb").read())
        latest_actual_num = df_curr[df_curr["Month_Type"].str.lower()=="actual"]["Month_Num"].max()
        curr_label = f"{MONTHS[int(latest_actual_num)-1]} 2026 Close (current)"
        # Only add if not already covered by a dated file for the same month
        existing_months = {r[0] for r in results}
        if int(latest_actual_num) not in existing_months:
            results.append((int(latest_actual_num), curr_label, df_curr))
    except Exception:
        pass

    return sorted(results, key=lambda x: x[0])


def forecast_evolution_figure(snapshots: list, df_budget: pd.DataFrame,
                               unit_mode_local: str, scope_filters: dict) -> go.Figure:
    """
    Plots Dec HC and Dec cost forecast as of each WFP close month.
    X axis = all 12 months (the 'close month' axis).
    Only months with snapshots have data points; others are blank.
    """
    scale = get_scale(unit_mode_local)
    budget_dec = df_budget[df_budget["Month"].eq("Dec")]
    budget_hc   = budget_dec["Budget_HC"].sum()
    budget_cost = (budget_dec["Budget_HC"] * budget_dec["Monthly_Rate_USD"]).sum() / scale

    close_months, dec_hc_vals, dec_cost_vals, labels_hover = [], [], [], []

    for mon_num, label, df_s in snapshots:
        # Apply same scope filters
        df_sc = df_s.copy()
        if scope_filters.get("mt", "All") != "All":
            df_sc = df_sc[df_sc["MT"] == scope_filters["mt"]]
        if scope_filters.get("country", "All") != "All":
            df_sc = df_sc[df_sc["Country"] == scope_filters["country"]]
        if scope_filters.get("grade", "All") != "All":
            df_sc = df_sc[df_sc["Grade"] == scope_filters["grade"]]
        dec_rows = df_sc[df_sc["Month"].eq("Dec")]
        hc   = dec_rows["Closing_HC"].sum()
        cost = (dec_rows["Closing_HC"] * dec_rows["Monthly_Rate_USD"]).sum() / scale
        close_months.append(MONTHS[mon_num - 1])
        dec_hc_vals.append(hc)
        dec_cost_vals.append(cost)
        labels_hover.append(label)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Dec HC Forecast — evolution by close month",
                        f"Dec Cost Forecast ({unit_mode_local}) — evolution by close month"],
        horizontal_spacing=0.1
    )

    common = dict(mode="lines+markers+text", textposition="top center",
                  line=dict(color="#1369e2", width=2.5), marker=dict(size=11, color="#1369e2"))

    fig.add_scatter(
        x=close_months, y=dec_hc_vals,
        text=[fmt_num(v) for v in dec_hc_vals],
        hovertext=[f"{lbl}<br>Dec HC: {fmt_num(v)}" for lbl, v in zip(labels_hover, dec_hc_vals)],
        hovertemplate="%{hovertext}<extra></extra>",
        name="Dec HC forecast", **common, row=1, col=1
    )
    fig.add_scatter(
        x=close_months, y=dec_cost_vals,
        text=[fmt_money(v * scale, unit_mode_local) for v in dec_cost_vals],
        hovertext=[f"{lbl}<br>Dec cost: {fmt_money(v*scale, unit_mode_local)}" for lbl, v in zip(labels_hover, dec_cost_vals)],
        hovertemplate="%{hovertext}<extra></extra>",
        name="Dec cost forecast", showlegend=False, **common, row=1, col=2
    )

    # Budget reference lines
    fig.add_hline(y=budget_hc, line_dash="dot", line_color="#f59e0b", line_width=1.8,
                  annotation_text=f"Budget {fmt_num(budget_hc)}", annotation_position="right",
                  annotation_font=dict(color="#b45309", size=11), row=1, col=1)
    fig.add_hline(y=budget_cost, line_dash="dot", line_color="#f59e0b", line_width=1.8,
                  annotation_text=f"Budget {fmt_money(budget_cost*scale, unit_mode_local)}",
                  annotation_position="right", annotation_font=dict(color="#b45309", size=11), row=1, col=2)

    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family=plotly_font(), color="#111827", size=12),
        showlegend=False, height=400,
        xaxis=dict(
            categoryorder="array", categoryarray=MONTHS,
            range=[-0.5, 11.5],
            tickfont=dict(color="#111827", size=11), gridcolor="#e5e7eb",
            title=dict(text="WFP close month", font=dict(size=12, color="#374151"))
        ),
        xaxis2=dict(
            categoryorder="array", categoryarray=MONTHS,
            range=[-0.5, 11.5],
            tickfont=dict(color="#111827", size=11), gridcolor="#e5e7eb",
            title=dict(text="WFP close month", font=dict(size=12, color="#374151"))
        ),
        yaxis=dict(tickfont=dict(color="#111827", size=11), gridcolor="#e5e7eb"),
        yaxis2=dict(tickfont=dict(color="#111827", size=11), gridcolor="#e5e7eb"),
        margin=dict(l=55, r=100, t=60, b=50),
        annotations=[
            dict(
                x=11.4, y=budget_hc, xref="x", yref="y",
                text=f"Budget<br>{fmt_num(budget_hc)}",
                showarrow=False, font=dict(color="#b45309", size=10),
                align="right", xanchor="right"
            ),
            dict(
                x=11.4, y=budget_cost, xref="x2", yref="y2",
                text=f"Budget<br>{fmt_money(budget_cost*scale, unit_mode_local)}",
                showarrow=False, font=dict(color="#b45309", size=10),
                align="right", xanchor="right"
            ),
        ]
    )
    # Shade Apr–Dec as "future closes" zone
    for xref, yref in [("x","y"), ("x2","y2")]:
        fig.add_vrect(
            x0="Apr", x1="Dec",
            fillcolor="rgba(200,210,230,0.12)",
            layer="below", line_width=0,
            xref=xref
        )
        fig.add_vline(
            x="Apr", line_dash="dot", line_color="#cbd5e1",
            line_width=1.2, xref=xref
        )
    return fig

# -------------------------------------------------
# DERIVED FIELDS
# -------------------------------------------------
df["Derived_WFP_Monthly_Cost"] = df.apply(
    lambda r: r["Actual_Cost"] if str(r["Month_Type"]).lower() == "actual" else r["Closing_HC"] * r["Monthly_Rate_USD"],
    axis=1
)
df["Derived_Budget_Monthly_Cost"] = df["Budget_HC"] * df["Monthly_Rate_USD"]

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">Filters</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Select display unit and scope for the dashboard view.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Display</div>', unsafe_allow_html=True)
    unit_mode = st.radio("Financial display", ["$000s", "$m"], horizontal=True, index=1)

    st.markdown('<div class="sidebar-section">Scope</div>', unsafe_allow_html=True)
    mt_options = ["All"] + sorted(df["MT"].dropna().astype(str).unique().tolist())
    selected_mt = st.selectbox("Management Team", mt_options, index=0)

    country_options = ["All"] + sorted(df["Country"].dropna().astype(str).unique().tolist())
    selected_country = st.selectbox("Country", country_options, index=0)

    grade_options = ["All"] + sorted(df["Grade"].dropna().astype(str).unique().tolist())
    selected_grade = st.selectbox("Grade", grade_options, index=0)

    if st.button("↺ Reset filters", use_container_width=True):
        st.query_params.clear()
        st.rerun()

    st.markdown('<div class="sidebar-section" style="margin-top:16px;">FORECAST TREND</div>', unsafe_allow_html=True)
    st.caption("Place dated WFP snapshots in the same folder as the app — e.g. WFP_Data_Jan26.csv, WFP_Data_Feb26.csv. They are detected automatically.")

# -------------------------------------------------
# FILTER DATA
# -------------------------------------------------
# df_scope_actuals: MT + Country only — used for YTD actuals (grade not in ledger)
df_scope_actuals = df.copy()
if selected_mt != "All":
    df_scope_actuals = df_scope_actuals[df_scope_actuals["MT"] == selected_mt]
if selected_country != "All":
    df_scope_actuals = df_scope_actuals[df_scope_actuals["Country"] == selected_country]

# df_scope: MT + Country + Grade — used for budget, forecast, drivers, charts
df_scope = df_scope_actuals.copy()
if selected_grade != "All":
    df_scope = df_scope[df_scope["Grade"] == selected_grade]

if df_scope.empty:
    st.warning("No records found for the selected scope.")
    st.stop()

# -------------------------------------------------
# GRADE FILTER BANNER
# -------------------------------------------------
if selected_grade != "All":
    st.info(
        f"**Grade filter active: {selected_grade}** — "
        "Forecast, budget and driver views are grade-filtered. "
        "YTD actuals reflect the full ledger cost for the selected MT / Country scope "
        "(actuals are not recorded at grade level in the ledger).",
        icon="ℹ️"
    )

# -------------------------------------------------
# MASKS
# -------------------------------------------------
# Forecast/budget masks on grade-filtered scope
actual_mask   = df_scope["Month_Type"].str.lower() == "actual"
forecast_mask = df_scope["Month_Type"].str.lower() == "forecast"
mar_mask      = df_scope["Month"].eq("Mar")
dec_mask      = df_scope["Month"].eq("Dec")
ytd_mask      = df_scope["Month"].isin(["Jan", "Feb", "Mar"])

# Actuals masks on ungraded scope
act_mar_mask  = df_scope_actuals["Month"].eq("Mar")
act_ytd_mask  = df_scope_actuals["Month"].isin(["Jan", "Feb", "Mar"])
act_actual_mask = df_scope_actuals["Month_Type"].str.lower() == "actual"

# -------------------------------------------------
# CORE CALCULATIONS
# -------------------------------------------------
current_wfp_outlook_cost = df_scope["Derived_WFP_Monthly_Cost"].sum()
scenario_outlook_cost = current_wfp_outlook_cost
cp26_budget_cost = df_scope["Derived_Budget_Monthly_Cost"].sum()

ytd_cost_actual = df_scope_actuals.loc[act_ytd_mask & act_actual_mask, "Actual_Cost"].sum()
ytd_cost_budget = df_scope.loc[ytd_mask, "Derived_Budget_Monthly_Cost"].sum()

noncomm_growth_cost = sum_cols(
    df_scope.loc[forecast_mask],
    [f"{prefix}_NonCommitted_Cost" for _, prefix in POSITIVE_DRIVERS]
).sum()

noncomm_reduction_cost = sum_cols(
    df_scope.loc[forecast_mask],
    [f"{prefix}_NonCommitted_Cost" for _, prefix in NEGATIVE_DRIVERS]
).sum()

addressable_growth_cost = noncomm_growth_cost
crr_line_of_sight_cost = current_wfp_outlook_cost - noncomm_growth_cost + noncomm_reduction_cost

current_wfp_hc = df_scope.loc[dec_mask, "Closing_HC"].sum()
scenario_hc = current_wfp_hc
cp26_budget_hc = df_scope.loc[dec_mask, "Budget_HC"].sum()

ytd_hc_actual = df_scope_actuals.loc[act_mar_mask, "Closing_HC"].sum()
ytd_hc_budget = df_scope.loc[mar_mask, "Budget_HC"].sum()

noncomm_growth_hc = sum_cols(
    df_scope.loc[forecast_mask],
    [f"{prefix}_NonCommitted_HC" for _, prefix in POSITIVE_DRIVERS]
).sum()

noncomm_reduction_hc = sum_cols(
    df_scope.loc[forecast_mask],
    [f"{prefix}_NonCommitted_HC" for _, prefix in NEGATIVE_DRIVERS]
).sum()

addressable_growth_hc = noncomm_growth_hc
crr_line_of_sight_hc = current_wfp_hc - noncomm_growth_hc + noncomm_reduction_hc

# -------------------------------------------------
# INSIGHT ENGINE
# -------------------------------------------------
def build_insights(df_in: pd.DataFrame):
    grade_active = selected_grade != "All"

    # ---- HC gap (always valid) ----
    hc_outlook_gap = current_wfp_hc - cp26_budget_hc
    hc_outlook_gap_pct = (hc_outlook_gap / cp26_budget_hc * 100) if cp26_budget_hc else 0
    ytd_hc_gap = ytd_hc_actual - ytd_hc_budget
    ytd_hc_gap_pct = (ytd_hc_gap / ytd_hc_budget * 100) if ytd_hc_budget else 0
    do_nothing_hc_gap = crr_line_of_sight_hc - cp26_budget_hc
    do_nothing_hc_gap_pct = (do_nothing_hc_gap / cp26_budget_hc * 100) if cp26_budget_hc else 0

    # ---- Cost gap (only valid when no grade filter) ----
    if not grade_active:
        outlook_gap = current_wfp_outlook_cost - cp26_budget_cost
        outlook_gap_pct = (outlook_gap / cp26_budget_cost * 100) if cp26_budget_cost else 0
        ytd_cost_gap = ytd_cost_actual - ytd_cost_budget
        ytd_cost_gap_pct = (ytd_cost_gap / ytd_cost_budget * 100) if ytd_cost_budget else 0
        do_nothing_gap = crr_line_of_sight_cost - cp26_budget_cost
        do_nothing_gap_pct = (do_nothing_gap / cp26_budget_cost * 100) if cp26_budget_cost else 0

    # ---- Top HC driver ----
    hc_driver_rows = []
    for label, prefix in POSITIVE_DRIVERS:
        c_col, n_col = get_driver_hc_columns(prefix)
        hc_driver_rows.append((label, df_in.loc[forecast_mask, c_col].sum() + df_in.loc[forecast_mask, n_col].sum()))
    for label, prefix in NEGATIVE_DRIVERS:
        c_col, n_col = get_driver_hc_columns(prefix)
        hc_driver_rows.append((label, -(df_in.loc[forecast_mask, c_col].sum() + df_in.loc[forecast_mask, n_col].sum())))
    hc_driver_df = pd.DataFrame(hc_driver_rows, columns=["Driver", "Value"])
    top_hc_driver = hc_driver_df.iloc[hc_driver_df["Value"].abs().idxmax()] if not hc_driver_df.empty else None

    # ---- Top cost driver (only when grade not active) ----
    top_cost_driver = None
    if not grade_active:
        cost_driver_rows = []
        for label, prefix in POSITIVE_DRIVERS:
            c_col, n_col = get_driver_cost_columns(prefix)
            cost_driver_rows.append((label, df_in.loc[forecast_mask, c_col].sum() + df_in.loc[forecast_mask, n_col].sum()))
        for label, prefix in NEGATIVE_DRIVERS:
            c_col, n_col = get_driver_cost_columns(prefix)
            cost_driver_rows.append((label, -(df_in.loc[forecast_mask, c_col].sum() + df_in.loc[forecast_mask, n_col].sum())))
        cost_driver_df = pd.DataFrame(cost_driver_rows, columns=["Driver", "Value"])
        top_cost_driver = cost_driver_df.iloc[cost_driver_df["Value"].abs().idxmax()] if not cost_driver_df.empty else None

    # ---- Country concentration message ----
    country_message = None
    if selected_country == "All":
        if grade_active:
            # HC-based concentration when grade filtered
            country_hc_out = df_in.groupby("Country", as_index=False)["Closing_HC"].sum()
            country_hc_bud = df_in.groupby("Country", as_index=False)["Budget_HC"].sum()
            c_merge = country_hc_out.merge(country_hc_bud, on="Country", how="outer").fillna(0)
            c_merge["Gap"] = c_merge["Closing_HC"] - c_merge["Budget_HC"]
        else:
            country_budget = df_in.groupby("Country", as_index=False)["Derived_Budget_Monthly_Cost"].sum()
            country_outlook = df_in.groupby("Country", as_index=False)["Derived_WFP_Monthly_Cost"].sum()
            c_merge = country_budget.merge(country_outlook, on="Country", how="outer").fillna(0)
            c_merge["Gap"] = c_merge["Derived_WFP_Monthly_Cost"] - c_merge["Derived_Budget_Monthly_Cost"]

        positive_risk = c_merge[c_merge["Gap"] > 0].copy()
        if not positive_risk.empty:
            total_positive = positive_risk["Gap"].sum()
            positive_risk["Share"] = positive_risk["Gap"] / total_positive if total_positive != 0 else 0
            top_country = positive_risk.sort_values("Gap", ascending=False).iloc[0]
            metric = "HC" if grade_active else "cost"
            country_message = (
                f"Positive {metric} overrun risk is most concentrated in {top_country['Country']}, "
                f"contributing {top_country['Share'] * 100:.1f}% of the total positive gap pool."
            )

    # ---- Grade mix (only meaningful without grade filter) ----
    forecast_dec = df_in.loc[dec_mask].copy()
    if forecast_dec.empty:
        forecast_dec = df_in.copy()

    grade_mix_expensive = False
    senior_forecast_share = senior_budget_share = 0.0
    if not grade_active:
        weighted_forecast_cph = (
            forecast_dec["Closing_HC"].mul(forecast_dec["Monthly_Rate_USD"]).sum() / forecast_dec["Closing_HC"].sum()
            if forecast_dec["Closing_HC"].sum() > 0 else 0
        )
        weighted_budget_cph = (
            forecast_dec["Budget_HC"].mul(forecast_dec["Monthly_Rate_USD"]).sum() / forecast_dec["Budget_HC"].sum()
            if forecast_dec["Budget_HC"].sum() > 0 else 0
        )
        grade_mix_expensive = weighted_forecast_cph > weighted_budget_cph

        senior_forecast = forecast_dec[forecast_dec["Grade"].astype(str).isin(SENIOR_GRADES)]["Closing_HC"].sum()
        senior_budget_val = forecast_dec[forecast_dec["Grade"].astype(str).isin(SENIOR_GRADES)]["Budget_HC"].sum()
        senior_forecast_share = (senior_forecast / forecast_dec["Closing_HC"].sum() * 100) if forecast_dec["Closing_HC"].sum() > 0 else 0
        senior_budget_share = (senior_budget_val / forecast_dec["Budget_HC"].sum() * 100) if forecast_dec["Budget_HC"].sum() > 0 else 0

    # ---- Severity: use HC gap when grade active, cost gap otherwise ----
    if grade_active:
        ref_gap_pct = hc_outlook_gap_pct
        severity_label = "HC outlook"
    else:
        ref_gap_pct = outlook_gap_pct
        severity_label = "outlook"

    if ref_gap_pct > 5:
        severity = (f"Material overrun risk ({severity_label})", "red")
    elif ref_gap_pct > 0:
        severity = (f"Mild overrun risk ({severity_label})", "amber")
    else:
        severity = (f"Within budget tolerance ({severity_label})", "green")

    # ---- Build insight lines ----
    insight_lines = []

    if grade_active:
        # HC-only insights
        insight_lines.append(
            f"HC outlook is {fmt_num(abs(hc_outlook_gap))} {'above' if hc_outlook_gap > 0 else 'below'} budget ({hc_outlook_gap_pct:.1f}%). "
            f"Cost view suppressed — not available at grade level."
        )
        insight_lines.append(
            f"YTD HC (Mar actual) is {fmt_num(abs(ytd_hc_gap))} {'above' if ytd_hc_gap > 0 else 'below'} YTD HC budget ({ytd_hc_gap_pct:.1f}%). "
            f"YTD cost reflects full ledger for this MT/Country scope."
        )
        insight_lines.append(
            f"Do nothing HC scenario is {fmt_num(abs(do_nothing_hc_gap))} {'above' if do_nothing_hc_gap > 0 else 'below'} HC budget ({do_nothing_hc_gap_pct:.1f}%)."
        )
        insight_lines.append(
            f"Challengeable HC growth stands at {fmt_num(addressable_growth_hc)} heads (non-committed)."
        )
        if top_hc_driver is not None:
            direction = "growth" if top_hc_driver["Value"] > 0 else "reduction"
            insight_lines.append(
                f"Largest HC movement driver is {top_hc_driver['Driver']} at {fmt_num(abs(top_hc_driver['Value']))} HC of {direction}."
            )
    else:
        insight_lines.append(
            f"Full-year outlook is {fmt_money(abs(outlook_gap), '$m')} {'above' if outlook_gap > 0 else 'below'} budget ({outlook_gap_pct:.1f}%)."
        )
        insight_lines.append(
            f"YTD actuals are {fmt_money(abs(ytd_cost_gap), '$m')} {'above' if ytd_cost_gap > 0 else 'below'} YTD budget ({ytd_cost_gap_pct:.1f}%)."
        )
        insight_lines.append(
            f"Do nothing scenario is {fmt_money(abs(do_nothing_gap), '$m')} {'above' if do_nothing_gap > 0 else 'below'} full-year budget ({do_nothing_gap_pct:.1f}%)."
        )
        insight_lines.append(
            f"Challengeable growth stands at {fmt_money(addressable_growth_cost, '$m')} (non-committed cost)."
        )
        if top_cost_driver is not None:
            direction = "growth" if top_cost_driver["Value"] > 0 else "reduction"
            insight_lines.append(
                f"Largest movement driver is {top_cost_driver['Driver']} at {fmt_money(abs(top_cost_driver['Value']), '$m')} of {direction}."
            )

    if country_message:
        insight_lines.append(country_message)

    if not grade_active:
        if grade_mix_expensive:
            insight_lines.append(
                f"Forecast grade mix is more expensive than budget — review hiring shape against affordability."
            )
        if senior_forecast_share > senior_budget_share:
            insight_lines.append(
                f"Senior grade mix is higher in forecast than budget ({senior_forecast_share:.1f}% vs {senior_budget_share:.1f}%)."
            )

    # ---- Build action lines ----
    action_lines = []
    if grade_active:
        if hc_outlook_gap_pct > 0:
            action_lines.append("Challenge non-committed HC growth requests first, especially in late forecast months.")
        else:
            action_lines.append("Protect the current below-budget HC position by controlling late-period growth additions.")
        if do_nothing_hc_gap_pct > 0:
            action_lines.append("Committed HC actions alone do not land within budget; incremental intervention is required.")
        else:
            action_lines.append("Committed HC profile is broadly manageable; focus should remain on discretionary growth.")
        action_lines.append(
            f"Switch to 'All' grades view to see the full cost picture for this scope."
        )
    else:
        if outlook_gap_pct > 0:
            action_lines.append("Challenge non-committed growth requests first, especially in late forecast months.")
        else:
            action_lines.append("Protect the current below-budget position by controlling late-period growth additions.")
        if country_message:
            action_lines.append("Prioritise challenge and review in the country carrying the highest positive overrun concentration.")
        if grade_mix_expensive or senior_forecast_share > senior_budget_share:
            action_lines.append("Review senior-grade demand and hiring mix against budgeted shape and affordability.")
        if do_nothing_gap_pct > 0:
            action_lines.append("Committed actions alone do not land within budget; incremental intervention is required.")
        else:
            action_lines.append("Committed profile is broadly manageable; focus should remain on discretionary growth.")

    return {
        "severity_text": severity[0],
        "severity_kind": severity[1],
        "insights": insight_lines[:6],
        "actions": action_lines[:4]
    }

insight_payload = build_insights(df_scope)

# -------------------------------------------------
# SIDEBAR CARDS
# -------------------------------------------------
with st.sidebar:
    pill_class = {
        "green": "insight-pill-green",
        "red": "insight-pill-red",
        "amber": "insight-pill-amber",
        "blue": "insight-pill-blue"
    }[insight_payload["severity_kind"]]

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Forecast Insight</div>
            <div class="insight-pill {pill_class}">{insight_payload['severity_text']}</div>
            {''.join([f'<div class="insight-bullet">• {line}</div>' for line in insight_payload["insights"]])}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Recommended Actions</div>
            {''.join([f'<div class="insight-bullet">• {line}</div>' for line in insight_payload["actions"]])}
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# HEADER
# -------------------------------------------------
logo_html = load_logo_html("sc_logo.png")
scope_parts = [s for s in [
    selected_mt if selected_mt != "All" else None,
    selected_country if selected_country != "All" else None,
    selected_grade if selected_grade != "All" else None,
] if s]
scope_pill = (
    f'<div style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.92);'
    f'font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;display:inline-block;margin-top:6px;">'
    f'Scope: {" | ".join(scope_parts) if scope_parts else "Enterprise — All MTs"}</div>'
)
latest_actual = df_scope[df_scope["Month_Type"].str.lower()=="actual"]["Month_Num"].max()
latest_actual_name = MONTHS[int(latest_actual)-1] if latest_actual > 0 else "—"

st.markdown(
    f"""
    <div class="banner-wrap">
        <div class="banner-inner">
            <div class="sc-logo-slot">{logo_html}</div>
            <div class="banner-center">
                <div class="banner-title">Workforce Intelligence Navigator</div>
                <div class="banner-sub">Cost &amp; headcount performance analytics</div>
                {scope_pill}
            </div>
            <div style="text-align:right;">
                <div style="color:rgba(255,255,255,0.7);font-size:11px;margin-bottom:4px;">Latest actual</div>
                <div style="color:white;font-size:18px;font-weight:700;">{latest_actual_name} 2026</div>
                <div style="color:rgba(255,255,255,0.7);font-size:11px;margin-top:4px;">Forecast: {MONTHS[int(latest_actual)] if latest_actual < 12 else '—'} – Dec</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    f"{'🔴' if insight_payload['severity_kind']=='red' else ('🟡' if insight_payload['severity_kind']=='amber' else '🟢')} WFP Outlook",
    "🔧 Scenario Builder",
    "📖 User Manual"
])

with tab1:
    # -------------------------------------------------
    # KPI DISPLAY
    # -------------------------------------------------
    grade_active = selected_grade != "All"

    st.markdown('<div class="section-title">💰 2026 Cost Overview</div>', unsafe_allow_html=True)

    if grade_active:
        st.markdown(
            """
            <div style="background:#fff8e1; border:1px solid #f59e0b; border-radius:14px;
                        padding:18px 22px; margin-bottom:12px;">
                <div style="font-size:14px; font-weight:700; color:#b45309; margin-bottom:6px;">
                    ⚠️ Cost view not available at grade level
                </div>
                <div style="font-size:13px; color:#78350f; line-height:1.6;">
                    Actuals (Jan–Mar) are extracted from the GL at cost centre level with no grade split,
                    so a full-year cost outlook filtered by grade would blend ungraded ledger actuals with
                    grade-specific forecast costs — producing a figure that cannot be meaningfully labelled
                    as a grade-level cost. Switch to <strong>All</strong> grades to see the full cost view.
                    <br><br>
                    The <strong>HC view below is fully valid</strong> at grade level and shows the complete
                    headcount outlook, budget comparison and driver breakdown for the selected grade.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        cost_cols = st.columns(6)
        ytd_footnote = ""
        with cost_cols[0]:
            kpi_card("YTD Actual Cost", fmt_money(ytd_cost_actual, unit_mode),
                     budget_variance_chip(ytd_cost_actual, ytd_cost_budget, unit_mode),
                     footnote=ytd_footnote)
        with cost_cols[1]:
            kpi_card("Current WFP Outlook", fmt_money(current_wfp_outlook_cost, unit_mode),
                     budget_variance_chip(current_wfp_outlook_cost, cp26_budget_cost, unit_mode))
        with cost_cols[2]:
            kpi_card("Scenario Outlook", fmt_money(scenario_outlook_cost, unit_mode),
                     budget_variance_chip(scenario_outlook_cost, cp26_budget_cost, unit_mode))
        with cost_cols[3]:
            kpi_card("CRR + Line of Sight (Do nothing scenario)", fmt_money(crr_line_of_sight_cost, unit_mode),
                     budget_variance_chip(crr_line_of_sight_cost, cp26_budget_cost, unit_mode))
        with cost_cols[4]:
            kpi_card("CP26 Budget", fmt_money(cp26_budget_cost, unit_mode),
                     chip_html("Reference", "grey"))
        with cost_cols[5]:
            kpi_card("Challengeable Growth", fmt_money(addressable_growth_cost, unit_mode),
                     chip_html("Non-committed growth", "blue"))

    st.markdown('<div class="section-title">👥 2026 HC Overview</div>', unsafe_allow_html=True)
    hc_cols = st.columns(6)

    ytd_hc_footnote = "Mar closing HC — full ledger scope (MT/Country)" if grade_active else ""
    with hc_cols[0]:
        kpi_card("YTD HC (Mar)", fmt_num(ytd_hc_actual),
                 budget_variance_chip(ytd_hc_actual, ytd_hc_budget, "$", is_hc=True),
                 footnote=ytd_hc_footnote)
    with hc_cols[1]:
        kpi_card("Current WFP Outlook", fmt_num(current_wfp_hc),
                 budget_variance_chip(current_wfp_hc, cp26_budget_hc, "$", is_hc=True))
    with hc_cols[2]:
        kpi_card("Scenario Outlook", fmt_num(scenario_hc),
                 budget_variance_chip(scenario_hc, cp26_budget_hc, "$", is_hc=True))
    with hc_cols[3]:
        kpi_card("CRR + Line of Sight (Do nothing scenario)", fmt_num(crr_line_of_sight_hc),
                 budget_variance_chip(crr_line_of_sight_hc, cp26_budget_hc, "$", is_hc=True))
    with hc_cols[4]:
        kpi_card("CP26 Budget", fmt_num(cp26_budget_hc),
                 chip_html("Reference", "grey"))
    with hc_cols[5]:
        kpi_card("Challengeable HC Growth", fmt_num(addressable_growth_hc),
                 chip_html("Non-committed growth", "blue"))

    # -------------------------------------------------
    # GRAPH FUNCTIONS
    # -------------------------------------------------
    def cost_waterfall_figure(df_in: pd.DataFrame, unit_mode_local: str) -> go.Figure:
        mar_actual_cost = df_in.loc[mar_mask, "Actual_Cost"].sum()
        dec_forecast_cost = df_in.loc[dec_mask, "Closing_HC"].mul(df_in.loc[dec_mask, "Monthly_Rate_USD"]).sum()
        forecast_df = df_in.loc[forecast_mask].copy()

        scale = 1_000_000 if unit_mode_local == "$m" else 1
        short_labels = {
            "Growth Hires": "Growth",
            "Regulatory Hires": "Reg Hires",
            "Replacements": "Repl",
            "Transfers In": "Transfers In",
            "Offshoring In": "Offshore In",
            "Transformation Exits": "Trans Exits",
            "Other Exits": "Other Exits",
            "Attrition": "Attrition",
            "Transfers Out": "Transfers Out",
            "Offshoring Out": "Offshore Out",
        }

        x_vals = ["Mar Actual"]
        measure = ["absolute"]
        y_vals = [mar_actual_cost / scale]
        step_vals = []
        hover_vals = [f"Mar Actual<br>Total: {fmt_money(mar_actual_cost, unit_mode_local)}"]

        for label, prefix in POSITIVE_DRIVERS:
            c_col, n_col = get_driver_cost_columns(prefix)
            committed = forecast_df.get(c_col, pd.Series(dtype=float)).sum()
            noncomm = forecast_df.get(n_col, pd.Series(dtype=float)).sum()
            total = committed + noncomm
            x_vals.append(short_labels.get(label, label))
            measure.append("relative")
            y_vals.append(total / scale)
            step_vals.append(total / scale)
            hover_vals.append(
                f"{label}<br>Committed: {fmt_money(committed, unit_mode_local)}"
                f"<br>Non-committed: {fmt_money(noncomm, unit_mode_local)}"
                f"<br>Total: {fmt_money(total, unit_mode_local)}"
            )

        for label, prefix in NEGATIVE_DRIVERS:
            c_col, n_col = get_driver_cost_columns(prefix)
            committed = forecast_df.get(c_col, pd.Series(dtype=float)).sum()
            noncomm = forecast_df.get(n_col, pd.Series(dtype=float)).sum()
            total = committed + noncomm
            x_vals.append(short_labels.get(label, label))
            measure.append("relative")
            y_vals.append(-(total / scale))
            step_vals.append(-(total / scale))
            hover_vals.append(
                f"{label}<br>Committed: {fmt_money(committed, unit_mode_local)}"
                f"<br>Non-committed: {fmt_money(noncomm, unit_mode_local)}"
                f"<br>Total reduction: {fmt_money(total, unit_mode_local)}"
            )

        end_val = dec_forecast_cost / scale
        x_vals.append("Dec Forecast")
        measure.append("total")
        y_vals.append(end_val)
        hover_vals.append(f"Dec Forecast<br>Total: {fmt_money(dec_forecast_cost, unit_mode_local)}")

        y_lower, y_upper = build_bridge_range(mar_actual_cost / scale, step_vals, end_val)
        axis_title = "Cost ($m)" if unit_mode_local == "$m" else "Cost ($)"

        fig = go.Figure(go.Waterfall(
            x=x_vals,
            y=y_vals,
            measure=measure,
            hovertext=hover_vals,
            hovertemplate="%{hovertext}<extra></extra>",
            connector={"line": {"color": "#8f8f8f", "width": 1.2}},
            increasing={"marker": {"color": "#ef4444"}},
            decreasing={"marker": {"color": "#22c55e"}},
            totals={"marker": {"color": "#2563eb"}},
            cliponaxis=False
        ))

        fig.update_layout(
            title="2026 Cost Bridge: Mar Actual to Dec Forecast",
            title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=plotly_font(), color="#374151", size=12),
            yaxis=dict(
                title=dict(text=axis_title, font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#374151", size=11),
                gridcolor="#e5e7eb",
                range=[y_lower, y_upper]
            ),
            xaxis=dict(
                title=dict(text="Drivers", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#6b7280", size=11),
                tickangle=-25
            ),
            margin=dict(l=55, r=15, t=55, b=85),
            height=470,
            showlegend=False
        )
        return fig

    def hc_waterfall_figure(df_in: pd.DataFrame) -> go.Figure:
        mar_actual_hc = df_in.loc[mar_mask, "Closing_HC"].sum()
        dec_forecast_hc = df_in.loc[dec_mask, "Closing_HC"].sum()
        forecast_df = df_in.loc[forecast_mask].copy()

        short_labels = {
            "Growth Hires": "Growth",
            "Regulatory Hires": "Reg Hires",
            "Replacements": "Repl",
            "Transfers In": "Transfers In",
            "Offshoring In": "Offshore In",
            "Transformation Exits": "Trans Exits",
            "Other Exits": "Other Exits",
            "Attrition": "Attrition",
            "Transfers Out": "Transfers Out",
            "Offshoring Out": "Offshore Out",
        }

        x_vals = ["Mar Actual"]
        measure = ["absolute"]
        y_vals = [mar_actual_hc]
        step_vals = []
        hover_vals = [f"Mar Actual<br>Total: {fmt_num(mar_actual_hc)}"]

        for label, prefix in POSITIVE_DRIVERS:
            c_col, n_col = get_driver_hc_columns(prefix)
            committed = forecast_df.get(c_col, pd.Series(dtype=float)).sum()
            noncomm = forecast_df.get(n_col, pd.Series(dtype=float)).sum()
            total = committed + noncomm
            x_vals.append(short_labels.get(label, label))
            measure.append("relative")
            y_vals.append(total)
            step_vals.append(total)
            hover_vals.append(
                f"{label}<br>Committed: {fmt_num(committed)}"
                f"<br>Non-committed: {fmt_num(noncomm)}"
                f"<br>Total: {fmt_num(total)}"
            )

        for label, prefix in NEGATIVE_DRIVERS:
            c_col, n_col = get_driver_hc_columns(prefix)
            committed = forecast_df.get(c_col, pd.Series(dtype=float)).sum()
            noncomm = forecast_df.get(n_col, pd.Series(dtype=float)).sum()
            total = committed + noncomm
            x_vals.append(short_labels.get(label, label))
            measure.append("relative")
            y_vals.append(-total)
            step_vals.append(-total)
            hover_vals.append(
                f"{label}<br>Committed: {fmt_num(committed)}"
                f"<br>Non-committed: {fmt_num(noncomm)}"
                f"<br>Total reduction: {fmt_num(total)}"
            )

        end_val = dec_forecast_hc
        x_vals.append("Dec Forecast")
        measure.append("total")
        y_vals.append(end_val)
        hover_vals.append(f"Dec Forecast<br>Total: {fmt_num(dec_forecast_hc)}")

        y_lower, y_upper = build_bridge_range(mar_actual_hc, step_vals, end_val)

        fig = go.Figure(go.Waterfall(
            x=x_vals,
            y=y_vals,
            measure=measure,
            hovertext=hover_vals,
            hovertemplate="%{hovertext}<extra></extra>",
            connector={"line": {"color": "#8f8f8f", "width": 1.2}},
            increasing={"marker": {"color": "#ef4444"}},
            decreasing={"marker": {"color": "#22c55e"}},
            totals={"marker": {"color": "#2563eb"}},
            cliponaxis=False
        ))

        fig.update_layout(
            title="2026 HC Bridge: Mar Actual to Dec Forecast",
            title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=plotly_font(), color="#374151", size=12),
            yaxis=dict(
                title=dict(text="HC", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#374151", size=11),
                gridcolor="#e5e7eb",
                range=[y_lower, y_upper]
            ),
            xaxis=dict(
                title=dict(text="Drivers", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#6b7280", size=11),
                tickangle=-25
            ),
            margin=dict(l=55, r=15, t=55, b=85),
            height=470,
            showlegend=False
        )
        return fig

    def monthly_growth_reduction_cost_figure(df_in: pd.DataFrame, unit_mode_local: str) -> go.Figure:
        forecast_df = df_in[df_in["Month_Type"].str.lower() == "forecast"].copy()
        if forecast_df.empty:
            return go.Figure()

        forecast_months = forecast_df[["Month", "Month_Num"]].drop_duplicates().sort_values("Month_Num")
        first_three_forecast = forecast_months["Month"].tolist()[:3]

        growth_comm_cols = [f"{prefix}_Committed_Cost" for _, prefix in POSITIVE_DRIVERS]
        growth_noncomm_cols = [f"{prefix}_NonCommitted_Cost" for _, prefix in POSITIVE_DRIVERS]
        red_comm_cols = [f"{prefix}_Committed_Cost" for _, prefix in NEGATIVE_DRIVERS]
        red_noncomm_cols = [f"{prefix}_NonCommitted_Cost" for _, prefix in NEGATIVE_DRIVERS]

        rows = []
        for m in forecast_months["Month"].tolist():
            temp = forecast_df[forecast_df["Month"] == m]
            cg = sum_cols(temp, growth_comm_cols).sum()
            ng = sum_cols(temp, growth_noncomm_cols).sum()
            cr = sum_cols(temp, red_comm_cols).sum()
            nr = sum_cols(temp, red_noncomm_cols).sum()

            if m in first_three_forecast:
                growth_total = cg
                reduction_total = cr
                growth_noncomm_show = 0
                reduction_noncomm_show = 0
            else:
                growth_total = cg + ng
                reduction_total = cr + nr
                growth_noncomm_show = ng
                reduction_noncomm_show = nr

            rows.append({
                "Month": m,
                "Month_Num": temp["Month_Num"].iloc[0],
                "Growth_Total": growth_total,
                "Reduction_Total": reduction_total,
                "Growth_Committed": cg,
                "Growth_NonCommitted": growth_noncomm_show,
                "Reduction_Committed": cr,
                "Reduction_NonCommitted": reduction_noncomm_show
            })

        monthly = pd.DataFrame(rows).sort_values("Month_Num")
        scale = 1_000_000 if unit_mode_local == "$m" else 1
        g_total = monthly["Growth_Total"] / scale
        r_total = -monthly["Reduction_Total"] / scale

        max_abs = max(g_total.abs().max(), r_total.abs().max(), 1) * 1.2
        axis_title = "Growth / Reduction ($m)" if unit_mode_local == "$m" else "Growth / Reduction ($)"

        growth_hover = []
        reduction_hover = []
        for _, r in monthly.iterrows():
            growth_hover.append(
                f"{r['Month']} Growth"
                f"<br>Committed: {fmt_money(r['Growth_Committed'], unit_mode_local)}"
                f"<br>Non-committed: {fmt_money(r['Growth_NonCommitted'], unit_mode_local)}"
                f"<br>Total: {fmt_money(r['Growth_Total'], unit_mode_local)}"
            )
            reduction_hover.append(
                f"{r['Month']} Reduction"
                f"<br>Committed: {fmt_money(r['Reduction_Committed'], unit_mode_local)}"
                f"<br>Non-committed: {fmt_money(r['Reduction_NonCommitted'], unit_mode_local)}"
                f"<br>Total reduction: {fmt_money(r['Reduction_Total'], unit_mode_local)}"
            )

        fig = go.Figure()
        fig.add_bar(x=monthly["Month"], y=g_total, name="Growth", marker_color="#ef4444",
                    hovertext=growth_hover, hovertemplate="%{hovertext}<extra></extra>")
        fig.add_bar(x=monthly["Month"], y=r_total, name="Reduction", marker_color="#22c55e",
                    hovertext=reduction_hover, hovertemplate="%{hovertext}<extra></extra>")
        fig.add_hline(y=0, line_width=2, line_color="#111827")

        fig.update_layout(
            title="Monthly Forecast Growth vs Reduction",
            title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=plotly_font(), color="#374151", size=12),
            barmode="relative",
            xaxis=dict(
                title=dict(text="Forecast Month", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#6b7280", size=11)
            ),
            yaxis=dict(
                title=dict(text=axis_title, font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#374151", size=11),
                gridcolor="#e5e7eb",
                range=[-max_abs, max_abs]
            ),
            legend=dict(orientation="h", y=1.08, x=0.0),
            margin=dict(l=55, r=15, t=55, b=40),
            height=470
        )
        return fig

    def monthly_growth_reduction_hc_figure(df_in: pd.DataFrame) -> go.Figure:
        forecast_df = df_in[df_in["Month_Type"].str.lower() == "forecast"].copy()
        if forecast_df.empty:
            return go.Figure()

        forecast_months = forecast_df[["Month", "Month_Num"]].drop_duplicates().sort_values("Month_Num")
        first_three_forecast = forecast_months["Month"].tolist()[:3]

        growth_comm_cols = [f"{prefix}_Committed_HC" for _, prefix in POSITIVE_DRIVERS]
        growth_noncomm_cols = [f"{prefix}_NonCommitted_HC" for _, prefix in POSITIVE_DRIVERS]
        red_comm_cols = [f"{prefix}_Committed_HC" for _, prefix in NEGATIVE_DRIVERS]
        red_noncomm_cols = [f"{prefix}_NonCommitted_HC" for _, prefix in NEGATIVE_DRIVERS]

        rows = []
        for m in forecast_months["Month"].tolist():
            temp = forecast_df[forecast_df["Month"] == m]
            cg = sum_cols(temp, growth_comm_cols).sum()
            ng = sum_cols(temp, growth_noncomm_cols).sum()
            cr = sum_cols(temp, red_comm_cols).sum()
            nr = sum_cols(temp, red_noncomm_cols).sum()

            if m in first_three_forecast:
                growth_total = cg
                reduction_total = cr
                growth_noncomm_show = 0
                reduction_noncomm_show = 0
            else:
                growth_total = cg + ng
                reduction_total = cr + nr
                growth_noncomm_show = ng
                reduction_noncomm_show = nr

            rows.append({
                "Month": m,
                "Month_Num": temp["Month_Num"].iloc[0],
                "Growth_Total": growth_total,
                "Reduction_Total": reduction_total,
                "Growth_Committed": cg,
                "Growth_NonCommitted": growth_noncomm_show,
                "Reduction_Committed": cr,
                "Reduction_NonCommitted": reduction_noncomm_show
            })

        monthly = pd.DataFrame(rows).sort_values("Month_Num")
        max_abs = max(monthly["Growth_Total"].abs().max(), monthly["Reduction_Total"].abs().max(), 1) * 1.2

        growth_hover = []
        reduction_hover = []
        for _, r in monthly.iterrows():
            growth_hover.append(
                f"{r['Month']} Growth"
                f"<br>Committed: {fmt_num(r['Growth_Committed'])}"
                f"<br>Non-committed: {fmt_num(r['Growth_NonCommitted'])}"
                f"<br>Total: {fmt_num(r['Growth_Total'])}"
            )
            reduction_hover.append(
                f"{r['Month']} Reduction"
                f"<br>Committed: {fmt_num(r['Reduction_Committed'])}"
                f"<br>Non-committed: {fmt_num(r['Reduction_NonCommitted'])}"
                f"<br>Total reduction: {fmt_num(r['Reduction_Total'])}"
            )

        fig = go.Figure()
        fig.add_bar(x=monthly["Month"], y=monthly["Growth_Total"], name="Growth", marker_color="#ef4444",
                    hovertext=growth_hover, hovertemplate="%{hovertext}<extra></extra>")
        fig.add_bar(x=monthly["Month"], y=-monthly["Reduction_Total"], name="Reduction", marker_color="#22c55e",
                    hovertext=reduction_hover, hovertemplate="%{hovertext}<extra></extra>")
        fig.add_hline(y=0, line_width=2, line_color="#111827")

        fig.update_layout(
            title="Monthly Forecast Growth vs Reduction (HC)",
            title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=plotly_font(), color="#374151", size=12),
            barmode="relative",
            xaxis=dict(
                title=dict(text="Forecast Month", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#6b7280", size=11)
            ),
            yaxis=dict(
                title=dict(text="Growth / Reduction (HC)", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#374151", size=11),
                gridcolor="#e5e7eb",
                range=[-max_abs, max_abs]
            ),
            legend=dict(orientation="h", y=1.08, x=0.0),
            margin=dict(l=55, r=15, t=55, b=40),
            height=470
        )
        return fig

    def monthly_cost_profile_figure(df_in: pd.DataFrame, unit_mode_local: str) -> go.Figure:
        monthly = (
            df_in.groupby(["Month_Num", "Month", "Month_Type"], as_index=False)["Derived_WFP_Monthly_Cost"]
            .sum()
            .sort_values("Month_Num")
        )

        scale = 1_000_000 if unit_mode_local == "$m" else 1
        monthly["Value"] = monthly["Derived_WFP_Monthly_Cost"] / scale

        actual = monthly[monthly["Month_Type"].str.lower() == "actual"]
        forecast = monthly[monthly["Month_Type"].str.lower() == "forecast"]

        y_min = monthly["Value"].min()
        y_max = monthly["Value"].max()
        spread = max(y_max - y_min, 1)
        lower = y_min - (spread * 0.35)
        upper = y_max + (spread * 0.25)

        axis_title = "Cost ($m)" if unit_mode_local == "$m" else "Cost ($)"

        fig = go.Figure()
        if not actual.empty:
            fig.add_bar(x=actual["Month"], y=actual["Value"], name="Actual", marker_color="#9ca3af")
        if not forecast.empty:
            fig.add_bar(x=forecast["Month"], y=forecast["Value"], name="Forecast", marker_color="#2563eb")

        fig.update_layout(
            title="2026 Cost Profile: Actual vs Forecast Months",
            title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=plotly_font(), color="#374151", size=12),
            barmode="group",
            xaxis=dict(
                title=dict(text="Month", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#6b7280", size=11),
                categoryorder="array",
                categoryarray=MONTHS
            ),
            yaxis=dict(
                title=dict(text=axis_title, font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#374151", size=11),
                gridcolor="#e5e7eb",
                range=[lower, upper]
            ),
            legend=dict(orientation="h", y=1.08, x=0.0),
            margin=dict(l=55, r=15, t=55, b=40),
            height=470
        )
        return fig

    def monthly_hc_profile_figure(df_in: pd.DataFrame) -> go.Figure:
        monthly = (
            df_in.groupby(["Month_Num", "Month", "Month_Type"], as_index=False)["Closing_HC"]
            .sum()
            .sort_values("Month_Num")
        )

        actual = monthly[monthly["Month_Type"].str.lower() == "actual"]
        forecast = monthly[monthly["Month_Type"].str.lower() == "forecast"]

        y_min = monthly["Closing_HC"].min()
        y_max = monthly["Closing_HC"].max()
        spread = max(y_max - y_min, 1)
        lower = y_min - (spread * 0.35)
        upper = y_max + (spread * 0.25)

        fig = go.Figure()
        if not actual.empty:
            fig.add_bar(x=actual["Month"], y=actual["Closing_HC"], name="Actual", marker_color="#9ca3af")
        if not forecast.empty:
            fig.add_bar(x=forecast["Month"], y=forecast["Closing_HC"], name="Forecast", marker_color="#2563eb")

        fig.update_layout(
            title="2026 HC Profile: Actual vs Forecast Months",
            title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=plotly_font(), color="#374151", size=12),
            barmode="group",
            xaxis=dict(
                title=dict(text="Month", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#6b7280", size=11),
                categoryorder="array",
                categoryarray=MONTHS
            ),
            yaxis=dict(
                title=dict(text="HC", font=dict(family=plotly_font(), color="#374151", size=13)),
                tickfont=dict(family=plotly_font(), color="#374151", size=11),
                gridcolor="#e5e7eb",
                range=[lower, upper]
            ),
            legend=dict(orientation="h", y=1.08, x=0.0),
            margin=dict(l=55, r=15, t=55, b=40),
            height=470
        )
        return fig

    # -------------------------------------------------
    # COUNTRY CONCENTRATION CHART
    # -------------------------------------------------
    def country_concentration_figure(df_in: pd.DataFrame, unit_mode_local: str, hc_mode: bool = False) -> go.Figure:
        unique_mts = sorted(df_in["MT"].dropna().astype(str).unique().tolist())
        use_mt_colours = len(unique_mts) > 1 and not hc_mode
        scale = get_scale(unit_mode_local)

        if use_mt_colours:
            axis_title = f"Overrun vs Budget ({unit_mode_local})"
            chart_title = "Country Overrun Concentration by MT (Outlook vs Budget)"
            grp = df_in.groupby(["Country", "MT"], as_index=False).agg(
                Outlook=("Derived_WFP_Monthly_Cost", "sum"),
                Budget=("Derived_Budget_Monthly_Cost", "sum")
            )
            grp["Gap"]        = grp["Outlook"] - grp["Budget"]
            grp["Gap_Scaled"] = grp["Gap"] / scale
            country_order = (
                grp.groupby("Country")["Gap"].sum()
                .sort_values(ascending=True).index.tolist()
            )
            mt_colours = {mt: MT_COLOUR_PALETTE[i % len(MT_COLOUR_PALETTE)]
                          for i, mt in enumerate(unique_mts)}
            bar_height = max(420, len(country_order) * 22)
            fig = go.Figure()
            for mt in unique_mts:
                mt_data = grp[grp["MT"] == mt].set_index("Country")
                x_vals, hover = [], []
                for c in country_order:
                    if c in mt_data.index:
                        row = mt_data.loc[c]
                        x_vals.append(float(row["Gap_Scaled"]))
                        hover.append(
                            f"{c} — {mt}"
                            f"<br>Outlook: {fmt_money(float(row['Outlook']), unit_mode_local)}"
                            f"<br>Budget: {fmt_money(float(row['Budget']), unit_mode_local)}"
                            f"<br>Gap: {fmt_money(float(row['Gap']), unit_mode_local)}"
                        )
                    else:
                        x_vals.append(0)
                        hover.append(f"{c} — {mt}<br>No data")
                fig.add_bar(
                    x=x_vals, y=country_order, name=mt,
                    orientation="h", marker_color=mt_colours[mt],
                    hovertext=hover, hovertemplate="%{hovertext}<extra></extra>"
                )
            fig.add_vline(x=0, line_width=1.5, line_color="#111827")
            fig.update_layout(
                title=chart_title,
                title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
                barmode="relative", plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family=plotly_font(), color="#374151", size=12),
                xaxis=dict(title=dict(text=axis_title, font=dict(family=plotly_font(), color="#374151", size=13)),
                           tickfont=dict(family=plotly_font(), color="#374151", size=11),
                           gridcolor="#e5e7eb", zeroline=False),
                yaxis=dict(tickfont=dict(family=plotly_font(), color="#374151", size=11), automargin=True),
                legend=dict(orientation="h", y=1.03, x=0, font=dict(size=11)),
                margin=dict(l=10, r=20, t=70, b=40),
                height=bar_height, showlegend=True
            )
            return fig

        # Single MT or HC mode — red/green single bar
        if hc_mode:
            country_out = df_in.groupby("Country", as_index=False)["Closing_HC"].sum().rename(columns={"Closing_HC": "Outlook"})
            country_bud = df_in.groupby("Country", as_index=False)["Budget_HC"].sum().rename(columns={"Budget_HC": "Budget"})
            merged = country_out.merge(country_bud, on="Country", how="outer").fillna(0)
            merged["Gap"] = merged["Outlook"] - merged["Budget"]
            merged["Gap_Scaled"] = merged["Gap"]
            axis_title = "HC Overrun vs Budget"
            chart_title = "Country HC Overrun Concentration (Outlook vs Budget)"
        else:
            country_out = df_in.groupby("Country", as_index=False)["Derived_WFP_Monthly_Cost"].sum().rename(columns={"Derived_WFP_Monthly_Cost": "Outlook"})
            country_bud = df_in.groupby("Country", as_index=False)["Derived_Budget_Monthly_Cost"].sum().rename(columns={"Derived_Budget_Monthly_Cost": "Budget"})
            merged = country_out.merge(country_bud, on="Country", how="outer").fillna(0)
            merged["Gap"] = merged["Outlook"] - merged["Budget"]
            merged["Gap_Scaled"] = merged["Gap"] / scale
            axis_title = f"Overrun vs Budget ({unit_mode_local})"
            chart_title = "Country Overrun Concentration (Outlook vs Budget)"

        merged = merged.sort_values("Gap", ascending=True).reset_index(drop=True)
        colors = ["#ef4444" if g > 0 else "#22c55e" for g in merged["Gap"]]
        if hc_mode:
            hover = [f"{r['Country']}<br>HC Outlook: {fmt_num(r['Outlook'])}<br>HC Budget: {fmt_num(r['Budget'])}<br>HC Gap: {fmt_num(r['Gap'])}" for _, r in merged.iterrows()]
        else:
            hover = [f"{r['Country']}<br>Outlook: {fmt_money(r['Outlook'], unit_mode_local)}<br>Budget: {fmt_money(r['Budget'], unit_mode_local)}<br>Gap: {fmt_money(r['Gap'], unit_mode_local)}" for _, r in merged.iterrows()]
        bar_height = max(420, len(merged) * 22)
        fig = go.Figure()
        fig.add_bar(x=merged["Gap_Scaled"], y=merged["Country"], orientation="h",
                    marker_color=colors, hovertext=hover, hovertemplate="%{hovertext}<extra></extra>")
        fig.add_vline(x=0, line_width=1.5, line_color="#111827")
        fig.update_layout(
            title=chart_title, title_font=dict(family=plotly_font(), size=18, color="#1f2937"),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family=plotly_font(), color="#374151", size=12),
            xaxis=dict(title=dict(text=axis_title, font=dict(family=plotly_font(), color="#374151", size=13)),
                       tickfont=dict(family=plotly_font(), color="#374151", size=11),
                       gridcolor="#e5e7eb", zeroline=False),
            yaxis=dict(tickfont=dict(family=plotly_font(), color="#374151", size=11), automargin=True),
            margin=dict(l=10, r=20, t=55, b=40), height=bar_height, showlegend=False
        )
        return fig


    # -------------------------------------------------
    # DRIVER DECOMPOSITION TABLE
    # -------------------------------------------------
    def driver_decomposition_table(df_in: pd.DataFrame, unit_mode_local: str, hc_only: bool = False) -> pd.DataFrame:
        forecast_df = df_in.loc[forecast_mask].copy()

        def make_row(label, direction, comm_hc, noncomm_hc, comm_cost=0, noncomm_cost=0, row_type="driver"):
            total_hc   = comm_hc + noncomm_hc
            total_cost = comm_cost + noncomm_cost
            row = {
                "Driver":             label,
                "Direction":          direction,
                "Committed HC":       int(round(comm_hc)),
                "Non-Committed HC":   int(round(noncomm_hc)),
                "Total HC":           int(round(total_hc)),
                "_row_type":          row_type,
                "_comm_cost_raw":     comm_cost,
                "_noncomm_cost_raw":  noncomm_cost,
                "_total_cost_raw":    total_cost,
            }
            if not hc_only:
                row["Committed Cost"]     = fmt_money(comm_cost, unit_mode_local)
                row["Non-Committed Cost"] = fmt_money(noncomm_cost, unit_mode_local)
                row["Total Cost"]         = fmt_money(total_cost, unit_mode_local)
            return row

        growth_rows    = []
        reduction_rows = []

        for label, prefix in POSITIVE_DRIVERS:
            c_hc_col, n_hc_col   = get_driver_hc_columns(prefix)
            c_cost_col, n_cost_col = get_driver_cost_columns(prefix)
            comm_hc    = forecast_df.get(c_hc_col,   pd.Series(dtype=float)).sum()
            noncomm_hc = forecast_df.get(n_hc_col,   pd.Series(dtype=float)).sum()
            comm_cost    = forecast_df.get(c_cost_col, pd.Series(dtype=float)).sum() if not hc_only else 0
            noncomm_cost = forecast_df.get(n_cost_col, pd.Series(dtype=float)).sum() if not hc_only else 0
            if int(round(comm_hc + noncomm_hc)) != 0:
                growth_rows.append(make_row(label, "Growth", comm_hc, noncomm_hc, comm_cost, noncomm_cost))

        for label, prefix in NEGATIVE_DRIVERS:
            c_hc_col, n_hc_col   = get_driver_hc_columns(prefix)
            c_cost_col, n_cost_col = get_driver_cost_columns(prefix)
            comm_hc    = forecast_df.get(c_hc_col,   pd.Series(dtype=float)).sum()
            noncomm_hc = forecast_df.get(n_hc_col,   pd.Series(dtype=float)).sum()
            comm_cost    = forecast_df.get(c_cost_col, pd.Series(dtype=float)).sum() if not hc_only else 0
            noncomm_cost = forecast_df.get(n_cost_col, pd.Series(dtype=float)).sum() if not hc_only else 0
            if int(round(comm_hc + noncomm_hc)) != 0:
                reduction_rows.append(make_row(label, "Reduction", comm_hc, noncomm_hc, comm_cost, noncomm_cost))

        def subtotal_row(rows, label, direction):
            s_comm_hc    = sum(r["Committed HC"]       for r in rows)
            s_noncomm_hc = sum(r["Non-Committed HC"]   for r in rows)
            s_comm_cost  = sum(r["_comm_cost_raw"]     for r in rows)
            s_noncomm_cost = sum(r["_noncomm_cost_raw"] for r in rows)
            return make_row(label, direction, s_comm_hc, s_noncomm_hc, s_comm_cost, s_noncomm_cost, row_type="subtotal")

        all_rows = []

        # Growth drivers + subtotal
        all_rows.extend(growth_rows)
        if growth_rows:
            all_rows.append(subtotal_row(growth_rows, "GROWTH SUBTOTAL", "Growth Subtotal"))

        # Reduction drivers + subtotal
        all_rows.extend(reduction_rows)
        if reduction_rows:
            all_rows.append(subtotal_row(reduction_rows, "REDUCTION SUBTOTAL", "Reduction Subtotal"))

        # Net movement row — non-committed cost should = Challengeable Growth tile
        g_sub = next((r for r in all_rows if r["Driver"] == "GROWTH SUBTOTAL"), None)
        r_sub = next((r for r in all_rows if r["Driver"] == "REDUCTION SUBTOTAL"), None)

        net_comm_hc      = (g_sub["Committed HC"]     if g_sub else 0) - (r_sub["Committed HC"]     if r_sub else 0)
        net_noncomm_hc   = (g_sub["Non-Committed HC"] if g_sub else 0) - (r_sub["Non-Committed HC"] if r_sub else 0)
        net_comm_cost    = (g_sub["_comm_cost_raw"]   if g_sub else 0) - (r_sub["_comm_cost_raw"]   if r_sub else 0)
        net_noncomm_cost = (g_sub["_noncomm_cost_raw"] if g_sub else 0) - (r_sub["_noncomm_cost_raw"] if r_sub else 0)

        all_rows.append(make_row("NET MOVEMENT", "Net", net_comm_hc, net_noncomm_hc, net_comm_cost, net_noncomm_cost, row_type="net"))

        df_out = pd.DataFrame(all_rows)

        # Drop internal raw columns
        df_out = df_out.drop(columns=["_comm_cost_raw", "_noncomm_cost_raw", "_total_cost_raw"], errors="ignore")

        return df_out


    # -------------------------------------------------
    # COST GRAPH SECTION
    # -------------------------------------------------
    st.markdown('<hr class="sc-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 2026 Cost Graphs</div>', unsafe_allow_html=True)

    if grade_active:
        st.markdown(
            """
            <div style="background:#fff8e1; border:1px solid #f59e0b; border-radius:14px;
                        padding:16px 20px; margin-bottom:8px;">
                <span style="font-size:13px; color:#78350f;">
                    ⚠️ Cost charts are not shown when a grade filter is active.
                    The cost waterfall and monthly profiles blend GL actuals (no grade) with grade-specific
                    forecast costs, which would produce misleading visuals.
                    Select <strong>All</strong> grades to restore the full cost graph view.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        c1, c2, c3 = st.columns([1.15, 1.15, 1.1], gap="medium")
        with c1:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(cost_waterfall_figure(df_scope, unit_mode), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(monthly_growth_reduction_cost_figure(df_scope, unit_mode), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(monthly_cost_profile_figure(df_scope, unit_mode), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------
    # HC GRAPH SECTION
    # -------------------------------------------------
    st.markdown('<div class="section-title">👥 2026 HC Graphs</div>', unsafe_allow_html=True)

    h1, h2, h3 = st.columns([1.15, 1.15, 1.1], gap="medium")
    with h1:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(hc_waterfall_figure(df_scope), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(monthly_growth_reduction_hc_figure(df_scope), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with h3:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(monthly_hc_profile_figure(df_scope), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------
    # FORECAST EVOLUTION SECTION
    # -------------------------------------------------
    wfp_snapshots = scan_wfp_snapshots()
    if wfp_snapshots:
        st.markdown('<hr class="sc-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Dec Forecast Evolution — WFP Close Trend</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:13px;color:#5f6878;margin-bottom:10px;'>"
            "Each data point shows the Dec forecast as of that month's WFP close. "
            "Months without a saved snapshot are blank. "
            "Converging towards the budget line = improving position.</p>",
            unsafe_allow_html=True
        )

        # Delta summary tiles between consecutive snapshots
        if len(wfp_snapshots) >= 2:
            delta_cols = st.columns(len(wfp_snapshots) - 1)
            prev_hc = None
            for idx, (mon_num, label, df_s) in enumerate(wfp_snapshots):
                df_sc = df_s.copy()
                if selected_mt != "All":      df_sc = df_sc[df_sc["MT"] == selected_mt]
                if selected_country != "All": df_sc = df_sc[df_sc["Country"] == selected_country]
                if selected_grade != "All":   df_sc = df_sc[df_sc["Grade"] == selected_grade]
                hc = df_sc[df_sc["Month"].eq("Dec")]["Closing_HC"].sum()
                if prev_hc is not None:
                    delta = hc - prev_hc
                    colour = "#15803d" if delta < 0 else "#b91c1c"
                    arrow  = "▼" if delta < 0 else "▲"
                    prev_label = wfp_snapshots[idx-1][1]
                    delta_cols[idx-1].markdown(
                        f"""<div class="kpi-card" style="min-height:unset;padding:10px 14px;">
                            <div class="kpi-title" style="font-size:11px;">{prev_label} → {label}</div>
                            <div style="font-size:17px;font-weight:700;color:{colour};">
                                {arrow} {fmt_num(abs(delta))} HC</div>
                            <div style="font-size:11px;color:#7d7d7d;margin-top:2px;">
                                Dec forecast movement</div>
                        </div>""", unsafe_allow_html=True
                    )
                prev_hc = hc

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        scope_filters = {
            "mt": selected_mt, "country": selected_country, "grade": selected_grade
        }
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(
            forecast_evolution_figure(wfp_snapshots, df_scope, unit_mode, scope_filters),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<hr class="sc-divider">', unsafe_allow_html=True)
        st.markdown(
            "<div style='background:#f9fafb;border:1px solid #e0e3ea;border-radius:12px;"
            "padding:14px 18px;color:#5f6878;font-size:13px;'>"
            "📈 <strong>Forecast Evolution:</strong> Place dated WFP snapshots "
            "(e.g. <code>WFP_Data_Jan26.csv</code>, <code>WFP_Data_Feb26.csv</code>) "
            "in the same folder as the app to enable the Dec forecast trend chart."
            "</div>",
            unsafe_allow_html=True
        )

    # -------------------------------------------------
    # COUNTRY CONCENTRATION SECTION
    # -------------------------------------------------
    st.markdown('<hr class="sc-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌍 Country Overrun Concentration</div>', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:13px; color:#5f6878; margin-bottom:10px;'>"
        "Red bars = outlook above budget (overrun risk). Green bars = outlook below budget (favourable). "
        "Sorted ascending so highest-risk countries appear at the top.</p>",
        unsafe_allow_html=True
    )

    if selected_country != "All":
        st.info("Country filter is active — showing single-country view. Select 'All' countries to see the full concentration chart.")
    else:
        if grade_active:
            st.markdown(
                "<p style='font-size:13px; color:#b45309; margin-bottom:8px;'>"
                "⚠️ Showing <strong>HC concentration</strong> (cost concentration not available at grade level). "
                "Red = HC outlook above budget. Green = below budget.</p>",
                unsafe_allow_html=True
            )
            st.markdown('<div class="chart-wrap" style="overflow-y:auto;">', unsafe_allow_html=True)
            st.plotly_chart(country_concentration_figure(df_scope, unit_mode, hc_mode=True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="chart-wrap" style="overflow-y:auto;">', unsafe_allow_html=True)
            st.plotly_chart(country_concentration_figure(df_scope, unit_mode, hc_mode=False), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------
    # DRIVER DECOMPOSITION SECTION
    # -------------------------------------------------
    st.markdown('<hr class="sc-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 Driver Decomposition: Committed vs Non-Committed</div>', unsafe_allow_html=True)

    driver_df_display = driver_decomposition_table(df_scope, unit_mode, hc_only=grade_active)

    # Drop internal helper column before display
    if "_row_type" in driver_df_display.columns:
        driver_df_display = driver_df_display.drop(columns=["_row_type"])

    if grade_active:
        st.markdown(
            "<p style='font-size:13px; color:#b45309; margin-bottom:8px;'>"
            "⚠️ Showing <strong>HC columns only</strong> — cost columns suppressed as they are not valid at grade level.</p>",
            unsafe_allow_html=True
        )

    def style_row(row):
        driver    = str(row.get("Driver", ""))
        direction = str(row.get("Direction", ""))
        if driver == "NET MOVEMENT":
            return [
                "background-color: #1f2b4d; color: white !important; font-weight:700; "
                "border-top: 2px solid #04145f;"
            ] * len(row)
        elif "SUBTOTAL" in driver and "Growth" in direction:
            return [
                "background-color: rgba(239,68,68,0.10); color: #1f2937; font-weight:700; "
                "border-top: 1.5px solid #ef4444; border-bottom: 1.5px solid #ef4444;"
            ] * len(row)
        elif "SUBTOTAL" in driver:
            return [
                "background-color: rgba(34,197,94,0.10); color: #1f2937; font-weight:700; "
                "border-top: 1.5px solid #22c55e; border-bottom: 1.5px solid #22c55e;"
            ] * len(row)
        return [""] * len(row)

    def colour_direction(val):
        if val == "Growth":
            return "background-color: rgba(239,68,68,0.08); color: #b91c1c; font-weight:600;"
        elif val == "Reduction":
            return "background-color: rgba(34,197,94,0.08); color: #15803d; font-weight:600;"
        elif val == "Growth Subtotal":
            return "background-color: rgba(239,68,68,0.18); color: #991b1b; font-weight:700;"
        elif val == "Reduction Subtotal":
            return "background-color: rgba(34,197,94,0.18); color: #14532d; font-weight:700;"
        elif val == "Net":
            return "background-color: #1f2b4d; color: white; font-weight:700;"
        return ""

    def _fmt_hc_cell(v):
        try:
            return f"{int(v):,}" if v != "" else ""
        except (ValueError, TypeError):
            return v

    styled = (
        driver_df_display.style
        .apply(style_row, axis=1)
        .map(colour_direction, subset=["Direction"])
        .format({
            "Committed HC":     _fmt_hc_cell,
            "Non-Committed HC": _fmt_hc_cell,
            "Total HC":         _fmt_hc_cell,
        })
        .set_table_styles([
            {"selector": "thead th", "props": [
                ("background-color", "#04145f"), ("color", "white"),
                ("font-size", "12px"), ("font-weight", "600"),
                ("padding", "8px 10px"), ("text-align", "center")
            ]},
            {"selector": "tbody td", "props": [
                ("font-size", "12px"), ("padding", "7px 10px"),
                ("text-align", "center"), ("border-bottom", "1px solid #f0f0f0"),
                ("color", "#1f2937")
            ]},
            {"selector": "tbody tr:nth-child(even)", "props": [
                ("background-color", "#fafafa")
            ]},
            {"selector": "tbody tr:hover", "props": [
                ("background-color", "#f0f4ff")
            ]},
        ])
        .hide(axis="index")
    )

    st.write(styled.to_html(), unsafe_allow_html=True)

    # -------------------------------------------------
    # EXPORT SECTION
    # -------------------------------------------------
    st.markdown('<hr class="sc-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⬇️ Export Data</div>', unsafe_allow_html=True)

    scope_label = f"MT={selected_mt}_Country={selected_country}_Grade={selected_grade}"

    exp1, exp2, exp3 = st.columns(3)

    with exp1:
        # When grade active, export only HC and non-cost columns from filtered dataset
        if grade_active:
            cost_cols_to_drop = [c for c in df_scope.columns if c.endswith("_Cost") or c in ["Actual_Cost", "Derived_WFP_Monthly_Cost", "Derived_Budget_Monthly_Cost"]]
            export_df = df_scope.drop(columns=[c for c in cost_cols_to_drop if c in df_scope.columns])
            export_label = "📥 Download filtered dataset — HC only (CSV)"
        else:
            export_df = df_scope
            export_label = "📥 Download filtered dataset (CSV)"
        csv_full = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=export_label,
            data=csv_full,
            file_name=f"WFP_filtered_{scope_label}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp2:
        driver_csv = driver_df_display.to_csv(index=False).encode("utf-8")
        driver_label = "📥 Download driver decomposition — HC only (CSV)" if grade_active else "📥 Download driver decomposition (CSV)"
        st.download_button(
            label=driver_label,
            data=driver_csv,
            file_name=f"WFP_driver_decomp_{scope_label}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp3:
        if selected_country == "All":
            if grade_active:
                # HC-based country concentration when grade filtered
                country_conc = df_scope.groupby("Country", as_index=False).agg(
                    HC_Outlook=("Closing_HC", "sum"),
                    HC_Budget=("Budget_HC", "sum")
                )
                country_conc["HC_Gap"] = country_conc["HC_Outlook"] - country_conc["HC_Budget"]
                country_conc = country_conc.sort_values("HC_Gap", ascending=False)
                conc_label = "📥 Download country HC concentration (CSV)"
            else:
                country_conc = df_scope.groupby("Country", as_index=False).agg(
                    Outlook_Cost=("Derived_WFP_Monthly_Cost", "sum"),
                    Budget_Cost=("Derived_Budget_Monthly_Cost", "sum"),
                    Closing_HC=("Closing_HC", "sum"),
                    Budget_HC=("Budget_HC", "sum")
                )
                country_conc["Cost_Gap"] = country_conc["Outlook_Cost"] - country_conc["Budget_Cost"]
                country_conc["HC_Gap"] = country_conc["Closing_HC"] - country_conc["Budget_HC"]
                country_conc = country_conc.sort_values("Cost_Gap", ascending=False)
                conc_label = "📥 Download country concentration (CSV)"
            conc_csv = country_conc.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=conc_label,
                data=conc_csv,
                file_name=f"WFP_country_concentration_{scope_label}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Select 'All' countries to enable country concentration export.")
# =================================================
# SCENARIO BUILDER FUNCTIONS
# =================================================
def get_grade_avg_rate(df_in: pd.DataFrame, grade: str) -> float:
    rates = df_in[df_in["Grade"] == grade]["Monthly_Rate_USD"]
    return float(rates.mean()) if not rates.empty else 0.0

def compute_scenario_impacts(df_in: pd.DataFrame, levers: dict) -> dict:
    fcast_df = df_in[df_in["Month_Type"].str.lower() == "forecast"].copy()
    baseline_cost = df_in["Derived_WFP_Monthly_Cost"].sum()
    baseline_hc   = df_in[df_in["Month"].eq("Dec")]["Closing_HC"].sum()
    baseline_budget_cost = df_in["Derived_Budget_Monthly_Cost"].sum()

    lever_rows = []
    total_cost_delta = 0.0
    total_hc_delta   = 0.0

    # --- Lever 1: Block non-committed growth ---
    block_pct = levers.get("block_pct", 0) / 100.0
    if block_pct > 0:
        nc_cost_cols = [f"{p}_NonCommitted_Cost" for _, p in POSITIVE_DRIVERS]
        nc_hc_cols   = [f"{p}_NonCommitted_HC"   for _, p in POSITIVE_DRIVERS]
        saved_cost = sum_cols(fcast_df, nc_cost_cols).sum() * block_pct
        dec_df = fcast_df[fcast_df["Month"].eq("Dec")]
        saved_hc   = sum_cols(dec_df, nc_hc_cols).sum() * block_pct
        lever_rows.append({
            "Lever": f"Block {levers['block_pct']:.0f}% non-committed growth",
            "Delta HC": -int(round(saved_hc)),
            "Delta Cost": -saved_cost
        })
        total_cost_delta -= saved_cost
        total_hc_delta   -= saved_hc

    # --- Lever 2: Delay hiring (applies to residual AFTER Lever 1 block) ---
    # If Lever 1 has already blocked block_pct of non-committed growth,
    # Lever 2 can only save on the remaining (1 - block_pct) share.
    delay_cutoff_num  = levers.get("delay_cutoff_num", 0)
    delay_cutoff_name = levers.get("delay_cutoff_name", "")
    delay_grade       = levers.get("delay_grade", "All grades")
    delay_n_roles     = int(levers.get("delay_n_roles", 0))
    if delay_cutoff_num > 0:
        early_df = fcast_df[fcast_df["Month_Num"] < delay_cutoff_num].copy()
        if delay_grade != "All grades":
            early_df = early_df[early_df["Grade"] == delay_grade]
        nc_cost_cols = [f"{p}_NonCommitted_Cost" for _, p in POSITIVE_DRIVERS]
        nc_hc_cols   = [f"{p}_NonCommitted_HC"   for _, p in POSITIVE_DRIVERS]
        total_nc_cost = sum_cols(early_df, nc_cost_cols).sum()
        total_nc_hc   = sum_cols(early_df, nc_hc_cols).sum()
        if delay_n_roles > 0 and total_nc_hc > 0:
            cap_frac      = min(1.0, delay_n_roles / total_nc_hc)
            total_nc_cost = total_nc_cost * cap_frac
        residual_factor = 1.0 - block_pct
        saved_cost = total_nc_cost * residual_factor
        grade_lbl = delay_grade if delay_grade != "All grades" else "all grades"
        roles_lbl = f"{delay_n_roles} roles" if delay_n_roles > 0 else "all roles"
        label = f"Delay hiring ({roles_lbl}, {grade_lbl}) — earliest start {delay_cutoff_name}"
        if block_pct > 0:
            label += f" (on {int(residual_factor*100)}% residual after Lever 1)"
        lever_rows.append({
            "Lever": label,
            "Delta HC": 0,
            "Delta Cost": -saved_cost
        })
        total_cost_delta -= saved_cost

    # --- Lever 3: Juniorisation (stackable) ---
    for conv in levers.get("juniorisations", []):
        from_grade    = conv.get("from_grade", "")
        to_grade      = conv.get("to_grade", "")
        n_roles       = int(conv.get("n_roles", 0))
        eff_month_num = int(conv.get("eff_month_num", 1))
        if not from_grade or not to_grade or n_roles <= 0:
            continue
        from_rate = get_grade_avg_rate(df_in, from_grade)
        to_rate   = get_grade_avg_rate(df_in, to_grade)
        if from_rate <= 0 or to_rate <= 0 or from_rate <= to_rate:
            continue
        rate_diff      = from_rate - to_rate
        months_ahead   = max(0, 12 - eff_month_num + 1)
        saved_cost     = n_roles * rate_diff * months_ahead
        lever_rows.append({
            "Lever": f"Juniorise {n_roles} {from_grade}→{to_grade} from {MONTHS[eff_month_num-1]}",
            "Delta HC": 0,
            "Delta Cost": -saved_cost
        })
        total_cost_delta -= saved_cost

    # --- Lever 4: Accelerate exits ---
    accel_hc        = int(levers.get("accel_exits_hc", 0))
    accel_month_num = int(levers.get("accel_exits_month_num", 0))
    accel_grade     = levers.get("accel_grade", "All grades")
    if accel_hc > 0 and accel_month_num > 0:
        if accel_grade != "All grades":
            grade_fcast = fcast_df[fcast_df["Grade"] == accel_grade]
            avg_rate = float(grade_fcast["Monthly_Rate_USD"].mean()) if not grade_fcast.empty else float(fcast_df["Monthly_Rate_USD"].mean())
        else:
            avg_rate = float(fcast_df["Monthly_Rate_USD"].mean()) if not fcast_df.empty else 0
        months_ahead   = max(0, 12 - accel_month_num + 1)
        saved_cost     = accel_hc * avg_rate * months_ahead
        grade_lbl = accel_grade if accel_grade != "All grades" else "all grades"
        lever_rows.append({
            "Lever": f"Accelerate {accel_hc} exits ({grade_lbl}) from {MONTHS[accel_month_num-1]}",
            "Delta HC": -accel_hc,
            "Delta Cost": -saved_cost
        })
        total_cost_delta -= saved_cost
        total_hc_delta   -= accel_hc

    # --- Lever 5: Rate card adjustment ---
    rate_adj_pct = levers.get("rate_adj_pct", 0.0)
    if rate_adj_pct != 0:
        fcast_cost  = fcast_df["Derived_WFP_Monthly_Cost"].sum()
        cost_delta  = fcast_cost * (rate_adj_pct / 100.0)
        lever_rows.append({
            "Lever": f"Rate card {rate_adj_pct:+.1f}%",
            "Delta HC": 0,
            "Delta Cost": cost_delta
        })
        total_cost_delta += cost_delta

    scenario_cost = baseline_cost + total_cost_delta
    scenario_hc   = baseline_hc   + total_hc_delta

    return {
        "baseline_cost":       baseline_cost,
        "baseline_hc":         baseline_hc,
        "baseline_budget_cost": baseline_budget_cost,
        "scenario_cost":       scenario_cost,
        "scenario_hc":         scenario_hc,
        "total_cost_delta":    total_cost_delta,
        "total_hc_delta":      total_hc_delta,
        "lever_rows":          lever_rows,
    }


def scenario_bridge_figure(result: dict, unit_mode_local: str) -> go.Figure:
    if unit_mode_local == "$m":
        scale = 1_000_000
        axis_title = "Cost ($m)"
    elif unit_mode_local == "$000s":
        scale = 1_000
        axis_title = "Cost ($000s)"
    else:
        scale = 1
        axis_title = "Cost ($)"

    x_vals    = ["WFP Outlook"]
    measure   = ["absolute"]
    y_vals    = [result["baseline_cost"] / scale]
    hover_vals = [f"WFP Outlook<br>{fmt_money(result['baseline_cost'], unit_mode_local)}"]

    for lr in result["lever_rows"]:
        x_vals.append(lr["Lever"])
        measure.append("relative")
        y_vals.append(lr["Delta Cost"] / scale)
        hc_str = f"{lr['Delta HC']:+,}" if lr["Delta HC"] != 0 else "No change"
        hover_vals.append(
            f"{lr['Lever']}"
            f"<br>Cost: {fmt_money(lr['Delta Cost'], unit_mode_local)}"
            f"<br>HC: {hc_str}"
        )

    x_vals.append("Scenario Outlook")
    measure.append("total")
    y_vals.append(result["scenario_cost"] / scale)
    hover_vals.append(f"Scenario Outlook<br>{fmt_money(result['scenario_cost'], unit_mode_local)}")

    step_vals = y_vals[1:-1]
    y_lower, y_upper = build_bridge_range(y_vals[0], step_vals, y_vals[-1])

    fig = go.Figure(go.Waterfall(
        x=x_vals, y=y_vals, measure=measure,
        hovertext=hover_vals, hovertemplate="%{hovertext}<extra></extra>",
        connector={"line": {"color": "#8f8f8f", "width": 1.2}},
        increasing={"marker": {"color": "#ef4444"}},
        decreasing={"marker": {"color": "#22c55e"}},
        totals={"marker": {"color": "#2563eb"}},
        cliponaxis=False
    ))
    fig.add_hline(
        y=result["baseline_budget_cost"] / scale,
        line_dash="dash", line_color="#f59e0b", line_width=1.5,
        annotation_text="Budget", annotation_position="right",
        annotation_font=dict(color="#b45309", size=11)
    )
    fig.update_layout(
        title="Scenario Bridge: WFP Outlook → Scenario Outlook",
        title_font=dict(family=plotly_font(), size=16, color="#1f2937"),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family=plotly_font(), color="#111827", size=11),
        yaxis=dict(
            title=dict(text=axis_title, font=dict(family=plotly_font(), size=12, color="#111827")),
            tickfont=dict(family=plotly_font(), size=11, color="#111827"),
            gridcolor="#e5e7eb", range=[y_lower, y_upper]
        ),
        xaxis=dict(
            tickfont=dict(family=plotly_font(), size=11, color="#111827"),
            tickangle=-25
        ),
        margin=dict(l=60, r=60, t=50, b=100),
        height=430, showlegend=False
    )
    return fig


def build_scenario_export_df(df_base: pd.DataFrame, levers: dict, result: dict) -> pd.DataFrame:
    df = df_base.copy()

    # Cast all numeric columns to float to avoid dtype errors on multiplication
    num_cols = [c for c in df.columns if df[c].dtype in ("int64", "int32", "float64", "float32")]
    df[num_cols] = df[num_cols].astype(float)

    fcast = df["Month_Type"].str.lower() == "forecast"

    # Block non-committed growth
    block_pct = levers.get("block_pct", 0) / 100.0
    if block_pct > 0:
        for _, p in POSITIVE_DRIVERS:
            for col in [f"{p}_NonCommitted_HC", f"{p}_NonCommitted_Cost"]:
                if col in df.columns:
                    df.loc[fcast, col] *= (1 - block_pct)

    # Delay hiring
    delay_cutoff_num = levers.get("delay_cutoff_num", 0)
    if delay_cutoff_num > 0:
        early = fcast & (df["Month_Num"] < delay_cutoff_num)
        for _, p in POSITIVE_DRIVERS:
            for col in [f"{p}_NonCommitted_HC", f"{p}_NonCommitted_Cost"]:
                if col in df.columns:
                    df.loc[early, col] = 0

    # Juniorisation — add cost adjustment column
    df["Scenario_Juniorisation_Adj"] = 0.0
    for conv in levers.get("juniorisations", []):
        from_grade    = conv.get("from_grade", "")
        to_grade      = conv.get("to_grade", "")
        n_roles       = int(conv.get("n_roles", 0))
        eff_month_num = int(conv.get("eff_month_num", 1))
        if not from_grade or not to_grade or n_roles <= 0:
            continue
        to_rate   = get_grade_avg_rate(df, to_grade)
        if to_rate <= 0:
            continue
        mask = (df["Grade"] == from_grade) & (df["Month_Num"] >= eff_month_num)
        rate_diff = (df.loc[mask, "Monthly_Rate_USD"] - to_rate).clip(lower=0)
        df.loc[mask, "Scenario_Juniorisation_Adj"] -= (
            rate_diff * n_roles.clip(upper=df.loc[mask, "Closing_HC"]) 
            if hasattr(n_roles, 'clip') else rate_diff * min(n_roles, 1)
        )
        # simpler: flat saving per row
        df.loc[mask, "Scenario_Juniorisation_Adj"] -= rate_diff * n_roles

    # Accelerate exits
    accel_hc        = int(levers.get("accel_exits_hc", 0))
    accel_month_num = int(levers.get("accel_exits_month_num", 0))
    if accel_hc > 0 and accel_month_num > 0:
        mask = fcast & (df["Month_Num"] >= accel_month_num)
        if "Transformation_Exits_Committed_HC" in df.columns:
            n_months = max(df.loc[mask, "Month_Num"].nunique(), 1)
            df.loc[mask, "Transformation_Exits_Committed_HC"] += accel_hc / n_months
            df.loc[mask, "Closing_HC"] = (df.loc[mask, "Closing_HC"] - accel_hc / n_months).clip(lower=0)

    # Derive scenario cost
    df["Derived_Scenario_Cost"] = df.apply(
        lambda r: r["Actual_Cost"] if str(r["Month_Type"]).lower() == "actual"
        else r["Closing_HC"] * r["Monthly_Rate_USD"], axis=1
    ) + df["Scenario_Juniorisation_Adj"]

    # Rate card
    rate_adj_pct = levers.get("rate_adj_pct", 0.0)
    if rate_adj_pct != 0:
        df.loc[fcast, "Derived_Scenario_Cost"] *= (1 + rate_adj_pct / 100.0)

    df["Scenario_Name"]  = levers.get("scenario_name", "Scenario")
    df["Scenario_Flag"]  = "Modified"
    df.loc[~fcast, "Scenario_Flag"] = "Actual (unchanged)"
    df.drop(columns=["Scenario_Juniorisation_Adj"], inplace=True, errors="ignore")
    return df


# =================================================
# TAB 2 — SCENARIO BUILDER
# =================================================
with tab2:
    st.markdown(
        """
        <div style="background:linear-gradient(95deg,#04145f 0%,#0a1d89 50%,#1239d0 100%);
                    border-radius:14px; padding:20px 24px; margin-bottom:16px;">
            <div style="color:white; font-size:22px; font-weight:600; margin-bottom:4px;">
                🔧 Scenario Builder
            </div>
            <div style="color:rgba(255,255,255,0.85); font-size:13px;">
                Adjust levers to model how targeted actions change the WFP cost and HC outlook.
                Scenarios are computed in-session — source data is never modified.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    lev_col, canvas_col, summary_col = st.columns([2.8, 4.4, 2.8], gap="large")

    # ── LEVER PANEL ──────────────────────────────
    with lev_col:
        st.markdown('<div class="section-title">⚙️ Levers</div>', unsafe_allow_html=True)

        nc_cost_cols_preview = [f"{p}_NonCommitted_Cost" for _, p in POSITIVE_DRIVERS]
        nc_hc_cols_preview   = [f"{p}_NonCommitted_HC"   for _, p in POSITIVE_DRIVERS]
        _fcast_df_prev = df_scope[df_scope["Month_Type"].str.lower()=="forecast"]
        total_nc_cost = sum_cols(_fcast_df_prev, nc_cost_cols_preview).sum()
        total_nc_hc   = sum_cols(_fcast_df_prev[_fcast_df_prev["Month"]=="Dec"], nc_hc_cols_preview).sum()
        available_grades = sorted(df_scope["Grade"].dropna().astype(str).unique().tolist())

        # ── Lever 1 ──────────────────────────────────
        st.markdown(
            '<div class="lever-tile">'
            '<div class="lever-tile-label">Lever 1 — Growth</div>'
            '<div class="lever-tile-title">Block Non-Committed Growth</div>'
            '</div>',
            unsafe_allow_html=True
        )
        block_pct = st.slider(
            "Block %", min_value=0, max_value=100, value=0, step=5,
            help="Removes this % of all non-committed growth hires from the forecast",
            label_visibility="collapsed"
        )
        if block_pct > 0:
            st.markdown(
                f'<div class="lever-preview">↳ Saves est. {fmt_money(total_nc_cost * block_pct/100, unit_mode)} | {fmt_num(total_nc_hc * block_pct/100)} HC removed</div>',
                unsafe_allow_html=True
            )

        # ── Lever 2 ──────────────────────────────────
        st.markdown(
            '<div class="lever-tile" style="margin-top:4px;">'
            '<div class="lever-tile-label">Lever 2 — Growth</div>'
            '<div class="lever-tile-title">Delay Non-Committed Hiring</div>'
            '</div>',
            unsafe_allow_html=True
        )
        # Forecast months only
        forecast_months_only = sorted(
            _fcast_df_prev["Month"].dropna().unique().tolist(),
            key=lambda m: MONTH_ORDER.get(m, 99)
        )
        l2col1, l2col2 = st.columns([1.4, 1])
        with l2col1:
            delay_grade = st.selectbox("Grade", ["All grades"] + available_grades, key="delay_grade")
        with l2col2:
            delay_n_roles = st.number_input("Max roles", min_value=0, value=0, step=5, key="delay_roles",
                                            help="0 = delay all non-committed hires for this grade")
        delay_month_name = st.selectbox(
            "Earliest start month (forecast months only)",
            options=["No delay"] + forecast_months_only,
            index=0,
            help="Non-committed growth hires before this month are zeroed out. Dec HC unchanged.",
            label_visibility="collapsed"
        )
        if delay_month_name != "No delay":
            delay_cutoff_num = MONTH_ORDER[delay_month_name]
            fcast_early = _fcast_df_prev[_fcast_df_prev["Month_Num"] < delay_cutoff_num]
            if delay_grade != "All grades":
                fcast_early = fcast_early[fcast_early["Grade"] == delay_grade]
            early_nc_cost = sum_cols(fcast_early, nc_cost_cols_preview).sum()
            early_nc_hc   = sum_cols(fcast_early, nc_hc_cols_preview).sum()
            if delay_n_roles > 0 and early_nc_hc > 0:
                cap_frac      = min(1.0, delay_n_roles / early_nc_hc)
                early_nc_cost = early_nc_cost * cap_frac
            residual     = 1.0 - block_pct / 100.0
            eff_save     = early_nc_cost * residual
            grade_lbl    = delay_grade if delay_grade != "All grades" else "all grades"
            roles_lbl    = f"{delay_n_roles} roles" if delay_n_roles > 0 else "all roles"
            if block_pct > 0:
                st.markdown(
                    f'<div class="lever-preview">↳ {roles_lbl}, {grade_lbl} — saves est. {fmt_money(eff_save, unit_mode)} '
                    f'(on {int(residual*100)}% residual after Lever 1)</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    "<div style='font-size:11px;color:#b45309;background:#fff8e1;border-radius:6px;"
                    "padding:4px 8px;margin-top:4px;display:inline-block;'>"
                    "⚠️ Levers 1 & 2 overlap — Lever 2 saving is net of Lever 1.</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="lever-preview">↳ {roles_lbl}, {grade_lbl} — saves est. {fmt_money(early_nc_cost, unit_mode)} before {delay_month_name}</div>',
                    unsafe_allow_html=True
                )
        else:
            delay_cutoff_num = 0
            delay_grade      = "All grades"
            delay_n_roles    = 0

        # ── Lever 3 ──────────────────────────────────
        st.markdown(
            '<div class="lever-tile" style="margin-top:4px;">'
            '<div class="lever-tile-label">Lever 3 — Grade Mix</div>'
            '<div class="lever-tile-title">Juniorisation of Roles</div>'
            '</div>',
            unsafe_allow_html=True
        )
        available_grades_unused = None  # already defined above
        n_conversions = st.number_input("Conversion lines", min_value=1, max_value=5, value=1, step=1)
        juniorisations = []
        for j in range(int(n_conversions)):
            st.markdown(
                f"<div style='font-size:11px;font-weight:700;color:#1369e2;margin-top:10px;margin-bottom:4px;'>Conversion {j+1}</div>",
                unsafe_allow_html=True
            )
            jcol1, jcol2, jcol3 = st.columns([1.2, 1.2, 1])
            with jcol1:
                from_g = st.selectbox("From grade", available_grades, key=f"from_g_{j}", index=0)
            with jcol2:
                to_g = st.selectbox("To grade", available_grades, key=f"to_g_{j}", index=min(1, len(available_grades)-1))
            with jcol3:
                n_r = st.number_input("Roles", min_value=0, value=0, step=1, key=f"n_r_{j}")
            eff_m = st.selectbox(f"Effective from", MONTHS, index=3, key=f"eff_m_{j}")
            eff_m_num = MONTH_ORDER[eff_m]
            if n_r > 0 and from_g != to_g:
                fr = get_grade_avg_rate(df_scope, from_g)
                tr = get_grade_avg_rate(df_scope, to_g)
                if fr > tr:
                    months_ahead = max(0, 12 - eff_m_num + 1)
                    preview_save = n_r * (fr - tr) * months_ahead
                    st.markdown(
                        f'<div class="lever-preview">↳ Est. {fmt_money(preview_save, unit_mode)} saved ({fmt_money(fr,"$")}/hd → {fmt_money(tr,"$")}/hd)</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.caption("⚠️ Target grade rate ≥ source — no saving")
            juniorisations.append({
                "from_grade": from_g, "to_grade": to_g,
                "n_roles": n_r, "eff_month_num": eff_m_num
            })

        # ── Lever 4 ──────────────────────────────────
        st.markdown(
            '<div class="lever-tile" style="margin-top:4px;">'
            '<div class="lever-tile-label">Lever 4 — Reduction</div>'
            '<div class="lever-tile-title">Accelerate Transformation Exits</div>'
            '</div>',
            unsafe_allow_html=True
        )
        accel_exits_hc = st.number_input(
            "Additional heads exiting",
            min_value=0, value=0, step=5,
            help="Heads exiting above current WFP plan",
            label_visibility="collapsed"
        )
        if accel_exits_hc > 0:
            l4col1, l4col2 = st.columns([1.4, 1])
            with l4col1:
                accel_grade = st.selectbox("Grade", ["All grades"] + available_grades, key="accel_grade")
            with l4col2:
                accel_month_name = st.selectbox("From month", forecast_months_only, index=0, key="accel_month")
            accel_month_num = MONTH_ORDER[accel_month_name]
            if accel_grade != "All grades":
                avg_r = _fcast_df_prev[_fcast_df_prev["Grade"] == accel_grade]["Monthly_Rate_USD"].mean()
                avg_r = avg_r if not pd.isna(avg_r) else _fcast_df_prev["Monthly_Rate_USD"].mean()
            else:
                avg_r = _fcast_df_prev["Monthly_Rate_USD"].mean()
            months_ahead = max(0, 12 - accel_month_num + 1)
            grade_lbl = accel_grade if accel_grade != "All grades" else "all grades"
            st.markdown(
                f'<div class="lever-preview">↳ {accel_exits_hc} {grade_lbl} exits from {accel_month_name} — saves est. {fmt_money(accel_exits_hc * avg_r * months_ahead, unit_mode)} | -{accel_exits_hc} HC</div>',
                unsafe_allow_html=True
            )
        else:
            accel_month_num = 0
            accel_grade     = "All grades"

        # ── Lever 5 ──────────────────────────────────
        st.markdown(
            '<div class="lever-tile" style="margin-top:4px;">'
            '<div class="lever-tile-label">Lever 5 — Rate Card</div>'
            '<div class="lever-tile-title">Blanket Rate Adjustment</div>'
            '</div>',
            unsafe_allow_html=True
        )
        rate_adj_pct = st.slider(
            "Rate adjustment %", min_value=-15.0, max_value=15.0, value=0.0, step=0.5,
            help="Applies a % uplift or reduction to forecast cost rates across all heads",
            label_visibility="collapsed"
        )
        if rate_adj_pct != 0:
            fcast_base_cost = _fcast_df_prev["Derived_WFP_Monthly_Cost"].sum()
            st.markdown(
                f'<div class="lever-preview">↳ Cost delta: {fmt_money(fcast_base_cost * rate_adj_pct/100, unit_mode)}</div>',
                unsafe_allow_html=True
            )

    # ── BUILD LEVERS DICT AND COMPUTE ────────────
    levers = {
        "block_pct":             block_pct,
        "delay_cutoff_num":      delay_cutoff_num,
        "delay_cutoff_name":     delay_month_name if delay_month_name != "No delay" else "",
        "delay_grade":           delay_grade,
        "delay_n_roles":         delay_n_roles,
        "juniorisations":        juniorisations,
        "accel_exits_hc":        accel_exits_hc,
        "accel_exits_month_num": accel_month_num,
        "accel_grade":           accel_grade,
        "rate_adj_pct":          rate_adj_pct,
        "scenario_name":         "",
    }
    result = compute_scenario_impacts(df_scope, levers)

    # ── SCENARIO CANVAS ───────────────────────────
    with canvas_col:
        st.markdown('<div class="section-title">📊 Scenario vs WFP Outlook</div>', unsafe_allow_html=True)

        # Before / After KPI comparison — 4 tiles
        comp_cols = st.columns(4)

        budget_hc = cp26_budget_hc  # already computed in outer scope

        metrics = [
            {
                "label":    "Full-Year Cost",
                "wfp":      result["baseline_cost"],
                "scen":     result["scenario_cost"],
                "budget":   result["baseline_budget_cost"],
                "is_hc":    False,
                "show_bud": True,
            },
            {
                "label":    "Dec Headcount",
                "wfp":      result["baseline_hc"],
                "scen":     result["scenario_hc"],
                "budget":   budget_hc,
                "is_hc":    True,
                "show_bud": True,
            },
            {
                "label":    "vs Budget — Cost",
                "wfp":      result["baseline_cost"] - result["baseline_budget_cost"],
                "scen":     result["scenario_cost"]  - result["baseline_budget_cost"],
                "budget":   0,
                "is_hc":    False,
                "show_bud": False,
            },
            {
                "label":    "vs Budget — HC",
                "wfp":      result["baseline_hc"] - budget_hc,
                "scen":     result["scenario_hc"]  - budget_hc,
                "budget":   0,
                "is_hc":    True,
                "show_bud": False,
            },
        ]

        for col, m in zip(comp_cols, metrics):
            wfp_fmt  = fmt_num(m["wfp"])  if m["is_hc"] else fmt_money(m["wfp"],  unit_mode)
            scen_fmt = fmt_num(m["scen"]) if m["is_hc"] else fmt_money(m["scen"], unit_mode)
            delta     = m["scen"] - m["wfp"]
            delta_fmt = fmt_num(abs(delta)) if m["is_hc"] else fmt_money(abs(delta), unit_mode)
            delta_pct = (delta / m["wfp"] * 100) if m["wfp"] else 0
            arrow  = "▼" if delta < 0 else ("▲" if delta > 0 else "—")
            colour = "#15803d" if delta < 0 else ("#b91c1c" if delta > 0 else "#5f6878")
            # For vs-budget tiles, green = below 0, red = above 0 for the scenario value
            if not m["show_bud"]:
                scen_raw = m["scen"]
                colour_scen = "#15803d" if scen_raw < 0 else ("#b91c1c" if scen_raw > 0 else "#5f6878")
            else:
                colour_scen = "#0e214f"
            col.markdown(
                f"""
                <div class="kpi-card" style="min-height:unset; padding:12px 14px;">
                    <div class="kpi-title" style="margin-bottom:8px;">{m['label']}</div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:4px; margin-bottom:6px;">
                        <div>
                            <div style="font-size:10px; color:#9ca3af; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:1px;">WFP Outlook</div>
                            <div style="font-size:14px; font-weight:600; color:#7d7d7d;">{wfp_fmt}</div>
                        </div>
                        <div style="font-size:16px; color:#d1d5db; font-weight:300; align-self:center;">→</div>
                        <div>
                            <div style="font-size:10px; color:#1369e2; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:1px;">Scenario</div>
                            <div style="font-size:16px; font-weight:700; color:{colour_scen};">{scen_fmt}</div>
                        </div>
                    </div>
                    <div style="font-size:11px; font-weight:700; color:{colour}; background:{'rgba(34,197,94,0.08)' if delta < 0 else ('rgba(239,68,68,0.08)' if delta > 0 else '#f3f4f6')}; border-radius:6px; padding:3px 7px; display:inline-block;">
                        {arrow} {delta_fmt} ({delta_pct:+.1f}%)
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Lever impact table
        if result["lever_rows"]:
            lever_df = pd.DataFrame(result["lever_rows"])
            lever_df["Delta Cost"] = lever_df["Delta Cost"].apply(lambda x: fmt_money(x, unit_mode))
            lever_df["Delta HC"]   = lever_df["Delta HC"].apply(lambda x: f"{x:+,}" if x != 0 else "—")
            lever_df.columns = ["Lever", "Cost Impact", "HC Impact"]
            styled_levers = (
                lever_df.style
                .set_table_styles([
                    {"selector": "thead th", "props": [
                        ("background-color","#04145f"),("color","white"),
                        ("font-size","11px"),("padding","6px 10px"),("text-align","left")
                    ]},
                    {"selector": "tbody td", "props": [
                        ("font-size","12px"),("padding","6px 10px"),
                        ("color","#1f2937"),("border-bottom","1px solid #f0f0f0")
                    ]},
                ])
                .hide(axis="index")
            )
            st.write(styled_levers.to_html(), unsafe_allow_html=True)
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        else:
            st.info("No levers activated yet — adjust the controls on the left to model a scenario.")

        # Scenario waterfall
        if result["lever_rows"]:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(scenario_bridge_figure(result, unit_mode), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── IMPACT SUMMARY + EXPORT ───────────────────
    with summary_col:
        st.markdown('<div class="section-title">📋 Summary</div>', unsafe_allow_html=True)

        # Scenario name
        scenario_name = st.text_input("Scenario name", value="Base scenario", placeholder="e.g. Conservative cut")
        levers["scenario_name"] = scenario_name

        # Verdict
        scen_gap      = result["scenario_cost"] - result["baseline_budget_cost"]
        scen_gap_pct  = (scen_gap / result["baseline_budget_cost"] * 100) if result["baseline_budget_cost"] else 0
        base_gap_pct  = ((result["baseline_cost"] - result["baseline_budget_cost"]) / result["baseline_budget_cost"] * 100) if result["baseline_budget_cost"] else 0

        if scen_gap_pct <= 0:
            verdict_bg, verdict_colour, verdict_text = "#f0fdf4", "#15803d", "✅ Lands within budget"
        elif scen_gap_pct < 3:
            verdict_bg, verdict_colour, verdict_text = "#fffbeb", "#b45309", "⚠️ Mild overrun remains"
        else:
            verdict_bg, verdict_colour, verdict_text = "#fef2f2", "#b91c1c", "❌ Material overrun remains"

        st.markdown(
            f"""
            <div style="background:{verdict_bg}; border-radius:10px; padding:12px 14px; margin-bottom:10px;">
                <div style="font-size:13px; font-weight:700; color:{verdict_colour};">{verdict_text}</div>
                <div style="font-size:12px; color:{verdict_colour}; margin-top:4px;">
                    Scenario vs budget: {fmt_money(abs(scen_gap), unit_mode)}
                    {'above' if scen_gap > 0 else 'below'} ({scen_gap_pct:+.1f}%)<br>
                    Improvement vs WFP: {fmt_money(abs(result['total_cost_delta']), unit_mode)}
                    ({base_gap_pct - scen_gap_pct:+.1f}pp)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Active levers summary
        active = [lr["Lever"] for lr in result["lever_rows"]]
        if active:
            st.markdown(
                "<div style='font-size:12px;font-weight:700;color:#5f6878;margin-bottom:6px;'>ACTIVE LEVERS</div>",
                unsafe_allow_html=True
            )
            for lv in active:
                st.markdown(f"<div style='font-size:12px;color:#1f2937;margin-bottom:3px;'>✓ {lv}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='font-size:12px;color:#9ca3af;'>No levers active</div>",
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Export buttons
        st.markdown(
            "<div style='font-size:12px;font-weight:700;color:#5f6878;margin-bottom:8px;'>EXPORT</div>",
            unsafe_allow_html=True
        )

        # Scenario summary CSV
        if result["lever_rows"]:
            summary_rows = []
            summary_rows.append({"Item": "WFP Outlook Cost",      "Value": fmt_money(result["baseline_cost"], unit_mode)})
            summary_rows.append({"Item": "WFP Outlook Dec HC",    "Value": fmt_num(result["baseline_hc"])})
            summary_rows.append({"Item": "CP26 Budget Cost",      "Value": fmt_money(result["baseline_budget_cost"], unit_mode)})
            for lr in result["lever_rows"]:
                summary_rows.append({"Item": lr["Lever"], "Value": fmt_money(lr["Delta Cost"], unit_mode)})
            summary_rows.append({"Item": "─────────────────", "Value": "──────"})
            summary_rows.append({"Item": "Scenario Cost",         "Value": fmt_money(result["scenario_cost"], unit_mode)})
            summary_rows.append({"Item": "Scenario Dec HC",       "Value": fmt_num(result["scenario_hc"])})
            summary_rows.append({"Item": "Scenario vs Budget",    "Value": fmt_money(scen_gap, unit_mode)})
            summary_rows.append({"Item": "Scenario Name",         "Value": scenario_name})
            sum_csv = pd.DataFrame(summary_rows).to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download scenario summary (CSV)",
                data=sum_csv,
                file_name=f"WFP_scenario_summary_{scenario_name.replace(' ','_')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Full adjusted WFP dataset
        export_df = build_scenario_export_df(df_scope, levers, result)
        full_csv  = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download adjusted WFP dataset (CSV)",
            data=full_csv,
            file_name=f"WFP_scenario_{scenario_name.replace(' ','_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# =================================================
# TAB 3 — USER MANUAL
# =================================================
with tab3:
    st.markdown(
        """
        <div style="background:linear-gradient(95deg,#04145f 0%,#0a1d89 50%,#1239d0 100%);
                    border-radius:14px; padding:20px 24px; margin-bottom:20px;">
            <div style="color:white; font-size:22px; font-weight:600; margin-bottom:4px;">
                📖 User Manual
            </div>
            <div style="color:rgba(255,255,255,0.85); font-size:13px;">
                Enterprise Workforce Cost Navigator — guidance for CFOs and finance teams
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    man_col1, man_col2 = st.columns([1, 1], gap="large")

    with man_col1:

        st.markdown(
            """
            <div style="background:white;border:1px solid #e0e3ea;border-radius:14px;padding:20px 22px;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:700;color:#04145f;margin-bottom:12px;">🎯 What Is This Tool?</div>
            <div style="font-size:13px;color:#334155;line-height:1.7;">
            The <strong>Enterprise Workforce Cost Navigator</strong> is a real-time workforce planning interrogation
            and scenario modelling tool built on Standard Chartered's WFP (Workforce Planning) data.
            <br><br>
            It gives CFOs, Finance Business Partners and Cost GPO teams a single view to:
            <ul style="margin-top:8px;padding-left:18px;">
                <li>Interrogate the current full-year cost and headcount outlook vs budget</li>
                <li>Understand which drivers are moving headcount and cost</li>
                <li>Identify where overrun risk is concentrated by country and grade</li>
                <li>Model scenario actions and instantly see their cost and HC impact</li>
                <li>Export adjusted datasets for offline review or re-upload to the WFP tool</li>
            </ul>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="background:white;border:1px solid #e0e3ea;border-radius:14px;padding:20px 22px;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:700;color:#04145f;margin-bottom:12px;">📊 Tab 1 — WFP Outlook</div>
            <div style="font-size:13px;color:#334155;line-height:1.7;">
            <strong>How to use it:</strong>
            <ol style="margin-top:8px;padding-left:18px;">
                <li><strong>Set your scope</strong> using the sidebar filters — Management Team, Country and Grade.
                Note that selecting a Grade will suppress cost views (see Data Notes below).</li>
                <li><strong>Read the KPI tiles</strong> — the top row shows cost, the second row shows headcount.
                Each tile shows the full-year position and a vs-budget chip (green = favourable, red = overrun).</li>
                <li><strong>Review the cost and HC bridges</strong> — waterfall charts show how each workforce driver
                (Growth Hires, Attrition, Transformation Exits etc.) moves the Mar actual position to the Dec forecast.</li>
                <li><strong>Use the country concentration chart</strong> to identify which markets carry the most overrun risk.</li>
                <li><strong>Review the driver decomposition table</strong> — shows Committed vs Non-Committed splits for
                every driver. The <em>Non-Committed Cost</em> in the Growth Subtotal row ties to the
                <strong>Challengeable Growth</strong> KPI tile.</li>
                <li><strong>Export</strong> filtered datasets or the driver table using the buttons at the bottom.</li>
            </ol>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="background:white;border:1px solid #e0e3ea;border-radius:14px;padding:20px 22px;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:700;color:#04145f;margin-bottom:12px;">🔧 Tab 2 — Scenario Builder</div>
            <div style="font-size:13px;color:#334155;line-height:1.7;">
            <strong>How to use it:</strong>
            <ol style="margin-top:8px;padding-left:18px;">
                <li><strong>Set your scope</strong> first using the sidebar (same MT / Country / Grade filters apply).</li>
                <li><strong>Activate levers</strong> on the left panel — adjust one or more of the five levers.
                Each lever shows a green preview of the estimated saving as soon as you move it.</li>
                <li><strong>Read the scenario canvas</strong> (centre) — four KPI tiles show WFP Outlook vs Scenario
                side by side for Full-Year Cost, Dec HC, vs Budget Cost and vs Budget HC.</li>
                <li><strong>Review the scenario bridge waterfall</strong> — shows how each lever contributes to moving
                from WFP Outlook to the Scenario Outlook. The dashed amber line marks the CP26 budget.</li>
                <li><strong>Check the verdict</strong> (right panel) — green = lands within budget,
                amber = mild overrun remains, red = material overrun remains.</li>
                <li><strong>Name your scenario</strong> and export using the two download buttons —
                one for the scenario summary, one for the full adjusted WFP dataset.</li>
            </ol>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with man_col2:

        st.markdown(
            """
            <div style="background:white;border:1px solid #e0e3ea;border-radius:14px;padding:20px 22px;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:700;color:#04145f;margin-bottom:14px;">⚙️ Lever Definitions</div>
            <div style="font-size:13px;color:#334155;line-height:1.75;">

            <div style="margin-bottom:10px;">
                <span style="background:#e8edf5;color:#04145f;font-weight:700;font-size:11px;padding:2px 8px;border-radius:6px;">Lever 1</span>
                <strong style="margin-left:6px;">Block Non-Committed Growth</strong><br>
                Removes a selected % of all non-committed growth hires from the forecast.
                Non-committed means the role has been planned but not yet approved or contracted.
                This lever reduces both cost and Dec HC.
            </div>

            <div style="margin-bottom:10px;">
                <span style="background:#e8edf5;color:#04145f;font-weight:700;font-size:11px;padding:2px 8px;border-radius:6px;">Lever 2</span>
                <strong style="margin-left:6px;">Delay Non-Committed Hiring</strong><br>
                Zeroes out non-committed growth hires planned before the selected start month.
                The saving is the cost of those roles in the months before the cutoff.
                Dec HC is unchanged — the hires are delayed, not cancelled.
            </div>

            <div style="margin-bottom:10px;">
                <span style="background:#e8edf5;color:#04145f;font-weight:700;font-size:11px;padding:2px 8px;border-radius:6px;">Lever 3</span>
                <strong style="margin-left:6px;">Juniorisation of Roles</strong><br>
                Converts a selected number of roles from a senior grade to a junior grade from a chosen effective month.
                Applies to all roles — existing headcount, committed and non-committed movements.
                The saving is the rate card differential multiplied by number of roles and months remaining.
                Up to 5 conversion lines can be stacked simultaneously.
            </div>

            <div style="margin-bottom:10px;">
                <span style="background:#e8edf5;color:#04145f;font-weight:700;font-size:11px;padding:2px 8px;border-radius:6px;">Lever 4</span>
                <strong style="margin-left:6px;">Accelerate Transformation Exits</strong><br>
                Models additional headcount exits above the current WFP plan, effective from a chosen month.
                Saves the cost of those heads for the remaining months of the year and reduces Dec HC.
            </div>

            <div style="margin-bottom:10px;">
                <span style="background:#e8edf5;color:#04145f;font-weight:700;font-size:11px;padding:2px 8px;border-radius:6px;">Lever 5</span>
                <strong style="margin-left:6px;">Blanket Rate Adjustment</strong><br>
                Applies a % increase or reduction to all forecast cost rates. Useful for modelling
                FX impact, merit cycle uplifts or negotiated rate reductions. Does not affect HC.
            </div>

            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="background:white;border:1px solid #e0e3ea;border-radius:14px;padding:20px 22px;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:700;color:#04145f;margin-bottom:12px;">📋 Glossary</div>
            <div style="font-size:13px;color:#334155;line-height:1.8;">
            <table style="width:100%;border-collapse:collapse;">
                <tr><td style="font-weight:700;padding:4px 0;color:#04145f;width:42%;">WFP Outlook</td><td>Full-year cost and HC forecast as currently entered in the Workforce Planning tool</td></tr>
                <tr style="background:#f9fafb;"><td style="font-weight:700;padding:4px 6px;color:#04145f;">CP26 Budget</td><td style="padding:4px 0;">The approved 2026 cost and HC budget</td></tr>
                <tr><td style="font-weight:700;padding:4px 0;color:#04145f;">Committed</td><td>HC movements and costs that are contractually or operationally locked in and cannot be easily reversed</td></tr>
                <tr style="background:#f9fafb;"><td style="font-weight:700;padding:4px 6px;color:#04145f;">Non-Committed</td><td style="padding:4px 0;">Planned but not yet approved or contracted — these are the "challengeable" movements</td></tr>
                <tr><td style="font-weight:700;padding:4px 0;color:#04145f;">Challengeable Growth</td><td>The total non-committed cost growth in the forecast — the maximum addressable saving if all non-committed hires were blocked</td></tr>
                <tr style="background:#f9fafb;"><td style="font-weight:700;padding:4px 6px;color:#04145f;">CRR + Line of Sight</td><td style="padding:4px 0;">The "do nothing" scenario — if all non-committed growth was blocked but all committed reductions still landed</td></tr>
                <tr><td style="font-weight:700;padding:4px 0;color:#04145f;">Closing HC</td><td>End-of-month headcount stock position</td></tr>
                <tr style="background:#f9fafb;"><td style="font-weight:700;padding:4px 6px;color:#04145f;">Monthly Rate (USD)</td><td style="padding:4px 0;">The average monthly cost per head for that grade and location, used to derive forecast cost</td></tr>
                <tr><td style="font-weight:700;padding:4px 0;color:#04145f;">Actual Cost</td><td>GL-extracted actual spend for closed months (Jan–Mar). Not split by grade.</td></tr>
            </table>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="background:#fff8e1;border:1px solid #f59e0b;border-radius:14px;padding:18px 20px;">
            <div style="font-size:14px;font-weight:700;color:#b45309;margin-bottom:10px;">⚠️ Important Data Notes</div>
            <div style="font-size:12px;color:#78350f;line-height:1.7;">
            <strong>Why cost is suppressed when a Grade filter is active:</strong><br>
            Actuals (Jan–Mar) are extracted from the GL at cost centre level with no grade split.
            Forecast months use Closing HC × Monthly Rate (grade-aware). Blending these two would produce
            a hybrid figure that is not a valid grade-level cost. When Grade is filtered, only HC views are shown.
            <br><br>
            <strong>Scenario figures are estimates:</strong><br>
            Scenario costs are computed using average rate cards and simplified cashflow logic.
            They are indicative directional estimates, not precise reforecast figures. For a formal
            reforecast, the adjusted WFP export should be reviewed and validated before upload.
            <br><br>
            <strong>Data refresh:</strong><br>
            The tool reads from <code>WFP_Data.csv</code> in the same folder as the app.
            Replace this file with the latest WFP extract and restart the app to refresh all views.
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )
