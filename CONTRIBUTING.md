# Contributing

Thanks for taking the time to contribute.

## Setup

```bash
uv sync
uv run pre-commit install   # optional, installs the git hooks
```

You need an API token only for the live smoke test. Create one at
<https://developer.clashroyale.com/#/account> and put it in `.env` as
`CLASH_ROYALE_API_TOKEN=...`.

## Commands

```bash
uv run pytest --cov --cov-fail-under=100   # tests + coverage gate
uv run ruff check src tests scripts examples
uv run ruff format src tests scripts examples
uv run mypy src
uv run mkdocs serve
uv run python scripts/smoke.py             # live API, needs a token
```

The unit tests never touch the network — `respx` mocks both clients. The
smoke script is the only thing that talks to the real API; run it after
changing a model.

## Guidelines

- Keep test coverage at 100%; CI fails below it.
- Public API must be fully type-hinted and covered by `mypy --strict`.
- Do not duplicate request logic between the sync and async paths: shared
  behavior belongs in `_transport.py` or `_responses.py`.
- Paginated methods return `Page` / `AsyncPage`; list endpoints return models.
- Add or update tests for every behavior change.
- Documentation lives in `docs/` and is built with MkDocs Material.

## Commit messages

Releases are automated with
[release-please](https://github.com/googleapis/release-please), which reads
[Conventional Commits](https://www.conventionalcommits.org/) to decide the
next version and to write the changelog. Please use this format:

```
<type>(<optional scope>): <description>

[optional body]

[optional footer]
```

Common types:

| Type | Effect |
|---|---|
| `feat` | Added — bumps the minor version |
| `fix` | Fixed — bumps the patch version |
| `perf` | Performance improvement — patch |
| `docs` | Documentation only — no version bump |
| `refactor`, `test`, `build`, `ci`, `chore` | No version bump |
| `feat!` or `BREAKING CHANGE:` footer | Breaking change (minor while pre-1.0) |

Examples:

```
feat(clans): add river race standings helper
fix(transport): honor Retry-After without crashing on bad dates
docs: clarify token environment variables
```

## Release process

1. Merge changes to `main` using Conventional Commit messages.
2. release-please opens a release PR that bumps `pyproject.toml` and updates
   `CHANGELOG.md`.
3. Merge that PR. release-please tags the release and publishes the GitHub
   release.
4. The `Publish` workflow builds the distributions and uploads them to PyPI
   using trusted publishing.

Do not bump the version or tag releases by hand. `__version__` is read from
the installed package metadata, so it follows `pyproject.toml` automatically.
