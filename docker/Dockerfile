FROM python:3.11

ENV PYTHONBUFFERED=1

RUN apt-get update -y \
  && apt-get install -y --no-install-recommends \
    sudo \
    bc \
    bzip2 \
    ca-certificates \
    curl \
    git \
    libssl-dev \
    libffi-dev \
	  libncurses-dev \
    libgl1 \
    jq \
    nfs-common \
    parallel \
    unzip \
	  vim \
    wget \
    build-essential \
    sshfs \
    nodejs \
    npm \
    chromium \
    fonts-ipafont \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
SHELL ["/bin/bash", "-c"]

COPY requirements.txt /tmp
WORKDIR /tmp
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install -r requirements.txt
RUN python3.11 -m pip install --upgrade pip setuptools
RUN python3.11 -m pip install awscli --upgrade --user

RUN npm install -g @marp-team/marp-cli

ENV CHROME_PATH /usr/bin/chromium

WORKDIR /workspace

# Add user
ARG USER_ID
ARG GROUP_ID
RUN getent group $GROUP_ID || addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
RUN usermod -aG sudo user
RUN passwd -d user
USER user

# Create python alias
RUN mkdir -p $HOME/bin
RUN ln -s /usr/bin/python3.11 $HOME/bin/python
ENV PATH $PATH:$HOME/bin:$HOME/.local/bin
ENV PYTHONPATH /workspace

# Add path to Marp CLI
ENV PATH $PATH:/usr/local/bin

RUN ["/bin/bash"]