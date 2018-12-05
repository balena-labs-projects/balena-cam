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

# repeat the same 30 frame test 10 times, which is the equivalent of 10 sec of video
rep = 10
times = timeit.repeat(c, number=30, repeat=rep, globals=globals())

print('Min: ', min(times), ' seconds')
print('Max: ', max(times), ' seconds')
print('Avg: ', sum(times)/rep, ' seconds')
