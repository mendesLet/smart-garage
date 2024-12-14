#!/bin/bash

# Clear and concise output for better readability
echo -e "\033[1;34mStarting to build dependencies...\033[0m"

# Install required Python dependencies
python3 -m pip install --no-cache-dir pandas paho-mqtt easyocr
apt-get install python3-opencv libgtk2.0-dev pkg-config

# Notify about OpenCV installation
echo -e "\033[1;32mInstalling OpenCV from root...\033[0m"

# Install minimal prerequisites (Ubuntu 18.04 as reference)
echo -e "\033[1;34mInstalling minimal prerequisites for OpenCV...\033[0m"
apt update && apt install -y cmake g++ wget unzip


# Set custom installation path
OPENCV_INSTALL_PATH=$HOME/opencv_install
echo -e "\033[1;34mSetting OpenCV installation path to $OPENCV_INSTALL_PATH...\033[0m"
mkdir -p $OPENCV_INSTALL_PATH

# Download and unpack sources to the installation path
echo -e "\033[1;34mDownloading and unpacking OpenCV sources to $OPENCV_INSTALL_PATH...\033[0m"
wget -O $OPENCV_INSTALL_PATH/opencv.zip https://github.com/opencv/opencv/archive/4.x.zip
unzip $OPENCV_INSTALL_PATH/opencv.zip -d $OPENCV_INSTALL_PATH

# Navigate to the build directory within the installation path
echo -e "\033[1;34mCreating build directory...\033[0m"
mkdir -p $OPENCV_INSTALL_PATH/build && cd $OPENCV_INSTALL_PATH/build

# Configure with custom installation path
echo -e "\033[1;34mConfiguring OpenCV build...\033[0m"
cmake -DCMAKE_INSTALL_PREFIX=$OPENCV_INSTALL_PATH ../opencv-4.x

# Build
echo -e "\033[1;34mBuilding OpenCV...\033[0m"
cmake --build . -- -j2

# Install to custom path
echo -e "\033[1;34mInstalling OpenCV to $OPENCV_INSTALL_PATH...\033[0m"
cmake --install . --prefix $OPENCV_INSTALL_PATH

# Notify about Darknet installation
echo -e "\033[1;32mInstalling Darknet...\033[0m"

# Install minimal prerequisites for Darknet
apt-get install -y build-essential git libopencv-dev

# Remove any existing cmake installation and reinstall via snap
# export PATH=/snap/bin:$PATH

# Set custom installation path for Darknet
DARKNET_INSTALL_PATH=$HOME/darknet_install
echo -e "\033[1;34mSetting Darknet installation path to $DARKNET_INSTALL_PATH...\033[0m"

# Clone Darknet source and build
mkdir -p $DARKNET_INSTALL_PATH/src
cd $DARKNET_INSTALL_PATH/src
git clone https://github.com/hank-ai/darknet
cd darknet
mkdir build && cd build

# Configure and build Darknet
echo -e "\033[1;34mConfiguring and building Darknet...\033[0m"
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$DARKHELP_INSTALL_PATH ..
make -j2

# Create Darknet package and install it
echo -e "\033[1;34mPackaging and installing Darknet...\033[0m"
make package
dpkg -i darknet-*.deb

# Notify about DarkHelp installation
echo -e "\033[1;32mInstalling DarkHelp...\033[0m"

# Install minimal prerequisites for DarkHelp
apt-get install -y build-essential libtclap-dev libmagic-dev libopencv-dev

# Set custom installation path for DarkHelp
DARKHELP_INSTALL_PATH=$HOME/darkhelp_install
echo -e "\033[1;34mSetting DarkHelp installation path to $DARKHELP_INSTALL_PATH...\033[0m"

# Clone DarkHelp source and build
mkdir -p $DARKHELP_INSTALL_PATH/src
cd $DARKHELP_INSTALL_PATH/src
git clone https://github.com/stephanecharette/DarkHelp.git
cd DarkHelp
mkdir build && cd build

# Ensure cmake is available
export PATH=/snap/bin:$PATH

# Configure and build DarkHelp
echo -e "\033[1;34mConfiguring and building DarkHelp...\033[0m"
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$DARKHELP_INSTALL_PATH ..
make -j2

# Create DarkHelp package and install it
echo -e "\033[1;34mPackaging and installing DarkHelp...\033[0m"
make package
dpkg -i darkhelp*.deb

# Completion message
echo -e "\033[1;32mInstallation of OpenCV, Darknet, and DarkHelp completed successfully!\033[0m"
