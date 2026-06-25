import requests
import logging
from config.settings import API_URL

def extract_data() -> dict:
    """Consumes the Open-Meteo REST API to obtain atmospheric telemetry."""
    logging.info("Starting extraction stage from public API...")
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        logging.info("Extraction completed successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Critical network error during Extraction: {e}")
        raise