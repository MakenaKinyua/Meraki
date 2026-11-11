FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir uv
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN uv sync --project backend --frozen --no-dev
COPY backend ./backend
COPY src ./src
ENV PYTHONPATH=/app
ENV PATH="/app/backend/.venv/bin:$PATH"
EXPOSE 8000
CMD ["fastapi", "run", "backend/main.py", "--host", "0.0.0.0", "--port", "8000"]
