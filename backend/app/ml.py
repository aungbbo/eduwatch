from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from xgboost import XGBRegressor


def build_features(prices: list[float], dates: list[datetime]) -> pd.DataFrame:
    df = pd.DataFrame({"price": prices, "date": pd.to_datetime(dates)})
    df = df.sort_values("date").reset_index(drop=True)

    df["lag_1"] = df["price"].shift(1)
    df["lag_7"] = df["price"].shift(7)
    df["lag_14"] = df["price"].shift(14)
    df["lag_30"] = df["price"].shift(30)
    df["lag_90"] = df["price"].shift(90)

    df["rolling_7"] = df["price"].rolling(7).mean()
    df["rolling_14"] = df["price"].rolling(14).mean()
    df["rolling_30"] = df["price"].rolling(30).mean()
    df["rolling_90"] = df["price"].rolling(90).mean()

    df["rolling_std_7"] = df["price"].rolling(7).std()
    df["rolling_std_30"] = df["price"].rolling(30).std()

    df["pct_change_1d"] = df["price"].pct_change(1)
    df["pct_change_7d"] = df["price"].pct_change(7)
    df["pct_change_30d"] = df["price"].pct_change(30)

    df["dist_from_7d_avg"] = (df["price"] - df["rolling_7"]) / df["rolling_7"]
    df["dist_from_30d_avg"] = (df["price"] - df["rolling_30"]) / df["rolling_30"]

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["quarter"] = df["date"].dt.quarter

    df = df.dropna()
    return df


FEATURE_COLS = [
    "lag_1", "lag_7", "lag_14", "lag_30", "lag_90",
    "rolling_7", "rolling_14", "rolling_30", "rolling_90",
    "rolling_std_7", "rolling_std_30",
    "pct_change_1d", "pct_change_7d", "pct_change_30d",
    "dist_from_7d_avg", "dist_from_30d_avg",
    "day_of_week", "month", "is_weekend", "quarter",
]


def _make_model() -> XGBRegressor:
    return XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        verbosity=0,
        random_state=42,
    )


def train_and_predict(prices: list[float], dates: list[datetime]) -> Optional[float]:
    df = build_features(prices, dates)
    if len(df) < 10:
        return None

    X = df[FEATURE_COLS]
    y = df["price"]

    model = _make_model()
    model.fit(X.iloc[:-1], y.iloc[:-1])
    predicted = model.predict(X.iloc[[-1]])[0]
    return round(float(predicted), 2)


def get_feature_importance(prices: list[float], dates: list[datetime]) -> dict:
    df = build_features(prices, dates)
    if len(df) < 10:
        return {}

    X = df[FEATURE_COLS]
    y = df["price"]

    model = _make_model()
    model.fit(X.iloc[:-1], y.iloc[:-1])

    importance = dict(zip(FEATURE_COLS, model.feature_importances_))
    top = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
    return {k: round(float(v), 4) for k, v in top}


def compute_statistics(prices: list[float]) -> dict:
    arr = np.array(prices)
    return {
        "current": round(float(arr[-1]), 2),
        "all_time_low": round(float(arr.min()), 2),
        "all_time_high": round(float(arr.max()), 2),
        "avg_30d": round(float(arr[-30:].mean()), 2),
        "avg_90d": round(float(arr[-90:].mean()), 2) if len(arr) >= 90 else round(float(arr.mean()), 2),
        "avg_365d": round(float(arr.mean()), 2),
        "std_30d": round(float(arr[-30:].std()), 2),
        "pct_vs_30d_avg": round(float((arr[-1] - arr[-30:].mean()) / arr[-30:].mean() * 100), 2),
        "pct_vs_90d_avg": round(float((arr[-1] - arr[-90:].mean()) / arr[-90:].mean() * 100), 2) if len(arr) >= 90 else None,
        "trend_7d": round(float((arr[-1] - arr[-7]) / arr[-7] * 100), 2) if len(arr) >= 7 else None,
        "trend_30d": round(float((arr[-1] - arr[-30]) / arr[-30] * 100), 2) if len(arr) >= 30 else None,
    }


def get_advice(current_price: float, predicted_price: float, prices: list[float]) -> dict:
    stats = compute_statistics(prices)
    all_time_low = stats["all_time_low"]
    avg_30d = stats["avg_30d"]
    pct_vs_30d = stats["pct_vs_30d_avg"]
    trend_7d = stats["trend_7d"] or 0
    predicted_drop = (current_price - predicted_price) / current_price * 100

    if current_price <= all_time_low * 1.03:
        return {
            "action": "BUY",
            "confidence": 95,
            "reason": f"Price is within 3% of its all-time low of ${all_time_low:.2f}. Historically this is the best time to buy.",
            "signals": ["All-time low proximity", "Strong historical support"],
        }

    if predicted_drop > 7:
        return {
            "action": "WAIT",
            "confidence": 85,
            "reason": f"The model predicts a ~{predicted_drop:.1f}% price drop soon. Waiting a few days could save you ${current_price - predicted_price:.2f}.",
            "signals": ["Strong downward prediction", f"Predicted price: ${predicted_price:.2f}"],
        }

    if pct_vs_30d < -10:
        return {
            "action": "BUY",
            "confidence": 80,
            "reason": f"Current price is {abs(pct_vs_30d):.1f}% below the 30-day average of ${avg_30d:.2f}. This is a solid deal.",
            "signals": ["Below 30-day average", f"30d avg: ${avg_30d:.2f}"],
        }

    if predicted_drop > 3:
        return {
            "action": "WAIT",
            "confidence": 70,
            "reason": f"A modest drop of ~{predicted_drop:.1f}% is predicted. Consider waiting a few days.",
            "signals": [f"Predicted price: ${predicted_price:.2f}", "Downward momentum"],
        }

    if pct_vs_30d > 10 and trend_7d > 3:
        return {
            "action": "WAIT",
            "confidence": 72,
            "reason": f"Price is {pct_vs_30d:.1f}% above the 30-day average and trending upward. Likely to correct soon.",
            "signals": ["Above 30-day average", "Upward 7-day trend"],
        }

    if pct_vs_30d < -5:
        return {
            "action": "BUY",
            "confidence": 65,
            "reason": "Price is slightly below the 30-day average. No significant drop predicted — decent time to buy.",
            "signals": ["Slightly below average", "Stable prediction"],
        }

    return {
        "action": "BUY",
        "confidence": 50,
        "reason": "Price is stable with no significant movement predicted. If you need the item, now is a reasonable time.",
        "signals": ["Stable price", "No strong signal"],
    }
