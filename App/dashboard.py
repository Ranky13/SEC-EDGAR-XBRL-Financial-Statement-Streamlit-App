import streamlit as st
import pandas as pd
import altair as alt

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


def company_colors_for(columns):
    return [COMPANY_COLORS.get(c, DEFAULT_PALETTE[i % len(DEFAULT_PALETTE)]) for i, c in enumerate(columns)]


METRIC_LABELS = {
    "net_margin": "Net Margin (%)",
    "roe": "ROE (%)",
    "roa": "ROA (%)",
    "current_ratio": "Current Ratio (x)",
    "debt_to_equity": "Debt-to-Equity (x)",
}

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
df = pd.read_excel("data/processed/ratios.xlsx")

# ---- Sidebar filters ----
st.sidebar.header("Filters")

companies = df["company"].unique().tolist()

MD_COLOR_KEYWORDS = {
    "Block, Inc.": "blue",
    "PayPal Holdings, Inc.": "orange",
    "VISA INC.": "green",
}

if "last_valid_selection" not in st.session_state:
    st.session_state.last_valid_selection = companies

selected_companies = []
for company in companies:
    color_keyword = MD_COLOR_KEYWORDS.get(company, "gray")
    is_checked = st.sidebar.checkbox(
        f":{color_keyword}[**{company}**]",
        value=company in st.session_state.last_valid_selection,
        key=f"checkbox_{company}",
    )
    if is_checked:
        selected_companies.append(company)

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
            help="Net income as a percentage of revenue.",
        )

st.divider()

# ---- Data table ----
with st.expander("View raw data table"):
    st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ---- Bar charts: comparison view ----
single_company_mode = len(selected_companies) == 1


def sorted_bar(data, metric_name, value_format=".1%"):
    chart_df = data.reset_index()[["company", metric_name]]
    color_scale = alt.Scale(
        domain=list(chart_df["company"]),
        range=company_colors_for(chart_df["company"]),
    )
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X(f"{metric_name}:Q", title=None, axis=alt.Axis(format=value_format)),
            y=alt.Y("company:N", sort="-x", title=None),
            color=alt.Color("company:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("company:N", title="Company"),
                alt.Tooltip(f"{metric_name}:Q", format=value_format, title=METRIC_LABELS.get(metric_name, metric_name)),
            ],
        )
        .properties(height=120)
    )
    st.altair_chart(chart, use_container_width=True)


def vertical_bar(data, metric_name, value_format=".1%"):
    chart_df = data.reset_index()[["company", metric_name]]
    color_scale = alt.Scale(
        domain=list(chart_df["company"]),
        range=company_colors_for(chart_df["company"]),
    )
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("company:N", title=None),
            y=alt.Y(f"{metric_name}:Q", title=None, axis=alt.Axis(format=value_format)),
            color=alt.Color("company:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("company:N", title="Company"),
                alt.Tooltip(f"{metric_name}:Q", format=value_format, title=METRIC_LABELS.get(metric_name, metric_name)),
            ],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


if single_company_mode:
    only_company = selected_companies[0]
    st.header(f"{only_company} — Year by Year")
    st.caption("Only one company is selected, so bars show its own trend across fiscal years instead of a comparison.")
    bar_source = filtered_df[filtered_df["company"] == only_company].set_index("fiscal_year_label")
    single_color = [COMPANY_COLORS.get(only_company, DEFAULT_PALETTE[0])]

    def draw_horizontal(metric_name, value_format=".1%"):
        st.bar_chart(bar_source[metric_name], color=single_color)

    def draw_vertical(metric_name, value_format=".1%"):
        st.bar_chart(bar_source[metric_name], color=single_color)

else:
    st.header(f"Company Comparison — Fiscal Year {latest_year}")
    st.caption("Net Margin and Current Ratio are ranked highest to lowest. ROE and Debt-to-Equity are shown as standard bars.")
    bar_source = latest_df.set_index("company")

    def draw_horizontal(metric_name, value_format=".1%"):
        sorted_bar(bar_source, metric_name, value_format)

    def draw_vertical(metric_name, value_format=".1%"):
        vertical_bar(bar_source, metric_name, value_format)


bar_col1, bar_col2 = st.columns(2)

with bar_col1:
    st.subheader("Net Margin")
    draw_horizontal("net_margin")

with bar_col2:
    st.subheader("Return on Equity (ROE)")
    draw_vertical("roe")

bar_col3, bar_col4 = st.columns(2)

with bar_col3:
    st.subheader("Current Ratio")
    draw_horizontal("current_ratio", value_format=".2f")

with bar_col4:
    st.subheader("Debt-to-Equity")
    draw_vertical("debt_to_equity", value_format=".2f")

st.divider()

