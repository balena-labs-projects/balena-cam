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

# repeat the same 30 frame test 50 times
rep = 50
times = timeit.repeat(c, number=30, repeat=rep, globals=globals())

print('Min: ', min(times))
print('Max: ', max(times))
print('Avg: ', sum(times)/rep)
