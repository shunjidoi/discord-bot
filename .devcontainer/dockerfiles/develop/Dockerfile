FROM ubuntu:20.04

RUN apt update -y \
  && apt upgrade -y \
  && apt autoremove -y \
  && apt-get update

ENV DEBIAN_FRONTEND=noninteractive
RUN apt install -y \
  git

RUN apt autoclean && apt clean && apt update && apt install -y \
  lsb-release \
  ca-certificates \
  bash-completion

RUN apt install -y \
  vim \
  gettext \
  make \
  curl \
  wget \
  less \
  unzip \
  gnupg

RUN apt update -y && apt install -y \
  sqlite3 \
  libsqlite3-dev \
  libcurl4-gnutls-dev \
  libexpat1-dev \
  libghc-zlib-dev \
  libbz2-dev \
  libssl-dev

RUN apt install -y \
  language-pack-ja

#
# Docker
# https://docs.docker.com/engine/install/linux-postinstall/
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
  && echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && apt update -y \
  && apt install -y docker-ce docker-ce-cli containerd.io
#
# tools
#
RUN apt install -y jq
#
# awscli install
#
RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
  unzip awscliv2.zip && \
  ./aws/install && \
  aws --version && \
  rm awscliv2.zip
#
# samcli install
#
RUN curl -L https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip -o samcli.zip && \
  unzip samcli.zip -d sam-installation && \
  sam-installation/install && \
  sam --version && \
  rm samcli.zip
#-------------------
# python install
ENV PYTHON_VER=3.8
ENV PYTHON_FULL_VER=3.8.15
RUN wget https://www.python.org/ftp/python/${PYTHON_FULL_VER}/Python-${PYTHON_FULL_VER}.tgz \
  && tar xvf Python-${PYTHON_FULL_VER}.tgz \
  && cd Python-${PYTHON_FULL_VER} \
  && ./configure --enable-optimizations --enable-loadable-sqlite-extensions \
  && make altinstall -j$(nproc) \
  && cd .. \
  && rm Python-${PYTHON_FULL_VER}.tgz \
  && rm -fr Python-${PYTHON_FULL_VER}
#
# upgrade pip & insall pipenv
#
RUN python${PYTHON_VER} -m pip install -U pip && python${PYTHON_VER} -m pip install pipenv
#
# add develop user
#
ARG USERNAME=developer
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
  && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
  && apt-get install -y sudo \
  && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
  && chmod 0440 /etc/sudoers.d/$USERNAME \
  && { \
  echo 'export PS1='\''\[\033[01;32m\]\u@\h\[\033[01;33m\] \w \[\033[01;31m\]$(__git_ps1 "(%s)") \n\[\033[01;34m\]\$\[\033[00m\] '\'''; \
  } >>/home/developer/.bashrc \
  && usermod -aG docker $USERNAME \
  && groupmod -g 1001 docker

#
# DockerCompose
#
ENV DOCKER_CONFIG /home/developer/.docker
RUN mkdir -p $DOCKER_CONFIG/cli-plugins \
  && curl -SL https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose \
  && chmod +x /usr/local/bin/docker-compose \
  && curl -SL https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-$(uname -s)-$(uname -m) -o $DOCKER_CONFIG/cli-plugins/docker-compose \
  && chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose \
  && curl -fL https://raw.githubusercontent.com/docker/compose-switch/master/install_on_linux.sh | sh
