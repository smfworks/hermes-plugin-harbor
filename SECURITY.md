# Security Policy

Harbor is an advisory classifier. It does not call networks, spawn agents,
execute task text, or persist secrets.

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | Yes |
| 1.0.x   | Security fixes only |

## What this plugin does not do

- It does not execute the task string.
- It does not install hooks or mutate conversation context.
- It does not swap models mid-turn.
- It does not send telemetry off-box.

## Reporting a vulnerability

Email **security@smfworks.com** or open a private advisory on GitHub:

https://github.com/smfworks/hermes-plugin-harbor/security/advisories/new

Please include:

1. Affected version / commit
2. Impact (what an attacker could cause)
3. Reproduction steps

We will acknowledge within 5 business days.

## Operational notes

Unexpected exceptions are logged locally and returned to the caller as
`{"success": false, "error": "internal error"}` without exception text.
Invalid enums fail closed with an explicit validation error
(`{"error": "..."}`).
