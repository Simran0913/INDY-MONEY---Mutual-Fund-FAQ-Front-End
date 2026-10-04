# INDY MONEY — Mutual Fund FAQ Assistant

A facts-only chatbot for selected SBI Mutual Fund schemes. Its Next.js
frontend is published on GitHub Pages and its FastAPI backend can be deployed
on Render.

## Live frontend

https://simran0913.github.io/INDY-MONEY---Mutual-Fund-FAQ-Front-End/

The frontend needs a deployed API to answer questions. Follow
[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) to deploy the backend and connect it
to the site. Keep `OPENAI_API_KEY` secret in Render; never add it to GitHub.

## Run locally

- Frontend: `npm ci` then `npm run dev`
- Backend: install `requirements.txt`, configure a local `.env` using
  `.env.example`, then run `uvicorn api.main:app --reload --port 8000`