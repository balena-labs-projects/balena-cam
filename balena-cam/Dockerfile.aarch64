FROM balenalib/raspberrypi3-debian:stretch-20190612

# Install dependencies
RUN apt-get update && \
  apt-get install -yq \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    gstreamer-1.0 \
    v4l-utils \
    libopus-dev \
    libvpx-dev \
    libsrtp2-dev \
    libopencv-dev \
    libatlas3-base \
    libatlas-base-dev \
    libjasper-dev \
    libilmbase12 \
    libopenexr22 \
    libavformat-dev \
    libswscale-dev \
    libqtgui4 \
    libqt4-test \
    libavdevice-dev \
    libavfilter-dev \
    libavcodec-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable the v4l2 driver for the Raspberry Pi camera
#RUN printf "bcm2835-v4l2\n" >> /etc/modules
RUN pip3 install --upgrade pip 
RUN pip3 install async-timeout av==6.1.0
RUN pip3 install aiohttp aiohttp_basicauth==0.1.3 aioice==0.6.10 aiortc==0.9.11 numpy==1.15.4 opencv-python==3.4.4.19 --index-url https://www.piwheels.org/simple

WORKDIR /usr/src/app

COPY ./app/ /usr/src/app/

CMD ["python3", "/usr/src/app/server.py"]
