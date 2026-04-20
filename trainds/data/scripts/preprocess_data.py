"""
Preprocess raw data files into ML-ready format.

Usage:
    python preprocess_data.py

Reads:
    data/sample_delays.csv  (or data/weather_history.csv if present)

Writes:
    data/processed_delays.csv   – cleaned, encoded, ready for training
"""

import os
import sys
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..')

WEATHER_MAP = {
    'Clear': 0, 'Clouds': 1, 'Rain': 2, 'Thunderstorm': 3,
    'Mist': 4, 'Haze': 5, 'Drizzle': 2,
}

LINE_MAP = {'Western': 0, 'Central': 1, 'Harbour': 2}


def load_raw(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f'File not found: {path}')
        sys.exit(1)
    df = pd.read_csv(path)
    print(f'Loaded {len(df)} rows from {path}')
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.dropna()
    df = df[df['delay_min'] >= 0]
    df = df[df['hour'].between(0, 23)]
    df = df[df['day_of_week'].between(0, 6)]
    df = df[df['rainfall_mm'] >= 0]
    # Remove extreme outliers (delay > 120 min is almost certainly bad data)
    df = df[df['delay_min'] <= 120]
    after = len(df)
    print(f'Cleaning: {before} → {after} rows ({before - after} dropped)')
    return df.reset_index(drop=True)


def encode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['weather_code'] = df['weather'].map(WEATHER_MAP).fillna(0).astype(int)
    df['line_code']    = df.get('line', pd.Series(['Central'] * len(df))).map(LINE_MAP).fillna(1).astype(int)

    # Engineer: is_peak flag
    df['is_peak'] = (
        df['hour'].between(7, 10) | df['hour'].between(17, 21)
    ).astype(int)

    # is_weekend
    df['is_weekend'] = df['day_of_week'].isin([0, 6]).astype(int)

    return df


def summarise(df: pd.DataFrame):
    print('\n── Summary ──────────────────────────')
    print(f'Rows       : {len(df)}')
    print(f'Delay mean : {df["delay_min"].mean():.2f} min')
    print(f'Delay std  : {df["delay_min"].std():.2f} min')
    print(f'Delay max  : {df["delay_min"].max():.1f} min')
    print(f'Peak rows  : {df["is_peak"].sum()} ({df["is_peak"].mean() * 100:.1f}%)')
    print(f'Weekend rows: {df["is_weekend"].sum()}')
    print('─────────────────────────────────────\n')


def main():
    raw_path = os.path.join(DATA_DIR, 'sample_delays.csv')
    out_path = os.path.join(DATA_DIR, 'processed_delays.csv')

    df = load_raw(raw_path)
    df = clean(df)
    df = encode(df)
    summarise(df)

    keep_cols = [
        'hour', 'day_of_week', 'weather_code', 'rainfall_mm',
        'line_code', 'is_peak', 'is_weekend', 'delay_min',
    ]
    df[keep_cols].to_csv(out_path, index=False)
    print(f'Processed data saved → {out_path}')


if __name__ == '__main__':
    main()
