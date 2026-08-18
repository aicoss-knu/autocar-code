import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

video_path = "driving_video.mp4"
csv_path = "driving_log.csv"

df = pd.read_csv(csv_path)

# Video 10프레임 간격 추출
STEP = 10
img_list = []
label_list = []

cap = cv2.VideoCapture(video_path, cv2.CAP_MSMF)  # cv2.CAP_MSMF: Windows only
frame_idx = 0

print("비디오 프레임 추출 중...")
pbar = tqdm(total=len(df) // STEP)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 10프레임 마다 1개씩만 선택
    if frame_idx % STEP == 0 and frame_idx < len(df):
        row = df.iloc[frame_idx]
        steering = float(row["steering"])
        throttle = float(row["throttle"])

        # 이미지 Crop (120:270)
        cropped_img = frame[120:270, :]
        img_list.append(cropped_img)

        # 레이블 정규화
        norm_steering = (steering + 1.0) / 2.0
        norm_throttle = throttle / 100.0
        label_list.append([norm_steering, norm_throttle])

        pbar.update(1)

    frame_idx += 1

cap.release()
pbar.close()

X_data = np.array(img_list, dtype=np.float32)
y_data = np.array(label_list, dtype=np.float32)

print(f"추출 완료 - 이미지: {X_data.shape}, 레이블: {y_data.shape}")

np.save("x_data.npy", X_data)
np.save("y_data.npy", y_data)