# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

FROM amazonlinux:2

# Replace the args to lock to a specific version
ARG GREENGRASS_RELEASE_VERSION=2.5.4
ARG GREENGRASS_ZIP_FILE=greengrass-${GREENGRASS_RELEASE_VERSION}.zip
ARG GREENGRASS_RELEASE_URI=https://d2s8p88vqu9w66.cloudfront.net/releases/${GREENGRASS_ZIP_FILE}
ARG GREENGRASS_ZIP_SHA256=greengrass.zip.sha256

# Author
LABEL maintainer="AWS IoT Greengrass"
# Greengrass Version
LABEL greengrass-version=${GREENGRASS_RELEASE_VERSION}

# Set up Greengrass v2 execution parameters
# TINI_KILL_PROCESS_GROUP allows forwarding SIGTERM to all PIDs in the PID group so Greengrass can exit gracefully
ENV TINI_KILL_PROCESS_GROUP=1 \ 
    GGC_ROOT_PATH=/greengrass/v2 \
    PROVISION=false \
    AWS_REGION=us-east-1 \
    THING_NAME=default_thing_name \
    THING_GROUP_NAME=default_thing_group_name \
    TES_ROLE_NAME=default_tes_role_name \
    TES_ROLE_ALIAS_NAME=default_tes_role_alias_name \
    COMPONENT_DEFAULT_USER=default_component_user \
    DEPLOY_DEV_TOOLS=false \
    INIT_CONFIG=default_init_config \
    TRUSTED_PLUGIN=default_trusted_plugin_path \
    THING_POLICY_NAME=default_thing_policy_name \
    EDGE_CONNECTOR_RESOURCE_PROVISION=false
RUN env


# install packages
RUN yum update -y && \
    yum install -y \
    python37 \
    tar \
    wget \
    sudo \
    procps \
    which \
    flex \
    bison \
    gcc \
    gcc-c++ \
    python3 \
    git \
    java-11-amazon-corretto \
    unzip && \
    amazon-linux-extras enable python3.8 && yum install -y python3.8 java-11-amazon-corretto-headless

# install meson and ninja
RUN pip3 install --user meson
RUN curl -L -O https://github.com/ninja-build/ninja/releases/download/v1.11.0/ninja-linux.zip && \
    unzip ninja-linux.zip -d $HOME/.local/bin && \
    rm ninja-linux.zip
ENV PATH "${PATH}:/root/.local/bin"

# get GStreamer and build shared libraries
WORKDIR /opt/gst/
RUN git clone https://gitlab.freedesktop.org/gstreamer/gstreamer.git --branch 1.20.2
RUN cd gstreamer && \
    meson --buildtype=release --strip -Dbase=enabled -Dgood=enabled -Dbad=enabled --prefix=/opt/gst build && \
    ninja -C build && \
    meson install -C build && \
    cd .. && \

# add GStreamer libraries to the loading path
RUN echo "/opt/gst/lib64" >> /etc/ld.so.conf.d/gst.conf && ldconfig

# Entrypoint script to install and run Greengrass
WORKDIR /
COPY "greengrass-entrypoint.sh" /
COPY "${GREENGRASS_ZIP_SHA256}" /

RUN wget $GREENGRASS_RELEASE_URI && sha256sum -c ${GREENGRASS_ZIP_SHA256} && \
    rm -rf /var/cache/yum && \
    chmod +x /greengrass-entrypoint.sh && \
    mkdir -p /opt/greengrassv2 $GGC_ROOT_PATH && unzip $GREENGRASS_ZIP_FILE -d /opt/greengrassv2 && rm $GREENGRASS_ZIP_FILE && rm $GREENGRASS_ZIP_SHA256


# modify /etc/sudoers
COPY "modify-sudoers.sh" /
RUN chmod +x /modify-sudoers.sh
RUN /modify-sudoers.sh


COPY "deployment.py" /
COPY "deployment.yml" /
COPY "resource_configure.yml" /
COPY "resourceManager.py" /

RUN pip3 install boto3 pyyaml

ENTRYPOINT ["/greengrass-entrypoint.sh"]
