# goga-tool-autonomous

A [goga](https://pypi.org/project/goga/) hook tool that turns `development` pipeline runs into
unattended ones: review gates auto-approve, acceptance stops requiring a manual click, and the
build stage is contributed automatically.

## How it works

The package registers exactly one hook — `autonomy` on the `pipeline / amend_workflow` action.
When a goga command composes a pipeline whose discovered name is exactly `development`, the hook
contributes a declarative `WorkflowDocument`:

- `approve: auto` for each of the six gated review stages (`architecture-review`,
  `apply-architecture`, `code-design`, `design-review`, `coding-plan`, `plan-review`) — but only
  when the authored workflow did not already set an approval instruction for that stage;
- `manual: false` for the `accept-result` acceptance stage — always;
- the `build` extension (`Build implementation`, positioned after `commit-changes`, timeout
  `8h`, the `goga build` entrypoint invoked with the run's plan artifact, and the
  `rm -rf .ralphex` cleanup).

Every other pipeline composes exactly as if the tool were not installed — the hook matches the
pipeline name verbatim and stays silent on a miss. Authored instructions always win per slot:
the platform merge keeps authored values, so a workflow that already encodes this knowledge is
left byte-identical.

## Installation

The tool has no runtime dependencies by design — goga imports the package facade, so the
platform is present whenever the tool runs. Install it into the environment goga runs in:

```bash
# from PyPI (once published)
goga install autonomous

# from a source checkout
goga install --local /path/to/goga-tool-autonomous:autonomous
```

## Development

The project venv lives outside the repository at `/opt/goga/project`:

```bash
/opt/goga/project/bin/pip install -e '.[test]'
/opt/goga/project/bin/python -m pytest tests/
/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/
/opt/goga/project/bin/ruff format --exclude '.usages' goga_tool_autonomous/ tests/
```

The `test` extra carries the platform (`goga>=2.0`, unpinned) and the test stack; the unpinned
platform is deliberate — a platform release that changes the development pipeline shape must
surface as test failures, not silent drift.

`CODEMANIFEST` and `.usages/` files are read-only contracts: when implementation and contract
disagree, the implementation is what gets fixed.
