#!/bin/bash
pip3 install aiohttp aiortc==0.9.11 opencv-python --index-url https://www.piwheels.org/simple
cd ./tests
python3 VideoFrame_test.py
python3 FrameCapture_test.py
python3 PiCameraDevice_test.py
cd ..
python3 server.py
