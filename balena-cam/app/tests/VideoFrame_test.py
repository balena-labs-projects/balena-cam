import sys, timeit
import numpy as np
from av import VideoFrame
sys.path.append('..')
from server import CameraDevice

print('+++++++ VideoFrame Generation Testing +++++++')

camera_device = CameraDevice()
frame = camera_device.get_latest_frame()
frame.dump('frame.dat')
loaded_frame = np.load('frame.dat')

c = "VideoFrame.from_ndarray(loaded_frame, format='bgr24')"

# repeat the same 30 frame test 900 times, which is the equivalent of 15 min of video
rep = 900
times = timeit.repeat(c, number=30, repeat=rep, globals=globals())

print('Min: ', min(times), ' second')
print('Max: ', max(times), ' second')
print('Avg: ', sum(times)/rep, ' second')
