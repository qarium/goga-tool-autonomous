# CLAUDE.md

Guidance for AI agents working in this repository.

## Commands

All tooling runs through the project venv, which lives outside the repository at
`/opt/goga/project` (create it with `python3 -m venv /opt/goga/project` if missing):

```bash
/opt/goga/project/bin/pip install -e '.[test]'                                  # setup
/opt/goga/project/bin/python -m pytest tests/ -x                                # tests
/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/                    # lint
/opt/goga/project/bin/ruff format --exclude '.usages' goga_tool_autonomous/ tests/  # format
/opt/goga/project/bin/python -c "import goga_tool_autonomous"                   # facade import
goga lint                                                                       # must stay cells: 4 errors: 0
```

- `ruff format` MUST carry `--exclude '.usages'`: ruff >= 0.16 formats Python blocks inside
  Markdown and would otherwise rewrite the read-only `.usages/` contract files.
- Commit gate (in this order, all green before every commit): facade import → `ruff check` →
  `ruff format --check --exclude '.usages'` → `pytest tests/ -x`.

## Invariants

- `CODEMANIFEST` and `.usages/` files are read-only contracts. When implementation and contract
  disagree, fix the implementation — never the contract. `goga lint` must keep reporting
  `cells: 4 errors: 0`.
- The root facade must import cleanly at all times (`import goga_tool_autonomous`) — a broken
  import is fatal to every goga command that loads tools.
- Runtime `dependencies = []` stays empty. The goga platform is declared only in the `test`
  extra (`goga>=2.0`, unpinned — platform drift must surface as test failures, never pass
  silently). The only runtime platform import lives in
  `goga_tool_autonomous/recipe/development/contribution.py`.
- No `try/except`, no validation, no caching, no state, no config/file reads inside the
  package: failures propagate to the platform's hard hook action.
- Intra-package imports are relative (`from .recipe import …`); absolute imports only for
  stdlib and third-party.

## Tests

- `tests/` mirrors the source tree (`goga_tool_autonomous/recipe/model/recipe.py` →
  `tests/recipe/model/test_recipe.py`); every test directory has an `__init__.py`.
- Import entities from the cell facades (e.g. `from goga_tool_autonomous.recipe import
  AutonomyRecipe`), not from deep implementation modules.
- Pure logic is tested mock-free; the suite exercises the real installed platform
  (`goga.pipeline.*`) for merge/compiler/registration integration tests.
