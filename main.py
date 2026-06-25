import logging
from datetime import datetime
from src.extract import extract_data
from src.transform import transform_data
from src.load import load_data

def run_pipeline():
    """Main pipeline orchestrator for batch data processing."""
    start_time = datetime.now()
    logging.info("==================================================")
    logging.info("EXECUTING MAIN PIPELINE ORCHESTRATOR")
    logging.info("==================================================")
    
    try:
        # Main execution flow for data extraction, transformation, and loading (ETL)
        raw_payload = extract_data()
        cleaned_df = transform_data(raw_payload)
        load_data(cleaned_df)
        
        execution_time = datetime.now() - start_time
        logging.info(f"SUCCESS | Pipeline completed successfully. Duration: {execution_time}")
        logging.info("==================================================")
        
    except Exception as e:
        logging.critical(f"PROCESS ABORTED: The pipeline failed during execution: {e}")
        logging.info("==================================================")

if __name__ == "__main__":
    run_pipeline()