import pandas as pd
import numpy as np

# 1. 실제 데이터 로드
df = pd.read_csv('uci-secom.csv')
print(f"[최초 데이터 로드] 총 레코드 수: {len(df)}건\n")

df_clean = df.copy()

# ==========================================
# 1. 유일성 (Uniqueness) 검증
# ==========================================
# 동일시간인 경우 중복으로 로깅된 오류
print("[1. 유일성 평가]")
duplicates = df_clean.duplicated(subset=['Time'], keep=False)
print(f" - 중복 기록 데이터 수: {duplicates.sum()}건 발견")

# 첫 번째 기록만 남기고 제거
df_clean = df_clean.drop_duplicates(subset=['Time'], keep='first')
print("중복 데이터 제거 완료\n")

# ==========================================
# 2. 완전성 (Completeness) 검증
# ==========================================
# 시간 데이터와 0번 센서값에 null값이 있는지 확인
print("[2. 완전성 평가]")
critical_cols = ['Time', '0']
missing_count = df_clean[critical_cols].isnull().any(axis=1).sum()
print(f" - 핵심 센서 결측치(NaN) 수: {missing_count}건 발견")

# 결측치가 포함된 행 제거
df_clean = df_clean.dropna(subset=critical_cols)
print("결측치 포함 사이클 제거 완료\n")

# ==========================================
# 3. 유효성 (Validity) 검증
# ==========================================
# 양/불 값이 -1, 1 외 데이터는 유효성 위배
print("[3. 유효성 평가]")
invalid_PassFail = ~df_clean['Pass/Fail'].isin([-1, 1])
print(f" - 유효하지 않은 양불값 -1, 1 외 데이터 수: {invalid_PassFail.sum()}건 발견")

df_clean = df_clean[~invalid_PassFail]
print("유효성 위배 데이터 제거 완료\n")

# ==========================================
# 4. 일관성 (Consistency) 검증
# 센서값이 없는데 양불 판정이 '1' 이면 모순
# ==========================================
print("[4. 일관성 평가]")
# 판정 모순
target_cols = [str(i) for i in range(8, 590)]
target_missing_count = df_clean[target_cols].isnull().any(axis=1).sum()
inconsistent_label = ((df_clean['Pass/Fail'] == 1) & (target_missing_count > 0))

print(f" - 양불/센서값 null 논리적 모순 수: {inconsistent_label.sum()}건 발견")

df_clean = df_clean[~inconsistent_label]
print("일관성 위배 데이터 제거 완료\n")

# ==========================================
# 5. 정확성 (Accuracy) 검증
# ==========================================
# 4번 센서 데이터 값이 소수점 5자리 이상인 경우 오류
print("[5. 정확성 평가]")
# 대상 센서 컬럼 (문자열!)
# 소수점 5자리 이상 여부 (컬럼별)
target_Round_cols = ['4']
over_5_decimal = (df_clean[target_Round_cols].apply(lambda col: np.round(col, 20) != col)
)

# 행 기준: 하나라도 해당되면 이상
row_anomaly = over_5_decimal.any(axis=1)
print(f"소수점 5자리 이상 포함 행 수: {row_anomaly.sum()}")

df_clean = df_clean[~row_anomaly]
print("정확성 위배 데이터 제거 완료\n")

# ==========================================
# [최종 결과] 정제된 고품질 데이터셋 저장
# ==========================================
print("=" * 60)
print("[최종 확보된 고품질 데이터셋 (Golden Dataset)]")
print(f" - 최초 원본 데이터: {len(df)}건")
print(f" - 최종 확보 데이터: {len(df_clean)}건")
print("=" * 60)

# 정제된 데이터를 새로운 CSV 파일로 저장
df_clean.to_csv('uci-secom_clean.csv', index=False)
print("파일이 'uci-secom_clean.csv'로 성공적으로 저장되었습니다.")