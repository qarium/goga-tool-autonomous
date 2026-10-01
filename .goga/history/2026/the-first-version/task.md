# Autonomous development pipeline by fixed workflow amendment — goga-tool-autonomous

## Current State

The repository is a greenfield Python package `goga-tool-autonomous` with no implementation:

- `pyproject.toml` is configured (setuptools + setuptools-scm, Python >= 3.10, empty `[project.dependencies]`, test extra with pytest / pytest-cov / pytest-mock / ruff — `goga` is **not** declared yet).
- `goga_tool_autonomous/__init__.py` is empty; `README.md` is a stub.
- The cell schema is empty (`goga schema` → `[]`) — no architecture exists yet; this task feeds the prototype stage that will create it.
- The repository's authored `.goga/history/2026/the-first-version/` topic holds the PRD and the accepted ADR this task is formulated from.
- The authored `.goga/workflows/development.yml` already carries everything the tool would contribute (`approve: auto` on all six gated stages, `accept-result: manual: false`, the `build` extend entry) — a natural no-op in the tool's own repository. The file stays as-is and is the authoritative reference for the build extension values.
- Synced goga platform usages are available read-only under `.goga/usages/github/goga/` (hooks registration, pipeline amendment semantics).

## Description

Implement the `goga-tool-autonomous` package as a goga tool that makes the `development` pipeline run unattended, entirely through the published hooks mechanism (no goga code changes):

1. **Facade** — the package exposes `register_hooks(hooks)` subscribing exactly one hook: address `pipeline` / `amend_workflow`, hook name `autonomy`, the callable taking only `context`. No `main` or `install` facades.
2. **Hook** — a pure function of the delivered facts: the contribution document is assembled at each call, the hook keeps no state and no cache, and adds no internal exception handling (failures flow through the hard-action channel as clean command errors naming the tool and the action).
3. **Gate** — the hook contributes only when `context.pipeline.name == "development"` exactly (`source` and display name ignored); for every other pipeline the tool is silent.
4. **Contribution** (development only), built as a declarative `WorkflowDocument`-shaped document:
   - `approve: auto` for each gated stage — `architecture-review`, `apply-architecture`, `code-design`, `design-review`, `coding-plan`, `plan-review` — whose authored entry in `context.workflow` carries no `approve`; when `context.workflow` is `None` (no authored workflow resolved), all six entries are contributed.
   - Always, unchecked: `accept-result` with `manual: false`, and the `extend.build` entry verbatim from the reference workflow `.goga/workflows/development.yml` (title `Build implementation`, after `commit-changes`, timeout `8h`, the goga build entrypoint invoked with the run's plan artifact, `.ralphex` cleanup in `after_script`).
   - Nothing else: no `prompt`, no `memory`, no other pipelines, no configuration amendments, no project-file writes.
5. **Recipe-as-data** — the pipeline → contribution knowledge (pipeline name, gated-stage set, contribution template, the single inspect rule) lives as data behind one generic delivery path, so adding another pipeline later is one more data entry. No other pipeline is named or exposed today.
6. **Tests** — exercise the hook against real platform semantics: constructed amendment views plus the real `merge_workflow_overlay` and `compile_flow` against the actual development pipeline, asserting authored-wins behavior, the never-empty contribution, and clean compilation. The test extra gains `goga>=2.0` (no upper bound) so pipeline-shape drift surfaces as test failures.

## Scope

**In scope:**

- The `goga_tool_autonomous` package: `register_hooks` facade, the `autonomy` hook, the recipe data and generic delivery path.
- The autonomy contribution itself: automatic approval on the six gated stages (inspect-then-fill), non-manual acceptance, the build extension with reference configuration.
- Boundary behavior: silence on all non-`development` pipelines, no configuration amendments, no project-file modification, authored-wins semantics, deterministic contribution.
- Tests against the real platform merge and compiler; the `goga>=2.0` test-extra declaration in `pyproject.toml`.

**Out of scope:**

- Amendments to any pipeline other than `development` (bugfix, patch, refinement, review, sync).
- Any configuration-domain contribution (`amend_config` is not subscribed).
- `reflect`, `prompt`, or `memory` content in the contribution — project-authored material stays project-authored.
- Modifying, regenerating, or removing the reference `.goga/workflows/development.yml`.
- Configurability of the tool itself (opt-in/opt-out switches, per-project settings) — an authored workflow is the override mechanism.
- Documentation pages (mkdocs), CI, and distribution infrastructure beyond the package being installable.
- Changes to the goga platform.

## Acceptance Criteria

- The package facade subscribes exactly one hook — address `pipeline`/`amend_workflow`, name `autonomy`, signature taking only `context` — and imports cleanly (an import failure of the facade is fatal to every goga command).
- For any pipeline other than `development`, the hook contributes nothing.
- For `development` with no authored workflow resolved, the contribution contains `approve: auto` for all six gated stages, `accept-result` with `manual: false`, and the `build` extend entry equal to the reference workflow's.
- For `development` with an authored `approve` on a gated stage, the contribution omits that stage's `approve` entry; after the real `merge_workflow_overlay`, authored values are byte-identical to authored intent — nothing overridden, nothing duplicated (same-named authored extend entry wins over the tool's).
- `accept-result` `manual: false` and the `build` extend entry are contributed unconditionally, and the merged workflow still equals authored intent when the author set them.
- The merged workflow passes the real `compile_flow` validation against the actual development pipeline — no structural error, including with skipped stages.
- The contribution is deterministic: identical delivered facts produce an identical document; the document is never empty (at minimum the `manual` entry and the build extension).
- `[project.dependencies]` remains empty; the test extra declares `goga>=2.0` with no upper bound; the full test suite passes in a virtualenv.

