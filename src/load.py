import sqlite3
import os
import logging
import pandas as pd
from config.settings import DB_DIR, DB_PATH, TABLE_NAME

def load_data(df: pd.DataFrame):
    """Loads the data into the local analytical warehouse using an Upsert strategy."""
    logging.info(f"Starting the data loading stage in the relational database...")
    conn = None
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Garantizar DDl del destino
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                date_time TEXT PRIMARY KEY,
                pm10_ug_m3 REAL,
                pm25_ug_m3 REAL,
                no2_ug_m3 REAL,
                processed_at TEXT
            );
        """)
        conn.commit()
        
        # Normalización de timestamps a string para compatibilidad estricta con SQLite
        staging_df = df.copy()
        staging_df['date_time'] = staging_df['date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        staging_df['processed_at'] = staging_df['processed_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Volcado a tabla intermedia de Staging
        staging_df.to_sql("temp_staging", conn, if_exists="replace", index=False)
        
        # Operación atómica de Upsert
        upsert_query = f"""
            INSERT OR REPLACE INTO {TABLE_NAME} (date_time, pm10_ug_m3, pm25_ug_m3, no2_ug_m3, processed_at)
            SELECT date_time, pm10_ug_m3, pm25_ug_m3, no2_ug_m3, processed_at FROM temp_staging;
        """
        cursor.execute(upsert_query)
        cursor.execute("DROP TABLE temp_staging;")
        conn.commit()
        
        logging.info("Load stage completed successfully with idempotent behavior (INSERT OR REPLACE).")
        
    except sqlite3.Error as e:
        logging.error("Rolling back the transaction to maintain data integrity.")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Connection with the database closed safely.")