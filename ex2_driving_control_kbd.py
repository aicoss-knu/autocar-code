import time

from autocar3g.driving import Driving
from pynput import keyboard


class TestDrive:
  def __init__(self):
    self.drv = Driving()
    self.time_tag = time.time()
    self.pressed = set()
    self.listener = keyboard.Listener(
      on_press=self.on_press,
      on_release=self.on_release,
    )
    self._init_motors()
    print("Press w/s to increase/decrease throttle, a/d to steer left/right, x to stop, q to quit.")

  def _init_motors(self):
    self.drv.set_drive(0.0, 0)
    self.listener.start()

  def on_press(self, key):
    try:
      k = key.char
    except AttributeError:
      return

    if k in ("w", "a", "s", "d", "x") and k not in self.pressed:
      if k == "w":
        self.drv.set_drive(self.drv.steering, 10)
      elif k == "a":
        self.drv.set_drive(-0.9, self.drv.throttle)
      elif k == "s":
        self.drv.set_drive(self.drv.steering, -10)
      elif k == "d":
        self.drv.set_drive(0.9, self.drv.throttle)
      elif k == "x":
        self.drv.set_drive(self.drv.steering, 0)
      self.pressed.add(k)

  def on_release(self, key):
    try:
      k = key.char
    except AttributeError:
      return

    if k in self.pressed:
      self.pressed.remove(k)
      if k in ("w", "s", "x"):
        self.drv.set_drive(self.drv.steering, 0)
      elif k in ("a", "d"):
        self.drv.set_drive(0.0, self.drv.throttle)

    if k == "q":
      self.listener.stop()
      self.drv.set_drive(0.0, 0)
      return False

  def run(self):
    self.listener.join()


def main():
  drive = TestDrive()
  try:
    drive.run()
  except KeyboardInterrupt:
    drive.drv.set_drive(0.0, 0)
    drive.listener.stop()


if __name__ == "__main__":
  main()
