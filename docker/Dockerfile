# Use an ARM-compatible Ubuntu base image
FROM dtcooper/raspberrypi-os:python3.10

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHON_VERSION=3.10

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

# Copy the requirements.sh script into the container
# COPY requirements.sh /usr/local/bin/requirements.sh

# Ensure the script is executable
# RUN chmod +x /usr/local/bin/requirements.sh

# Run the script
# RUN /usr/local/bin/requirements.sh

# Clean up unnecessary files
RUN apt-get autoremove -y && apt-get clean
