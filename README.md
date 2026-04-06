# LA Crime Rate Trend Analysis Dashboard

An interactive Streamlit dashboard for analysing LAPD crime data (2020–2025)
built entirely in Python with Plotly visualisations.

---

## Project Structure

```
crime_dashboard/
├── app.py              # Main Streamlit entry point
├── data_loader.py      # All data loading, cleaning & preprocessing
├── charts.py           # All Plotly chart builder functions
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Place your CSV file

Copy `Crime_Data_from_2020_to_Present.csv` into the `crime_dashboard/` folder,
OR note its full path — you can enter it in the sidebar at runtime.

### 3. Launch the dashboard

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Data Cleaning & Preprocessing (data_loader.py)

| Step | Action |
|------|--------|
| 1 | Load raw CSV with `pandas.read_csv` |
| 2 | Rename all columns to `snake_case` |
| 3 | Parse `date_rptd` and `date_occ` → `datetime64` |
| 4 | Parse `time_occ` (HHMM integer) → `hour_occ` (0–23) |
| 5 | Engineer `year`, `month`, `month_name`, `day_of_week`, `quarter` |
| 6 | Remove invalid victim ages (sentinel 0, negatives, >120) |
| 7 | Bin ages → `age_group` categories (0–17, 18–24, 25–34, …, 65+) |
| 8 | Decode sex codes: M→Male, F→Female, X/H/-→Unknown |
| 9 | Decode 18 descent codes: H→Hispanic, W→White, B→Black, … |
| 10 | Decode status codes: AA→Adult Arrest, IC→Investigation Continued, … |
| 11 | Strip whitespace & title-case text fields |
| 12 | Drop mostly-null columns: `crm_cd_2/3/4`, `cross_street`, `mocodes` |
| 13 | Remove duplicate rows by `DR_NO` |
| 14 | Reset DataFrame index |

All cleaning is cached with `@st.cache_data` so it runs only once per session.

---

## Dashboard Tabs

| Tab | Charts |
|-----|--------|
| 📈 Trends | Annual bar · YoY % change line · Monthly multi-year line |
| 🏙️ Geography & Crimes | Top N crime types · Top N LAPD divisions |
| 🕐 Time Analysis | Crime by hour · Crime by day of week |
| 👥 Victim Demographics | Gender donut · Age group bar · Ethnicity donut |
| 🔫 Weapons & Status | Top weapons bar · Case status donut |

Sidebar filters apply across **all tabs**: Year, LAPD Division, Crime Type.

---

## Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Pandas** — data loading, cleaning, aggregation
- **NumPy** — numerical operations
- **Plotly** — interactive charts

---

## Dataset

Source: [LAPD Open Data Portal](https://data.lacity.org/)  
File: `Crime_Data_from_2020_to_Present.csv`  
Records: ~1,005,198 | Columns: 28
