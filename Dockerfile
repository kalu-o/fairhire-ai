ARG DOCKER_REGISTRY=docker.io
FROM ${DOCKER_REGISTRY}/library/python:3.10-slim-bookworm
ENV HOST 0.0.0.0

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get -qq update \
    && apt-get -qq upgrade \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt dist/fair_hire_ai_service-*.whl /app/

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps --find-links . fair_hire_ai_service

EXPOSE 8000/tcp

ENTRYPOINT ["fair_hire_ai_service"]