import time

import cv2
from autocar3g.AI import Track_Follow_TF
from autocar3g.camera import Camera
from autocar3g.driving import Driving

cam = Camera()
cam.start()

car = Driving()
# throttle = 0

TF = Track_Follow_TF(cam)
TF.load_model("Track_Model_forward.h5")

while True:
  try:
    ret_tf = TF.run()
    if ret_tf is not None:
      print(f"예측값: {ret_tf}", end="\r")
      steering = (ret_tf["x"] * 2) - 1
      throttle = int(ret_tf["y"] * 100)
      car.set_drive(steering, throttle)
      time.sleep(0.04)
  except KeyboardInterrupt:
    car.set_drive(0.0, 0)
    break