## Stack

- **Language:** Python 3.10+
- **Frameworks:** none — a pure subscriber of the goga hooks API
- **Libraries:** none at runtime (empty `[project.dependencies]` per ADR); recipe data uses plain Python data structures, deliberately not pydantic (pydantic would become a runtime dependency)
- **Testing:** pytest, pytest-cov, pytest-mock, ruff (existing), plus `goga>=2.0` in the test extra
- **Packaging:** setuptools + setuptools-scm (existing `pyproject.toml`)
- **Infrastructure:** none

## External Dependencies

| Component | Usage file | Status |
|-----------|------------|--------|
| goga platform (hooks + pipeline amendment API) | `.goga/usages/github/goga/hooks/registering-hooks.md`, `.goga/usages/github/goga/pipeline/registering-hooks.md` | existing (synced) |
| goga platform (overlay merge + compiler surfaces for tests) | `.goga/usages/github/goga/pipeline/hooks/checkpoints.md`, `.goga/usages/github/goga/pipeline/compiler/compile-flow.md` | existing (synced) |
| pytest / ruff / testing rules | `.goga/usages/conventions.md` | existing |

Synced usage files are managed by `goga usages sync` — reference them read-only, never create or update them in the task.

## Risks and Constraints

- **Pipeline-shape coupling:** the enumerated six-stage gated set and the manual `accept-result` are tied to the development-pipeline shape of the goga 2.0.x line; a future goga release renaming or adding gated stages requires a tool revision — surfaced as test failures thanks to the unpinned `goga>=2.0` test dependency, not as stalled unattended runs. A project-authored `development` pipeline deviating from that shape (a gated stage absent, a non-manual `accept-result`) fails `compile_flow` with a structural error after the contribution commits — the clean pre-launch failure accepted in the ADR; no guard is added.
- **Hard-action semantics:** any hook failure stops the command with a clean error and discards the whole contribution — the hook must not swallow or wrap exceptions by design.
- **Import cleanliness is fatal everywhere:** the facade module must stay import-clean; the model import from `goga.pipeline.workflow` is safe because goga itself imports the facade.
- **No runtime goga dependency:** the ecosystem provides goga (the tool is installed into a goga image); declaring it risks resolver conflicts — deviates from the conventions' general dependency rule and from "pydantic for models", both deliberately per ADR.
- **Platform-owned behaviors** the tool must not duplicate: authored-wins merge, `--no-workflow` silence, skip-flags merge before amendment, empty-contribution warning path (unreachable — the contribution is never empty).

## Scope Estimate

Single task. One package, one responsibility (development-pipeline autonomy), one facade + one hook + recipe data + tests; no independent subsystems. Internal decomposition into cells is the prototype stage's work, not a topic-level decomposition.

## Existing Architecture

None — the cell schema is empty. The seed is the empty `goga_tool_autonomous/__init__.py`. Inputs consumed by later stages: the PRD and ADR in this topic directory, and the reference `.goga/workflows/development.yml` (authoritative build-extension values).

## Notes

- `pyproject.toml` needs one change: `goga>=2.0` added to `[project.optional-dependencies].test`. The stray `[tool.setuptools.package-data] swax = []` block is a leftover unrelated to this task and may be cleaned opportunistically.
- Per user decision, the target-API orientation example below is part of the task; exact syntax and internal structure are fixed by the prototype/design stages — this is an orientation, not a specification:

```python
# goga_tool_autonomous — facade invoked by the goga platform
def register_hooks(hooks):
    hooks.subscribe("pipeline", "amend_workflow", "autonomy", autonomy)


def autonomy(context):
    if context.pipeline.name != "development":
        return
    context.contribute(build_contribution(context.workflow))


# the contribution — a WorkflowDocument-shaped document:
# stages: {"architecture-review": {"approve": "auto"}, ...,
#          "accept-result": {"manual": False}},
# extend:  {"build": {...verbatim from the reference workflow...}}
```
