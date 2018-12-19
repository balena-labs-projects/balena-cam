import timeit, cv2

class CameraDevice():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    def get_latest_frame(self):
        ret, frame = self.cap.read()
        return frame

if __name__ == '__main__':
    # This test measures how fast we are getting the frames from the camera 
    print('+++++++ Frame Capture Testing +++++++')
    camera_device = CameraDevice()
    c = "camera_device.get_latest_frame()"
    # repeat the same 30 frame test 10 times, which is the equivalent of 10 sec of video
    rep = 10
    times = timeit.repeat(c, number=30, repeat=rep, globals=globals())
    # All the values should be less than 1 sec
    print('Min: ', min(times), ' seconds')
    print('Max: ', max(times), ' seconds')
    print('Avg: ', sum(times)/rep, ' seconds')
