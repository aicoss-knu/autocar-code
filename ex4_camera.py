import cv2
from autocar3g.camera import Camera

cam = Camera()
cam.start()
print("Press 'q' to exit.")

while True:
  cv2.imshow("img", cam.read())
  if cv2.waitKey(1) & 0xFF == ord("q"):
    break
cv2.destroyAllWindows()
