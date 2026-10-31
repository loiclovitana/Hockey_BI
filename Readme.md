# Hockey BI

Hockey BI is a web app for Swiss fantasy hockey managers. It collects data from Hockey Manager to help you follow player performance, track your teams, and assess transfers.

[Open Hockey BI](https://aml.bunny-wyrm.ts.net/)

- Explore player statistics, prices, and their evolution over time.
- Track your teams’ value and compare potential transfers.
- Read Swiss Hockey News articles linked to players and teams.

See [Architecture](Architecture.md) for diagrams of the app and data flow.

> [!CAUTION]
> This project is not affiliated with, endorsed by, or connected to hockeymanager.ch or its owners.
> The website hockeymanager.ch and its contents are protected by intellectual property laws and are the exclusive property of Redesign Sagl de Camorino.
> Use of this software may violate the Terms of Service of hockeymanager.ch or other applicable laws. The authors of this project do not assume any responsibility for misuse. You are solely responsible for ensuring that your use of this software complies with all legal and contractual obligations.

## Install and run locally

You need Python 3.13+, uv, Node.js 22.12+, pnpm, and a Hockey Manager account to import data and access your teams.

From the repository root, install the backend dependencies and create your local configuration:

```sh
cd backend
uv sync
cp resources/.env_template .env.local
```

Edit `backend/.env.local`:

- Set `HM_DATABASE_URL=sqlite:///hockey.db` for a local database.
- Fill in `HM_USER` and `HM_PASSWORD` with your Hockey Manager credentials.
- Choose `HMTRACKER_ADMIN_USER` and `HMTRACKER_ADMIN_PASSWORD` for the app’s admin page.
- Set `HM_SECRET_KEY` to a long random secret. You can generate one with `uv run python -c 'import secrets; print(secrets.token_hex(32))'`.
- Leave `HM_ROOT_PATH` empty for local use. News processing is optional and requires `OPENAI_API_KEY` and a suitable `HM_PLAYER_NEWS_MODEL`.

Still in `backend`, initialize the database once, import player data, and start the API:

```sh
uv run --env-file .env.local python -m hmtracker.database.creation
uv run --env-file .env.local python -m hmtracker.loader.main
uv run --env-file .env.local python main.py
```

The API runs at http://localhost:8000, with API documentation at http://localhost:8000/docs. Repeat the player import regularly to keep statistics current and build historical data.

In another terminal, from the repository root, start the web app:

```sh
cd frontend
pnpm install
pnpm dev
```

Open http://localhost:5173 and sign in with your Hockey Manager account to load your teams.
