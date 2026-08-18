import csv
import os
import time
from datetime import datetime

import cv2
import pygame
from autocar3g.camera import Camera
from autocar3g.driving import Driving
from pynput import keyboard as pynput_keyboard


class BaseController:
  def __init__(self):
    self.current_steering = 0.0
    self.current_throttle = 0

  def start(self):
    pass

  def stop(self):
    pass

  def update(self):
    return self.current_steering, self.current_throttle


class KeyboardController(BaseController):
  def __init__(self):
    super().__init__()
    self.pressed = set()
    self.listener = pynput_keyboard.Listener(
      on_press=self.on_press, on_release=self.on_release
    )

  def start(self):
    self.listener.start()

  def stop(self):
    self.listener.stop()

  def on_press(self, key):
    try:
      k = key.char
      if k in ("w", "a", "s", "d", "x") and k not in self.pressed:
        if k == "w":
          self.current_throttle += 5
        elif k == "a":
          self.current_steering = -0.6
        elif k == "s":
          self.current_throttle -= 5
        elif k == "d":
          self.current_steering = 0.6
        elif k == "x":
          self.current_throttle = 0
        self.pressed.add(k)
    except AttributeError:
      pass

  def on_release(self, key):
    try:
      k = key.char
      if k in self.pressed:
        self.pressed.remove(k)
        if k in ("a", "d"):
          self.current_steering = 0.0
        elif k == "x":
          self.current_throttle = 0
      if k == "q":
        return False
    except AttributeError:
      pass
    return True


class GamepadController(BaseController):
  def __init__(self, steering_deadzone=0.12, throttle_deadzone=0.12):
    super().__init__()
    self.steering_deadzone = steering_deadzone
    self.throttle_deadzone = throttle_deadzone
    self.joystick = None
    self._init_pygame()

  def _init_pygame(self):
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
      self.joystick = pygame.joystick.Joystick(0)
      self.joystick.init()
      print(f"Gamepad detected: {self.joystick.get_name()}")
    else:
      print("No gamepad detected. Starting with neutral controls.")

  def update(self):
    if self.joystick is None:
      return 0.0, 0

    pygame.event.pump()
    steering_axis = self.joystick.get_axis(0)
    throttle_axis = -self.joystick.get_axis(3)

    if abs(steering_axis) < self.steering_deadzone:
      steering_axis = 0.0
    if abs(throttle_axis) < self.throttle_deadzone:
      throttle_axis = 0.0

    self.current_steering = max(-1.0, min(1.0, steering_axis)) * 0.9
    self.current_throttle = int(max(-30, min(30, throttle_axis * 30)))
    return self.current_steering, self.current_throttle


