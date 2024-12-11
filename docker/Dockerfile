# Use a lightweight base image for Raspberry Pi (Debian-based)
# FROM arm64v8/python:3.10-slim-buster
FROM python:3.10-slim-buster

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install prerequisites
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    wget \
    unzip \
    git \
    libopencv-dev \
    libtclap-dev \
    libmagic-dev \
    python3-pip \
    && apt-get clean

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install pandas paho-mqtt opencv-python

# Set custom installation paths
ENV OPENCV_INSTALL_PATH=/opt/opencv_install
ENV DARKNET_INSTALL_PATH=/opt/darknet_install
ENV DARKHELP_INSTALL_PATH=/opt/darkhelp_install

# Install OpenCV
RUN mkdir -p ${OPENCV_INSTALL_PATH} \
    && cd ${OPENCV_INSTALL_PATH} \
    && wget -O opencv.zip https://github.com/opencv/opencv/archive/4.x.zip \
    && unzip opencv.zip -d ${OPENCV_INSTALL_PATH} \
    && mkdir -p ${OPENCV_INSTALL_PATH}/build \
    && cd ${OPENCV_INSTALL_PATH}/build \
    && cmake -DCMAKE_INSTALL_PREFIX=${OPENCV_INSTALL_PATH} ../opencv-4.x \
    && cmake --build . \
    && cmake --install . --prefix ${OPENCV_INSTALL_PATH}

# Install Darknet
RUN mkdir -p ${DARKNET_INSTALL_PATH}/src \
    && cd ${DARKNET_INSTALL_PATH}/src \
    && git clone https://github.com/hank-ai/darknet \
    && cd darknet \
    && mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${DARKNET_INSTALL_PATH} .. \
    && make -j$(nproc) \
    && make package \
    && dpkg -i darknet-*.deb

# Install DarkHelp
RUN mkdir -p ${DARKHELP_INSTALL_PATH}/src \
    && cd ${DARKHELP_INSTALL_PATH}/src \
    && git clone https://github.com/stephanecharette/DarkHelp.git \
    && cd DarkHelp \
    && mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${DARKHELP_INSTALL_PATH} .. \
    && make -j$(nproc) \
    && make package \
    && dpkg -i darkhelp*.deb

# Clean up unnecessary files
RUN apt-get autoremove -y && apt-get clean


