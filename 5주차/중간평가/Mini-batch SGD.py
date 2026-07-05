import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

# =========================
# 1. 데이터 로드
# =========================
df = pd.read_csv("ta_20260411215422.csv")

df['date'] = df['date'].astype(str).str.strip()
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])

df = df.set_index('date')
df = df.infer_objects(copy=False)
df = df.interpolate(method='time')

# =========================
# 2. 3월 데이터
# =========================
march = df[df.index.month == 3].copy()

march['lag_1'] = march['avg_temp'].shift(1)
march['lag_7'] = march['avg_temp'].shift(7)
march['ma_7']  = march['avg_temp'].rolling(7).mean()

march = march.dropna()

# =========================
# 3. Train / Test
# =========================
train = march[march.index.year <= 2025]
test  = march[march.index.year == 2026]

X_train = train[['lag_1', 'lag_7', 'ma_7']]
X_test  = test[['lag_1', 'lag_7', 'ma_7']]

y_train = train['avg_temp']
y_test  = test['avg_temp']

# =========================
# 4. X만 스케일링
# =========================
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

# =========================
# 5. Mini-batch SGD
# =========================
sgd = SGDRegressor(
    loss='squared_error',
    learning_rate='constant',  # 고정
    eta0=0.001,                # 핵심
    max_iter=3000,
    tol=None,                  # 조기종료 OFF
    shuffle=False,             # 재현성
    random_state=42
)

# =========================
# 6. 학습
# =========================
sgd.fit(X_train_s, y_train)

# =========================
# 7. 예측
# =========================
pred = sgd.predict(X_test_s)

# =========================
# 8. 평가
# =========================
rmse = np.sqrt(mean_squared_error(y_test, pred))
mae  = mean_absolute_error(y_test, pred)

print(f"[Mini-batch SGD 비교용]")
print(f"RMSE: {rmse:.2f}℃")
print(f"MAE : {mae:.2f}℃")

# =========================
# 9. 시각화
# =========================
plt.figure(figsize=(12,5))
plt.plot(test.index, y_test.values, label='Actual Avg Temp', color='blue')
plt.plot(test.index, pred, label='Predicted Avg Temp (SGD)',
         color='red', linestyle='--')

plt.title("2026 March Average Temperature Prediction (Mini-batch SGD)")
plt.xlabel("Date")
plt.ylabel("Temperature (℃)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()