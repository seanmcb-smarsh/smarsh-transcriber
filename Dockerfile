# syntax=docker/dockerfile:experimental
ARG DOCKER_BASE="docker-sandbox.artifacts.corp.digitalreasoning.com/"
ARG SNAPSHOT_MASTER

ARG CI_TAG

FROM ${DOCKER_BASE}k8s-base-images/centos7-python3-build:${CI_TAG} as build

USER 0

RUN --mount=type=secret,id=artifactory.repo,dst=/etc/yum.repos.d/artifactory.repo \
  INSTALL_PKGS="libsndfile sox" && \
  yum install -y --setopt=tsflags=nodocs $INSTALL_PKGS && \
  rpm -V $INSTALL_PKGS && \
  yum -y clean all --enablerepo='*'


ARG CMAKE_VERSION=3.21.3
RUN --mount=type=secret,mode=440,id=.netrc,dst=/opt/app-root/.netrc \
  wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-linux-x86_64.tar.gz

RUN tar -xzf cmake-${CMAKE_VERSION}-linux-x86_64.tar.gz && \
    mv cmake-${CMAKE_VERSION}-linux-x86_64 ../cmake

USER default

ENV PATH=$HOME/cmake/bin/:$PATH

COPY setup.py ./
RUN --mount=type=secret,id=pip.conf,dst=/etc/pip.conf,mode=0440 \
    pip install .

RUN --mount=type=secret,id=pip.conf,dst=/etc/pip.conf,mode=0440 \
    pip install -e .[dev]
