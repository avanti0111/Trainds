import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    DEBUG        = os.getenv('DEBUG', 'false').lower() == 'true'
    SECRET_KEY   = os.getenv('SECRET_KEY', 'trainds-dev-secret-2024')

    # External APIs
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    OPENWEATHER_URL     = '[api.openweathermap.org](https://api.openweathermap.org/data/2.5/weather)'

    # ML model path
    MODEL_PATH = os.getenv('MODEL_PATH', '../ml/model/delay_model.pkl')

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '[localhost](http://localhost:5173)').split(',')
