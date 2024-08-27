FROM python:3.12.5-slim

WORKDIR /py-wa-scheduler
COPY . /py-wa-scheduler

RUN echo "deb http://deb.debian.org/debian/ bookworm-backports main contrib non-free unstable" | tee /etc/apt/sources.list.d/backports.list

RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    nano \
    libgbm-dev \
    libzbar-dev \
    wget \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

ENTRYPOINT ["python", "script.py"]
CMD ["", ""]