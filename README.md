# Air-Quality ETL Pipeline (Sevilla)

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/library-pandas%20v2.2-purple)](https://pandas.pydata.org/)
[![Database](https://img.shields.io/badge/database-SQLite3-green)](https://www.sqlite.org/index.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository features a robust, modular batch ETL (Extract, Transform, Load) data pipeline developed in Python. The core objective is to ingest daily ambient air quality metrics (PM10, PM2.5, and NO2) for the geographic coordinates of Seville, Spain, utilizing the Open-Meteo public REST API. The pipeline cleanses and normalizes the incoming data stream using Pandas and handles persistence **idempotently** within a local relational SQLite database.

The project is architected following industry best practices for data engineering: decoupled stages, granular exception handling, structured logging, and defensive database modeling.

---

## 🏗️ Architecture & Data Flow

The pipeline executes synchronously, enforcing a clear separation of concerns across the standard ETL stages:

```text
[ REST API ] --(JSON)--> [ EXTRACT ] 
                            │
                            ▼
                         [ TRANSFORM ] ──(Data Validation & Imputation)
                            │
                            ▼
                         [ STAGING ] ──(Temporary Table)
                            │
                            ▼
 [ SQLite DB ] <─────── [ LOAD ] ──(UPSERT Strategy)
```

* **Extract:** Consumes the REST API using optimized HTTP requests configured with explicit timeouts to prevent execution hangs.
* **Transform:** Parses the JSON payload into a vector-optimized **Pandas DataFrame**. This stage handles chronological data typing, maps fields to standard `snake_case` nomenclature, and executes an automated null-value handling strategy (imputation via the batch's moving average).
* **Load:** Stages the transformed data within a temporary transaction area in **SQLite** before executing an atomic, conflict-free database merge (**Upsert**).

---

## 🌟 Production-Grade Features

* **Idempotency by Design:** Multiple pipeline executions within the same temporal window will not cause data duplication or corrupt historical states. The pipeline uses an `INSERT OR REPLACE` strategy anchored on the primary key (`fecha_hora`).
* **Traceability & Monitoring:** Fully replaces standard output `print` statements with Python's native `logging` library. Logs are structured with ISO-8601 timestamps and distinct severity levels (`INFO`, `WARNING`, `ERROR`, `CRITICAL`) for seamless integration with log aggregators.
* **Data Audit Trail:** Every row includes an execution timestamp (`procesado_en`) to ensure data lineage, allowing clear visibility into exactly when a specific record batch was processed and loaded.

---

## 📂 Project Structure

```text
.
├── data/
│   └── calidad_aire_sevilla.db  # Relational database file (Auto-generated)
├── .gitignore
├── etl_script.py               # Main pipeline orchestrator and logic
├── README.md
└── requirements.txt            # Project dependencies pinned to specific versions
```

---

## 🛠️ Setup & Installation

### Prerequisites

* Python 3.9 or higher installed locally.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/air-quality-etl-sevilla.git](https://github.com/your-username/air-quality-etl-sevilla.git)
cd air-quality-etl-sevilla
```

### 2. Virtual Environment & Dependency Isolation

It is highly recommended to isolate your environment dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate environment (Linux/macOS)
source venv/bin/activate

# Activate environment (Windows)
./venv/Scripts/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Execute the Pipeline

To trigger the batch processing manually, run the main orchestrator script:

```bash
python etl_script.py
```

---

## 📊 Data Model (Relational Schema)

The target table `metr_calidad_aire` is explicitly typed and optimized under the following SQL schema:

```sql
CREATE TABLE IF NOT EXISTS metr_calidad_aire (
    fecha_hora TEXT PRIMARY KEY,
    pm10_ug_m3 REAL,
    pm25_ug_m3 REAL,
    no2_ug_m3 REAL,
    procesado_en TEXT
);
```

### Data Dictionary

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `fecha_hora` | **TEXT** | **PRIMARY KEY** | Target measurement timestamp (Format: `YYYY-MM-DD HH:MM:SS`). |
| `pm10_ug_m3` | **REAL** | **NULLABLE** | Concentration of particulate matter < 10 µm in diameter (µg/m³). |
| `pm25_ug_m3` | **REAL** | **NULLABLE** | Concentration of particulate matter < 2.5 µm in diameter (µg/m³). |
| `no2_ug_m3` | **REAL** | **NULLABLE** | Nitrogen Dioxide concentration (µg/m³). |
| `procesado_en` | **TEXT** | **NOT NULL** | System audit timestamp indicating when the row was loaded into the database. |

---

## 🧪 Data Validation & Verification

Once the pipeline run completes successfully, you can easily inspect the integrity and structure of the loaded records directly from your terminal using the interactive SQLite engine:

```bash
sqlite3 data/calidad_aire_sevilla.db "SELECT * FROM metr_calidad_aire LIMIT 5;"
```

---

## 📈 Scalability Roadmap

To evolve this localized batch process into a production-grade enterprise data solution, the following enhancements are planned:

* **Containerization:** Wrapping the execution runtime into a multi-stage **Docker** image to guarantee absolute environment parity across environments.
* **Orchestration:** Transitioning the localized execution into an **Apache Airflow** or Prefect DAG to handle scheduling, SLA tracking, and automated failure alerts.
* **Cloud Infrastructure:** Migrating the storage layer from a local SQLite instance to a fully managed relational database (such as PostgreSQL via Amazon RDS or GCP Cloud SQL), saving raw JSON responses into a landing Data Lake (S3/GCS) for data historical archiving.