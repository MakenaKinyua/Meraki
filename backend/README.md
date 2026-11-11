# Meraki API

FastAPI service for the existing ingredient explainer. It imports the repository's `src` modules by adding the repository root to `sys.path`; `src/` remains the shared application code.

## Run locally

From the repository root:

```bash
cd backend
uv sync
uv run fastapi dev
```

The API is at `http://localhost:8000`; interactive API docs are at `/docs`. Chat conversations are stored in `data/chat.db`, which is created automatically. Each new chat receives a UUID and messages are stored in order. The source ingredient database must exist at `data/ingredients.db`, and `GROQ_API_KEY` plus `GROQ_MODEL` in the repository-root `.env` are required for answers. Set `FRONTEND_ORIGINS` to a comma-separated list of allowed browser origins when deploying (the default allows Vite at `http://localhost:5173`).

## Deploy separately

Build from the repository root so the image can include both `backend/` and the shared `src/` directory:

```bash
docker build -f backend/Dockerfile -t meraki-api .
docker run --rm -p 8000:8000 \
  -e GROQ_API_KEY -e GROQ_MODEL \
  -e FRONTEND_ORIGINS=https://your-frontend.example \
  -v "$PWD/data:/app/data" meraki-api
```

The API image is independently deployable from the Vue frontend. Supply the database and secrets through the deployment environment or mounted storage.
