import asyncio
import json
import os
import cv2
import platform
import sys
from time import sleep
import time
from aiohttp import web
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCIceServer, RTCConfiguration
from aiohttp_basicauth import BasicAuthMiddleware
import numpy as np
from constant.camera import resolution_presets
# import picamera

kernel_dil = np.ones((10, 10), np.uint8)
# reference:
# https://stackoverflow.com/questions/60989671/white-blue-balance-error-in-high-resolution-with-opencv-and-picamera-v2
# resoultion_defulat = (640, 480)
# resolution_good = (1280, 704)
# resolution_high = (1920, 1088)
# resolution_nice = (1640, 928)
resolution_picked = resolution_presets["picamera"]["default"]
motion_detected_on = False
use_picamera = True


class FPS():
    def __init__(self):
        self.counter = 0
        self.calculate_frequence = 5  # 5s
        self.start_time = time.time()

    def per_frame(self):
        self.counter = self.counter + 1
        if (time.time() - self.start_time) > self.calculate_frequence:
            print("FPS: ", self.counter /
                  (time.time() - self.start_time))
            self.counter = 0
            self.start_time = time.time()


class CameraDevice():
    def __init__(self, resolution_picked):
        print('Cv2 is used as camera source lib')
        self.cap = cv2.VideoCapture(0)
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        ret, frame = self.cap.read()
        if not ret:
            print('Failed to open default camera. Exiting...')
            sys.exit()
        # self.cap.set(3, 640)# ?why capture in such small space
        # self.cap.set(4, 480)
        # ?why capture in such small space
        self.cap.set(3, resolution_picked[0])
        self.cap.set(4, resolution_picked[1])
        self.f_counter = 0
        self.fps = FPS()
        print("Cam set to resolution: begin===")
        print(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )
        print("===end")

    def rotate(self, frame):
        if flip:
            (h, w) = frame.shape[:2]
            center = (w / 2, h / 2)
            M = cv2.getRotationMatrix2D(center, 180, 1.0)
            frame = cv2.warpAffine(frame, M, (w, h))
            print(frame.shape)
        return frame

    def get_background_mask_3channel(self, frame):
        fgmask = self.get_background_mask(frame)
        # fgmask = self.fgbg.apply(frame)
        img2 = np.zeros_like(frame)
        img2[:, :, 0] = fgmask
        img2[:, :, 1] = fgmask
        img2[:, :, 2] = fgmask
        # print("img2 shape", img2.shape, self.f_counter)
        return img2

    def get_background_mask(self, frame):
        fgmask = self.fgbg.apply(frame)
        print("fgmask shape", fgmask.shape, self.f_counter)

        # dilation
        dilation = cv2.dilate(fgmask, kernel_dil, iterations=1)
        return dilation

        return fgmask

    def print_img_info(self, image, title):
        # print(title)
        # print(image)
        # print(image.shape)
        # print(image.dtype)
        image_max_value_each_channel = image.reshape(
            (image.shape[0] * image.shape[1], 3)).max(axis=0)
        image_min_value_each_channel = image.reshape(
            (image.shape[0] * image.shape[1], 3)).min(axis=0)

        print("{}, shape: {}, dtype: {}, max (in each channels) value: {}, min value: {}".format(
            title, image.shape, image.dtype, image_max_value_each_channel, image_min_value_each_channel))

    async def get_latest_frame(self):
        if motion_detected_on == False:
            # start_time = time.time()
            # self.f_counter = self.f_counter + 1
            # print(self.f_counter)
            self.fps.per_frame()
            ret, frame = self.cap.read()
            await asyncio.sleep(0)
            return frame

        self.f_counter = self.f_counter + 1
        ret, frame = self.cap.read()

        # print("frame shape", frame.shape)
        # bg_mask = self.get_background_mask_3channel(frame)
        bg_mask = self.get_background_mask_3channel(frame)
        ret, thresh1 = cv2.threshold(
            bg_mask, 128, 255, cv2.THRESH_BINARY)

        alpha = thresh1 / 255
        # alpha = np.ones(frame.shape, np.uint8)
        # Force the left side all non-pass
        # alpha[:, 0:frame.shape[1] // 2] = (0, 0, 0)

        # Force the left side all pass
        alpha[:, frame.shape[1] // 2:] = (1, 1, 1)

        alpha_unit8 = alpha.astype(np.uint8)

        self.print_img_info(bg_mask, "bg_mask")
        self.print_img_info(thresh1, "thresh1")
        self.print_img_info(alpha, "alpha")
        self.print_img_info(alpha_unit8, "alpha_unit8")

        fg = cv2.multiply(alpha_unit8, frame)

        # fg = cv2.bitwise_and(frame, frame, mask=bg_mask)
        # fgmask = frame
        await asyncio.sleep(0)

        if self.f_counter % 50 >= 25:
            return self.rotate(frame)
        return self.rotate(fg)

    async def get_jpeg_frame(self):
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
        frame = await self.get_latest_frame()
        frame, encimg = cv2.imencode('.jpg', frame, encode_param)
        return encimg.tostring()


class PiCameraDevice():
    def __init__(self, resolution_picked):
        print('Picamera is used as camera source')
        # resolution = (640, 480) # fps should be like 15
        # resolution = (1640, 1232) # has problem
        # resolution = (1280, 720)
        # resolution = (1920, 1088) # work for only a period
        # resolution = (3280, 2464)
        framerate = 24
        from utils.pivideostream import PiVideoStream
        self.stream = PiVideoStream(resolution=resolution_picked,
                                    framerate=framerate)
        self.stream.start()

        self.fps = FPS()
        print("Cam set to resolution: begin===")
        print(self.stream.camera.resolution
              )
        print("===end")

    async def get_latest_frame(self):
        self.fps.per_frame()
        frame = self.stream.read()
        return frame

    async def get_jpeg_frame(self):
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
        frame = await self.get_latest_frame()
        frame, encimg = cv2.imencode('.jpg', frame, encode_param)
        return encimg.tostring()


class PeerConnectionFactory():
    def __init__(self):
        self.config = {'sdpSemantics': 'unified-plan'}
        self.STUN_SERVER = None
        self.TURN_SERVER = None
        self.TURN_USERNAME = None
        self.TURN_PASSWORD = None
        if all(k in os.environ for k in ('STUN_SERVER',
                                         'TURN_SERVER', 'TURN_USERNAME', 'TURN_PASSWORD')):
            print(
                'WebRTC connections will use your custom ICE Servers (STUN / TURN).')
            self.STUN_SERVER = os.environ['STUN_SERVER']
            self.TURN_SERVER = os.environ['TURN_SERVER']
            self.TURN_USERNAME = os.environ['TURN_USERNAME']
            self.TURN_PASSWORD = os.environ['TURN_PASSWORD']
            iceServers = [
                {
                    'urls': self.STUN_SERVER
                },
                {
                    'urls': self.TURN_SERVER,
                    'credential': self.TURN_PASSWORD,
                    'username': self.TURN_USERNAME
                }
            ]
            self.config['iceServers'] = iceServers

    def create_peer_connection(self):
        if self.TURN_SERVER is not None:
            iceServers = []
            iceServers.append(RTCIceServer(self.STUN_SERVER))
            iceServers.append(
                RTCIceServer(
                    self.TURN_SERVER,
                    username=self.TURN_USERNAME,
                    credential=self.TURN_PASSWORD))
            return RTCPeerConnection(RTCConfiguration(iceServers))
        return RTCPeerConnection()

    def get_ice_config(self):
        return json.dumps(self.config)


class RTCVideoStream(VideoStreamTrack):
    def __init__(self, camera_device):
        super().__init__()
        self.camera_device = camera_device
        self.data_bgr = None

    async def recv(self):
        self.data_bgr = await self.camera_device.get_latest_frame()
        frame = VideoFrame.from_ndarray(self.data_bgr, format='bgr24')
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        return frame


async def index(request):
    content = open(
        os.path.join(
            ROOT,
            'client/index.html'),
        'r').read()
    return web.Response(content_type='text/html', text=content)


async def stylesheet(request):
    content = open(os.path.join(ROOT, 'client/style.css'), 'r').read()
    return web.Response(content_type='text/css', text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, 'client/client.js'), 'r').read()
    return web.Response(
        content_type='application/javascript', text=content)


