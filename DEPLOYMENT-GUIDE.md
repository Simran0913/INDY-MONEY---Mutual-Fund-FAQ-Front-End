# Deploy the full chatbot

The frontend is published on GitHub Pages. This repository also contains the
FastAPI backend, prebuilt FAISS index, and a Render Blueprint. Deploy the
backend first, then connect its public URL to the frontend.

## 1. Deploy the backend on Render

1. Sign in to [Render](https://render.com/) and choose **New → Blueprint**.
2. Connect the repository
   [Simran0913/INDY-MONEY---Mutual-Fund-FAQ-Front-End](https://github.com/Simran0913/INDY-MONEY---Mutual-Fund-FAQ-Front-End).
   Render reads `render.yaml` from the repository root.
3. When prompted, provide `OPENAI_API_KEY` as a Render secret. Do not put the
   key in GitHub, frontend settings, or source files.
4. Deploy the Blueprint and wait for the service to become live. The blueprint
   already sets `ALLOWED_ORIGINS` to `https://simran0913.github.io`.
5. Open `https://YOUR-RENDER-SERVICE.onrender.com/api/health`. Confirm the
   response reports `"status":"ok"` and `"index_ready":true`.

The prebuilt vector index and metadata are included in `data/vector_store/`.
Keep both files in the repository when updating the deployment.

## 2. Connect the frontend to the backend

1. In the GitHub repository, open **Settings → Secrets and variables → Actions
   → Variables**.
2. Add a repository variable named `NEXT_PUBLIC_API_URL`.
3. Set its value to the Render service's HTTPS URL, for example
   `https://your-service.onrender.com`. Do not include `/api` or a trailing
   slash.
4. In the repository, open **Actions → Deploy frontend to GitHub Pages**.
5. Choose **Run workflow**, select `main`, and confirm. Wait for the run to
   finish successfully.

This variable is public because it is embedded in the frontend. Never use a
`NEXT_PUBLIC_*` variable for API keys or other secrets.

## 3. Verify the live chatbot

Open the Pages site:

https://simran0913.github.io/INDY-MONEY---Mutual-Fund-FAQ-Front-End/

Ask a factual question such as “What is the expense ratio of SBI Bluechip
Fund?” Confirm that the chatbot answers with an official source citation. If
the frontend still says the API is not connected, confirm
`NEXT_PUBLIC_API_URL` and rerun the Pages workflow. If the browser reports a
CORS error, set Render's `ALLOWED_ORIGINS` to exactly
`https://simran0913.github.io` and redeploy the service.

Render's free service may sleep when idle; the first request after inactivity
can take longer to respond.
