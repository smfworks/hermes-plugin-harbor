# Contributing

Thanks for helping harden Harbor.

## Development

```bash
git clone https://github.com/smfworks/hermes-plugin-harbor.git
cd hermes-plugin-harbor
python -m pip install -e ".[dev]"   # or: pip install pytest ruff
python -m pytest -q
ruff check hermes_harbor tests
```

## Rules

1. **No hooks.** This plugin is advisory. Do not register automatic conversation hooks.
2. **Handlers never raise.** Return JSON error objects.
3. **Tests first for classifier changes.** If you change cue lexicons or scoring, add a failing case, then fix.
4. **Do not treat volume as quality.** A recommendation that over-promotes swarm is a defect.

## Pull requests

- Target `main`
- Keep the dual-surface layout: repo-root `plugin.yaml` + `hermes_harbor/` package
- Update CHANGELOG.md

## Release

```bash
# After CI is green on main
git tag -a v1.x.0 -m "Harbor v1.x.0"
git push origin v1.x.0
gh release create v1.x.0 --generate-notes
```
