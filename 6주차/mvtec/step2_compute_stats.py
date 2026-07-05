"""
훈련된 모델을 로드하여 픽셀별 재구성 오차 통계를 계산하고
anomaly_stats.pt에 추가합니다. 재학습 없이 실행 가능합니다.

실행: python step2_compute_stats.py
"""
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from step1_data_eda import MVTecDataset
from step2_train import ConvAutoencoder

ROOT_DIR   = './mvtec_ad'
CATEGORY   = 'bottle'
MODEL_PATH = 'autoencoder_model.pth'
STATS_PATH = 'anomaly_stats.pt'

# 통계 계산 시에는 랜덤 증강 없이 평가 모드와 동일한 변환 사용
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

train_dataset = MVTecDataset(ROOT_DIR, CATEGORY, is_train=True, transform=transform)
train_loader  = DataLoader(train_dataset, batch_size=16, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = ConvAutoencoder().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

print("훈련 이미지의 픽셀별 재구성 오차 분포 계산 중...")
pixel_errors = []
with torch.no_grad():
    for images, _, _ in train_loader:
        images  = images.to(device)
        outputs = model(images)
        error   = torch.mean((images - outputs) ** 2, dim=1)  # (B, H, W)
        pixel_errors.append(error.cpu())

pixel_tensor = torch.cat(pixel_errors, dim=0)   # (N, 256, 256)
pixel_mean   = pixel_tensor.mean(dim=0)          # (256, 256): 각 픽셀의 평균 정상 오차
pixel_std    = pixel_tensor.std(dim=0) + 1e-6    # (256, 256): 표준편차 (0 방지)

# 기존 stats에 픽셀별 통계 추가
stats = torch.load(STATS_PATH, map_location='cpu')
stats['pixel_mean'] = pixel_mean
stats['pixel_std']  = pixel_std
torch.save(stats, STATS_PATH)

print(f"완료: anomaly_stats.pt 업데이트")
print(f"  pixel_mean  shape: {pixel_mean.shape}")
print(f"  pixel_std   shape: {pixel_std.shape}")
