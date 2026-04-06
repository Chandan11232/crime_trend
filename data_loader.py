"""
data_loader.py
==============
Handles all data loading, cleaning, and preprocessing for the
LA Crime Rate Trend Analysis dashboard.

Preprocessing steps:
  1.  Load raw CSV with pandas
  2.  Rename columns → clean snake_case
  3.  Parse date columns (Date Rptd, DATE OCC) → datetime
  4.  Parse TIME OCC (HHMM int) → hour integer
  5.  Engineer date features: Year, Month, Month Name, Day of Week, Quarter
  6.  Clean victim age — remove sentinel values (0, negative, >120)
  7.  Engineer age groups (bins: 0-17, 18-24, 25-34, …, 65+)
  8.  Decode victim sex codes  (M/F/X/H/- → Male/Female/Unknown)
  9.  Decode victim descent codes (H→Hispanic, W→White, B→Black, …)
  10. Decode case status codes (AA→Adult Arrest, IC→Investigation Cont., …)
  11. Normalise text fields (strip whitespace, title-case)
  12. Drop low-signal / mostly-null columns
  13. Remove duplicate records (by DR_NO)
  14. Reset index
"""

import numpy as np
import pandas as pd
import streamlit as st

# ── Mapping tables ────────────────────────────────────────────────────────────

DESCENT_MAP = {
    "A": "Other Asian",
    "B": "Black",
    "C": "Chinese",
    "D": "Cambodian",
    "F": "Filipino",
    "G": "Guamanian",
    "H": "Hispanic",
    "I": "American Indian",
    "J": "Japanese",
    "K": "Korean",
    "L": "Laotian",
    "O": "Other",
    "P": "Pacific Islander",
    "S": "Samoan",
    "U": "Hawaiian",
    "V": "Vietnamese",
    "W": "White",
    "X": "Unknown",
    "Z": "Asian Indian",
}

SEX_MAP = {
    "M": "Male",
    "F": "Female",
    "X": "Unknown",
    "H": "Unknown",
    "-": "Unknown",
    "N": "Unknown",
}

STATUS_MAP = {
    "AA": "Adult Arrest",
    "AO": "Adult Other",
    "IC": "Investigation Continued",
    "JA": "Juvenile Arrest",
    "JO": "Juvenile Other",
    "CC": "Case Closed",
    "UNK": "Unknown",
}

AGE_BINS = [0, 17, 24, 34, 44, 54, 64, 120]
AGE_LABELS = ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]


# ── Main loader (cached by Streamlit) ────────────────────────────────────────


