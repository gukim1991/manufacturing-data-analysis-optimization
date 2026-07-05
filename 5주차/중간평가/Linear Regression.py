import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

# =========================
# 1. 데이터 로드
# =========================
df = pd.read_csv("ta_20260411215422.csv")
print(f"원본 데이터 행 수: {len(df)}")

# 1.날짜 문자열 정리 (공백/탭 제거)
df['date'] = df['date'].astype(str).str.strip()
# 2️.datetime 변환
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# =========================
# 3️.날짜 변환 실패(NaT) 행 제거
# =========================
before_drop = len(df)
df = df.dropna(subset=['date'])
after_drop = len(df)
print(f"날짜 파싱 실패로 제거된 행 수: {before_drop - after_drop}")

# 4️.날짜를 index로 설정
df = df.set_index('date')
# 5️.수치형 컬럼만 추출 (FutureWarning 방지)
df = df.infer_objects(copy=False)

# =========================
# 보간 전 결측치 개수 확인
# =========================
missing_before = df.isna().sum()
print("\n보간 전 결측치 개수:")
print(missing_before)

# 6️.시간 기반 보간(결측치를 주변값으로 추정 채움)
df = df.interpolate(method='time')

# =========================
# 보간 후 결측치 개수 확인
# =========================
missing_after = df.isna().sum()
print("\n보간 후 결측치 개수:")
print(missing_after)

# =========================
# 최종 데이터 크기
# =========================
print(f"\n최종 데이터 행 수: {len(df)}")

# =========================
# 2. 3월 데이터만 사용
# =========================
march = df[df.index.month == 3].copy()

# Feature Engineering
march.loc[:, 'lag_1'] = march['avg_temp'].shift(1)#전날 평균기온
march.loc[:, 'lag_7'] = march['avg_temp'].shift(7)#7일전 평균기온
march.loc[:, 'ma_7']  = march['avg_temp'].rolling(7).mean()#지난 7일 평균기온

march = march.dropna()

# =========================
# 3. 학습 / 테스트 분리
# =========================
train = march[march.index.year <= 2025]
test  = march[march.index.year == 2026]

X_train = train[['lag_1', 'lag_7', 'ma_7']]
X_test  = test[['lag_1', 'lag_7', 'ma_7']]

y_train_avg = train['avg_temp']
y_train_min = train['min_temp']
y_train_max = train['max_temp']

# =========================
# 4. 모델 학습
# =========================
model_avg = LinearRegression()
model_min = LinearRegression()
model_max = LinearRegression()

model_avg.fit(X_train, y_train_avg)
model_min.fit(X_train, y_train_min)
model_max.fit(X_train, y_train_max)

# =========================
# 5. 예측
# =========================
pred_avg = model_avg.predict(X_test)
pred_min = model_min.predict(X_test)
pred_max = model_max.predict(X_test)

actual_avg = test['avg_temp'].values
actual_min = test['min_temp'].values
actual_max = test['max_temp'].values

# =========================
# 6. 평가 함수
# =========================
def evaluate(actual, predicted, label):
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae  = mean_absolute_error(actual, predicted)
    print(f"[{label}] RMSE: {rmse:.2f}℃ | MAE: {mae:.2f}℃")

evaluate(actual_avg, pred_avg, "Average Temp")
evaluate(actual_min, pred_min, "Min Temp")
evaluate(actual_max, pred_max, "Max Temp")

# =========================
# 7. 시각화
# =========================
plt.figure(figsize=(12,5))
plt.plot(test.index, actual_avg, label="Actual Avg Temp", color="blue")
plt.plot(test.index, pred_avg, label="Predicted Avg Temp", color="red", linestyle="--")

plt.title("2026 March Average Temperature: Actual vs Predicted(Linear Regression)")
plt.xlabel("Date")
plt.ylabel("Temperature (℃)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()