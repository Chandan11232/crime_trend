"""
app.py  ─  LA Crime Rate Trend Analysis Dashboard
==================================================
Entry point for the Streamlit application.

Run with:
    streamlit run app.py

Project layout:
    crime_dashboard/
    ├── app.py              ← you are here
    ├── data_loader.py      ← loading, cleaning, preprocessing
    ├── charts.py           ← all Plotly chart builders
    ├── requirements.txt    ← Python dependencies
    └── README.md           ← setup & usage guide
"""

import os

import pandas as pd
import streamlit as st

import charts as ch
from data_loader import get_summary_stats, load_and_clean

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LA Crime Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0b0d11;
    color: #e8eaf0;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background-color: #13161d;
    border-right: 1px solid #252a36;
  }

  /* KPI metric cards */
  div[data-testid="metric-container"] {
    background-color: #13161d;
    border: 1px solid #252a36;
    border-radius: 4px;
    padding: 16px 20px;
    border-left: 3px solid #ff4c4c;
  }

  div[data-testid="metric-container"] label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b7280 !important;
  }

  div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px;
    color: #ffffff !important;
  }

  div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #6b7280 !important;
  }

  /* Section headers */
  h2, h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 2px !important;
    color: #ffffff !important;
  }

  /* Expander */
  details summary {
    color: #6b7280;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
  }

  /* Divider */
  hr { border-color: #252a36; }

  /* Hide Streamlit branding */
  #MainMenu { visibility: hidden; }
  footer    { visibility: hidden; }
  header    { visibility: hidden; }

  /* Chart container */
  .stPlotlyChart {
    background-color: #13161d;
    border: 1px solid #252a36;
    border-radius: 4px;
    padding: 4px;
  }

  /* Selectbox / multiselect */
  .stMultiSelect > div, .stSelectbox > div {
    background-color: #13161d;
    border-color: #252a36;
    color: #e8eaf0;
  }

  /* Insight boxes */
  .insight-box {
    background: #13161d;
    border: 1px solid #252a36;
    border-left: 3px solid #ff4c4c;
    border-radius: 4px;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.6;
    color: #9ca3af;
  }

  .insight-box b { color: #e8eaf0; }

  /* Badge */
  .badge {
    display: inline-block;
    background: rgba(255,76,76,0.12);
    border: 1px solid rgba(255,76,76,0.3);
    color: #ff4c4c;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 2px;
    margin-bottom: 8px;
  }
</style>
""",
    unsafe_allow_html=True,
)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="badge">● Live Analytics</div>', unsafe_allow_html=True)
    st.title("🚨 LA Crime\nDashboard")
    st.markdown("---")

    default_path = "https://drive.google.com/uc?export=download&id=1Exky_OVFKVTg2n3ENWED8_hcPuXJLYgx"

    csv_path = st.text_input(
        "📂 Data Source (URL or Local Path)",
        value=default_path,
        help="Using Google Drive link for 238MB dataset to stay within GitHub limits.",
    )
    # File path input

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    # Load data (cached)
    if not os.path.exists(csv_path):
        st.error(f"File not found:\n`{csv_path}`\n\nPlease update the path above.")
        st.stop()

    with st.spinner("Loading & cleaning data…"):
        df_raw = load_and_clean(csv_path)

    # Year filter
    available_years = sorted(df_raw["year"].dropna().astype(int).unique().tolist())
    # Exclude partial years at the end
    full_years = [y for y in available_years if y <= 2024]

    selected_years = st.multiselect(
        "📅 Year",
        options=full_years,
        default=full_years,
    )

    # Area filter
    all_areas = sorted(df_raw["area_name"].dropna().unique().tolist())
    selected_areas = st.multiselect(
        "📍 LAPD Division",
        options=all_areas,
        default=[],
        placeholder="All divisions",
    )

    # Crime type filter
    all_crimes = sorted(df_raw["crm_cd_desc"].dropna().unique().tolist())
    selected_crimes = st.multiselect(
        "🔎 Crime Type",
        options=all_crimes,
        default=[],
        placeholder="All crime types",
    )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:10px; color:#6b7280; font-family:DM Mono,monospace;">'
        "Source: LAPD Open Data Portal<br>"
        "Records: 1,005,198<br>"
        "Features: 28 columns<br>"
        "Cleaned & processed in Python"
        "</p>",
        unsafe_allow_html=True,
    )


# ── Apply filters ─────────────────────────────────────────────────────────────

df = df_raw.copy()

if selected_years:
    df = df[df["year"].isin(selected_years)]

if selected_areas:
    df = df[df["area_name"].isin(selected_areas)]

if selected_crimes:
    df = df[df["crm_cd_desc"].isin(selected_crimes)]

if len(df) == 0:
    st.warning("⚠️ No data matches the current filters. Please adjust your selections.")
    st.stop()


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown('<div class="badge">● LAPD · 2020 – 2025</div>', unsafe_allow_html=True)
st.markdown(
    "## LA CRIME RATE  <span style='color:#ff4c4c'>TREND ANALYSIS</span>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='color:#6b7280; font-size:13px; font-family:DM Mono,monospace; margin-top:-8px;'>"
    f"Showing <b style='color:#e8eaf0'>{len(df):,}</b> records after filters · "
    f"{len(selected_years) if selected_years else len(full_years)} year(s) selected"
    f"</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ── KPI Cards ─────────────────────────────────────────────────────────────────

stats = get_summary_stats(df)

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Crimes", f"{stats['total_crimes']:,}")
k2.metric(
    "Peak Year", str(stats["peak_year"]), f"{stats['peak_year_count']:,} incidents"
)
k3.metric("Avg Victim Age", str(stats["avg_victim_age"]))
k4.metric("Weapon Involved", f"{stats['weapon_pct']}%")
k5.metric("Arrest Rate", f"{stats['arrest_pct']}%")
k6.metric("Crime Types", str(stats["unique_crime_types"]))

st.markdown("<br>", unsafe_allow_html=True)


# ── Tab layout ────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📈  Trends",
        "🏙️  Geography & Crimes",
        "🕐  Time Analysis",
        "👥  Victim Demographics",
        "🔫  Weapons & Status",
    ]
)


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — Trends
# ────────────────────────────────────────────────────────────────────────────

with tab1:
    st.markdown("### Annual & Monthly Crime Trends")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(ch.annual_bar(df), use_container_width=True)
    with col2:
        st.plotly_chart(ch.yoy_growth_line(df), use_container_width=True)

    st.plotly_chart(
        ch.monthly_line(df, selected_years if selected_years else full_years),
        use_container_width=True,
    )

    st.markdown("#### 💡 Trend Insights")
    st.markdown(
        """
    <div class="insight-box">
      <b>📈 Crime peaked in 2022</b> at 235,258 incidents — a 17.7% rise from 2020.
      Post-pandemic relaxation of restrictions and increased socioeconomic stress
      are likely contributing factors.
    </div>
    <div class="insight-box">
      <b>📉 2023 held steady</b> at 232,350 — nearly matching 2022 levels,
      suggesting the post-COVID crime surge stabilized rather than reversed.
    </div>
    <div class="insight-box">
      <b>📊 Seasonal patterns</b> show higher crime in summer months (Jul–Oct)
      across most years, consistent with national criminology research on
      warm-weather crime spikes.
    </div>
    """,
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — Geography & Crime Types
# ────────────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown("### Crime Types & LAPD Divisions")

    col1, col2 = st.columns([1, 1])
    with col1:
        n_crimes = st.slider("Show top N crime types", 5, 20, 10, key="n_crimes")
        st.plotly_chart(ch.top_crimes_bar(df, n_crimes), use_container_width=True)
    with col2:
        n_areas = st.slider("Show top N divisions", 5, 21, 15, key="n_areas")
        st.plotly_chart(ch.area_bar(df, n_areas), use_container_width=True)

    st.markdown("#### 💡 Geography Insights")
    st.markdown(
        """
    <div class="insight-box">
      <b>🚗 Vehicle crimes dominate</b> — Vehicle Stolen (115K) and Burglary from
      Vehicle (63K) together account for nearly 18% of all crimes. Improving
      anti-theft measures is a high-impact intervention.
    </div>
    <div class="insight-box">
      <b>🏙️ Central Division leads</b> in total incidents (69,674). Downtown LA's
      high population density, tourist activity, and homeless population create
      overlapping risk factors.
    </div>
    """,
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — Time Analysis
# ────────────────────────────────────────────────────────────────────────────

with tab3:
    st.markdown("### Temporal Crime Patterns")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(ch.hourly_bar(df), use_container_width=True)
    with col2:
        st.plotly_chart(ch.day_of_week_bar(df), use_container_width=True)

    # Hour distribution raw table (expander)
    with st.expander("📋 View raw hourly counts"):
        by_hour = df.groupby("hour_occ").size().reset_index(name="Crime Count")
        by_hour["Hour"] = by_hour["hour_occ"].apply(
            lambda h: (
                "12 AM"
                if h == 0
                else f"{h} AM" if h < 12 else "12 PM" if h == 12 else f"{h-12} PM"
            )
        )
        st.dataframe(
            by_hour[["Hour", "Crime Count"]].set_index("Hour"),
            use_container_width=True,
        )

    st.markdown("#### 💡 Time Insights")
    st.markdown(
        """
    <div class="insight-box">
      <b>☀️ Noon is the single busiest hour</b> — 67,836 incidents recorded at
      12:00 PM. This likely reflects both reporting patterns and actual lunchtime
      street crime. A secondary evening surge runs from 5–8 PM.
    </div>
    <div class="insight-box">
      <b>📅 Friday & Saturday are highest-crime days</b>, consistent with
      increased social activity, nightlife, and alcohol-related incidents
      on weekends.
    </div>
    <div class="insight-box">
      <b>🌙 4–6 AM is the safest window</b> with the fewest incidents —
      ~17,000–19,000 per hour, compared to the noon peak of 67,836.
    </div>
    """,
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — Victim Demographics
# ────────────────────────────────────────────────────────────────────────────

with tab4:
    st.markdown("### Victim Demographics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(ch.sex_donut(df), use_container_width=True)
    with col2:
        st.plotly_chart(ch.age_bar(df), use_container_width=True)
    with col3:
        st.plotly_chart(ch.descent_donut(df), use_container_width=True)

    # Summary table
    st.markdown("#### 📊 Demographic Summary Table")
    col_a, col_b = st.columns(2)
    with col_a:
        sex_table = (
            df["vict_sex"]
            .value_counts()
            .reset_index()
            .rename(columns={"vict_sex": "Gender", "count": "Count"})
        )
        sex_table["% Share"] = (
            sex_table["Count"] / sex_table["Count"].sum() * 100
        ).round(1)
        st.dataframe(sex_table, use_container_width=True, hide_index=True)

    with col_b:
        age_table = (
            df["age_group"]
            .value_counts()
            .reindex(
                ["0–17", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"],
                fill_value=0,
            )
            .reset_index()
            .rename(columns={"age_group": "Age Group", "count": "Count"})
        )
        age_table["% Share"] = (
            age_table["Count"] / age_table["Count"].sum() * 100
        ).round(1)
        st.dataframe(age_table, use_container_width=True, hide_index=True)

    st.markdown("#### 💡 Demographic Insights")
    st.markdown(
        """
    <div class="insight-box">
      <b>👨 Male victims slightly outnumber female</b> (47% vs 42%).
      However, female victims are disproportionately represented in
      domestic/intimate partner assault categories.
    </div>
    <div class="insight-box">
      <b>🎯 Ages 25–34 are most victimized</b> — 205,229 victims,
      reflecting their higher exposure due to commuting, nightlife, and
      public-space activity compared to other age groups.
    </div>
    <div class="insight-box">
      <b>🌎 Hispanic victims are most numerous</b> at 296,437 — consistent with
      LA's overall demographic composition (~49% Hispanic population).
    </div>
    """,
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 5 — Weapons & Case Status
# ────────────────────────────────────────────────────────────────────────────

with tab5:
    st.markdown("### Weapons Used & Case Resolution")

    col1, col2 = st.columns([3, 2])
    with col1:
        n_weapons = st.slider("Show top N weapons", 5, 15, 10, key="n_weapons")
        st.plotly_chart(ch.weapons_bar(df, n_weapons), use_container_width=True)
    with col2:
        st.plotly_chart(ch.status_donut(df), use_container_width=True)

        # Status breakdown table
        status_tbl = (
            df["status_full"]
            .value_counts()
            .reset_index()
            .rename(columns={"status_full": "Status", "count": "Count"})
        )
        status_tbl["% Share"] = (
            status_tbl["Count"] / status_tbl["Count"].sum() * 100
        ).round(1)
        st.dataframe(status_tbl, use_container_width=True, hide_index=True)

    st.markdown("#### 💡 Weapon & Status Insights")
    st.markdown(
        """
    <div class="insight-box">
      <b>✊ Physical force dominates</b> — "Strong-Arm" (hands, fists, feet)
      is the most common weapon at 174,777 incidents, accounting for more than
      half of all weapon-involved crimes.
    </div>
    <div class="insight-box">
      <b>🔫 Handguns are the top firearm</b> — 20,186 incidents involved a
      handgun, with semi-automatic pistols adding another 7,267.
    </div>
    <div class="insight-box">
      <b>⚖️ Only 9% of cases end in arrest</b> — 80% remain in "Investigation
      Continued" status, highlighting a systemic clearance rate challenge
      for LAPD across all crime categories.
    </div>
    """,
        unsafe_allow_html=True,
    )


# ── Raw Data Explorer ─────────────────────────────────────────────────────────

st.markdown("---")
with st.expander("🔬 Raw Data Explorer — browse cleaned records"):
    st.markdown(
        f"<p style='font-size:12px; color:#6b7280;'>"
        f"Showing filtered dataset: <b style='color:#e8eaf0'>{len(df):,}</b> rows × "
        f"<b style='color:#e8eaf0'>{len(df.columns)}</b> columns after preprocessing.</p>",
        unsafe_allow_html=True,
    )

    # Column selector
    default_cols = [
        "dr_no",
        "date_occ",
        "area_name",
        "crm_cd_desc",
        "vict_age",
        "vict_sex",
        "vict_descent_full",
        "weapon_desc",
        "status_full",
        "year",
        "month",
    ]
    visible_cols = [c for c in default_cols if c in df.columns]
    selected_cols = st.multiselect(
        "Columns to display", df.columns.tolist(), default=visible_cols
    )

    n_rows = st.slider("Rows to preview", 10, 500, 100, step=10)
    st.dataframe(df[selected_cols].head(n_rows), use_container_width=True)

    # Download button
    @st.cache_data
    def convert_for_download(dataframe):
        return dataframe.to_csv(index=False).encode("utf-8")

    csv_bytes = convert_for_download(df[selected_cols])
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="la_crime_cleaned_filtered.csv",
        mime="text/csv",
    )


# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#252a36; font-family:Bebas Neue,sans-serif;"
    "font-size:20px; letter-spacing:4px;'>"
    "LA CRIME DASHBOARD · LAPD OPEN DATA · 2020–2025"
    "</p>",
    unsafe_allow_html=True,
)
