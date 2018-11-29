#!/bin/bash
pip3 install aiohttp aiortc==0.9.11 opencv-python --index-url https://www.piwheels.org/simple
python3 server.py
