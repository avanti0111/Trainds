import json
import os

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Delay Prediction Model for TRAiNDS\n",
    "\n",
    "This notebook demonstrates the training and evaluation of a machine learning model designed to predict train delays for the **TRAiNDS** (Mumbai Local AI Assistant) project. The model uses environmental and temporal factors to provide real-time delay estimations.\n",
    "\n",
    "### Objectives:\n",
    "1. Generate a realistic synthetic dataset for Mumbai Local Train delays.\n",
    "2. Preprocess and analyze the features.\n",
    "3. Compare multiple regression models.\n",
    "4. Optimize a Random Forest Regressor using Grid Search.\n",
    "5. Evaluate the model using R², MAE, and MSE."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Import Libraries"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from sklearn.model_selection import train_test_split, GridSearchCV\n",
    "from sklearn.preprocessing import StandardScaler\n",
    "from sklearn.linear_model import LinearRegression\n",
    "from sklearn.tree import DecisionTreeRegressor\n",
    "from sklearn.ensemble import RandomForestRegressor\n",
    "from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error\n",
    "\n",
    "# Set visual style\n",
    "sns.set(style=\"whitegrid\")\n",
    "plt.rcParams[\"figure.figsize\"] = (10, 6)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Dataset Creation\n",
    "\n",
    "We create a synthetic dataset (300 rows) that simulates typical Mumbai local train delays. \n",
    "\n",
    "**Logic:**\n",
    "- `rainfall`: 0-50 mm (heavier rain causes more delays).\n",
    "- `hour_of_day`: 0-23.\n",
    "- `is_peak_hour`: 1 if the hour is between 7-10 or 17-21, else 0.\n",
    "- `line_congestion`: 0.0-1.0 (representing crowd/traffic density).\n",
    "- **Target (`delay_minutes`)**: `0.45*rainfall + 12*is_peak + 18*congestion + 0.1*hour + Gaussian Noise`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "np.random.seed(42)\n",
    "n_samples = 300\n",
    "\n",
    "# Generate features\n",
    "rainfall = np.random.uniform(0, 50, n_samples)\n",
    "hour = np.random.randint(0, 24, n_samples)\n",
    "is_peak = np.array([1 if (7 <= h <= 10 or 17 <= h <= 21) else 0 for h in hour])\n",
    "congestion = np.random.uniform(0, 1, n_samples)\n",
    "\n",
    "# Target logic with noise\n",
    "noise = np.random.normal(0, 1, n_samples)\n",
    "delay = (rainfall * 0.45) + (is_peak * 12) + (congestion * 18) + (hour * 0.1) + noise\n",
    "\n",
    "df = pd.DataFrame({\n",
    "    'rainfall_mm': rainfall,\n",
    "    'hour_of_day': hour,\n",
    "    'is_peak_hour': is_peak,\n",
    "    'line_congestion': congestion,\n",
    "    'delay_minutes': delay.clip(min=0) # No negative delays\n",
    "})\n",
    "\n",
    "print(\"Dataset Preview:\")\n",
    "display(df.head())\n",
    "print(f\"\\nDataset Shape: {df.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### EDA: Correlation Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "sns.heatmap(df.corr(), annot=True, cmap=sns.color_palette(\"Blues\", as_cmap=True))\n",
    "plt.title(\"Feature Correlation with Delay\")\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Preprocessing"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "X = df.drop('delay_minutes', axis=1)\n",
    "y = df['delay_minutes']\n",
    "\n",
    "# Split: 80% train, 20% test\n",
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n",
    "\n",
    "# Scale features\n",
    "scaler = StandardScaler()\n",
    "X_train_scaled = scaler.fit_transform(X_train)\n",
    "X_test_scaled = scaler.transform(X_test)\n",
    "\n",
    "print(f\"Training set size: {X_train.shape[0]}\")\n",
    "print(f\"Testing set size: {X_test.shape[0]}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Model Training & Comparison"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "models = {\n",
    "    \"Linear Regression\": LinearRegression(),\n",
    "    \"Decision Tree\": DecisionTreeRegressor(random_state=42),\n",
    "    \"Random Forest\": RandomForestRegressor(random_state=42)\n",
    "}\n",
    "\n",
    "results = {}\n",
    "\n",
    "for name, model in models.items():\n",
    "    model.fit(X_train_scaled, y_train)\n",
    "    preds = model.predict(X_test_scaled)\n",
    "    results[name] = r2_score(y_test, preds)\n",
    "\n",
    "print(\"Model Comparison (R² Score):\")\n",
    "for name, score in results.items():\n",
    "    print(f\"{name}: {score:.4f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Hyperparameter Tuning (Grid Search)\n",
    "\n",
    "We use GridSearchCV to find the optimal parameters for the Random Forest model."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "param_grid = {\n",
    "    'n_estimators': [50, 100, 200],\n",
    "    'max_depth': [None, 10, 20],\n",
    "    'min_samples_split': [2, 5]\n",
    "}\n",
    "\n",
    "grid_search = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=5, scoring='r2')\n",
    "grid_search.fit(X_train_scaled, y_train)\n",
    "\n",
    "best_rf = grid_search.best_estimator_\n",
    "print(f\"Best Parameters: {grid_search.best_params_}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Evaluation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "y_pred = best_rf.predict(X_test_scaled)\n",
    "\n",
    "mae = mean_absolute_error(y_test, y_pred)\n",
    "mse = mean_squared_error(y_test, y_pred)\n",
    "r2  = r2_score(y_test, y_pred)\n",
    "\n",
    "print(\"Best Model Performance (Test Set):\")\n",
    "print(f\"MAE: {mae:.2f} minutes\")\n",
    "print(f\"MSE: {mse:.2f}\")\n",
    "print(f\"R² Score: {r2:.4f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Visualization: Actual vs Predicted"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.scatter(y_test, y_pred, alpha=0.6, color='b')\n",
    "plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)\n",
    "plt.xlabel(\"Actual Delay (min)\")\n",
    "plt.ylabel(\"Predicted Delay (min)\")\n",
    "plt.title(\"Actual vs Predicted Train Delays\")\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Feature Importance"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "importances = best_rf.feature_importances_\n",
    "feature_names = X.columns\n",
    "indices = np.argsort(importances)\n",
    "\n",
    "plt.barh(range(len(indices)), importances[indices], align='center', color='teal')\n",
    "plt.yticks(range(len(indices)), [feature_names[i] for i in indices])\n",
    "plt.xlabel('Importance')\n",
    "plt.title('Feature Importance Analysis')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. Sample Prediction\n",
    "\n",
    "Testing with inputs: `rainfall = 10mm`, `hour = 8`, `is_peak = 1`, `congestion = 0.8`"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "sample_input = [[10, 8, 1, 0.8]]\n",
    "sample_scaled = scaler.transform(sample_input)\n",
    "prediction = best_rf.predict(sample_scaled)\n",
    "\n",
    "print(f\"Input: Rainfall=10mm, Hour=8am, PeakHour=Yes, Congestion=0.8\")\n",
    "print(f\"Predicted Delay: {prediction[0]:.2f} minutes\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 8. Conclusion and Explanation\n",
    "\n",
    "### Feature Selection\n",
    "- **Rainfall**: Heavily impacts railway signals and track conditions.\n",
    "- **Peak Hours**: High commuter density during 7-10 AM and 5-9 PM increases dwelling times at stations.\n",
    "- **Line Congestion**: Directly correlates with operational throughput and bottleneck formation.\n",
    "- **Hour of Day**: Captures temporal patterns beyond binary peak hours.\n",
    "\n",
    "### Model Relevance\n",
    "This regression model provides the foundation for the **TRAiNDS** backend decision engine. By predicting specific delay minutes, the routing algorithm can calculate more accurate 'total travel time' for commuters.\n",
    "\n",
    "### Limitations\n",
    "While the synthetic data used here yields high performance (**R² > 0.9**), real-world data would introduce more variance (e.g., technical failure of specific rakes, signal outages, or irregular megablocks) which might lower the R² score but improve actual robustness."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('c:/Users/Avanti/OneDrive/Documents/trainds/trainds/ml/delay_prediction_model.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook generated successfully.")
