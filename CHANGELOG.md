# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Releases after 0.1.0 are prepared automatically by
[release-please](https://github.com/googleapis/release-please) from
[Conventional Commits](https://www.conventionalcommits.org/). Do not edit the
generated sections by hand.

## [0.2.0](https://github.com/AndreVarandas/clash-royale-api-py/compare/clash-royale-api-py-v0.1.0...clash-royale-api-py-v0.2.0) (2026-11-12)


### Features

* initial release of clash-royale-api-py ([76a5894](https://github.com/AndreVarandas/clash-royale-api-py/commit/76a5894a2d3e9a88ea533961d5e35549bf61c6c7))


### Documentation

* add a pull request template and release PR guidance ([ef99b16](https://github.com/AndreVarandas/clash-royale-api-py/commit/ef99b165fc85efb19e1c039a16b926325a39dac2))

## [0.1.0] - 2026-11-12

### Added

- `ClashRoyaleAPI` and `AsyncClashRoyaleAPI` clients with a shared transport.
- Resource wrappers for clans, players, cards, events, tournaments, global
  tournaments, locations, leaderboards, and a `raw` escape hatch.
- Pydantic v2 models for every endpoint, with `snake_case` fields, retained
  extra fields, and a `.raw` dict view.
- Iterable `Page` / `AsyncPage` pagination with cursor support.
- Tag normalization: `2PP`, `#2PP`, `%232PP`, and padded input are accepted.
- Exception hierarchy mapped to HTTP status codes, including `GoneError` for
  the retired `currentwar` endpoint.
- Automatic retries with exponential backoff and jitter for 429 and 5xx,
  honoring `Retry-After`.
- Token resolution from `CLASH_ROYALE_API_TOKEN` or `CLASH_ROYALE_TOKEN_API`.
- Support for custom `httpx` clients and proxy base URLs.
- Documentation site covering configuration, resources, models, and errors.

[0.1.0]: https://github.com/AndreVarandas/clash-royale-api-py/releases/tag/v0.1.0
