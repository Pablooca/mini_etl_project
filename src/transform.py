import pandas as pd
import logging
from datetime import datetime

def transform_data(raw_data: dict) -> pd.DataFrame:
    """Cleans, types, and enriches the raw data received from the API."""
    logging.info("Starting transformation and normalization stage...")
    try:
        hourly_data = raw_data.get("hourly", {})
        if not hourly_data:
            raise ValueError("The API payload does not contain the 'hourly' section.")
        
        df = pd.DataFrame(hourly_data)
        
        # Cronological casting
        df['time'] = pd.to_datetime(df['time'])
        
        # Quality Filter: Remove records with all null values in key metrics
        metrics = ['pm10', 'pm2_5', 'nitrogen_dioxide']
        df.dropna(subset=metrics, how='all', inplace=True)
        
        # Imputation of partial nulls using batch mean
        for col in metrics:
            if df[col].isnull().sum() > 0:
                logging.warning(f"Null values detected in '{col}'. Imputing with the mean.")
                df[col] = df[col].fillna(df[col].mean())
        
        # Mapping to database schema (snake_case)
        df.rename(columns={
            'time': 'date_time',
            'pm10': 'pm10_ug_m3',
            'pm2_5': 'pm25_ug_m3',
            'nitrogen_dioxide': 'no2_ug_m3'
        }, inplace=True)
        
        # Lineage: Adding processing timestamp for traceability
        df['processed_at'] = datetime.now()
        
        logging.info(f"Transformation completed successfully. {len(df)} records processed.")
        return df
    except Exception as e:
        logging.error(f"Error in the data transformation process: {e}")
        raise