# syntax=docker/dockerfile:1.7
ARG APP_VERSION=3.3.1

FROM python:3.12-slim AS builder
ARG APP_VERSION

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /build
RUN python -m venv "$VIRTUAL_ENV"
COPY requirements.txt constraints/runtime.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install "pip>=26,<27" "setuptools>=80,<81" "wheel>=0.45,<1" && \
    python -m pip install --no-compile -r requirements.txt -c runtime.txt && \
    python -m pip check

# Build and install the application as the same wheel shape verified by CI. This
# prevents the runtime image from relying on a mutable source-tree PYTHONPATH.
COPY . ./
RUN python scripts/verify_version.py --expected "$APP_VERSION"
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip wheel --no-deps --no-build-isolation --wheel-dir /tmp/wheels . && \
    python -m pip install --no-deps /tmp/wheels/*.whl && \
    cd /tmp && \
    NEXUS_ENV=test \
    NEXUS_MODEL_VALIDATION_MODE=off \
    NEXUS_COMPACTION_ENABLED=false \
    NEXUS_OTEL_ENABLED=false \
    cognexus-skills validate

FROM python:3.12-slim AS runtime

ARG APP_VERSION
ARG VCS_REF=unknown
ARG SOURCE_URL=unknown
LABEL org.opencontainers.image.title="Cognexus" \
      org.opencontainers.image.version="$APP_VERSION" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.source="$SOURCE_URL" \
      org.opencontainers.image.description="Production OpenAI Agents SDK orchestration with portable Agent Skills"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app
RUN groupadd --system --gid 10001 nexus && \
    useradd --system --uid 10001 --gid nexus --home-dir /app --shell /usr/sbin/nologin nexus && \
    mkdir -p /app/data /tmp/nexus && \
    chown -R nexus:nexus /app/data /tmp/nexus

COPY --from=builder /opt/venv /opt/venv

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os, urllib.request; port=os.getenv('NEXUS_PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3)" || exit 1

CMD ["cognexus-server"]
