# watchLater-Backend

Backend service and data pipeline for organizing YouTube Watch Later videos into structured categories and tags.

## What This Project Does

- Scrapes YouTube Watch Later playlist continuation responses.
- Normalizes raw response data into a clean video list.
- Classifies videos into categories and tag triplets (`concept`, `tool`, `topic`) with Claude.
- Serves the final dataset through a FastAPI + PostgreSQL API.

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL (`psycopg2` driver)
- Playwright (for scraping)
- Docker

## Repository Layout

- `watchLater-api/`: FastAPI app, models, schemas, database session, CRUD.
- `api/`: JSON data files (`watchlater_grouped.json`, historical data).
- `scraper.py`: Captures YouTube continuation payloads to `data.json`.
- `readJson.py`: Converts raw payloads into normalized `response.json`.
- `claude-quickstart/claude.py`: Classifies videos into category + tags and writes `claude.json`.
- `merge_tags.py`: Merges tags from `api/watchlater_old.json` into `api/watchlater_grouped.json`.

## Prerequisites

1. Python 3.11+
2. PostgreSQL running locally
3. A database matching the connection string in `watchLater-api/database.py`
4. (Optional for classification) Anthropic API key in `.env`

## Local Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install PostgreSQL driver if not already present:

```bash
pip install psycopg2-binary
```

4. Review database connection in `watchLater-api/database.py`:

```python
engine = create_engine("postgresql+psycopg2://wilson@localhost:5432/wilson")
```

Update username, host, port, and database name to match your local setup.

5. Start the API:

```bash
cd watchLater-api
uvicorn routes:app --reload
```

Default local URL: `http://127.0.0.1:8000`

## API Endpoints

### `GET /videos`

Returns videos with cursor pagination and optional filtering.

Query params:

- `cursor` (int, default `0`): return records with `id > cursor`
- `category` (string, optional)
- `tag` (repeatable query param, optional)

Example:

```bash
curl "http://127.0.0.1:8000/videos?cursor=20&category=Frontend&tag=React&tag=TypeScript"
```

### `GET /categories`

Returns video counts per category and total videos.

```bash
curl "http://127.0.0.1:8000/categories"
```

### `GET /tags_by_category`

Returns all tags for a category.

```bash
curl "http://127.0.0.1:8000/tags_by_category?category=Frontend"
```

### `PATCH /videos/{video_id}`

Updates ordered tag slots by field name (`concept`, `tool`, `topic`).

```bash
curl -X PATCH "http://127.0.0.1:8000/videos/1" \
  -H "Content-Type: application/json" \
  -d '{"concept":"Hooks","tool":"React","topic":"State Management"}'
```

### `DELETE /videos/{video_id}`

Deletes one video.

```bash
curl -X DELETE "http://127.0.0.1:8000/videos/1"
```

## Data Pipeline Workflow

1. Scrape Watch Later continuation responses:

```bash
python scraper.py
```

This writes `data.json`.

2. Normalize scraped payload:

```bash
python readJson.py
```

This writes `response.json`.

3. Classify with Claude:

```bash
cd claude-quickstart
python claude.py
```

This writes `claude.json` at repo root.

4. (Optional) Merge tags from historical grouped data:

```bash
cd ..
python merge_tags.py
```

## Docker

Build image:

```bash
docker build -t watchlater-backend .
```

Run container:

```bash
docker run --rm -p 8080:8080 watchlater-backend
```

API will be available at `http://127.0.0.1:8080`.

Database note for Docker:

- Inside a container, `localhost` refers to the container itself.
- This image defaults `DATABASE_URL` to `postgresql+psycopg2://wilson@host.docker.internal:5432/wilson` so it can reach PostgreSQL running on your host machine.
- Override it if needed:

```bash
docker run --rm -p 8080:8080 \
  -e DATABASE_URL="postgresql+psycopg2://<user>:<password>@<host>:5432/<db>" \
  watchlater-backend
```

## Notes

- The current DB URL is hardcoded in `watchLater-api/database.py`.
- Keep `.env` files out of git history; this repository already ignores `.env` in `.gitignore`.
- If you previously exposed secrets, rotate them immediately.

## Future Improvements

- Move DB config to environment variables.
- Add migrations (Alembic).
- Add seed command that loads `api/watchlater_grouped.json` into PostgreSQL.
- Add tests for API endpoints and CRUD behavior.
