FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy LCA_BASE_DIR=/app

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY lca ./lca
RUN uv sync --frozen --no-dev

# Stockfish is fetched (sha256-verified) at image build time, not committed.
RUN uv run --no-sync fetch-stockfish --platform linux --dest /app/stockfish

EXPOSE 42069

CMD ["uv", "run", "--no-sync", "uvicorn", "lca.main:app", "--host", "0.0.0.0", "--port", "42069"]
