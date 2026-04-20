"""
Training script for the TRAiNDS delay prediction model.

Usage:
    python train.py [--model xgboost|random_forest] [--data PATH]

Outputs:
    ml/model/delay_model.pkl
    ml/model/metrics.json
"""

import argparse
import json
import os
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from preprocess import load_and_preprocess


def generate_synthetic_data(n: int = 5000) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates synthetic training data using the same heuristics
    as the backend fallback predictor.
    Use when no real CSV dataset is available.
    """
    rng  = np.random.default_rng(42)

    hour        = rng.integers(0,   24,  n).astype(np.float32)
    day         = rng.integers(0,    7,  n).astype(np.float32)
    weather     = rng.integers(0,    6,  n).astype(np.float32)
    rainfall    = rng.exponential(3.0, n).astype(np.float32)

    # Label generation mirrors heuristic_predict
    delay = np.zeros(n, dtype=np.float32)

    peak_mask     = ((hour >= 7) & (hour <= 10)) | ((hour >= 17) & (hour <= 21))
    offpeak_mask  = (hour > 10) & (hour < 17)
    delay[peak_mask]    += 6.0
    delay[offpeak_mask] += 1.5
    delay[~peak_mask & ~offpeak_mask] += 0.5

    weekend_mask = (day == 0) | (day == 6)
    delay[weekend_mask] -= 2.0

    # Weather penalties: 0=Clear,1=Clouds,2=Rain,3=Thunderstorm,4=Mist,5=Haze
    weather_penalties = np.array([0.0, 0.5, 5.0, 8.0, 2.0, 1.5])
    delay += weather_penalties[weather.astype(int)]
    delay += rainfall * 0.06

    # Noise
    delay += rng.normal(0, 1.5, n)
    delay  = np.clip(delay, 0, 60)

    X = np.column_stack([hour, day, weather, rainfall])
    return X, delay


def train_model(model_type: str, X_train, y_train):
    if model_type == 'xgboost' and XGBOOST_AVAILABLE:
        model = XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
        )
    else:
        if model_type == 'xgboost':
            print('XGBoost not installed – falling back to RandomForest')
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,
        )
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2   = r2_score(y_test, y_pred)
    return {'mae': round(mae, 3), 'rmse': round(rmse, 3), 'r2': round(r2, 3)}


def main():
    parser = argparse.ArgumentParser(description='Train TRAiNDS delay model')
    parser.add_argument('--model', default='xgboost',
                        choices=['xgboost', 'random_forest'])
    parser.add_argument('--data',  default=None,
                        help='Path to CSV; omit to use synthetic data')
    args = parser.parse_args()

    print(f'═══ TRAiNDS Delay Model Training ═══')
    print(f'Model : {args.model}')

    # ── Data ──────────────────────────────────────────────────────────────
    if args.data and os.path.exists(args.data):
        print(f'Data  : {args.data}')
        X, y = load_and_preprocess(args.data)
    else:
        print('Data  : synthetic (5 000 samples)')
        X, y = generate_synthetic_data(5000)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f'Train : {len(X_train)} | Test: {len(X_test)}')

    # ── Train ─────────────────────────────────────────────────────────────
    model   = train_model(args.model, X_train, y_train)
    metrics = evaluate(model, X_test, y_test)

    print(f'\nEvaluation:')
    print(f'  MAE  : {metrics["mae"]} min')
    print(f'  RMSE : {metrics["rmse"]} min')
    print(f'  R²   : {metrics["r2"]}')

    # ── Save ──────────────────────────────────────────────────────────────
    out_dir = os.path.join(os.path.dirname(__file__), 'model')
    os.makedirs(out_dir, exist_ok=True)

    model_path   = os.path.join(out_dir, 'delay_model.pkl')
    metrics_path = os.path.join(out_dir, 'metrics.json')

    joblib.dump(model, model_path)
    with open(metrics_path, 'w') as f:
        json.dump({k: float(v) for k, v in metrics.items()} | {'model_type': args.model}, f, indent=2)

    print(f'\nModel saved  → {model_path}')
    print(f'Metrics saved→ {metrics_path}')
    print('═══ Done ═══')


if __name__ == '__main__':
    main()
