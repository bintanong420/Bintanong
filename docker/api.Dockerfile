ARG PYTHON_IMAGE=python:3.13.15-slim-bookworm
FROM ${PYTHON_IMAGE} AS swipl-build

ARG SWIPL_VERSION=10.0.2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates cmake curl libarchive-dev libedit-dev \
    libgmp-dev libpcre2-dev libssl-dev libyaml-dev ninja-build pkg-config \
    zlib1g-dev && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL "https://www.swi-prolog.org/download/stable/src/swipl-${SWIPL_VERSION}.tar.gz" -o /tmp/swipl.tar.gz \
    && mkdir /tmp/swipl \
    && tar -xzf /tmp/swipl.tar.gz -C /tmp/swipl --strip-components=1 \
    && cmake -S /tmp/swipl -B /tmp/swipl/build -G Ninja \
       -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local \
       -DINSTALL_DOCUMENTATION=OFF -DSWIPL_PACKAGES_JAVA=OFF \
       -DSWIPL_PACKAGES_ODBC=OFF -DSWIPL_PACKAGES_QT=OFF \
    && cmake --build /tmp/swipl/build --parallel 2 \
    && cmake --install /tmp/swipl/build

FROM ${PYTHON_IMAGE} AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libarchive13 libedit2 libgmp10 libpcre2-8-0 libssl3 \
    libyaml-0-2 zlib1g && rm -rf /var/lib/apt/lists/*
COPY --from=swipl-build /usr/local /usr/local
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/
WORKDIR /workspace
COPY backend/pyproject.toml backend/uv.lock /workspace/backend/
RUN cd /workspace/backend && uv sync --frozen --no-dev --extra api
COPY backend /workspace/backend
COPY knowledge /workspace/knowledge
ENV PATH=/workspace/backend/.venv/bin:$PATH PYTHONPATH=/workspace/backend
EXPOSE 8000
CMD ["uvicorn", "bintanong_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
