# Genetic Algorithm Student Assignment Solver

This project implements a Genetic Algorithm (GA) to solve a student-group assignment problem.

## Features

- **Genetic Algorithm**: Uses tournament selection, uniform crossover, and swap mutation.
- **Fitness Function**: Incorporates hard constraints (group sizes, exclusions, prerequisites) and soft constraints (minimizing deviations, pull, and rankings).
- **FastAPI Interface**: Provides an async REST API for solving assignment problems with callbacks.
- **CLI Tool**: Command-line interface for batch processing JSON files.
- **Deployment**: Includes `Dockerfile` and `railway.toml`.

## Local Setup

Step 1: Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Step 2: Install dependencies:

```bash
uv sync
```

Step 3: Run the CLI (synchronous, local):

```bash
uv run python -m src.assignment.main examples/sample_input.json
```

## Async REST API

Start the server:

```bash
uv run python -m src.assignment.main --serve
```

The `/solve` endpoint now accepts a deferred request and returns an immediate acknowledgement. The solver runs in the background and POSTs results (including stats) to your callback URL.

Request shape:

```json
{
  "deferredId": "uuid-string",
  "callbackUrl": "http://localhost:9000/callback",
  "input": { "num_students": 10, "num_groups": 2, "groups": [], "students": [], "exclude": [] }
}
```

Ack response:

```json
{ "acknowledged": true, "deferredId": "uuid-string" }
```

Callback payload:

```json
{
  "deferredId": "uuid-string",
  "assignments": [ { "student_id": 0, "group_id": 1 } ],
  "stats": { "rankings": { "avg_rank": 2.4 } }
}
```

Example curl (requires a callback server):

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d @- <<JSON
{
  "deferredId": "00000000-0000-0000-0000-000000000000",
  "callbackUrl": "http://localhost:9000/callback",
  "input": $(cat examples/sample_input.json)
}
JSON
```
