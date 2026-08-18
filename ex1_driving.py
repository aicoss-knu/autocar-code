import time

from autocar3g.driving import Driving

try:
  drv = Driving()

  drv.steering = -0.33
  drv.throttle =  5
  time.sleep(1)

  drv.set_drive(steering=0.5, throttle=10)
  time.sleep(0.5)

  drv.set_drive(steering=0.25, throttle=110)
  time.sleep(0.5)

except Exception as e:
  print(f"An error occurred: {e}")
finally:
  drv.set_drive(steering=0.0, throttle=0)
  drv.disconnect()
# # time.sleep(0.5)

# input("Press Enter to stop...")


# with Driving() as drv:
#   try:
#     drv.steering, drv.throttle = -0.33, 10
#     time.sleep(1)

#     drv.set_drive(steering=0.5, throttle=10)
#     time.sleep(0.5)

#     drv.set_drive(steering=0.25, throttle=110)
#     time.sleep(0.5)

#     # drv.set_drive(steering=0.0, throttle=0)

#   except Exception as e:
#     print(f"An error occurred: {e}")



# with Driving() as drv:
#   try:
#     st = 0.1
#     for k in range(9):
#       drv.set_drive(steering=st, throttle=0)
#       st += 0.1
#       time.sleep(0.5)
#   except Exception as e:
#     print(f"An error occurred: {e}")
