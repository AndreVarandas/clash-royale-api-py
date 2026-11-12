# Security Policy

## Supported versions

Only the latest release receives security fixes.

| Version | Supported |
|---|---|
| 0.1.x | Yes |
| < 0.1 | No |

## Reporting a vulnerability

Please do **not** open a public issue for security problems.

Report privately through GitHub's
[Security Advisories](https://github.com/AndreVarandas/clash-royale-api-py/security/advisories/new).
Include the affected version, a description of the issue, and a minimal
reproduction if you have one. You can expect an initial response within a
few days.

## API tokens

This library sends your Clash Royale API token in the `Authorization` header
of every request. Your token is as sensitive as a password:

- Keep it in an environment variable or a local `.env` file, never in source
  code or a committed file. `.env` is already ignored by git.
- Tokens are bound to IP addresses. Treat the whitelist as part of the secret.
- If a token is exposed, revoke it immediately at
  <https://developer.clashroyale.com/#/account> and issue a new one.

## Scope

This project is an unofficial wrapper. Vulnerabilities in the Clash Royale
API, in Supercell's services, or in your account are outside its scope — the
library only makes HTTP requests to the endpoints you call.
