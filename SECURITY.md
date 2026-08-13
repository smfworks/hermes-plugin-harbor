# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | Yes |
| 1.0.x   | Security fixes only |

## What this plugin does and does not do

Harbor is an **advisory classifier**. It does not execute task text, spawn agents, call models, or open network connections. Input is treated as data.

## Reporting a vulnerability

Email **aionaedge@agentmail.to** with:

- Plugin version / commit SHA
- Description of the issue
- Reproduction steps (no exploit payloads)

Do not open a public GitHub issue for security reports.

We aim to acknowledge within 5 business days.

## Threat notes

- Task text is truncated and control characters are stripped before classification.
- Invalid enums fail closed with JSON errors; handlers never raise.
- Do not pipe untrusted task text into shells. Harbor's CLI prints JSON/Markdown; treat it as untrusted display.
