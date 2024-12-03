# Use an ARM-compatible Ubuntu image as the base
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3

# Update the package list and install necessary OS packages
RUN apt-get update && apt-get -y install --no-install-recommends \
    curl \
    git \
    python3 \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install \
    autogen \
    autogen-core==0.4.0.dev7 \
    cryptography \
    PyJWT \
    rsa \
    autogen-core[openai]==0.4.0.dev7 \
    autogen-ext==0.4.0.dev7

RUN pip install grpcio grpcio-tools

# Verify Python installation and installed packages
RUN python3 --version && python3 -m pip show autogen-core

# Comments for running and building the image
# Build: docker build -f Dockerfile -t autogen_base_img .
# Run: docker run -it -v /Users/nateanecone/projects/AgentSec:/home/autogen/autogen/myapp autogen_base_img:latest python3 /home/autogen/autogen/myapp/main.py