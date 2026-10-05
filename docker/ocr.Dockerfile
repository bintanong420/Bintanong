# syntax=docker/dockerfile:1
# OCR measurement image (plans/2026-10-04-prospectus-ocr-measurement.md). CPU is the default.
#   CPU: docker build -f docker/ocr.Dockerfile -t bintanong-ocr:cpu .
#   GPU: docker build -f docker/ocr.Dockerfile --build-arg OCR_EXTRA=ocr-gpu --build-arg OCR_DEVICE=cuda -t bintanong-ocr:gpu .
# The GPU image needs no nvidia/cuda base: the ocr-gpu extra brings CUDA 13.0 torch and the CUDA and cuDNN
# runtime libraries as wheels. At run time the host driver is injected by the NVIDIA Container Toolkit
# (see compose.ocr-gpu.yaml in the plan). Build context is the repository root.
ARG PYTHON_IMAGE=python:3.13.15-slim-bookworm
FROM ${PYTHON_IMAGE}
ARG OCR_EXTRA=ocr-cpu
ARG OCR_DEVICE=cpu
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY backend/pyproject.toml backend/uv.lock /workspace/backend/
RUN --mount=type=cache,target=/root/.cache/uv \
    cd /workspace/backend && UV_HTTP_TIMEOUT=300 uv sync --locked --no-dev --extra tools --extra ${OCR_EXTRA}
COPY backend /workspace/backend
COPY scripts/ocr_bench.py scripts/fetch_tessdata.py scripts/fetch_rapidocr_models.py /workspace/scripts/
# the pinned fil and eng models, hash-checked at build time, same files as on every other OS
RUN /workspace/backend/.venv/bin/python /workspace/scripts/fetch_tessdata.py --dest /opt/tessdata
# the RapidOCR models of the three RapidOCR configs (RapidOCR checks each against the SHA-256 in its own
# default_models.yaml); the hashes of what was fetched are kept in /opt/rapidocr-models.json. The image then runs offline.
RUN /workspace/backend/.venv/bin/python /workspace/scripts/fetch_rapidocr_models.py --manifest /opt/rapidocr-models.json
ENV PATH=/workspace/backend/.venv/bin:$PATH \
    TESSDATA_PREFIX=/opt/tessdata \
    OCR_BENCH_DEVICE=${OCR_DEVICE} \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENTRYPOINT []
CMD ["python", "scripts/ocr_bench.py", "ocr", "--list"]
