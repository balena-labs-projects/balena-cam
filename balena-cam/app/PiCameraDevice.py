from picamera.array import PiRGBArray
from picamera import PiCamera
from av import VideoFrame

class CameraDevice():
    def __init__(self):
        self.camera = PiCamera(sensor_mode=7)
        self.camera.framerate = 24
        self.camera.resolution = (640, 480)
        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))

    def get_latest_frame(self):
        self.rawCapture.truncate(0)
        self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        video_frame = VideoFrame.from_ndarray(self.rawCapture.array, format='bgr24')
        return video_frame