# ---- Line charts: trends over time ----
st.header("Trends Over Time")


def line_with_reference(data, metric_name, ref_value, ref_label, value_format=".1%"):
    long_df = data.reset_index().melt(id_vars="fiscal_year_label", var_name="company", value_name=metric_name)
    color_scale = alt.Scale(domain=list(data.columns), range=company_colors_for(data.columns))

    lines = (
        alt.Chart(long_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("fiscal_year_label:N", title=None),
            y=alt.Y(f"{metric_name}:Q", axis=alt.Axis(format=value_format), title=None),
            color=alt.Color("company:N", scale=color_scale, legend=alt.Legend(title=None)),
            tooltip=[
                alt.Tooltip("company:N", title="Company"),
                alt.Tooltip("fiscal_year_label:N", title="Fiscal Year"),
                alt.Tooltip(f"{metric_name}:Q", format=value_format, title=METRIC_LABELS.get(metric_name, metric_name)),
            ],
        )
    )
    reference = (
        alt.Chart(pd.DataFrame({"y": [ref_value]}))
        .mark_rule(strokeDash=[4, 4], color="gray")
        .encode(y="y:Q")
    )
    st.altair_chart((lines + reference).properties(height=320), use_container_width=True)
    st.caption(f"Dashed line = {ref_label}")


st.subheader("Net Margin")
st.caption("Zero marks the line between profit and loss.")
chart_data = filtered_df.pivot(index="fiscal_year_label", columns="company", values="net_margin")
line_with_reference(chart_data, "net_margin", 0, "break-even (0% margin)")

st.subheader("Return on Equity (ROE)")
st.caption("Zero marks the line between generating and destroying shareholder value.")
chart_data_roe = filtered_df.pivot(index="fiscal_year_label", columns="company", values="roe")
line_with_reference(chart_data_roe, "roe", 0, "break-even (0% ROE)")

st.subheader("Return on Assets (ROA)")
chart_data_roa = filtered_df.pivot(index="fiscal_year_label", columns="company", values="roa")
long_roa = chart_data_roa.reset_index().melt(id_vars="fiscal_year_label", var_name="company", value_name="roa")
roa_chart = (
    alt.Chart(long_roa)
    .mark_line(point=True)
    .encode(
        x=alt.X("fiscal_year_label:N", title=None),
        y=alt.Y("roa:Q", axis=alt.Axis(format=".1%"), title=None),
        color=alt.Color(
            "company:N",
            scale=alt.Scale(domain=list(chart_data_roa.columns), range=company_colors_for(chart_data_roa.columns)),
            legend=alt.Legend(title=None),
        ),
        tooltip=[
            alt.Tooltip("company:N", title="Company"),
            alt.Tooltip("fiscal_year_label:N", title="Fiscal Year"),
            alt.Tooltip("roa:Q", format=".1%", title=METRIC_LABELS["roa"]),
        ],
    )
    .properties(height=320)
)
st.altair_chart(roa_chart, use_container_width=True)

st.subheader("Current Ratio")
st.caption("Below 1.0 means a company's short-term debts exceed its short-term assets.")
chart_data_cr = filtered_df.pivot(index="fiscal_year_label", columns="company", values="current_ratio")
line_with_reference(chart_data_cr, "current_ratio", 1.0, "current ratio = 1.0 (liquidity floor)", value_format=".2f")

st.subheader("Debt-to-Equity")
st.caption("Shown as an area chart to emphasize the scale of leverage building up over time.")
chart_data_dte = filtered_df.pivot(index="fiscal_year_label", columns="company", values="debt_to_equity")
long_dte = chart_data_dte.reset_index().melt(id_vars="fiscal_year_label", var_name="company", value_name="debt_to_equity")
area = (
    alt.Chart(long_dte)
    .mark_area(opacity=0.55, line=True)
    .encode(
        x=alt.X("fiscal_year_label:N", title=None),
        y=alt.Y("debt_to_equity:Q", axis=alt.Axis(format=".2f"), title=None, stack=None),
        color=alt.Color(
            "company:N",
            scale=alt.Scale(domain=list(chart_data_dte.columns), range=company_colors_for(chart_data_dte.columns)),
            legend=alt.Legend(title=None),
        ),
        tooltip=[
            alt.Tooltip("company:N", title="Company"),
            alt.Tooltip("fiscal_year_label:N", title="Fiscal Year"),
            alt.Tooltip("debt_to_equity:Q", format=".2f", title=METRIC_LABELS["debt_to_equity"]),
        ],
    )
    .properties(height=320)
)
st.altair_chart(area, use_container_width=True)

# ---- Footer ----
st.divider()
st.caption("Data source: SEC EDGAR XBRL Financial Statement Data | Built with Streamlit")