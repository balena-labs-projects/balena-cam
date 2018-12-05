import sys, timeit
sys.path.append('..')
from PiCameraDevice import CameraDevice

# This test measures how fast we are getting the frames from the camera 
print('+++++++ Video Frame Capture Testing (using picamera)+++++++')

# The CameraDevice object currently uses picamera to get the frames
camera_device = CameraDevice()

c = "camera_device.get_latest_frame()"


# repeat the same 30 frame test 10 times, which is the equivalent of 10 sec of video
rep = 10
times = timeit.repeat(c, number=30, repeat=rep, globals=globals())

# All the values should be less than 1 sec
print('Min: ', min(times), ' seconds')
print('Max: ', max(times), ' seconds')
print('Avg: ', sum(times)/rep, ' seconds')
