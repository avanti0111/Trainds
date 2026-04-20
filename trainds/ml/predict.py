"""
CLI prediction utility for quick testing.

Usage:
    python predict.py --hour 8 --day 1 --weather Rain --rain 12
"""

import argparse
import joblib
import os
import numpy as np

WEATHER_MAP = {
    'Clear': 0, 'Clouds': 1, 'Rain': 2, 'Thunderstorm': 3,
    'Mist': 4, 'Haze': 5, 'Drizzle': 2,
}

def predict(hour, day_of_week, weather, rainfall_mm):
    model_path = os.path.join(
        os.path.dirname(__file__), 'model', 'delay_model.pkl'
    )
    if not os.path.exists(model_path):
        print('Model not found. Run train.py first.')
        return

    model       = joblib.load(model_path)
    weather_code = WEATHER_MAP.get(weather, 0)
    features    = np.array([[hour, day_of_week, weather_code, rainfall_mm]])
    pred        = float(model.predict(features)[0])
    pred        = max(round(pred, 1), 0.0)

    risk = 'Low' if pred <= 3 else 'Medium' if pred <= 8 else 'High'
    print(f'\nPredicted delay : {pred} min')
    print(f'Risk level      : {risk}')
    return pred


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--hour',    type=int,   default=8)
    parser.add_argument('--day',     type=int,   default=1,     help='0=Sun … 6=Sat')
    parser.add_argument('--weather', type=str,   default='Clear')
    parser.add_argument('--rain',    type=float, default=0.0,   help='Rainfall in mm')
    args = parser.parse_args()

    predict(args.hour, args.day, args.weather, args.rain)
