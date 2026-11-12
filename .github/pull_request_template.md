## What changed

<!-- One or two sentences describing the change and why. -->

## Type of change

- [ ] `feat` — new behavior
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `perf` / `refactor` / `test` / `build` / `ci` / `chore`

## Checklist

- [ ] Tests added or updated
- [ ] `uv run pytest --cov --cov-fail-under=100` passes (coverage gate is 100%)
- [ ] `uv run ruff check src tests scripts examples` passes
- [ ] `uv run ruff format --check .` passes
- [ ] `uv run mypy src` passes
- [ ] Docs updated when public behavior changed
- [ ] Commit message follows [Conventional Commits](https://www.conventionalcommits.org/) — it drives the next version and the changelog

## Release PRs

If this PR was opened by release-please, it is generated. Do not edit the
version in `pyproject.toml` or the `CHANGELOG.md` section by hand. Review the
entry and the proposed version, wait for CI to pass, and merge. Merging creates
the `vX.Y.Z` tag and GitHub release; the `Publish` workflow then uploads the
distributions to PyPI.
