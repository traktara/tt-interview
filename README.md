# TT Interview — ONS local authorities

A starter web app for a technical interview:

```text
ONS API → Python pipeline → PostgreSQL → Flask API → React
```

## Before the interview

Install and start Docker Desktop with Linux containers, or Docker Engine with
Compose v2. No local Python, Node, database, API key or input files are needed.
Internet access is required for the first build and every data import.

Clone the repository, open a terminal in its root and run:

```sh
docker compose up --build
```

Keep this terminal running. The first build can take a few minutes. Startup waits
for Postgres, imports ONS data, then starts the API and web app. The pipeline
container exiting with code **0** is expected.

Open **http://localhost:8088** and check that:

- The unfiltered page shows **296 local authorities** and **9 regions**.
- Searching for **Bristol** returns one authority; selecting **South West** keeps it visible.
- “Behind the data” shows a successful import time.

Please complete these setup checks before the interview. No feature implementation
is expected beforehand; tasks will be provided during the session.

## Stop and restart

Run commands from the repository root in a second terminal.

```sh
docker compose down
docker compose up --build
```

`down` retains the database. To deliberately discard it and start fresh, use
`docker compose down -v` before starting again.

## Troubleshooting

- **Docker connection error:** start Docker and check that Linux containers are enabled.
- **Port 8088 is in use:** create `.env` with `WEB_PORT=8089`, run
  `docker compose up -d`, then open http://localhost:8089. Otherwise no `.env` is needed.
- **Startup fails or the page will not load:** inspect the services and logs:

  ```sh
  docker compose ps -a
  docker compose logs --tail=100 pipeline api web
  ```

  An ONS connection failure prevents startup. Restore internet access and rerun
  `docker compose up --build`. If it still fails, share the error with the interviewer.

## Working during the interview

Edit `frontend/src/main.jsx` and `frontend/src/style.css` for the UI, or
`backend/app.py` for the API. Saved React and Python API changes reload automatically.
The pipeline is in `backend/pipeline.py` and the database schema is in `backend/schema.sql`.

To rerun the pipeline after a change:

```sh
docker compose run --rm pipeline
```

Then click **Refresh view**. This button reloads the display; it does not import data.
Failed imports leave the previous successful dataset intact.

Dependency changes require `docker compose up --build`. After editing frontend
dependencies in `frontend/package.json`, update its lockfile before rebuilding:

```sh
docker compose run --rm --no-deps --volume ./frontend:/app web npm install --package-lock-only
```

Existing backend checks can be run with:

```sh
docker compose run --rm --no-deps api python -m unittest discover -v
```

The API is available through the web port at `/api/health` and `/api/dashboard`.
For example: http://localhost:8088/api/dashboard?region=E12000009&q=Bristol.
This Docker setup is for local development and publishes only the web port on loopback.

## Data and licence

The app imports the December 2024 England authority-to-region lookup directly
from ONS. No local snapshot is bundled. See [source and attribution](docs/data-sources.md).
Application code is supplied under the [MIT licence](LICENSE).
