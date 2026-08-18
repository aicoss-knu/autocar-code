import numpy as np
import tensorflow as tf
from tensorflow import keras

# ==========================================
# 1. 데이터 로드 (.npy 파일 읽기)
# ==========================================
x_data = np.load("x_data.npy")
y_data = np.load("y_data.npy")

print(f"데이터 로드 완료 - X: {x_data.shape}, y: {y_data.shape}")

# ==========================================
# 2. 모델 정의
# ==========================================
input1 = keras.layers.Input(shape=(150, 400, 3))

conv1 = keras.layers.Conv2D(
    filters=16, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish"
)(input1)
norm1 = keras.layers.BatchNormalization()(conv1)
pool1 = keras.layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(norm1)

conv2 = keras.layers.Conv2D(
    filters=32, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish"
)(pool1)
norm2 = keras.layers.BatchNormalization()(conv2)
conv3 = keras.layers.Conv2D(
    filters=32, kernel_size=(3, 3), strides=(1, 1), padding="same", activation="swish"
)(norm2)
norm3 = keras.layers.BatchNormalization()(conv3)
add1 = keras.layers.Add()([norm2, norm3])

conv4 = keras.layers.Conv2D(
    filters=64, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish"
)(add1)
norm4 = keras.layers.BatchNormalization()(conv4)
conv5 = keras.layers.Conv2D(
    filters=64, kernel_size=(3, 3), strides=(1, 1), padding="same", activation="swish"
)(norm4)
norm5 = keras.layers.BatchNormalization()(conv5)
add2 = keras.layers.Add()([norm4, norm5])

conv6 = keras.layers.Conv2D(
    filters=128, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish"
)(add2)
norm6 = keras.layers.BatchNormalization()(conv6)
conv7 = keras.layers.Conv2D(
    filters=128, kernel_size=(3, 3), strides=(1, 1), padding="same", activation="swish"
)(norm6)
norm7 = keras.layers.BatchNormalization()(conv7)
add3 = keras.layers.Add()([norm6, norm7])

conv8 = keras.layers.Conv2D(
    filters=256, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish"
)(add3)
norm8 = keras.layers.BatchNormalization()(conv8)
conv9 = keras.layers.Conv2D(
    filters=512, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish"
)(norm8)
norm9 = keras.layers.BatchNormalization()(conv9)

flat1 = keras.layers.Flatten()(norm9)
dense1 = keras.layers.Dense(128, activation="swish")(flat1)
norm10 = keras.layers.BatchNormalization()(dense1)
dense2 = keras.layers.Dense(64, activation="swish")(norm10)
norm11 = keras.layers.BatchNormalization()(dense2)
dense3 = keras.layers.Dense(64, activation="swish")(norm11)
norm12 = keras.layers.BatchNormalization()(dense3)

# 출력층: 2개의 연속값 (Steering, Throttle) -> 범위 0~1
dense4 = keras.layers.Dense(2, activation="sigmoid", name="driving_outputs")(norm12)

model = keras.models.Model(inputs=input1, outputs=dense4)

# ==========================================
# 3. 모델 학습 (fit) 및 저장
# ==========================================
adam = keras.optimizers.Adam(learning_rate=1e-3)
model.compile(optimizer=adam, loss="mse", metrics=["mae"])

es = keras.callbacks.EarlyStopping(
    monitor="val_loss", mode="min", patience=20, min_delta=1e-4, restore_best_weights=True
)

# EarlyStopping 콜백을 포함하여 학습 진행
model.fit(
    x=x_data,
    y=y_data,
    batch_size=32,
    epochs=20,
    validation_split=0.1,
    callbacks=[es]
)

model.save("Track_Model_forward.h5")
print("모델 저장 완료: Track_Model_forward.h5")