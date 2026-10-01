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
platform is present whenever the tool runs. The tool is installed into the project's goga
docker image — the environment goga commands run in.

### Declare it as a project dependency

Add the tool to the project's `.goga/config.yml`:

```yaml
tools:
  autonomous: latest
```

A plain `goga install` during the image build then resolves it together with the rest of the
project's declared tools:

```dockerfile
FROM <goga-base-image>

USER root

COPY . /tmp/project
RUN cd /tmp/project && goga install && rm -rf /tmp/project

USER goga
```

### Install it by name

Install the tool by name during the image build:

```dockerfile
FROM <goga-base-image>

USER root

COPY . /tmp/project
RUN cd /tmp/project && goga install autonomous && rm -rf /tmp/project

USER goga
```

## Documentation

- [Architecture](architecture.md) — the cell map and the amendment data flow
- [API reference](api/facade.md) — the facade, the recipe zone, the development domain, and the
  recipe model

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
