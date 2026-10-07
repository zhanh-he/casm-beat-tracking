FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential ffmpeg git libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/requirements.txt \
    && if [ -d /app/third_party/beatfm_source ]; then \
         python -m pip install -r /app/requirements-beatfm.txt; \
       fi \
    && python -m pip install 'Cython==0.29.37' \
    && python -m pip install --no-build-isolation -r /app/requirements-dbn.txt

RUN chmod +x /app/run.sh /app/install.sh

ENTRYPOINT ["/app/run.sh"]
