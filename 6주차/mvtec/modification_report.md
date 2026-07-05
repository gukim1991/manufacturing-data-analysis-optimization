# 수정 내역 보고서

## 개요
이 보고서는 `step2_train.py`와 `step3_evaluate_upgrade`에서 수행한 주요 수정 사항을 정리합니다.

## 1. `step2_train.py` 수정 내역

### 모델 구조
- 기존: Encoder 3개 conv 레이어(32-64-128), Decoder 3개 transposed conv
- 수정: BatchNorm을 추가한 안정적 구조로 유지
- 최종 구조: Encoder 32-64-128, Decoder 128-64-32

### 학습 설정
- 배치 크기: 16 → `64`
- 에포크: 100 → `300`
- 옵티마이저: `Adam(lr=3e-4 -> 1e-3, weight_decay=1e-5)`
- 러닝레이트 스케줄러: `StepLR(step_size=75, gamma=0.7)`

### 데이터 처리
- 기존: `Resize`, `ToTensor`
- 수정: `Resize`, `RandomHorizontalFlip`, `ToTensor`
- `RandomRotation`, `ColorJitter` 제거하여 정상 패턴 학습 안정화

### 손실 및 입력 방식
- 기존: SSDIM+L1+MSE 복합 손실, 노이즈 추가 입력
- 수정: `nn.L1Loss()` 단일 손실로 안정화
- `noisy_images` 학습 제거, 모델은 정상 이미지 재구성에 집중

### latent 통계 저장
- `ConvAutoencoder`에 `encode()` 메서드 추가
- 학습 후 정상 데이터의 latent feature 통계 및 reconstruction error 통계를 계산하여 `anomaly_stats.pt`로 저장

## 2. `step3_evaluate_upgrade` 수정 내역

### anomaly score 계산 개선
- 기존: `Top-5%` 이상치 점수, 과도한 blur
- 수정: `Top-1%` 평균 + `5x5` blur
- 정상 latent 통계와의 거리 기반 score 결합

### 평가 함수 개선
- `evaluate_performance()`에서 `auroc` 계산 코드 추가
- `stats`를 전달받아 latent score를 anomaly score에 포함
- threshold 탐색은 1000개 후보로 유지

### 시각화 함수 개선
- `visualize_anomaly()`에서 `latent` 및 `stats`를 사용하여 이상치 점수 계산
- `main()`에서 `stats`를 로드하고 시각화 함수에 전달

### 오류 수정
- `compute_anomaly_score()`에서 CUDA/CPU 디바이스 불일치 수정
- `visualize_anomaly()` 호출 시 `latent` 인자 누락 수정
- 평가 함수에서 `auroc` 변수 미정의 문제 해결

## 3. 생성/저장 파일
- `autoencoder_model.pth`: 학습된 모델 가중치
- `anomaly_stats.pt`: 정상 학습 데이터의 latent, reconstruction 통계

## 4. 기대 효과
- 정상/비정상 분리도가 보다 명확해지고, F1-score 개선 가능성 증대
- 재구성 오차에 latent 분포 정보를 결합하여 이상 탐지 성능 향상

---
작성일: 2026-04-20
