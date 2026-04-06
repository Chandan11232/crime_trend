"""
charts.py
=========
All Plotly chart-building functions for the LA Crime Dashboard.
Fixed for Python 3.14 / Plotly keyword argument compatibility.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Theme Constants ──────────────────────────────────────────────────────────

BG = "#0b0d11"
SURFACE = "#13161d"
BORDER = "#252a36"
TEXT = "#e8eaf0"
MUTED = "#6b7280"
RED = "#ff4c4c"
ORANGE = "#ff8c42"
YELLOW = "#f7c948"
BLUE = "#4c9fff"

PALETTE = [RED, ORANGE, YELLOW, "#4cffb3", BLUE, "#a78bfa", "#f472b6"]

# base layout without axis-specific titles to avoid TypeErrors
LAYOUT_BASE = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="DM Sans, sans-serif", color=TEXT, size=12),
    margin=dict(l=12, r=12, t=40, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=11)),
    hoverlabel=dict(
        bgcolor="#1a1e28",
        bordercolor=BORDER,
        font=dict(family="DM Mono, monospace", color=TEXT, size=11),
    ),
)


def _apply_theme(fig: go.Figure, title: str):
    """Internal helper to apply consistent dark theme and titles."""
    fig.update_layout(
        **LAYOUT_BASE, title=dict(text=title, font=dict(color=TEXT, size=13), x=0)
    )
    fig.update_xaxes(
        gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED, size=10)
    )
    fig.update_yaxes(
        gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED, size=10)
    )
    return fig


# ── 1. Annual Crime Volume Bar ────────────────────────────────────────────────


def annual_bar(df: pd.DataFrame) -> go.Figure:
    yearly = df.groupby("year").size().reset_index(name="crimes")
    yearly = yearly[yearly["year"].between(2020, 2024)]
    peak = yearly["crimes"].max()

    colors = [RED if v == peak else "#2e3340" for v in yearly["crimes"]]

    fig = go.Figure(
        go.Bar(
            x=yearly["year"].astype(str),
            y=yearly["crimes"],
            marker_color=colors,
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Crimes: %{y:,}<extra></extra>",
        )
    )

    _apply_theme(fig, "Annual Crime Volume")
    fig.update_yaxes(title="Total Incidents", tickformat=",")
    return fig


# ── 2. Monthly Trend Line ─────────────────────────────────────────────────────


def monthly_line(df: pd.DataFrame, selected_years: list) -> go.Figure:
    MONTH_NAMES = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    fig = go.Figure()
    for i, yr in enumerate(sorted(selected_years)):
        sub = (
            df[df["year"] == yr]
            .groupby("month")
            .size()
            .reindex(range(1, 13), fill_value=0)
        )
        fig.add_trace(
            go.Scatter(
                x=MONTH_NAMES,
                y=sub.values,
                mode="lines+markers",
                name=str(yr),
                line=dict(width=2),
                marker=dict(size=5),
                hovertemplate=f"<b>{yr}</b> – %{{x}}<br>Crimes: %{{y:,}}<extra></extra>",
            )
        )

    _apply_theme(fig, "Monthly Trend by Year")
    fig.update_layout(legend=dict(orientation="h", y=1.1))
    fig.update_yaxes(tickformat=",")
    return fig


# ── 3. Top Crime Types Horizontal Bar ─────────────────────────────────────────


def top_crimes_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    top = df["crm_cd_desc"].value_counts().head(n).sort_values()

    fig = go.Figure(
        go.Bar(
            x=top.values,
            y=top.index,
            orientation="h",
            marker_color=BLUE,
            hovertemplate="%{y}<br>Count: %{x:,}<extra></extra>",
        )
    )

    _apply_theme(fig, f"Top {n} Crime Types")
    fig.update_layout(height=420, bargap=0.25)
    fig.update_xaxes(tickformat=",")
    fig.update_yaxes(tickfont=dict(color=TEXT, size=11))
    return fig


# ── 4. Crimes by Area Horizontal Bar ──────────────────────────────────────────


def area_bar(df: pd.DataFrame, n: int = 15) -> go.Figure:
    by_area = df["area_name"].value_counts().head(n).sort_values()

    fig = go.Figure(
        go.Bar(
            x=by_area.values,
            y=by_area.index,
            orientation="h",
            marker_color=BLUE,
            opacity=0.85,
            hovertemplate="%{y}<br>Count: %{x:,}<extra></extra>",
        )
    )

    _apply_theme(fig, f"Top {n} LAPD Divisions")
    fig.update_layout(height=450, bargap=0.25)
    fig.update_xaxes(tickformat=",")
    return fig


# ── 5. Hour-of-Day Bar ────────────────────────────────────────────────────────


def hourly_bar(df: pd.DataFrame) -> go.Figure:
    by_hour = df.groupby("hour_occ").size().reindex(range(24), fill_value=0)
    max_val = by_hour.max()

    labels = [
        (
            "12 AM"
            if h == 0
            else f"{h} AM" if h < 12 else "12 PM" if h == 12 else f"{h-12} PM"
        )
        for h in range(24)
    ]
    colors = [RED if v == max_val else "#2e3340" for v in by_hour.values]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=by_hour.values,
            marker_color=colors,
            hovertemplate="Hour: %{x}<br>Crimes: %{y:,}<extra></extra>",
        )
    )

    _apply_theme(fig, "Crime by Hour of Day")
    fig.update_layout(bargap=0.15)
    fig.update_yaxes(tickformat=",")
    fig.update_xaxes(tickangle=-45)
    return fig


# ── 6. Victim Sex Donut ───────────────────────────────────────────────────────


def sex_donut(df: pd.DataFrame) -> go.Figure:
    counts = df["vict_sex"].value_counts()
    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.65,
            marker_colors=[BLUE, "#f472b6", MUTED],
            textinfo="label+percent",
            hovertemplate="%{label}<br>Count: %{value:,}<extra></extra>",
        )
    )

    _apply_theme(fig, "Victim Gender")
    fig.update_layout(showlegend=False)
    return fig


# ── 7. Victim Age Group Bar ───────────────────────────────────────────────────


def age_bar(df: pd.DataFrame) -> go.Figure:
    order = ["0–17", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"]
    counts = df["age_group"].value_counts().reindex(order, fill_value=0)

    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=ORANGE,
            hovertemplate="Age %{x}<br>Victims: %{y:,}<extra></extra>",
        )
    )

    _apply_theme(fig, "Victim Age Groups")
    fig.update_yaxes(tickformat=",")
    return fig


# ── 8. Victim Descent Donut ───────────────────────────────────────────────────


def descent_donut(df: pd.DataFrame, n: int = 8) -> go.Figure:
    counts = df["vict_descent_full"].value_counts().head(n)
    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.55,
            marker_colors=PALETTE,
            textinfo="label+percent",
            hovertemplate="%{label}<br>Count: %{value:,}<extra></extra>",
        )
    )

    _apply_theme(fig, "Victim Ethnicity")
    fig.update_layout(showlegend=False)
    return fig


# ── 9. Weapons Bar ────────────────────────────────────────────────────────────


def weapons_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    top = df["weapon_desc"].dropna().str.title().value_counts().head(n).sort_values()

    fig = go.Figure(
        go.Bar(
            x=top.values,
            y=top.index,
            orientation="h",
            marker_color=RED,
            hovertemplate="%{y}<br>Count: %{x:,}<extra></extra>",
        )
    )

    _apply_theme(fig, f"Top {n} Weapons Used")
    fig.update_layout(height=380, bargap=0.25)
    fig.update_xaxes(tickformat=",")
    return fig


# ── 10. Case Status Donut ─────────────────────────────────────────────────────


def status_donut(df: pd.DataFrame) -> go.Figure:
    counts = df["status_full"].value_counts()
    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.65,
            marker_colors=PALETTE,
            textinfo="label+percent",
            hovertemplate="%{label}<br>Count: %{value:,}<extra></extra>",
        )
    )

    _apply_theme(fig, "Case Status")
    fig.update_layout(showlegend=False)
    return fig


# ── 11. Day-of-Week Bar ───────────────────────────────────────────────────────


def day_of_week_bar(df: pd.DataFrame) -> go.Figure:
    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    counts = df["day_of_week"].value_counts().reindex(order, fill_value=0)

    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=[
                RED if d in ("Friday", "Saturday") else "#2e3340" for d in counts.index
            ],
            hovertemplate="%{x}<br>Crimes: %{y:,}<extra></extra>",
        )
    )

    _apply_theme(fig, "Crimes by Day of Week")
    fig.update_yaxes(tickformat=",")
    return fig


# ── 12. YoY Growth Line ───────────────────────────────────────────────────────


def yoy_growth_line(df: pd.DataFrame) -> go.Figure:
    yearly = df[df["year"].between(2020, 2024)].groupby("year").size()
    pct = yearly.pct_change() * 100

    fig = go.Figure(
        go.Scatter(
            x=pct.index.astype(str),
            y=pct.values,
            mode="lines+markers+text",
            line=dict(color=ORANGE, width=2),
            text=[f"{v:+.1f}%" for v in pct.values],
            textposition="top center",
            hovertemplate="<b>%{x}</b><br>YoY Change: %{y:.1f}%<extra></extra>",
        )
    )

    fig.add_hline(y=0, line_color=BORDER, line_dash="dash")
    _apply_theme(fig, "Year-over-Year % Change")
    fig.update_yaxes(ticksuffix="%")
    return fig
