FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md requirements.txt requirements-dev.txt ./
COPY src ./src

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir build && \
    python -m build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*.whl

ENTRYPOINT ["copyast"]
CMD ["--help"]