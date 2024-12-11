# Use a lightweight base image for Raspberry Pi (Debian-based)
# FROM arm64v8/python:3.10-slim-buster
FROM python:3.10-slim-buster

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic dependencies required to run the script
RUN apt-get update && apt-get install -y \
    sudo \
    wget \
    unzip \
    git \
    build-essential \
    && apt-get clean

# Copy the requirements.sh script into the container
COPY requirements.sh /usr/local/bin/requirements.sh

# Ensure the script is executable
RUN chmod +x /usr/local/bin/requirements.sh

# Run the script
RUN /usr/local/bin/requirements.sh

# Clean up unnecessary files
RUN apt-get autoremove -y && apt-get clean
