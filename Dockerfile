ARG PYTHON_VERSION="3.13"

FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim

ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_COMPILE_BYTECODE=1

# CUDA packages are huge
ENV UV_HTTP_TIMEOUT=300

# 1. Install apt dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked   \
    apt-get update &&           \
    # `events` is installed from a git repository
    apt-get -y install git &&   \
    # cv2 required dependencies
    apt-get -y install libgl1-mesa-dev libglib2.0-0

WORKDIR /app

# 2. Create virtual environment
ARG INFERENCE_TYPE="cpu"
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --extra ${INFERENCE_TYPE} --locked --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

# 3. Download YOLO and TrOCR models
ARG TROCR_MODEL_TYPE="pytorch"
RUN --mount=type=cache,target=/root/.cache/huggingface/hub \
    --mount=type=bind,source=./scripts/download_models.py,target=download_models.py \
    uv run download_models.py --docker --yolo --${TROCR_MODEL_TYPE}

# 4. Copy application files
COPY ./src            /app/src
COPY ./pyproject.toml /app/pyproject.toml
COPY ./alembic.ini    /app/alembic.ini
