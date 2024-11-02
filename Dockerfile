# Use an ARM-compatible Ubuntu image as the base
FROM ubuntu:22.04

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl git python3 python3-pip && pip3 install autogen

# docker build -f Dockerfile -t autogen_base_img .
# docker run -it -v /Users/nateanecone/projects/AgentSec:/home/autogen/autogen/myapp autogen_base_img:latest python3 /home/autogen/autogen/myapp/main.py


