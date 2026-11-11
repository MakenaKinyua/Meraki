# Meraki frontend

Small Vue 3 app built with Vite and shadcn-vue. The chat uses shadcn-vue's AI Elements Chat composition: Message Scroller, Message, Bubble, and Input Group. These are copied UI components, not a separate AI Elements runtime package. The frontend is independent of the FastAPI process and calls its HTTP API.

## Run locally

In one terminal, start the API from `backend/` as described in `backend/README.md`. Then, from this directory:

```bash
npm install
npm run dev
```

Open the local URL Vite prints (normally `http://localhost:5173`). Vite proxies `/api` and `/health` to the local API during development.

## Build and deploy separately

```bash
npm run build
```

Deploy the generated `dist/` directory to any static host. For a separately hosted API, set `VITE_API_URL` to the API's public origin when building, for example:

```bash
VITE_API_URL=https://api.example.com npm run build
```

Configure the API's `FRONTEND_ORIGINS` to include the deployed frontend origin.
