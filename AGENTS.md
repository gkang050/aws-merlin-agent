# Repository Guidelines

## Project Structure & Module Organization
The repository is intentionally lean today (only the root `README.md`). As you add features, place application code in `src/aws_merlin_agent/` with subpackages for AWS clients, orchestration logic, and shared helpers. Keep IaC assets in `infra/`, prompt artifacts in `agents/prompts/`, docs in `docs/`, and fixtures in `tests/resources/`. Mirror each `src/` package with tests (for example, `src/aws_merlin_agent/workflows/pipeline.py` pairs with `tests/workflows/test_pipeline.py`). For every new top-level directory, add a brief `README.md` describing its intent.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create and activate the project virtual environment.
- `pip install -r requirements.txt`: install dependencies; rerun after editing the lock file.
- `pytest`: execute the full suite; use `pytest tests/workflows -k scenario` for targeted runs.
- `ruff check src tests`: lint code and surface style issues (`--fix` to auto-apply safe fixes).
- `black src tests`: format Python files before committing.

## Coding Style & Naming Conventions
Target Python 3.11, lean on type hints, and prefer dataclasses for structured payloads. Follow `black` defaults (88-character lines, double quotes) and run `ruff` to enforce import ordering. Use snake_case for modules and functions, PascalCase for classes, and UPPER_SNAKE_CASE for constants. Group AWS resource identifiers in `enums.py` or `constants.py` modules for quick reuse.

## Testing Guidelines
Use `pytest` for all unit and integration tests. Name files `test_<module>.py` and fixtures `conftest.py` scoped per package. Strive for ≥90% statement coverage by running `pytest --cov=src --cov-report=term-missing`. Mock AWS APIs with `moto` or `botocore.stub`, and mark long-running cloud calls with `@pytest.mark.slow` so CI can skip them when needed.

## Commit & Pull Request Guidelines
The current history is minimal (`Initial commit`), so anchor on Conventional Commits (`feat:`, `fix:`, `chore:`) with ≤72-character subjects and descriptive bodies when context is non-obvious. Before opening a pull request, ensure linting and tests pass locally, then provide: (1) a summary of intent, (2) linked issue or ticket, (3) verification steps with command output, and (4) screenshots or logs for agent transcript changes. Label the PR with the expected release impact (`major`, `minor`, or `patch`) and request review after CI succeeds.

## Security & Configuration Tips
Do not commit credentials or AWS account IDs. Use `aws-vault` or environment variables loaded via `.env` (ignored by default) for local secrets. Encrypt shared configuration in `infra/` with AWS KMS or SSM Parameter Store, and sanitize transcripts before sharing them in issues.
