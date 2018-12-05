import sys, timeit
sys.path.append('..')
from server import CameraDevice

# This test measures how fast we are getting the frames from the camera 
print('+++++++ Frame Capture Testing +++++++')

# The CameraDevice object currently uses cv2 to get the frames
camera_device = CameraDevice()

c = "camera_device.get_latest_frame()"


# repeat the same 30 frame test 900 times, which is the equivalent of 10 sec of video
rep = 10
times = timeit.repeat(c, number=30, repeat=rep, globals=globals())

# All the values should be less than 1 sec
print('Min: ', min(times), ' second')
print('Max: ', max(times), ' second')
print('Avg: ', sum(times)/rep, ' second')