async def balena(request):
    content = open(
        os.path.join(
            ROOT,
            'client/balena-cam.svg'),
        'r').read()
    return web.Response(
        content_type='image/svg+xml', text=content)


async def balena_logo(request):
    content = open(
        os.path.join(
            ROOT,
            'client/balena-logo.svg'),
        'r').read()
    return web.Response(
        content_type='image/svg+xml', text=content)


async def favicon(request):
    return web.FileResponse(os.path.join(ROOT, 'client/favicon.png'))


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type'])
    pc = pc_factory.create_peer_connection()
    pcs.add(pc)
    # Add local media
    local_video = RTCVideoStream(camera_device)
    pc.addTrack(local_video)

    @ pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == 'failed':
            await pc.close()
            pcs.discard(pc)
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.Response(
        content_type='application/json',
        text=json.dumps({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }))


async def mjpeg_handler(request):
    boundary = "frame"
    response = web.StreamResponse(status=200, reason='OK', headers={
        'Content-Type': 'multipart/x-mixed-replace; '
                        'boundary=%s' % boundary,
    })
    await response.prepare(request)
    while True:
        data = await camera_device.get_jpeg_frame()
        # this means that the maximum FPS is 5
        await asyncio.sleep(0.1)  # ????
        await response.write(
            '--{}\r\n'.format(boundary).encode('utf-8'))
        await response.write(b'Content-Type: image/jpeg\r\n')
        await response.write('Content-Length: {}\r\n'.format(
            len(data)).encode('utf-8'))
        await response.write(b"\r\n")
        await response.write(data)
        await response.write(b"\r\n")
    return response


