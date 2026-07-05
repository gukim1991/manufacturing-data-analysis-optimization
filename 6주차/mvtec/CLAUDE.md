# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Unsupervised anomaly detection on manufacturing products (MVTec AD dataset - Bottle category) using a Convolutional Autoencoder. The model is trained only on normal images and detects defects by measuring reconstruction error at inference time.

## Commands

```bash
# Step 1: Explore and visualize dataset
python step1_data_eda.py

# Step 2: Train the autoencoder (saves autoencoder_model.pth and anomaly_stats.pt)
python step2_train.py

# Step 3: Evaluate and visualize defect detection results
python step3_evaluate.py
```

No package manager config exists. Required: `torch`, `torchvision`, `opencv-python`, `numpy`, `matplotlib`, `scikit-learn`.

## Architecture

The pipeline is three sequential scripts — each depends on outputs from the previous:

**step1_data_eda.py** — `MVTecDataset` PyTorch Dataset class (also imported by steps 2 & 3). Loads images from `mvtec_ad/<category>/train/good/` (label=0) and `mvtec_ad/<category>/test/<defect_type>/` (label=1). Resizes all images to 256×256 RGB.

**step2_train.py** — `ConvAutoencoder` with 3-layer encoder (3→32→64→128 channels + BatchNorm) and symmetric decoder. Trained with L1Loss, Adam (lr=1e-3), StepLR scheduler over 300 epochs on normal images only. Outputs `autoencoder_model.pth` and `anomaly_stats.pt`.

**step3_evaluate.py** — Anomaly score = mean of top-1% pixel-level L2 reconstruction errors (Gaussian-blurred, 15×15 kernel). Threshold optimized by F1-score on test set. Metrics: AUROC, Precision-Recall, F1. Visualizes: original, reconstruction, error heatmap, overlay.

## Key Design Decisions

- **Top-1% pixel score** (not mean or max): robust to noise while sensitive to small localized defects — a single flaw fails QA.
- **Train on normal-only**: unsupervised setup; anomaly types are unknown at training time.
- Dataset path is hardcoded as `./mvtec_ad` relative to script location.
- `anomaly_stats.pt` stores mean/std of latent features and reconstruction errors from the training set, used to calibrate the threshold.
