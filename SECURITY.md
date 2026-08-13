# Security Policy

## Reporting

Use GitHub Security Advisories on this repository.

## Design

Harbor is advisory text classification. It does not execute task text, spawn agents, or open network connections. Control characters are stripped from task input. `max_agents` is clamped to 1–32. Invalid enums return JSON errors, never exceptions.

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | Yes |
| 1.0.x   | Best-effort |