async def config(request):
    return web.Response(
        content_type='application/json',
        text=pc_factory.get_ice_config()
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)


def checkDeviceReadiness():
    if not os.path.exists(
            '/dev/video0') and platform.system() == 'Linux':
        print('Video device is not ready')
        print('Trying to load bcm2835-v4l2 driver...')
        os.system('bash -c "modprobe bcm2835-v4l2"')
        sleep(1)
        sys.exit()
    else:
        print('Video device is ready')


if __name__ == '__main__':
    checkDeviceReadiness()
    print("Camera detected!!!")

    ROOT = os.path.dirname(__file__)
    pcs = set()
    if use_picamera == True:
        camera_device = PiCameraDevice(resolution_picked)
    else:
        camera_device = CameraDevice(resolution_picked)

    flip = False
    try:
        if os.environ['rotation'] == '1':
            flip = True
    except BaseException:
        pass

    auth = []
    if 'username' in os.environ and 'password' in os.environ:
        print('\n#############################################################')
        print('Authorization is enabled.')
        print('Your balenaCam is password protected.')
        print('#############################################################\n')
        auth.append(
            BasicAuthMiddleware(
                username=os.environ['username'],
                password=os.environ['password']))
    else:
        print('\n#############################################################')
        print('Authorization is disabled.')
        print('Anyone can access your balenaCam, using the device\'s URL!')
        print(
            'Set the username and password environment variables \nto enable authorization.')
        print(
            'For more info visit: \nhttps://github.com/balena-io-playground/balena-cam')
        print('#############################################################\n')

    # Factory to create peerConnections depending on the iceServers
    # set by user
    pc_factory = PeerConnectionFactory()

    app = web.Application(middlewares=auth)
    app.on_shutdown.append(on_shutdown)
    app.router.add_get('/', index)
    app.router.add_get('/favicon.png', favicon)
    app.router.add_get('/balena-logo.svg', balena_logo)
    app.router.add_get('/balena-cam.svg', balena)
    app.router.add_get('/client.js', javascript)
    app.router.add_get('/style.css', stylesheet)
    app.router.add_post('/offer', offer)
    app.router.add_get('/mjpeg', mjpeg_handler)
    app.router.add_get('/ice-config', config)
    web.run_app(app, port=80)