class DataLogger:
  def __init__(self, controller, target_fps=20):
    dt_postfix = datetime.now().strftime("%Y%m%d-%H%M%S")
    self.save_dir = f"collected_data_{dt_postfix}"
    if not os.path.exists(self.save_dir):
      os.makedirs(self.save_dir)

    self.drv = Driving()
    self.cam = Camera()
    self.controller = controller

    self.current_steering = 0.0
    self.current_throttle = 0
    self.control_logs = []
    self.image_logs = []

    self.target_fps = max(10, min(30, int(target_fps)))
    self.running = True
    self.screen = None
    self.font = None
    self.clock = None

    self._init_motors()
    self._init_display()

  def _init_motors(self):
    print("Wait...")
    self.drv.throttle = 0
    time.sleep(0.5)
    self.drv.steering = 0
    time.sleep(0.5)
    print("Motors are initialized.")

  def _init_display(self):
    if isinstance(self.controller, GamepadController):
      self.font = pygame.font.SysFont(None, 24)
      self.clock = pygame.time.Clock()
    else:
      self.font = None
      self.clock = None

  def _handle_events(self):
    if isinstance(self.controller, GamepadController):
      for event in pygame.event.get():
        if event.type == pygame.QUIT or (
          event.type == pygame.KEYDOWN
          and event.key
          in (
            pygame.K_q,
            pygame.K_ESCAPE,
          )
        ):
          self.running = False
    return self.running

  def _apply_controls(self, steering, throttle):
    self.drv.steering = steering
    self.drv.throttle = throttle
    self.current_steering = steering
    self.current_throttle = throttle

  def _render_frame(self, frame):
    if isinstance(self.controller, GamepadController):
      height, width = frame.shape[:2]
      if self.screen is None or self.screen.get_size() != (width, height):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Gamepad Data Logger")

      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      pygame_frame = pygame.image.frombuffer(
        rgb_frame.tobytes(), (width, height), "RGB"
      )
      self.screen.blit(pygame_frame, (0, 0))

      text = self.font.render(
        f"S: {self.current_steering:.2f} | T: {self.current_throttle}",
        True,
        (0, 255, 0),
      )
      self.screen.blit(text, (10, 10))
      pygame.display.update()
    else:
      display_frame = frame.copy()
      cv2.putText(
        display_frame,
        f"S: {self.current_steering:.2f} | T: {self.current_throttle}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
      )
      cv2.imshow("Keyboard Remote Control", display_frame)
      if cv2.waitKey(1) & 0xFF == ord("q"):
        self.running = False

  def run(self):
    self.cam.start()
    self.controller.start()

    print("==================================================")
    print(" 데이터 수집을 시작합니다.")
    print(" 주행을 마치려면 q 또는 ESC를 누르세요.")
    print("==================================================")

    start_time = time.time()

    try:
      while self.running:
        if not self._handle_events():
          break

        frame = self.cam.read()
        if frame is not None:
          steering, throttle = self.controller.update()
          self._apply_controls(steering, throttle)
          self.control_logs.append(
            (time.time(), self.current_steering, self.current_throttle)
          )
          self.image_logs.append((time.time(), frame.copy()))
          self._render_frame(frame)

        if self.clock is not None:
          self.clock.tick(self.target_fps)
        else:
          time.sleep(1.0 / self.target_fps)

    except KeyboardInterrupt:
      pass
    finally:
      self.cleanup(start_time)

  def cleanup(self, start_time):
    if isinstance(self.controller, GamepadController):
      pygame.quit()
    cv2.destroyAllWindows()
    self.controller.stop()
    self.cam.stop()
    self.drv.steering = 0
    self.drv.throttle = 0

    end_time = time.time()
    total_time = end_time - start_time
    total_frames = len(self.image_logs)

    if total_frames == 0:
      print("수집된 영상 프레임이 없습니다.")
      return

    actual_fps = total_frames / total_time if total_time > 0 else self.target_fps
    print(
      f"\n[F] Total running time: {total_time:.2f}sec | Total {total_frames} frames"
    )
    print(f"Actual FPS: {actual_fps:.2f} FPS")
    print("--------------------------------------------------")
    print("Saving... Please wait...")
    self.save_data(actual_fps)

  def save_data(self, actual_fps):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_path = os.path.join(self.save_dir, "driving_video.mp4")

    if self.image_logs:
      frame_height, frame_width = self.image_logs[0][1].shape[:2]
      out = cv2.VideoWriter(video_path, fourcc, actual_fps, (frame_width, frame_height))
      for _, img in self.image_logs:
        out.write(img)
      out.release()

    csv_path = os.path.join(self.save_dir, "driving_log.csv")
    with open(csv_path, mode="w", newline="") as f:
      writer = csv.writer(f)
      writer.writerow(["frame_id", "steering", "throttle"])
      for frame_id, (img_time, _) in enumerate(self.image_logs):
        matched_steer = 0.0
        matched_throttle = 0
        for ctrl_time, steer, throttle in self.control_logs:
          if ctrl_time <= img_time:
            matched_steer = steer
            matched_throttle = throttle
          else:
            break
        writer.writerow([frame_id, matched_steer, matched_throttle])

    print("Saving completed! output files:")
    print(f" - video(mp4): {video_path}")
    print(f" - log(csv)  : {csv_path}")


if __name__ == "__main__":
  logger = DataLogger(controller=KeyboardController(), target_fps=20)
  # logger = DataLogger(controller=GamepadController(), target_fps=20)
  logger.run()
