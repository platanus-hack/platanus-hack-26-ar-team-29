# 📈 Atajo
[![Backend Lint](https://github.com/platanus-hack/platanus-hack-26-ar-team-29/actions/workflows/backend-lint.yml/badge.svg)](https://github.com/platanus-hack/platanus-hack-26-ar-team-29/actions/workflows/backend-lint.yml)
[![Frontend Lint](https://github.com/platanus-hack/platanus-hack-26-ar-team-29/actions/workflows/frontend-lint.yml/badge.svg)](https://github.com/platanus-hack/platanus-hack-26-ar-team-29/actions/workflows/frontend-lint.yml)

**Track:** Agentic Money (Platanus Hack 26: Buenos Aires)

<img src="./project-logo.png" alt="Project Logo" width="150" align="center" />

**Atajo** is a conversational AI agent designed to unify your finances. It reads balances and history across all your connected accounts (e.g., Wallbit, Ethereum) and is capable of proposing and executing complex, multi-step money-moving plans, always waiting for a single explicit approval from you.

---

## 01.- Project Description

Managing multiple financial platforms can be tedious and full of friction. Atajo solves this by allowing you to **manage your trades easily and without friction**. Our main selling point is simple: **you can buy and sell assets with just one message.**

- **Trade in natural language:** Simply tell Atajo what you want to do (e.g., "Buy 10 USD of Apple"), and it will draft the exact execution steps for you.
- **Consolidates financial platforms:** It unifies different financial platforms into a single interface. Today it integrates with Wallbit for live balances and transactions, with a hexagonal architecture ready to expand to Ethereum and others.
- **Secure by design:** Atajo proposes multi-step plans but never executes a trade without your explicit, one-click approval.
- **Real-time feedback:** Everything from the agent's LLM generation to the step-by-step execution of a plan is streamed live to the frontend via WebSockets.

For a deeper dive into the product vision, check out the [project-description.md](./project-description.md) file.

---

## 02.- Tech Stack 🛠️

The project is divided into two main parts:

*   **Frontend:** [Next.js 15](https://nextjs.org) (App Router), React 19, TypeScript, Tailwind CSS v4. Real-time connection with the backend via WebSockets.
*   **Backend:** Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/), asyncpg, SQLAlchemy. Integrates the official Anthropic Claude SDK for agent orchestration.
*   **Database:** PostgreSQL.

---

## 💻 Local Development

To run the project locally, you will need: [Docker](https://docs.docker.com/engine/install/), [Bun](https://bun.sh/) (for the frontend), and [uv](https://docs.astral.sh/uv/) (for the Python backend).

### 1. Start the Database
From the project root, start the PostgreSQL container:
```bash
docker compose up -d
```

### 2. Backend (FastAPI)
Open a terminal and navigate to the `backend/` directory:
```bash
cd backend
# Install dependencies
uv sync
# Run database migrations
uv run alembic upgrade head
# Start the server (DO NOT use --reload as it breaks WebSocket state)
uv run uvicorn app.main:app --port 8000
```
> **Note:** You will need to configure your environment variables in `backend/.env`. Copy the `backend/.env.example` file and fill in the keys (especially `ANTHROPIC_API_KEY` and `FERNET_KEY`).

### 3. Frontend (Next.js)
Open another terminal and navigate to the `frontend/` directory:
```bash
cd frontend
# Install dependencies
bun install
# Start the development server
bun dev
```
The frontend will be available at [http://localhost:3000](http://localhost:3000). The backend will serve the API at `http://localhost:8000`.

---

## 🚀 Deployment

### Database (Supabase)
The project is designed to use a PostgreSQL database hosted on [Supabase](https://supabase.com/).
1. Create a project in Supabase.
2. Obtain the PostgreSQL connection URI.
3. This URI will be used in the backend (`DATABASE_URL`).

### Backend (Heroku via Containers)
The Atajo backend is deployed using the Heroku Container Registry to have absolute control over the Docker environment.

Ensure you have the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed and have logged in (`heroku login` and `heroku container:login`).

```bash
cd backend

# Create a Heroku app (if you don't have one)
heroku create atajo-backend

# Configure the necessary environment variables in Heroku
heroku config:set DATABASE_URL="your_supabase_url"
heroku config:set ANTHROPIC_API_KEY="your_api_key"
heroku config:set FERNET_KEY="your_fernet_key"

# Build the image and push it to the Heroku registry
heroku container:push web -a atajo-backend

# Release the image to deploy it
heroku container:release web -a atajo-backend
```

*(Do not forget to run migrations in the production environment using an interactive command or by connecting remotely).*

### Frontend (Vercel CLI)
The Next.js frontend is ideally deployed natively on [Vercel](https://vercel.com/).

Ensure you have the [Vercel CLI](https://vercel.com/docs/cli) installed (`npm i -g vercel`).

```bash
cd frontend

# Deploy the application
vercel deploy --prod
```
> During the Vercel configuration, make sure to provide the following environment variables:
> `NEXT_PUBLIC_API_BASE_URL="https://atajo-backend.herokuapp.com"`
> `NEXT_PUBLIC_WS_BASE_URL="wss://atajo-backend.herokuapp.com"`

---

## 👥 Team (team-29)
- Rubén Bohórquez ([@Rpetey317](https://github.com/Rpetey317))
- Juan Ignacio Medone ([@juanimedone](https://github.com/juanimedone))
- Vladimir Kozow ([@vladimirkozow](https://github.com/vladimirkozow))
- Luca Lazcano ([@lazcanoluca](https://github.com/lazcanoluca))
- Alen Davies ([@alendavies](https://github.com/alendavies))