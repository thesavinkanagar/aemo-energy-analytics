# ⚡ AEMO Energy Analytics Platform

An end-to-end data engineering project built on **Snowflake**, **dbt**, and **Python** —
ingesting Australian electricity market data and transforming it into analytics-ready models,
visualised in an interactive Streamlit dashboard.

---

## Dashboard Preview

![KPI Metrics](assets/dashboard_kpi.png)
![Demand Trend](assets/dashboard_demand_trend.png)
![Regional Breakdown](assets/dashboard_regional.png)

---

## Architecture

```mermaid
flowchart TD
    A[🌐 AEMO Public Website] -->|HTTP requests - 60 CSV files| B[Python Ingestion Script]
    B -->|snowflake-connector-python| C[(Snowflake RAW Schema\nRAW_GENERATION\n~500k rows)]
    C -->|dbt run| D[STAGING\nstg_generation\nclean + rename]
    D -->|dbt run| E[INTERMEDIATE\nint_generation_daily\ndaily aggregations]
    E -->|dbt run| F[(MARTS\nmart_generation_summary\n1,830 rows)]
    E -->|dbt run| G[(MARTS\ndim_region\n5 rows)]
    F --> H[Streamlit Dashboard]
    G --> H
```
---

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake |
| Transformation | dbt |
| Ingestion | Python, pandas |
| Visualisation | Streamlit, Plotly |
| Source Data | AEMO NEM — Price & Demand |

---

## Dataset

Public electricity market data from the **Australian Energy Market Operator (AEMO)**,
covering all 5 NEM regions (NSW, VIC, QLD, SA, TAS) across 2025 — ~500k rows of
5-minute interval settlement data.

| Column | Description |
|---|---|
| REGION | NEM region code |
| SETTLEMENTDATE | 5-minute settlement interval timestamp |
| TOTALDEMAND | Total electricity demand in MW |
| RRP | Regional reference price in AUD/MWh |
| PERIODTYPE | Settlement period type |

> Note: Western Australia operates a separate grid (SWIS/WEM) and is not part of the NEM dataset.

---

## dbt Data Model

```mermaid
flowchart LR
    S1[(RAW_GENERATION)] --> M1[stg_generation]
    M1 --> M2[int_generation_daily]
    M2 --> M3[mart_generation_summary]
    M4[dim_region] --> M3

    style S1 fill:#f0f0f0
    style M1 fill:#d4e6f1
    style M2 fill:#d5f5e3
    style M3 fill:#fdebd0
    style M4 fill:#fdebd0
```
- **11 dbt tests** across all layers (not_null, unique, accepted_values, relationships)
- Star schema design with fact and dimension tables

---

## Key Insights

- **NSW consistently has the highest electricity demand** across all NEM regions
- **South Australia shows the most price volatility** — driven by high renewable penetration
- **Peak demand occurs on weekdays** across all regions, dropping significantly on weekends
- **7-day rolling averages** reveal clear seasonal demand patterns across 2024

---

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/your-username/aemo-energy-analytics.git
cd aemo-energy-analytics
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up credentials**

Create a `.env` file in the root folder and fill in your Snowflake credentials:
```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Then open `.env` and fill in your values:
```
SNOWFLAKE_ACCOUNT=your-account-identifier
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=ANALYTICS_WH
SNOWFLAKE_DATABASE=ENERGY_DB
SNOWFLAKE_SCHEMA=RAW
```

**4. Run ingestion**
```bash
python ingestion/load_aemo.py
```

**5. Run dbt**
```bash
cd aemo_analytics
dbt run
dbt test
```

**6. Launch dashboard**
```bash
cd ..
streamlit run dashboard/app.py
```
