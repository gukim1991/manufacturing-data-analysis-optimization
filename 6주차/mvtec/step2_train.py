# 02_train.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from step1_data_eda import MVTecDataset # 앞서 만든 Dataset 클래스 임포트

class ConvAutoencoder(nn.Module):
    """합성곱 오토인코더 아키텍처"""
    def __init__(self):
        super(ConvAutoencoder, self).__init__()
        # self.encoder = nn.Sequential(
        #     nn.Conv2d(3, 16, 3, stride=2, padding=1), nn.ReLU(),
        #     nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),
        #     nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.ReLU()
        # )
        # self.decoder = nn.Sequential(
        #     nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1), nn.ReLU(),
        #     nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1), nn.ReLU(),
        #     nn.ConvTranspose2d(16, 3, 3, stride=2, padding=1, output_padding=1), nn.Sigmoid()
        # )

        # ===== 적절한 모델 용량으로 anomaly detection 성능을 높입니다 =====
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=2, padding=1), nn.BatchNorm2d(128), nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 3, stride=2, padding=1, output_padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 3, stride=2, padding=1, output_padding=1), nn.Sigmoid()
        )

    def encode(self, x):
        return self.encoder(x)

    def forward(self, x):
        return self.decoder(self.encoder(x))

if __name__ == "__main__": 
    ROOT_DIR = './mvtec_ad' 
    CATEGORY = 'bottle' 
    BATCH_SIZE = 64  # 더 큰 배치 사이즈로 안정성 향상
    NUM_EPOCHS = 300  # 더 긴 학습

    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomHorizontalFlip(p=0.5),  # 좌우 반전
        transforms.ToTensor(),
    ])

    # 증폭된 노이즈 기반 학습은 anomaly separation을 악화시킬 수 있으므로 제거합니다.

    train_dataset = MVTecDataset(ROOT_DIR, CATEGORY, is_train=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"학습 디바이스: {device}")

    model = ConvAutoencoder().to(device)
    
    # ===== 안정적인 anomaly autoencoder 손실 =====
    criterion = nn.L1Loss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=75, gamma=0.7)  # 더 천천히 감소
    
    # ===== 이전 옵티마이저 (주석) =====
    # optimizer = optim.Adam(model.parameters(), lr=1e-3)

    print("모델 학습 시작...")
    model.train()
    for epoch in range(NUM_EPOCHS):
        epoch_loss = 0
        for images, _, _ in train_loader:
            images = images.to(device)

            outputs = model(images)
            loss = criterion(outputs, images)  # 정상 이미지 재구성 학습
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        scheduler.step()
            
        if (epoch+1) % 20 == 0:
            print(f'Epoch [{epoch+1}/{NUM_EPOCHS}], Loss: {epoch_loss/len(train_loader):.4f}, LR: {optimizer.param_groups[0]["lr"]:.6f}')
        
        # ===== 이전 로깅 방식 (주석) =====
        # if (epoch+1) % 10 == 0:
        #     print(f'Epoch [{epoch+1}/{NUM_EPOCHS}], Loss: {epoch_loss/len(train_loader):.4f}')

    # 학습된 모델 가중치 저장
    SAVE_PATH = 'autoencoder_model.pth'
    torch.save(model.state_dict(), SAVE_PATH)

    # 정상 잠재 표현 통계 저장
    model.eval()
    with torch.no_grad():
        latent_vectors = []
        recon_scores = []
        for images, _, _ in train_loader:
            images = images.to(device)
            latent = model.encode(images)
            latent_vectors.append(latent.cpu())
            outputs = model(images)
            recon_scores.append(torch.mean((outputs - images) ** 2, dim=(1, 2, 3)).cpu())

    latent_tensor = torch.cat(latent_vectors, dim=0)
    feature_mean = latent_tensor.mean(dim=0)
    feature_var = latent_tensor.var(dim=0, unbiased=False) + 1e-6
    feature_std = torch.sqrt(feature_var)

    recon_tensor = torch.cat(recon_scores, dim=0)
    recon_mean = torch.mean(recon_tensor)
    recon_std = torch.std(recon_tensor) + 1e-6

    stats = {
        'feature_mean': feature_mean,
        'feature_std': feature_std,
        'recon_mean': recon_mean,
        'recon_std': recon_std,
    }
    torch.save(stats, 'anomaly_stats.pt')
    print(f"모델과 통계 저장 완료: {SAVE_PATH}, anomaly_stats.pt")