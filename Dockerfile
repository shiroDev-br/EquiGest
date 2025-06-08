FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app/

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock /app/

RUN uv pip install --system --no-deps --require-hashes --requirement uv.lock || \
    uv sync --locked --no-install-project --no-dev

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

EXPOSE 8000
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
