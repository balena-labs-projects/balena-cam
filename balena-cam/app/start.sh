#!/bin/bash
cd tests
python3 FrameCapture_test.py
python3 VideoFrame_test.py
cd ..
python3 server.py
