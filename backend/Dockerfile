FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY lca ./lca
RUN uv sync --frozen --no-dev

EXPOSE 42069

CMD ["uv", "run", "--no-sync", "uvicorn", "lca.main:app", "--host", "0.0.0.0", "--port", "42069"]
