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

## REST API

Start the server:

```bash
uv run python -m src.assignment.main --serve
```

The `/solve` endpoint accepts a problem input and returns the solution directly (including stats when available).

Request shape:

```json
{
  "num_students": 10,
  "num_groups": 2,
  "groups": [],
  "students": [],
  "exclude": []
}
```

Response:

```json
{
  "assignments": [ { "student_id": 0, "group_id": 1 } ],
  "status": "FITNESS: 123.4; INITIAL FITNESS: 234.5;",
  "stats": { "rankings": { "avg_rank": 2.4 } }
}
```

Example curl:

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d @- <<JSON
$(cat examples/sample_input.json)
JSON
```
