import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

def test_data_generation():
    np.random.seed(42)
    n_samples = 300
    
    rainfall = np.random.uniform(0, 50, n_samples)
    hour = np.random.randint(0, 24, n_samples)
    is_peak = np.array([1 if (7 <= h <= 10 or 17 <= h <= 21) else 0 for h in hour])
    congestion = np.random.uniform(0, 1, n_samples)
    
    # Target logic
    # delay = rain*0.5 + peak*10 + cong*15 + small_noise
    noise = np.random.normal(0, 1, n_samples)
    delay = (rainfall * 0.45) + (is_peak * 12) + (congestion * 18) + (hour * 0.1) + noise
    
    df = pd.DataFrame({
        'rainfall': rainfall,
        'hour_of_day': hour,
        'is_peak_hour': is_peak,
        'line_congestion': congestion,
        'delay_minutes': delay
    })
    
    X = df.drop('delay_minutes', axis=1)
    y = df['delay_minutes']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    
    print(f"R2 Score: {r2:.4f}")
    return r2

if __name__ == "__main__":
    test_data_generation()
