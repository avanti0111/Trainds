"""
Preprocessing pipeline for Mumbai train delay data.
Input : data/sample_delays.csv
Output: preprocessed numpy arrays (X, y)
"""

import pandas as pd
import numpy as np
import os

WEATHER_MAP = {
    'Clear': 0, 'Clouds': 1, 'Rain': 2, 'Thunderstorm': 3,
    'Mist': 4, 'Haze': 5, 'Drizzle': 2,
}

def load_and_preprocess(csv_path: str) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv_path)

    # ── Required columns ──────────────────────────────────────────────────
    required = {'hour', 'day_of_week', 'weather', 'rainfall_mm', 'delay_min'}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {missing}')

    # ── Clean ─────────────────────────────────────────────────────────────
    df = df.dropna(subset=list(required))
    df = df[df['delay_min'] >= 0]
    df = df[df['hour'].between(0, 23)]
    df = df[df['day_of_week'].between(0, 6)]
    df = df[df['rainfall_mm'] >= 0]

    # ── Encode weather ────────────────────────────────────────────────────
    df['weather_code'] = df['weather'].map(WEATHER_MAP).fillna(0).astype(int)

    # ── Feature matrix ────────────────────────────────────────────────────
    feature_cols = ['hour', 'day_of_week', 'weather_code', 'rainfall_mm']
    X = df[feature_cols].values.astype(np.float32)
    y = df['delay_min'].values.astype(np.float32)

    print(f'Preprocessed {len(df)} samples | '
          f'delay range: [{y.min():.1f}, {y.max():.1f}] min')
    return X, y


if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    csv  = os.path.join(base, '..', 'data', 'sample_delays.csv')
    X, y = load_and_preprocess(csv)
    print('X shape:', X.shape, '| y shape:', y.shape)
