# dep layer caching, need to test later
FROM python:3.12-slim-trixie

# System deps (and clean up)
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install uv
ADD https://astral.sh/uv/0.6.13/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

# Copy only files that define dependencies first
COPY pyproject.toml uv.lock ./

# Install deps into project venv; this layer caches nicely
# If you use BuildKit, you can also add a cache mount for speed:
# RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked
RUN uv sync --locked

# copy rest of the source
COPY . .

# (optional) prevent ENTRYPOINT surprises
ENTRYPOINT []
CMD ["uv", "run", "main.py"]
