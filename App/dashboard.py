import streamlit as st
import pandas as pd

# ---- Page setup ----
st.set_page_config(
    page_title="Fintech Financial Health Dashboard",
    page_icon="📊",
    layout="wide",
)

# ---- Dark / light mode toggle ----
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

toggle_col1, toggle_col2 = st.columns([6, 1])
with toggle_col2:
    if st.button("🌙 Dark mode" if not st.session_state.dark_mode else "☀️ Light mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ---- Neutral, professional color scheme ----
if st.session_state.dark_mode:
    bg_color = "#0f1117"
    text_color = "#e6e6e6"
    card_bg = "#1a1d27"
    border_color = "#2e323f"
else:
    bg_color = "#ffffff"
    text_color = "#1a1a1a"
    card_bg = "#f7f8fa"
    border_color = "#e0e2e6"

COMPANY_COLORS = {
    "Block, Inc.": "#4C72B0",
    "PayPal Holdings, Inc.": "#DD8452",
    "VISA INC.": "#55A868",
}
DEFAULT_PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#8172B2", "#937860"]

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {card_bg};
    }}
    h1, h2, h3, h4, .stMarkdown, .stCaption, p, span, label {{
        color: {text_color} !important;
    }}
    div[data-testid="stMetric"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 12px;
    }}
    hr {{
        border-color: {border_color};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Fintech Financial Health Dashboard")
st.caption("Comparing Block, PayPal, and Visa across key financial ratios — sourced from SEC EDGAR filings")

# ---- Load data ----
df = pd.read_excel("../data/processed/ratios.xlsx")

# ---- Sidebar filters ----
st.sidebar.header("Filters")

companies = df["company"].unique().tolist()

if "last_valid_selection" not in st.session_state:
    st.session_state.last_valid_selection = companies

selected_companies = st.sidebar.multiselect(
    "Select companies", companies, default=st.session_state.last_valid_selection
)

if not selected_companies:
    st.sidebar.warning("At least one company must be selected. Showing your last selection.")
    selected_companies = st.session_state.last_valid_selection
else:
    st.session_state.last_valid_selection = selected_companies

years = sorted(df["fiscal_year"].unique().tolist())
year_range = st.sidebar.slider(
    "Fiscal year range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years))),
)

# ---- Filter data ----
filtered_df = df[
    (df["company"].isin(selected_companies))
    & (df["fiscal_year"] >= year_range[0])
    & (df["fiscal_year"] <= year_range[1])
].sort_values("fiscal_year")

# Keep a text version of the year for anything that goes into a chart's axis —
# otherwise Streamlit treats 2019 as a plain number and adds a thousands
# separator (showing "2,019" instead of "2019").
filtered_df["fiscal_year_label"] = filtered_df["fiscal_year"].astype(int).astype(str)

latest_year = filtered_df["fiscal_year"].max()
earliest_year = filtered_df["fiscal_year"].min()
latest_df = filtered_df[filtered_df["fiscal_year"] == latest_year]

# ---- Headline insight callouts ----
st.subheader(f"Snapshot — Fiscal Year {latest_year}")

metric_cols = st.columns(len(selected_companies) if selected_companies else 1)
for col, (_, row) in zip(metric_cols, latest_df.iterrows()):
    with col:
        first_year_row = filtered_df[
            (filtered_df["company"] == row["company"]) & (filtered_df["fiscal_year"] == earliest_year)
        ]
        if not first_year_row.empty:
            delta = row["net_margin"] - first_year_row["net_margin"].values[0]
            delta_str = f"{delta:+.1%} since {earliest_year}"
        else:
            delta_str = None

        st.metric(
            label=f"{row['company']} — Net Margin",
            value=f"{row['net_margin']:.1%}",
            delta=delta_str,
        )

st.divider()

# ---- Data table ----
with st.expander("View raw data table"):
    st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ---- Bar charts: comparison view ----
single_company_mode = len(selected_companies) == 1

if single_company_mode:
    only_company = selected_companies[0]
    st.header(f"{only_company} — Year by Year")
    st.caption("Only one company is selected, so bars show its own trend across fiscal years instead of a comparison.")
    bar_source = filtered_df[filtered_df["company"] == only_company].set_index("fiscal_year_label")
else:
    st.header(f"Company Comparison — Fiscal Year {latest_year}")
    st.caption("Bar charts are best for comparing companies side by side at a single point in time.")
    bar_source = latest_df.set_index("company")

bar_col1, bar_col2 = st.columns(2)

with bar_col1:
    st.subheader("Net Margin")
    st.bar_chart(bar_source["net_margin"])

with bar_col2:
    st.subheader("Return on Equity (ROE)")
    st.bar_chart(bar_source["roe"])

bar_col3, bar_col4 = st.columns(2)

with bar_col3:
    st.subheader("Current Ratio")
    st.bar_chart(bar_source["current_ratio"])

with bar_col4:
    st.subheader("Debt-to-Equity")
    st.bar_chart(bar_source["debt_to_equity"])

st.divider()

# ---- Line charts: trends over time ----
st.header("Trends Over Time")
st.caption("Line charts are best for seeing how each company has changed year over year.")


def company_colors_for(columns):
    return [COMPANY_COLORS.get(c, DEFAULT_PALETTE[i % len(DEFAULT_PALETTE)]) for i, c in enumerate(columns)]


st.subheader("Net Margin")
chart_data = filtered_df.pivot(index="fiscal_year_label", columns="company", values="net_margin")
st.line_chart(chart_data, color=company_colors_for(chart_data.columns))

st.subheader("Return on Equity (ROE)")
chart_data_roe = filtered_df.pivot(index="fiscal_year_label", columns="company", values="roe")
st.line_chart(chart_data_roe, color=company_colors_for(chart_data_roe.columns))

st.subheader("Return on Assets (ROA)")
chart_data_roa = filtered_df.pivot(index="fiscal_year_label", columns="company", values="roa")
st.line_chart(chart_data_roa, color=company_colors_for(chart_data_roa.columns))

st.subheader("Current Ratio")
chart_data_cr = filtered_df.pivot(index="fiscal_year_label", columns="company", values="current_ratio")
st.line_chart(chart_data_cr, color=company_colors_for(chart_data_cr.columns))

st.subheader("Debt-to-Equity")
chart_data_dte = filtered_df.pivot(index="fiscal_year_label", columns="company", values="debt_to_equity")
st.line_chart(chart_data_dte, color=company_colors_for(chart_data_dte.columns))


st.divider()
st.caption("Data source: SEC EDGAR XBRL Financial Statement Data | Built with Streamlit")