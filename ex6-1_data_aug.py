import cv2
import numpy as np

# ==========================================
# 1. 저장된 .npy 파일 불러오기
# ==========================================
x_data = np.load("x_data.npy")  # Shape 예: (N, 150, 400, 3)
y_data = np.load("y_data.npy")  # Shape 예: (N, 2)

print(f"Original shapes -> X: {x_data.shape}, Y: {y_data.shape}")

# ==========================================
# 2. 데이터 증강 (좌/우 반전)
# ==========================================
# 이미지 수평 반전 (flipCode = 1)
x_data_fliplr = np.array([cv2.flip(img, 1) for img in x_data], dtype=np.float32)

# Y 데이터 복사 및 Steering 값 반전 (0~1 범위 정규화 상태이므로 1.0 - val)
y_data_fliplr = y_data.copy()
y_data_fliplr[:, 0] = 1.0 - y_data[:, 0]

# ==========================================
# 3. 원본 데이터 + 증강 데이터 통합 및 저장
# ==========================================
# 두 데이터를 축(axis=0)을 기준으로 이어붙임
x_data_aug = np.concatenate([x_data, x_data_fliplr], axis=0)
y_data_aug = np.concatenate([y_data, y_data_fliplr], axis=0)

print(f"Augmented shapes -> X: {x_data_aug.shape}, Y: {y_data_aug.shape}")

# 결과 저장
np.save("x_data_a.npy", x_data_aug)
np.save("y_data_a.npy", y_data_aug)

print("성공적으로 x_data_a.npy, y_data_a.npy 파일에 저장되었습니다.")