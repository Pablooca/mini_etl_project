import os
import logging

# Logging system configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Data infrastructure constants
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "calidad_aire_sevilla.db")
TABLE_NAME = "metr_calidad_aire"

# Origin API parameters (Seville)
API_URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    "?latitude=37.3891&longitude=-5.9845"
    "&hourly=pm10,pm2_5,nitrogen_dioxide"
)