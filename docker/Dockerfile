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

COPY docker/requirements.txt /tmp
WORKDIR /tmp
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install -r requirements.txt
RUN python3.11 -m pip install --upgrade pip setuptools
RUN python3.11 -m pip install awscli --upgrade --user
ENV PYTHONPATH /workspace

RUN npm install -g @marp-team/marp-cli

ENV CHROME_PATH /usr/bin/chromium

WORKDIR /workspace
COPY . .

# Add path to Marp CLI
ENV PATH $PATH:/usr/local/bin

EXPOSE 5000

# RUN python3.11 app/main.py
RUN /bin/bash