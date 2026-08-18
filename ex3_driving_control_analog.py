import time

import pygame
from autocar3g.driving import Driving


class GamepadDrive:
  def __init__(self, steering_axis=0, throttle_axis=3, deadzone=0.05):
    self.drv = Driving()
    self.steering_axis = steering_axis
    self.throttle_axis = throttle_axis
    self.deadzone = deadzone
    self.joy = None
    self._init_gamepad()

    # 마지막으로 전송한 값을 기록해 중복 전송 방지
    self.last_steering = None
    self.last_throttle = None

    self.drv.set_drive(0.0, 0)

  def _init_gamepad(self):
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
      raise RuntimeError("Gamepad not detected.")

    self.joy = pygame.joystick.Joystick(0)
    self.joy.init()
    print(f"Gamepad detected: {self.joy.get_name()}")

  def _clamp(self, value, low, high):
    return max(low, min(high, value))

  def update(self):
    pygame.event.pump()

    steering = self.joy.get_axis(self.steering_axis)
    throttle = -self.joy.get_axis(self.throttle_axis)

    if abs(steering) < self.deadzone:
      steering = 0.0
    if abs(throttle) < self.deadzone:
      throttle = 0.0

    steering = self._clamp(steering, -0.9, 0.9)
    throttle = self._clamp(throttle, -1.0, 1.0)

    steering_cmd = round(steering, 3)
    throttle_cmd = int(round(throttle * 20))
    print(f"steering={steering_cmd:+4.2f} throttle={throttle_cmd:+04d}", end="\r")

    # 값이 이전과 달라졌을 때만 MQTT 패킷 전송 (네트워크 병목 방지)
    if steering_cmd != self.last_steering or throttle_cmd != self.last_throttle:
      self.drv.set_drive(steering_cmd, throttle_cmd)
      self.last_steering = steering_cmd
      self.last_throttle = throttle_cmd

    return steering_cmd, throttle_cmd

  def close(self):
    self.drv.set_drive(0.0, 0)

    time.sleep(0.05)
    if hasattr(self.drv, "disconnect"):
      self.drv.disconnect()
    pygame.quit()


def main():
  controller = GamepadDrive()
  print("Gamepad control started. Press Ctrl+C to stop.")

  try:
    while True:
      steering, throttle = controller.update()
      # 권장 주기: 0.03 ~ 0.05 (초당 20~30회 전송이 무선 제어에 가장 적합)
      time.sleep(0.03)
  except KeyboardInterrupt:
    print("Stop driving.")
  finally:
    controller.close()


if __name__ == "__main__":
  main()

