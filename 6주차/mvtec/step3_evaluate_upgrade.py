import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, precision_recall_curve
from torch.utils.data import DataLoader
from torchvision import transforms
from step1_data_eda import MVTecDataset
from step2_train import ConvAutoencoder


def compute_anomaly_score(model, images, stats, device):
    """픽셀별 z-score 정규화 이상치 점수를 계산합니다.

    단순 L2 재구성 오차 대신, 훈련셋 기준 '픽셀별 정상 오차 분포'로 z-score 정규화합니다.
    엣지·복잡한 질감처럼 원래부터 재구성이 어려운 픽셀의 영향을 제거하고,
    실제 결함 위치의 '이상한 정도'만을 정량화합니다.
    """
    images_dev = images.to(device)
    outputs    = model(images_dev)

    # L2 픽셀 오차 맵 + 가우시안 블러
    error     = torch.mean((images_dev - outputs) ** 2, dim=1)
    error_map = error.squeeze().cpu().numpy()                    # (256, 256)
    error_map = cv2.GaussianBlur(error_map, (11, 11), 0)

    # 픽셀별 z-score 정규화 (훈련 정상 이미지 분포 기준)
    pixel_mean = stats['pixel_mean'].numpy()                     # (256, 256)
    pixel_std  = stats['pixel_std'].numpy()                      # (256, 256)
    z_map      = (error_map - pixel_mean) / pixel_std
    z_map      = np.clip(z_map, 0, None)    # 정상보다 낮은 오차 제거

    # 상위 3% z-score 평균 → 이미지 레벨 이상치 점수
    k     = max(1, int(0.03 * z_map.size))
    topk  = np.partition(z_map.flatten(), -k)[-k:]
    score = np.mean(topk)

    return score, z_map


def evaluate_performance(model, test_loader, device, stats):
    """테스트 데이터셋 전체를 평가하여 정량적 지표를 산출합니다."""
    model.eval()
    y_true   = []
    y_scores = []

    print("전체 테스트 데이터셋 정량 평가를 진행합니다...")
    with torch.no_grad():
        for images, labels, _ in test_loader:
            score, _ = compute_anomaly_score(model, images, stats, device)
            y_scores.append(score)
            y_true.append(labels.item())  # 0: 정상, 1: 불량

    auroc = roc_auc_score(y_true, y_scores)

    precisions, recalls, thresholds = precision_recall_curve(y_true, y_scores)
    f1_scores  = (2 * precisions * recalls) / (precisions + recalls + 1e-8)
    best_idx   = np.argmax(f1_scores)
    best_f1    = f1_scores[best_idx]
    best_threshold = thresholds[best_idx]

    print("-" * 40)
    print(f"[전체 평가 결과]")
    print(f"AUROC Score          : {auroc:.4f}")
    print(f"Best F1-Score        : {best_f1:.4f}")
    print(f"Optimal Threshold    : {best_threshold:.4f}")
    print("-" * 40)

    return best_threshold


def visualize_anomaly(model, test_loader, device, stats, threshold, num_samples=3):
    """결함 탐지 시각화 및 판정 결과를 출력합니다."""
    model.eval()
    samples_shown = 0

    print(f"\n최적 임계값({threshold:.4f})을 적용하여 시각화를 시작합니다.")

    with torch.no_grad():
        for images, labels, _ in test_loader:
            if labels.item() == 0:
                continue

            score, z_map = compute_anomaly_score(model, images, stats, device)
            prediction   = "NG (Defect)" if score >= threshold else "OK (Normal)"

            images_dev = images.to(device)
            outputs    = model(images_dev)

            z_map_norm = cv2.normalize(z_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap    = cv2.applyColorMap(z_map_norm, cv2.COLORMAP_JET)

            img_np = images.squeeze().cpu().permute(1, 2, 0).numpy()
            out_np = outputs.squeeze().cpu().permute(1, 2, 0).numpy()

            heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            overlay     = cv2.addWeighted((img_np * 255).astype(np.uint8), 0.5, heatmap_rgb, 0.5, 0)

            _, axes = plt.subplots(1, 4, figsize=(16, 4))
            axes[0].imshow(img_np); axes[0].set_title(f'Original\nScore: {score:.4f} -> {prediction}')
            axes[1].imshow(out_np); axes[1].set_title('Reconstructed')
            axes[2].imshow(z_map, cmap='hot'); axes[2].set_title('Z-score Error Map')
            axes[3].imshow(overlay); axes[3].set_title('Overlay Heatmap')

            for ax in axes:
                ax.axis('off')
            plt.show()

            samples_shown += 1
            if samples_shown >= num_samples:
                break


if __name__ == "__main__":
    ROOT_DIR   = './mvtec_ad'
    CATEGORY   = 'bottle'
    MODEL_PATH = 'autoencoder_model.pth'
    STATS_PATH = 'anomaly_stats.pt'

    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])

    test_dataset = MVTecDataset(ROOT_DIR, CATEGORY, is_train=False, transform=transform)
    test_loader  = DataLoader(test_dataset, batch_size=1, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = ConvAutoencoder().to(device)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))

    stats = torch.load(STATS_PATH, map_location='cpu')

    # pixel_mean/pixel_std가 없으면 안내
    if 'pixel_mean' not in stats:
        raise RuntimeError(
            "anomaly_stats.pt에 픽셀별 통계가 없습니다.\n"
            "먼저 'python step2_compute_stats.py'를 실행하세요."
        )

    optimal_thresh = evaluate_performance(model, test_loader, device, stats)
    visualize_anomaly(model, test_loader, device, stats, optimal_thresh, num_samples=3)
