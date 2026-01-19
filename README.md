# Genetic Algorithm Student Assignment Solver

This project implements a Genetic Algorithm (GA) to solve a student-group assignment problem.

## Features

- **Genetic Algorithm**: Uses tournament selection, uniform crossover, and swap mutation.
- **Fitness Function**: Incorporates hard constraints (group sizes, exclusions, prerequisites) and soft constraints (minimizing deviations, pull, and rankings).
- **FastAPI Interface**: Provides a REST API for solving assignment problems.
- **CLI Tool**: Command-line interface for batch processing JSON files.
- **Deployment**: Includes `Dockerfile` and `railway.toml`.

## Local Setup

1. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the CLI:
   ```bash
   uv run python -m src.assignment.main examples/sample_input.json
   ```

4. Start the server:
   ```bash
   uv run python -m src.assignment.main --serve
   ```