@st.cache_data(show_spinner="Loading & cleaning data...")
def load_and_clean(filepath: str) -> pd.DataFrame:
    if "drive.google.com" in filepath:
        # This converts a share link to a direct download link automatically
        if "/file/d/" in filepath:
            # Extract the ID from whatever link is passed in
            file_id = filepath.split("/file/d/")[1].split("/")[0]
            # Use that specific file_id dynamically
            filepath = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Load the data
    df = pd.read_csv(filepath, low_memory=False)

    # 2. Rename columns to snake_case
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[\s\-/]", "_", regex=True)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )

    # 3. Parse date columns
    for col in ["date_rptd", "date_occ"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%m/%d/%Y %H:%M", errors="coerce")

    # 4. Parse time (HHMM int -> hour int)
    if "time_occ" in df.columns:
        df["time_occ"] = pd.to_numeric(df["time_occ"], errors="coerce")
        df["hour_occ"] = (df["time_occ"] // 100).clip(0, 23).astype("Int64")

    # 5. Engineer date features
    if "date_occ" in df.columns:
        df["year"] = df["date_occ"].dt.year.astype("Int64")
        df["month"] = df["date_occ"].dt.month.astype("Int64")
        df["month_name"] = df["date_occ"].dt.strftime("%b")
        df["day_of_week"] = df["date_occ"].dt.day_name()
        df["quarter"] = df["date_occ"].dt.quarter.astype("Int64")

    # 6. Clean victim age
    if "vict_age" in df.columns:
        df["vict_age"] = pd.to_numeric(df["vict_age"], errors="coerce")
        df.loc[df["vict_age"] <= 0, "vict_age"] = np.nan
        df.loc[df["vict_age"] > 120, "vict_age"] = np.nan

    # 7. Engineer age groups
    if "vict_age" in df.columns:
        df["age_group"] = pd.cut(
            df["vict_age"], bins=AGE_BINS, labels=AGE_LABELS, right=True
        )

    # 8. Decode victim sex
    if "vict_sex" in df.columns:
        df["vict_sex"] = (
            df["vict_sex"]
            .astype(str)
            .str.strip()
            .str.upper()
            .map(SEX_MAP)
            .fillna("Unknown")
        )

    # 9. Decode victim descent
    if "vict_descent" in df.columns:
        df["vict_descent_full"] = (
            df["vict_descent"]
            .astype(str)
            .str.strip()
            .str.upper()
            .map(DESCENT_MAP)
            .fillna("Unknown")
        )

    # 10. Decode case status
    if "status" in df.columns:
        df["status_full"] = (
            df["status"]
            .astype(str)
            .str.strip()
            .str.upper()
            .map(STATUS_MAP)
            .fillna("Unknown")
        )

    # 11. Normalise text fields
    for col in ["crm_cd_desc", "area_name", "premis_desc"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    if "weapon_desc" in df.columns:
        df["weapon_desc"] = (
            df["weapon_desc"].astype(str).str.strip().str.title().replace("Nan", np.nan)
        )

    # 12. Drop low-signal / mostly-null columns
    cols_to_drop = ["crm_cd_2", "crm_cd_3", "crm_cd_4", "cross_street", "mocodes"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

    # 13. Remove duplicate records
    if "dr_no" in df.columns:
        df.drop_duplicates(subset=["dr_no"], keep="first", inplace=True)

    # 14. Reset index
    df.reset_index(drop=True, inplace=True)

    return df


# ── Summary statistics ────────────────────────────────────────────────────────


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Compute high-level KPI statistics from the cleaned DataFrame.

    Parameters
    ----------
    df : pd.DataFrame  cleaned crime DataFrame (may be filtered)

    Returns
    -------
    dict with keys: total_crimes, year_range, peak_year, peak_year_count,
         top_crime, top_crime_count, top_area, avg_victim_age,
         weapon_pct, arrest_pct, unique_crime_types, unique_areas
    """
    total = len(df)
    if total == 0:
        return {}

    valid_years = df["year"].dropna().astype(int)
    year_counts = df.groupby("year").size()
    top_crime = df["crm_cd_desc"].value_counts()
    top_area = df["area_name"].value_counts()
    weapon_used = df["weapon_desc"].notna() & (df["weapon_desc"] != "Nan")
    arrested = df["status_full"].isin(["Adult Arrest", "Juvenile Arrest"])

    return {
        "total_crimes": total,
        "year_range": (
            f"{int(valid_years.min())} - {int(valid_years.max())}"
            if len(valid_years)
            else "N/A"
        ),
        "peak_year": int(year_counts.idxmax()) if len(year_counts) else "N/A",
        "peak_year_count": int(year_counts.max()) if len(year_counts) else 0,
        "top_crime": top_crime.index[0] if len(top_crime) else "N/A",
        "top_crime_count": int(top_crime.iloc[0]) if len(top_crime) else 0,
        "top_area": top_area.index[0] if len(top_area) else "N/A",
        "avg_victim_age": (
            round(float(df["vict_age"].dropna().mean()), 1)
            if df["vict_age"].notna().any()
            else 0
        ),
        "weapon_pct": round(weapon_used.sum() / total * 100, 1),
        "arrest_pct": round(arrested.sum() / total * 100, 1),
        "unique_crime_types": int(df["crm_cd_desc"].nunique()),
        "unique_areas": int(df["area_name"].nunique()),
    }
