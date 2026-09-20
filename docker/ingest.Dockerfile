ARG PYTHON_IMAGE=python:3.13.15-slim-bookworm
FROM ${PYTHON_IMAGE}
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/
WORKDIR /workspace
COPY backend/pyproject.toml backend/uv.lock /workspace/backend/
RUN cd /workspace/backend && uv sync --frozen --no-dev --extra tools
COPY backend /workspace/backend
ENV PATH=/workspace/backend/.venv/bin:$PATH PYTHONPATH=/workspace/backend
ENTRYPOINT []
CMD ["python", "-m", "bintanong_tools.ingest", "--help"]
