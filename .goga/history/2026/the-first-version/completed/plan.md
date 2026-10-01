# Plan: `the-first-version`

Result of compiling the verified design document (`.goga/history/2026/the-first-version/design.md`,
reviewed by the design-review stage) into a ralphex-compatible execution plan. The plan also
carries the **mandatory rules extracted from the project convention** (`.goga/usages/conventions.md`,
`pyproject.toml`, and the run requirements) — see the `## Mandatory Rules` section; they bind every
task, every development stage, and every local commit.

## Purpose

Implement the complete greenfield contract of the `goga-tool-autonomous` package: the tool that
makes goga `development` pipeline runs unattended. After implementation the package provides:

- one immutable recipe shape (`AutonomyRecipe`) — plain data carrying one pipeline's autonomy
  knowledge;
- one pipeline domain — the development zone: its entry (`development_recipe`, mirroring
  `.goga/workflows/development.yml` verbatim) and its delivery (`build_development_contribution`,
  building the never-empty declarative contribution `WorkflowDocument`);
- the recipe zone facade re-exporting the three names;
- the package facade: `register_hooks` subscribing the single `autonomy` hook to
  `pipeline / amend_workflow`, and `autonomy` resolving the composing pipeline's domain and
  contributing the document through the amendment view.

The most important gaps between contract and code: everything is missing — the repository holds
only the four CODEMANIFESTs, the `.usages/` files, an empty root `__init__.py`, and `pyproject.toml`
(without the mandated `goga>=2.0` test-extra entry).

Overall implementation strategy: bottom-up cell order (`recipe/model` → `recipe/development` →
`recipe` facade → package facade), TDD per entity (contract tests first, logic tests after
implementation, integration tests last), every entity developed through **REPL cycles** against the
real installed platform (goga 2.0.0), with the project-convention linter/formatter gate enforced at
every task and before every local commit.

## Context

### Contract Surface

**Entity: `AutonomyRecipe`**
- Type: `class` (Entity — four properties, no methods)
- Declared `location`: `goga_tool_autonomous/recipe/model/recipe.py`
- Facade obligation: must be importable from `goga_tool_autonomous.recipe.model` (and, via the
  embedding chain, from `goga_tool_autonomous.recipe` and `goga_tool_autonomous`)
- Signature (constructor): `AutonomyRecipe(pipeline: str, gated_stages: list[str], accept_stage: str, build_extend: dict[str, str | list[str]])`
- Properties:
  - `pipeline -> str` — exact target pipeline name; compared verbatim against the composing
    pipeline's name — source and display name never participate
  - `gated_stages -> list[str]` — stages receiving the approve instruction `auto` when their
    authored entry carries no approve instruction
  - `accept_stage -> str` — the acceptance stage receiving the unconditional non-manual instruction
  - `build_extend -> dict[str, str | list[str]]` — the build extension entry as plain data in the
    extend-entry vocabulary of `workflow_document` (title, after, timeout, script, after_script)
- Semantic requirements from annotations: construction captures all four fields; instances expose
  them read-only; a data carrier only — no methods, no computed state, no I/O; plain data
  structures only (no pydantic) — the cell-wide deviation from `conventions`
- Imported dependencies: none (leaf cell). Usages context: `conventions`, `workflow_document`
- Annotation cascade: file level (recipe knowledge is plain data; pydantic deviation accepted for
  this cell; empty runtime dependencies) → entity level (immutable data recipe, single source of
  every entry the delivery path contributes) → property level (see above)

**Entity: `development_recipe`**
- Type: `function` (Routine — pure factory)
- Declared `location`: `goga_tool_autonomous/recipe/development/entry.py`
- Facade obligation: must be importable from `goga_tool_autonomous.recipe.development` (and via
  embeddings from `goga_tool_autonomous.recipe` and `goga_tool_autonomous`)
- Signature: `development_recipe() -> entry: AutonomyRecipe`
- Semantic requirements from annotations: values mirror the reference workflow
  `.goga/workflows/development.yml` verbatim — `gated_stages` is exactly `architecture-review`,
  `apply-architecture`, `code-design`, `design-review`, `coding-plan`, `plan-review`;
  `accept_stage` is `accept-result`; `build_extend` carries title `Build implementation`, after
  `commit-changes`, timeout `8h`, the goga build entrypoint invoked with the run's plan artifact,
  and the after_script cleanup; pure and deterministic — every call returns an equal entry; the
  reference file is never read at runtime; data only
- Imported dependencies: `AutonomyRecipe` from `goga_tool_autonomous/recipe/model` (+ the
  `recipe` practice, aliased `recipe_guide`). Usages context: `conventions`, `workflow_document`,
  `goga_dependency`
- Annotation cascade: file level (development zone; the reference is authoritative documentation,
  never read at runtime) → routine level (see above)

**Entity: `build_development_contribution`**
- Type: `function` (Routine — pure transformer)
- Declared `location`: `goga_tool_autonomous/recipe/development/contribution.py`
- Facade obligation: must be importable from `goga_tool_autonomous.recipe.development` (and via
  embeddings from `goga_tool_autonomous.recipe` and `goga_tool_autonomous`)
- Signature: `build_development_contribution(recipe: AutonomyRecipe, workflow: WorkflowDocument | None) -> document: WorkflowDocument`
- Semantic requirements from annotations (Algorithm):
  1. Place the build extension: put the build extension entry of `recipe` under the fresh
     extension name `build`
  2. Fill the gated stages: for each gated stage of `recipe` — contribute the approve instruction
     `auto` when `workflow` is `None`, the stage has no authored entry, or its authored entry
     carries no approve instruction; skip a stage whose authored entry already carries one
  3. Set the acceptance trigger: contribute the manual instruction `false` for the acceptance
     stage of `recipe` — always, unchecked
  4. Assemble the document from the collected stage instructions and the build extension, and
     return it
- Further requirements: the result is never empty (at minimum the acceptance-stage instruction and
  the build extension); deterministic — the same recipe and workflow always produce the identical
  document; use `workflow_document` for both the construction and the authored-instruction reads
- Constraints: contribute stage instructions and the build extension only — never prompt or memory
  entries; do not implement merge or override logic — the platform owns authored-wins semantics;
  no I/O, no state, no time or environment dependence
- Imported dependencies: `AutonomyRecipe` from `goga_tool_autonomous/recipe/model` (+ the `recipe`
  practice aliased `recipe_guide`). Runtime platform import (the only one in the package, per
  `goga_dependency`): `from goga.pipeline.workflow import WorkflowDocument, WorkflowExtendStage, WorkflowStage`
- Annotation cascade: file level (development zone) → routine level (see above)

**Entity: `register_hooks`**
- Type: `function` (Routine)
- Declared `location`: `goga_tool_autonomous/registration.py`
- Facade obligation: must be importable from `goga_tool_autonomous`
- Signature: `register_hooks(hooks: Hooks)` — `Hooks` denotes the platform registrar exposing
  `subscribe(domain, action, name, hook)`
- Semantic requirements from annotations (Algorithm): subscribe the hook routine `autonomy` under
  domain `pipeline`, action `amend_workflow`, hook name `autonomy` — exactly one subscription,
  unconditional. Requirements: the facade imports cleanly at all times — an import failure stops
  every goga command; no other facades exist (no CLI entry, no install lifecycle). Constraints:
  never subscribe any other address or hook name; no configuration or file reads during
  registration
- Imported dependencies: the three recipe-zone types + the `development` practice from
  `goga_tool_autonomous/recipe`. Usages context: `conventions`, `workflow_document`,
  `hooks_registration`, `pipeline_amendment`, `goga_dependency`

**Entity: `autonomy`**
- Type: `function` (Routine — the amendment hook)
- Declared `location`: `goga_tool_autonomous/registration.py`
- Facade obligation: must be importable from `goga_tool_autonomous`
- Signature: `autonomy(context: WorkflowAmendment)` — must declare exactly the offered parameter
  name `context` (the platform injects hook arguments by offered names: `context`, `self`)
- Semantic requirements from annotations (Algorithm):
  1. Resolve the functional domain for the exact pipeline name of `context` — the development
     pipeline maps to the `development` domain from Imports; a miss returns silently
  2. Build the contribution document with the delivery of the resolved domain —
     `build_development_contribution` applied to the domain entry `development_recipe` — and the
     authored workflow of `context` (a `workflow_document`, or none when unresolved)
  3. Contribute the document through `context`
- Requirements: a pure function of the delivered facts — identical facts produce the identical
  contribution; read only the pipeline identity and the authored workflow from the view
- Constraints: no state, no cache, no internal exception handling — failures propagate as clean
  command errors through the hard action; no project-file or configuration reads; contribute
  nothing beyond the built document
- Registry form (module-level constant in `registration.py`):
  ```
  _PIPELINE_DOMAINS = {
      "development": (development_recipe, build_development_contribution),
  }
  ```
  keys are exact pipeline names; values are (entry factory, delivery) pairs imported from the zone
  facade via relative import (`from .recipe import ...`)

### Re-exports

- Name: `AutonomyRecipe` — Source: `Imports` from `goga_tool_autonomous/recipe/model` (via the
  `recipe` zone facade embedding) — Facade obligation: importable from
  `goga_tool_autonomous.recipe` and `goga_tool_autonomous`
- Name: `development_recipe` — Source: `Imports` from
  `goga_tool_autonomous/recipe/development` (via the zone facade embedding) — Facade obligation:
  importable from `goga_tool_autonomous.recipe` and `goga_tool_autonomous`
- Name: `build_development_contribution` — Source: `Imports` from
  `goga_tool_autonomous/recipe/development` (via the zone facade embedding) — Facade obligation:
  importable from `goga_tool_autonomous.recipe` and `goga_tool_autonomous`

Hierarchy constraint: every embedding source sits at a lower filesystem level than the embedding
facade (`recipe/model` and `recipe/development` below `recipe`; `recipe` below the package root).

### Entity Interaction and Data Flow (verbatim from the design)

```
goga platform (run / card composition of the `development` pipeline)
  │ 1. imports the facade module goga_tool_autonomous            [call_register_hooks]
  ▼
register_hooks(hooks)                                   [registration.py]
  └─ hooks.subscribe("pipeline", "amend_workflow", "autonomy", autonomy)
       exactly one subscription; tool identity assigned by the platform ("autonomous")
  │
  ▼  pipeline / amend_workflow checkpoint (hard; after workflow decision + runner-skip
  │  merge, before compilation; fires in the run form and the card form alike)
  │
  │ delivered view (read-only proxy over WorkflowAmendment): pipeline, decision, workflow, work
  ▼
autonomy(context)                                       [registration.py]
  │ 1. name = context.pipeline.name                     (exact stem; display/source ignored)
  │ 2. (entry_factory, delivery) = _PIPELINE_DOMAINS[name]   (miss → return silently)
  │ 3. document = delivery(entry_factory(), context.workflow)
  │ 4. context.contribute(document)                     (buffer; commits after a clean return)
  ▼
development_recipe()                                    [entry.py]
  └─ AutonomyRecipe(pipeline="development", gated_stages=<six>, accept_stage="accept-result",
                    build_extend={title, after, timeout, script, after_script})
  ▼
build_development_contribution(recipe, workflow)        [contribution.py]
  ├─ WorkflowExtendStage(after=["commit-changes"], body={title, timeout, script, after_script})
  │    → extend under the fresh name "build"
  ├─ for each gated stage whose authored approve is unset → WorkflowStage(approve="auto")
  └─ WorkflowStage(manual=False) → stages["accept-result"]  (always, unchecked)
  ▼
WorkflowDocument(stages={...}, extend={"build": ...})   (prompt=None, memory=None)
  ▼
platform: merge_workflow_overlay (authored wins per slot) → compile_flow → runner
```

Data flows:

**Scenario A — unattended run, no authored workflow** (decision `disabled` or `silent-miss`, or
an authored workflow resolving to `None`): `context.workflow is None` → the delivery contributes
`approve: auto` for **all six** gated stages, `manual: false` for `accept-result`, and the `build`
extension. The merge starts from the unset shape (no authored entry per name); the compiled flow
runs with every review gate non-interactive, acceptance non-manual, and the build stage after
`commit-changes`.

**Scenario B — partially authored workflow** (the author set `approve` on some stages only): the
delivery skips the stages whose authored entry carries an `approve` instruction and fills the rest;
the acceptance instruction and the build extension are contributed regardless; authored values win
per slot in the platform merge.

**Scenario C — the full reference workflow** (`.goga/workflows/development.yml` authored): every
gated stage already carries `approve: auto`, `accept-result` already carries `manual: false`, and
the authored `extend` already owns the name `build` → the contribution carries only the
`accept-result` stage entry, and the merge drops the contributed `build` extension under the
authored name. **Verified experimentally on goga 2.0.0**: the merged workflow is field-equal to the
authored one, and `compile_flow` output is byte-identical with and without the contribution — the
tool is neutral exactly when the author already authored its knowledge.

**Scenario D — any other pipeline** (name ≠ `development`): the registry lookup misses, `autonomy`
returns without contributing; the delivery sees `None` and continues silently; composition is
identical to a project without the tool.

Entity dependencies (implementation order, bottom-up):

```
goga_tool_autonomous (register_hooks, autonomy; embeddings)
  └─ goga_tool_autonomous/recipe (embeddings; Imports: 3 types + `development` practice)
       ├─ goga_tool_autonomous/recipe/development (development_recipe,
       │    build_development_contribution; Imports: AutonomyRecipe + `recipe` practice)
       │    └─ goga_tool_autonomous/recipe/model (AutonomyRecipe) — leaf
       └─ goga_tool_autonomous/recipe/model
```

Runtime platform imports (`goga.pipeline.workflow`) occur only inside
`recipe/development/contribution.py`; per `goga_dependency` this is safe (goga imports the facade,
so the platform is present whenever the package runs) and keeps the runtime dependency list empty.

### Usages Context

- `conventions` (`.goga/usages/conventions.md`) — the project-wide code and test law, referenced by
  all four manifests. Mandatory Python rules: 3.10+ compatibility, `pyproject.toml` configuration,
  venv execution, relative intra-package imports, pydantic data models (with the sanctioned
  recipe-cell deviation), logging standards, formatting, Google-style docstrings, and the full
  testing standard (structure, naming, mocks, venv). Relevance: every entity of every cell — the
  rules are extracted into this plan's `## Mandatory Rules` section and enforced everywhere.
- `workflow_document` (`.goga/usages/github/goga/pipeline/workflow/parse-workflow.md`) — the
  platform's workflow vocabulary: the `WorkflowDocument` shape, per-stage instruction keys
  (`approve` one of "auto"/"plan"/"dialog", `manual` strictly bool, …), and the extend-entry
  vocabulary (positioning `before`/`after` — at least one required, list[str]; inline overrides
  `agent`/`loop`/`approve` extracted into the model; `body` verbatim; forbidden keys `manual`,
  `notes`, `reflect`, `memory`, `depends_on`, `skip` in extend entries). Relevance:
  `AutonomyRecipe.build_extend` (carried-data vocabulary), `build_development_contribution`
  (construction + authored-instruction reads), `autonomy` (reading `context.workflow`).
- `hooks_registration` (`.goga/usages/github/goga/hooks/registering-hooks.md`) — the facade and
  subscription contract: `register_hooks(hooks)` callback, `hooks.subscribe(domain, action, name,
  hook)`, hook-argument injection by offered names (`context`, `self`), failure behavior (a broken
  import is fatal; a failing hook stops the command). Relevance: `register_hooks`, `autonomy`.
- `pipeline_amendment` (`.goga/usages/github/goga/pipeline/registering-hooks.md`) — the
  `pipeline / amend_workflow` action semantics: error class `hard`; fires after workflow resolution
  and the runner-skip merge, before compilation, in run and card forms; the `WorkflowAmendment`
  reads (`pipeline`, `decision`, `workflow`, `work`); `contribute(document)` buffering (commits
  after a clean return); authored-wins merge per slot. Relevance: `autonomy`.
- `goga_dependency` (`.goga/usages/cooks/goga-dependency.md`) — the platform dependency rule:
  runtime dependencies stay empty (`dependencies = []`); importing platform modules inside the
  package is safe (goga imports the facade); the test extra declares `goga>=2.0` unpinned.
  Relevance: `build_development_contribution` (the runtime `goga.pipeline.workflow` import), the
  facade cells' import-cleanliness, and Task 1's `pyproject.toml` change.

### Imported Usages

- `recipe` (aliased `recipe_guide`) — from cell `goga_tool_autonomous/recipe/model` — source path
  `goga_tool_autonomous/recipe/model/.usages/recipe.md` — the entry shape and field semantics for
  the development zone's entry construction and for the delivery's reads. Referenced in the
  development manifest's global annotation. Used by: Tasks 3 and 4.
- `contribution` — from cell `goga_tool_autonomous/recipe/development` — source path
  `goga_tool_autonomous/recipe/development/.usages/contribution.md` — the delivery call form
  (`build_development_contribution(recipe=…, workflow=…)`) for zone consumers. Referenced in the
  recipe facade manifest's global annotation. Used by: Task 5.
- `development` — from cell `goga_tool_autonomous/recipe` — source path
  `goga_tool_autonomous/recipe/.usages/development.md` — the domain API (entry + delivery) the
  package facade wires into its registry. Referenced in the main manifest's global annotation.
  Used by: Task 6.

### Local Usages

No new `.usages/` files are planned — the design's `.usages/` Update audit found all four cell-level
files current and matching the manifests; each cell's files already partition by functional domain
(the shape / the delivery / the zone domain / the facade domain). They are **read-only** for the
implementation, same as the CODEMANIFESTs:

- `goga_tool_autonomous/recipe/model/.usages/recipe.md` — status: existing, current — related
  entities: `AutonomyRecipe` — no creation/update task
- `goga_tool_autonomous/recipe/development/.usages/contribution.md` — status: existing, current —
  related entities: `build_development_contribution` — no creation/update task
- `goga_tool_autonomous/recipe/.usages/development.md` — status: existing, current — related
  entities: the zone facade embeddings — no creation/update task
- `goga_tool_autonomous/.usages/development.md` — status: existing, current — related entities:
  `register_hooks`, `autonomy`, `_PIPELINE_DOMAINS` — no creation/update task

### External Dependencies

- The goga platform (goga 2.0.0 installed at `/opt/goga`; ref `2.0.x` per `.goga/config.yml`) —
  imported at runtime only inside `contribution.py` (`goga.pipeline.workflow`); declared in the
  `test` extra as `goga>=2.0` unpinned; never a runtime dependency.
- Test/tooling stack from `pyproject.toml` `[project.optional-dependencies].test`: `pytest>=8.0`,
  `pytest-cov>=5.0`, `pytest-mock>=3.10`, `ruff>=0.15.0` (ruff is both linter and formatter).
- No other third-party runtime libraries — the package's runtime `dependencies` list stays empty.

## Facts

- The repository is greenfield for code: only the four CODEMANIFESTs, four `.usages/` files, an
  empty `goga_tool_autonomous/__init__.py`, `pyproject.toml`, `README.md`, `LICENSE`, `docs/`,
  `mkdocs.yml` exist. `tests/` does not exist.
- `goga lint` reports `cells: 4 errors: 0`; the dependency tree is
  `goga_tool_autonomous` → `recipe` → `recipe/development` → `recipe/model` — clean, no cycles.
- The reference workflow `.goga/workflows/development.yml` exists and parses cleanly on goga 2.0.0
  (8 stage entries + 1 extend entry `build`).
- The installed platform exposes `HookRegistrar.subscribe(domain, action, name, hook)`, the hard
  action `pipeline/amend_workflow`, `WorkflowAmendment` (reads `pipeline`/`decision`/`workflow`/
  `work`; single write channel `contribute(document)`), `WorkflowDocument`/`WorkflowStage`/
  `WorkflowExtendStage` (including `WorkflowStage.approve: str | None = None` and the three-state
  `manual`), `merge_workflow_overlay` (authored wins per slot), `compile_flow`, and fixed-name
  hook-argument injection offering exactly `context` and `self` — all verified by the design and
  design-review stages against goga 2.0.0.
- `pyproject.toml` already carries the full ruff configuration (target `py310`, line-length 120,
  rule selection `E,W,F,I,N,UP,B,SIM,PL,PLR,C4,DTZ,PT,ARG,RUF,PTH,C90`, mccabe `max-complexity =
  10`, per-file ignores for `tests/**`, format: double quotes, space indent, LF) and pytest/coverage
  configuration (`testpaths = ["tests"]`, `addopts = "-v --tb=short"`, coverage source
  `goga_tool_autonomous`, branch coverage).
- The `test` extra currently lacks the mandated `goga>=2.0` entry; `[tool.setuptools.package-data]`
  carries a dead `swax = []` entry.
- The run requires the development venv to live outside the project, at `/opt/goga/project` (it does not
  exist yet — Task 1 creates it).
- System Python is 3.12.14; the code must stay compatible with Python 3.10+ (ruff enforces
  `target-version = "py310"`).

## Gap Analysis

- Missing contract entities: all five — `AutonomyRecipe`, `development_recipe`,
  `build_development_contribution`, `register_hooks`, `autonomy`.
- Missing facade exposure: `goga_tool_autonomous/recipe/model/__init__.py`,
  `goga_tool_autonomous/recipe/development/__init__.py`, `goga_tool_autonomous/recipe/__init__.py`
  do not exist; `goga_tool_autonomous/__init__.py` exists but is empty (no re-exports, no
  `__all__`).
- Incorrect `location` placement: none yet (greenfield — locations are created fresh per contract).
- API mismatches: none yet (greenfield).
- Behavioral mismatches: none yet (greenfield).
- Existing code that can be reused: `pyproject.toml` configuration (ruff/pytest/coverage) is
  already contract-compliant except the two Task 1 fixes; nothing else.
- Test coverage gaps: the entire test tree (layout per the design's General Setup) is missing —
  20 test scenarios planned across 5 test files.
- Missing visibility in workspace or git: the package skeleton directories (`recipe/model`,
  `recipe/development`) are untracked and empty; `tests/` absent.
- `pyproject.toml` gaps: missing `goga>=2.0` in the `test` extra (mandated by `goga_dependency`);
  dead `swax` package-data entry to drop.

---

## Mandatory Rules

> Extracted from the project convention (`.goga/usages/conventions.md` — the `conventions` practice
> referenced by all four CODEMANIFESTs), the `pyproject.toml` tool configuration, and the run
> requirements. **These rules are MANDATORY for every task, every development stage, and every
> local commit.** Precedence per the project conventions: the contract first, the package boundary
> and facade obligations second, these project conventions next, target-language idioms last. The
> only sanctioned deviations are the ones listed explicitly below (they come from the manifest
> headers, i.e. from the contract, and therefore win).

### M1. Coding style (from `conventions` — Development)

- Python 3.10 and above only; test code included.
- `pyproject.toml` is the only configuration surface — no setup.py, no cfg files, no tool side
  config files.
- Execute all code within a virtualenv — create it if missing. **For this project the venv lives
  outside the project at `/opt/goga/project`** (run requirement). Every python/pytest/ruff command in
  this plan runs through `/opt/goga/project/bin/…`.
  **Environment adaptation (recorded in Task 1)**: the container's `/opt` is root-owned and
  unwritable (no sudo/su/caps), so the mandated `/opt/project` cannot be created; the venv lives at
  `/opt/goga/project` instead — still outside the project, satisfying the run requirement's intent.
- Imports: relative imports for all intra-package references (`from .recipe import …`,
  `from ..utils import helper`); absolute imports only for stdlib and third-party (e.g.
  `from goga.pipeline.workflow import …`). An absolute import of this package's own modules inside
  the package is forbidden.
- Data models: pydantic with `kw_only=True` and empty defaults — **sanctioned deviation (manifest
  headers of the recipe cells)**: recipe data is a `@dataclass(frozen=True, kw_only=True)` plain
  carrier with no pydantic and no defaults, because the package keeps its runtime dependencies
  empty. This deviation applies to `AutonomyRecipe` only; it does not license pydantic-free models
  anywhere else.
- Logging per `conventions` (`logging` library, structured, lowercase messages) — application
  surface in this package: **none**. No logging anywhere in the package (the design's recorded
  decision — the platform already logs the meaningful moments). Do not add loggers.
- Code formatting (source layout): inside function and method bodies, logical blocks are separated
  by one blank line — variable initialization from conditionals/loops, loops from conditions, data
  preparation from processing, processing from the return.
- Docstrings: all public functions, methods, and classes MUST have Google-style docstrings — first
  line capitalized and ending with a period; `Args` when parameters exist; `Returns` when a value
  is returned; `Raises` for exceptions beyond built-in types.
- Dependencies: every third-party library MUST be in `pyproject.toml` with a minimum version.
  Runtime `dependencies = []` stays empty (per `goga_dependency`).
- Type hints are mandatory (Python cell rules). Allowed shapes: `str`, `int`, `float`, `bool`,
  `list[T]`, `dict[str, T]`, `T | None`. Forbidden: `*args`, `**kwargs`, unparameterized `dict` /
  `list`.
- Cross-cutting package constraints from the contract: no `try/except` anywhere in the package, no
  validation, no caching, no state, no configuration or file reads (failures propagate to the
  platform's hard action).

### M2. Test writing rules (from `conventions` — Testing)

- Tools: pytest (running), ruff (linting and formatting test code), pytest-cov (coverage).
- Tests mirror the source tree directly, without an intermediate root package directory:
  `goga_tool_autonomous/recipe/model/recipe.py` → `tests/recipe/model/test_recipe.py`; tests for
  root-package modules go directly in `tests/` (e.g. `tests/test_registration.py`); integration
  tests covering multiple packages go directly in `tests/` (`tests/test_integration.py`).
- Every test directory MUST contain an `__init__.py`. Shared fixtures live in `tests/conftest.py`;
  local fixtures in `tests/<package>/conftest.py`.
- Naming: files `test_<module>.py`; functions `test_<what>_<scenario>`
  (e.g. `test_complexity_with_empty_input`); grouping `class Test<Component>:`.
- Test types and coverage: unit tests for every public function/method/class with the main scenario
  and typical data; edge cases for empty inputs (`None`, `""`, `[]`, `{}`), boundary values,
  invalid types, and expected exceptions via `pytest.raises`; integration tests only for
  interaction between modules/packages.
- Boundary tests (thresholds, ranges, state transitions) use `@pytest.mark.parametrize` with a
  table of values including each boundary.
- Mocks only at external boundaries: pure logic is tested mock-free; file I/O uses the `tmp_path`
  fixture exclusively; subprocesses and external dependencies are `mock.patch`-ed (at the import
  point). Business-logic tests stay mock-free. This package needs no mocks at all (pure logic;
  `tmp_path` only in integration tests).
- Self-documenting test names; keep comments minimal.
- All test libraries MUST be declared in `pyproject.toml` under
  `[project.optional-dependencies].test`.
- Test classification (plan conventions, binding the TDD workflow): **contract tests** — facade
  accessibility, public API shape, method/property signatures — written FIRST in each coding task
  and expected to fail initially; **logic tests** — behavioral requirements (positive, negative,
  edge) — written AFTER implementation; **integration tests** — cross-entity/end-to-end scenarios —
  separate tasks after all coding tasks of the package. Integration tests never replace contract or
  logic tests.
- Tests import entities from the cell facade (e.g. `from goga_tool_autonomous.recipe.model import
  AutonomyRecipe`), not from deep implementation modules — the facade is the tested surface.

### M3. Linters and formatters — enforced across all development stages and local commits

- ruff (>=0.15.0) is the project's linter AND formatter, configured in `pyproject.toml`
  (target `py310`, line-length 120, rules `E,W,F,I,N,UP,B,SIM,PL,PLR,C4,DTZ,PT,ARG,RUF,PTH,C90`,
  mccabe `max-complexity = 10`, per-file ignores for `tests/**`; format: double quotes, space
  indent, LF line endings).
- Task gate (every task, every stage): `ruff check goga_tool_autonomous/ tests/` must exit 0, and
  `ruff format goga_tool_autonomous/ tests/` must be applied (no diff left unformatted) before a
  task is complete. Lint covers test code equally.
  **Environment adaptation (recorded in Task 1)**: the installed ruff (0.16.9) also formats Python
  code blocks inside Markdown, so the bare `ruff format` / `ruff format --check` commands rewrite
  the read-only `.usages/` contract files (M5 violation) and `--check` exits 1 on them. Both
  formatter commands therefore run with `--exclude '.usages'` (a CLI scope choice, not a config
  relaxation: `ignore = []` and the formatter config stay untouched).
- Complexity gate: ruff's mccabe check enforces max function complexity 10 — decompose rather than
  suppress.
- **Local commit gate (mandatory)**: before every local `git commit`, the full gate must pass in
  the `/opt/goga/project` venv, in this exact order:
  1. `/opt/goga/project/bin/python -c "import goga_tool_autonomous"` (facade import — a broken import
     is fatal to every goga command),
  2. `/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/` (exit 0),
  3. `/opt/goga/project/bin/ruff format --check --exclude '.usages' goga_tool_autonomous/ tests/`
     (exit 0),
  4. `/opt/goga/project/bin/python -m pytest tests/ -x` (all green).
  A commit made with a failing gate violates this plan. If the gate fails, fix the implementation
  code — never weaken the tests, never widen `ignore = []`, never relax the formatter config.
- `CODEMANIFEST` and `.usages/` files are never touched by lint fixes or any other edit.

### M4. REPL-cycle development workflow (structuring rule for all coding tasks)

Development of every entity proceeds through interactive evaluation cycles in the project venv
interpreter — not blind write-then-run:

1. **Open a REPL** — `/opt/goga/project/bin/python -i` (the `/opt/goga/project` venv); import the module
   under development and the real platform APIs (`goga.pipeline.workflow`,
   `goga.pipeline.compiler`, the parsed reference workflow).
2. **Evaluate continuously** — exercise the entity's behavior interactively against the real
   platform before and while writing tests: parse the reference workflow, construct documents,
   merge overlays, compile flows. Expected values pinned in tests come from REPL observations of
   the real platform, not from assumptions.
3. **Hot reload** — after each source edit, pick up the change inside the same session with
   `importlib.reload(<module>)` (then re-import the facade names / rebuild dependent instances);
   do not restart the interpreter to pick up a change within a task.
4. **Migrate to source files** — once a REPL expression is verified (observed output equals the
   designed expectation), migrate it verbatim into the source or test file. Committed code is the
   REPL-verified form, not a re-typed approximation.
5. **Scratch discipline** — experiments live in the REPL session or in scratch files under `/tmp`
   (outside the repository); nothing unverified enters the repository; no scratch files are
   committed.

REPL cycles are embedded in the ralphex protocol steps of every coding task below (STEP 1
expectation pinning, STEP 2 implementation, STEP 5 debugging) as explicit checkboxes.

### M5. Contract immutability and boundaries

- The four `CODEMANIFEST` files and all `.usages/` files are **read-only** contract definitions and
  documentation. If the implementation does not match the contract, fix the implementation — never
  the contract.
- No new cells, no new facade-level interfaces beyond the declared contract, no package-boundary
  expansion. Internal helpers within the existing cells are allowed when they preserve the contract
  surface and the `location` placement.
- Every implementation and test unit must stay traceable to a contract entity, property, method,
  or described requirement.

---

## Tasks

> **Package ordering rule**: coding tasks for each package (cell) are completed before starting the
> next. Within each coding task, contract tests are written first (TDD workflow). Cell order:
> `recipe/model` → `recipe/development` → `recipe` facade → `goga_tool_autonomous` (registration +
> root facade) → integration. The `## Mandatory Rules` section binds every task; each task's
> checkboxes include the convention gates explicitly.

### Task 1: Development environment, package skeleton, and test scaffolding (infrastructure)

This task prepares everything the later TDD tasks build on: the `/opt/goga/project` venv (outside the
project — run requirement; conventions: create if missing), the `pyproject.toml` fixes mandated by
`goga_dependency`, the package directory skeleton with docstring-only `__init__.py` files (so the
editable install exposes the full package tree and the facade imports cleanly from the start), and
the test tree with the shared fixtures designed in the design's General Setup. No contract entity
is implemented here.

**Usages relevant to this task:**
- `conventions`: venv execution (create if missing); tests mirror the source tree; `__init__.py`
  in every test directory; shared fixtures in `tests/conftest.py`; all test libraries declared
  under `[project.optional-dependencies].test`.
- `goga_dependency`: add `"goga>=2.0"` (unpinned above) to the `test` extra; keep
  `dependencies = []` untouched.

**CRITICAL: `CODEMANIFEST` files — read-only contract definitions. Do NOT modify them. If
implementation does not match the contract, fix the implementation — never fix the contract. The
`.usages/` files are equally read-only.**

- [x] Create the venv outside the project: `python3 -m venv /opt/goga/project` (skip creation if it
  already exists; conventions: create if missing) — **adapted**: `/opt` is root-owned and unwritable
  in this container (no sudo/su/caps/docker), so the mandated `/opt/project` cannot exist; the venv
  was created at `/opt/goga/project` (goga-owned, still outside the project) and every plan path
  was adapted accordingly (Task 1, recorded here once)
- [x] Update `pyproject.toml`: add `"goga>=2.0"` to `[project.optional-dependencies].test` (no
  upper bound, per `goga_dependency`); keep `dependencies = []` untouched; remove the dead
  `[tool.setuptools.package-data]` `swax = []` entry
- [x] Install the package editable with the test extra, from the project root:
  `/opt/goga/project/bin/pip install -e '.[test]'` — then verify the toolchain:
  `/opt/goga/project/bin/python -m pytest --version` and `/opt/goga/project/bin/ruff --version` and
  `/opt/goga/project/bin/python -c "import goga; print('platform present')"`
  (installed: pytest 9.1.1, ruff 0.16.9, goga 2.0.1 from PyPI — the unpinned test-extra platform)
- [x] Create the package skeleton (docstring-only `__init__.py` per package — one-line Google-style
  module docstring; no re-exports yet, they come with each cell's coding task):
  `goga_tool_autonomous/recipe/__init__.py`, `goga_tool_autonomous/recipe/model/__init__.py`,
  `goga_tool_autonomous/recipe/development/__init__.py`; replace the empty
  `goga_tool_autonomous/__init__.py` with the same docstring-only form
- [x] Create the test tree with `__init__.py` in every directory: `tests/__init__.py`,
  `tests/recipe/__init__.py`, `tests/recipe/model/__init__.py`,
  `tests/recipe/development/__init__.py`
- [x] Create `tests/conftest.py` with the two shared fixtures exactly as designed (imports:
  `importlib.resources`, `pathlib.Path`, `goga.pipeline.workflow.parse_workflow`):
  - `development_pipeline_path` — the real installed pipeline file, located via
    `importlib.resources.files("goga") / "assets" / "pipelines" / "development.yml"` (a platform
    release changing the development pipeline shape must surface as test failures — that is the
    unpinned-`goga` rationale of `goga_dependency`)
  - `reference_workflow` — session-scoped, read-only:
    `parse_workflow(Path(__file__).resolve().parents[1] / ".goga" / "workflows" / "development.yml")`
    (for `tests/conftest.py`, `parents[1]` is the project root)
- [x] Verify facade import-cleanliness: `/opt/goga/project/bin/python -c "import goga_tool_autonomous"`
  (exit 0 — a broken facade import is fatal to every goga command)
- [x] Verify test collection: `/opt/goga/project/bin/python -m pytest tests/` — reports "no tests ran"
  (exit code 5 is expected and acceptable at this stage; there must be no collection errors)
- [x] Lint + format: `/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/` and
  `/opt/goga/project/bin/ruff format goga_tool_autonomous/ tests/` — both clean — **adapted**: both
  formatter commands run with `--exclude '.usages'` (see the M3 note) so the read-only `.usages/`
  files stay untouched; `ruff check` passes without exclusion
- [x] Verify the contracts are untouched: `goga lint` still reports `cells: 4 errors: 0`

### Task 2: `AutonomyRecipe` — the recipe shape cell (TDD coding)

This task implements the leaf cell `goga_tool_autonomous/recipe/model`: the `AutonomyRecipe`
entity at `goga_tool_autonomous/recipe/model/recipe.py` and its facade re-export in the cell's
`__init__.py`. It is an immutable plain-data carrier with four read-only properties — no methods,
no validation, no I/O. Implementation form (designed and verified):
`@dataclass(frozen=True, kw_only=True)` — the cell-wide sanctioned deviation from `conventions`'
pydantic rule (manifest header: runtime dependencies stay empty). No defaults: an entry without
all four fields is meaningless, and the constructors are few and internal.

**Usages relevant to this task:**
- `conventions`: M1 coding style (relative imports, Google docstrings, blank-line block
  separation, type hints) and M2 test rules (tests at `tests/recipe/model/test_recipe.py`,
  naming `test_<what>_<scenario>`, class grouping, edge cases).
- `workflow_document`: the extend-entry vocabulary `build_extend` carries — positioning
  `before`/`after` (list[str]), inline `agent`/`loop`/`approve`, verbatim `body` (title, timeout,
  script, after_script); extend-entry forbidden keys (`manual`, `notes`, `reflect`, `memory`,
  `depends_on`, `skip`) must not appear in the carried data.

**CRITICAL: `CODEMANIFEST` files — read-only contract definitions. Do NOT modify them. If
implementation does not match the contract, fix the implementation — never fix the contract. The
`.usages/` files are equally read-only.**

Verified code stack trace (from the design — transfer into implementation decisions):

```
1. Input: a consumer (test, future zone, or development_recipe) constructs the entity with four
   values: pipeline: str, gated_stages: list[str], accept_stage: str,
   build_extend: dict[str, str | list[str]].
2. The constructor captures all four fields at once (keyword-only per the conventions' kw_only
   rule) → four properties exist, each returning the captured value verbatim; instances are
   frozen — field assignment raises FrozenInstanceError (read-only exposure).
3. No validation, no coercion, no I/O occurs — the entity is inert data (plain-data deviation
   sanctioned by the manifest header).
4. Output: an immutable AutonomyRecipe instance held by the consumer.
```

Edge cases the carrier tolerates (do not add validation for them): duplicate names inside
`gated_stages`, or a `gated_stages` entry equal to `accept_stage` — the delivery collapses
duplicates in the stages map and an overlap contributes both instructions for that name.

- [x] **STEP 0 (DECLARATION)** — declare this is Task 2: implementing `AutonomyRecipe` in
  `goga_tool_autonomous/recipe/model/recipe.py` with the facade re-export in
  `goga_tool_autonomous/recipe/model/__init__.py`
- [x] **STEP 1 (CONTRACT TESTS)** — create `tests/recipe/model/test_recipe.py` with
  `class TestAutonomyRecipeContract:` — import from the cell facade
  (`from goga_tool_autonomous.recipe.model import AutonomyRecipe`); assert `AutonomyRecipe` is in
  the facade `__all__`; assert the constructor signature via `inspect.signature`: exactly four
  keyword-only parameters `pipeline`, `gated_stages`, `accept_stage`, `build_extend`, no defaults,
  annotations `str`, `list[str]`, `str`, `dict[str, str | list[str]]`; assert each property is
  readable on a constructed instance. Run
  `/opt/goga/project/bin/python -m pytest tests/recipe/model/test_recipe.py -v` — failure at this stage
  is expected (the entity does not exist yet)
- [x] **STEP 2 (IMPLEMENTATION — REPL cycle)** — open `/opt/goga/project/bin/python -i`; evaluate the
  designed form interactively: construct with the four keyword arguments; verify property reads
  return each value verbatim; verify `dataclasses.FrozenInstanceError` on field assignment;
  verify equality semantics of equal instances. After each edit of
  `goga_tool_autonomous/recipe/model/recipe.py`, hot-reload with `importlib.reload` of the module
  and re-run the checks in the same session. Migrate the REPL-verified form into the file:
  `@dataclass(frozen=True, kw_only=True)` with a Google-style docstring covering the four `Args`
  and the plain-data deviation; add the facade re-export to
  `goga_tool_autonomous/recipe/model/__init__.py`: `from .recipe import AutonomyRecipe` with
  `__all__ = ["AutonomyRecipe"]` and a Google-style module docstring
- [x] **STEP 3 (INTERFACE VERIFICATION)** — run
  `/opt/goga/project/bin/python -m pytest tests/recipe/model/test_recipe.py -v` — all contract tests
  pass
- [x] **STEP 4 (LOGIC TESTS)** — add the three behavioral scenarios below to
  `tests/recipe/model/test_recipe.py` (positive + edge; names per M2)
- [x] **STEP 5 (DEBUGGING)** — run `/opt/goga/project/bin/python -m pytest tests/ -x`; for any failure,
  reproduce it in the REPL, fix the implementation code (never the test code), hot-reload,
  re-run — until all tests pass
- [x] **STEP 6 (CONTRACT RE-VERIFICATION)** — facade, API shape, and behavior still match the
  contract: `/opt/goga/project/bin/python -c "from goga_tool_autonomous.recipe.model import
  AutonomyRecipe"` exits 0; the four properties are read-only; no methods were added
- [x] **STEP 7 (LINT)** — `/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/` (exit 0) and
  `/opt/goga/project/bin/ruff format goga_tool_autonomous/ tests/`; decompose if complexity or style
  requires it
- [x] **STEP 8 (COMPLETION)** — mark the checkboxes; run the M3 local-commit gate
  (facade import → ruff check → ruff format --check → `pytest tests/ -x`) before any commit

Logic test scenarios (verbatim from the design — implement exactly):

**`test_recipe_construction_captures_all_fields`**
- Setup: none (pure construction).
- Input: `AutonomyRecipe(pipeline="my-pipeline", gated_stages=["first-review"],
  accept_stage="accept-result", build_extend={"title": "T", "after": ["commit-changes"],
  "timeout": "1h", "script": "make", "after_script": "rm -rf tmp"})`
- Trace: `AutonomyRecipe(pipeline=..., gated_stages=..., accept_stage=..., build_extend=...)` →
  frozen dataclass `__init__` captures the four keyword-only fields → property reads return each
  captured value verbatim
- Assertions:
  ```python
  recipe.pipeline == "my-pipeline"
  recipe.gated_stages == ["first-review"]
  recipe.accept_stage == "accept-result"
  recipe.build_extend["title"] == "T" and recipe.build_extend["after"] == ["commit-changes"]
  ```
- Sufficiency: pins the four-property contract — construction captures everything, reads return it
  verbatim; prevents a future refactor from dropping or renaming a field.

**`test_recipe_fields_are_read_only`**
- Setup: `recipe = AutonomyRecipe(pipeline="p", gated_stages=[], accept_stage="a",
  build_extend={})`.
- Input: `recipe.pipeline = "other"` (assignment).
- Trace: attribute assignment on a frozen dataclass instance → `dataclasses.FrozenInstanceError`
  raised.
- Assertions: `with pytest.raises(FrozenInstanceError): recipe.pipeline = "other"`.
- Sufficiency: the read-only exposure requirement — prevents a mutable-recipe refactor that would
  let a consumer (or a hook bug) mutate shared autonomy knowledge.

**`test_recipe_empty_collections`**
- Setup/Input: `AutonomyRecipe(pipeline="p", gated_stages=[], accept_stage="a", build_extend={})`.
- Trace: construction with empty list/dict → fields captured verbatim.
- Assertions: `recipe.gated_stages == [] and recipe.build_extend == {} and
  recipe.accept_stage == "a"`.
- Sufficiency: the shape stays a dumb carrier at the empty boundary — no defaults injected, no
  validation errors; a hand-built test entry with no gated stages is legal and the delivery must
  cope (it would contribute only acceptance + build).

### Task 3: `development_recipe` — the development zone entry (TDD coding)

This task implements the first entity of `goga_tool_autonomous/recipe/development`: the pure
factory `development_recipe()` at `goga_tool_autonomous/recipe/development/entry.py`, plus its
re-export on the cell facade. The values mirror `.goga/workflows/development.yml` verbatim — the
reference is authoritative documentation, never read at runtime (all values are compile-time
constants of the zone; nothing is read from disk).

**Usages relevant to this task:**
- `conventions`: M1 style (relative intra-package import
  `from ..model import AutonomyRecipe` — the model cell is the sibling package `recipe/model`;
  Google docstring; blank-line block separation) and M2 test rules
  (`tests/recipe/development/test_entry.py`).
- `recipe_guide` (imported usage, from `goga_tool_autonomous/recipe/model/.usages/recipe.md`): the
  entry shape and field semantics — the defining example matches the frozen-dataclass form; the
  consumer import path `from goga_tool_autonomous.recipe import AutonomyRecipe` matches the zone
  facade built in Task 5.
- `workflow_document`: the vocabulary of the mirrored values (gated stages carry `approve: auto`
  in the reference; the acceptance stage carries `manual: false`; the `build` extend entry carries
  title/after/timeout/script/after_script).

**CRITICAL: `CODEMANIFEST` files — read-only contract definitions. Do NOT modify them. If
implementation does not match the contract, fix the implementation — never fix the contract. The
`.usages/` files are equally read-only.**

Verified code stack trace (from the design):

```
1. Input: called with no arguments by autonomy (per-run) or by consumers/tests.
2. Constructs and returns AutonomyRecipe(pipeline="development", gated_stages=[...],
   accept_stage="accept-result", build_extend={...}) → values mirror
   .goga/workflows/development.yml verbatim:
   - gated_stages is exactly ["architecture-review", "apply-architecture", "code-design",
     "design-review", "coding-plan", "plan-review"] — the six stages carrying approve: auto in the
     reference, in file order.
   - accept_stage is "accept-result" — the stage carrying manual: false in the reference; the
     stage exists in the development pipeline with trigger: manual, so the explicit cancel always
     has something to cancel.
   - build_extend carries title="Build implementation", after=["commit-changes"], timeout="8h",
     script='python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"',
     after_script="rm -rf .ralphex" — verbatim from the reference extend.build entry.
3. Nothing is read from disk — the reference file is documentation only.
4. Output: a fresh, equal-on-every-call AutonomyRecipe (determinism; fresh mutable containers per
   call so no caller can mutate shared state).
```

- [x] **STEP 0 (DECLARATION)** — declare this is Task 3: implementing `development_recipe` in
  `goga_tool_autonomous/recipe/development/entry.py` with the re-export on the cell facade
- [x] **STEP 1 (CONTRACT TESTS)** — create `tests/recipe/development/test_entry.py` with
  `class TestDevelopmentRecipeContract:` — import from the cell facade
  (`from goga_tool_autonomous.recipe.development import development_recipe`); assert
  `development_recipe` is in the facade `__all__`; assert via `inspect.signature`: zero
  parameters, return annotation `AutonomyRecipe`. Run the file — failure is expected at this stage
  (observed: ImportError, as designed)
- [x] **STEP 2 (IMPLEMENTATION — REPL cycle)** — open `/opt/goga/project/bin/python -i`; first pin the
  expectations against the real reference: `parse_workflow` the repo
  `.goga/workflows/development.yml`, list the stages whose entry carries `approve == "auto"`,
  read `extend["build"]` (after/title/timeout/script/after_script) — these observed values are the
  assertion basis for STEP 4. Then evaluate the factory interactively (constant construction with
  fresh `list`/`dict` per call), hot-reloading `entry` after each edit, and migrate the verified
  form into `goga_tool_autonomous/recipe/development/entry.py` with a Google-style docstring;
  add the re-export to `goga_tool_autonomous/recipe/development/__init__.py`
  (`from .entry import development_recipe`, `__all__ = ["development_recipe"]` — extended in
  Task 4)
- [x] **STEP 3 (INTERFACE VERIFICATION)** — run
  `/opt/goga/project/bin/python -m pytest tests/recipe/development/test_entry.py -v` — all contract
  tests pass (2 passed)
- [x] **STEP 4 (LOGIC TESTS)** — add the two behavioral scenarios below (the mirroring test uses
  the shared `reference_workflow` fixture from `tests/conftest.py`)
- [x] **STEP 5 (DEBUGGING)** — `/opt/goga/project/bin/python -m pytest tests/ -x`; reproduce any
  failure in the REPL, fix implementation (never tests), hot-reload, re-run (11 passed, nothing
  to debug)
- [x] **STEP 6 (CONTRACT RE-VERIFICATION)** — facade + API shape + behavior;
  `/opt/goga/project/bin/python -c "from goga_tool_autonomous.recipe.development import
  development_recipe"` exits 0; the routine performs no action beyond construction
- [x] **STEP 7 (LINT)** — `ruff check` + `ruff format` over `goga_tool_autonomous/ tests/` — clean
  (one E501 in the test fixed by extracting the comprehension into a local)
- [x] **STEP 8 (COMPLETION)** — mark checkboxes; run the M3 local-commit gate before any commit

Logic test scenarios (verbatim from the design):

**`test_entry_mirrors_reference_workflow`**
- Setup: fixture `reference_workflow` (parsed repo `.goga/workflows/development.yml`).
- Input: `entry = development_recipe()`
- Trace: `development_recipe()` → `AutonomyRecipe(pipeline="development", gated_stages=[six],
  accept_stage="accept-result", build_extend={title, after, timeout, script, after_script})` →
  compared against `parse_workflow(reference).stages` / `.extend`
- Assertions:
  ```python
  entry.pipeline == "development"
  entry.gated_stages == [s for s in reference.stages if reference.stages[s].approve == "auto"] \
      == ["architecture-review", "apply-architecture", "code-design", "design-review",
          "coding-plan", "plan-review"]
  entry.accept_stage == "accept-result"
  entry.build_extend == {
      "title": "Build implementation",
      "after": ["commit-changes"],
      "timeout": "8h",
      "script": 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"',
      "after_script": "rm -rf .ralphex",
  }
  reference.extend["build"].after == entry.build_extend["after"]
  ```
- Sufficiency: enforces the verbatim-mirroring requirement against the authoritative reference;
  any drift (either side edited alone) fails here instead of silently changing unattended runs.

**`test_entry_deterministic`**
- Setup: none.
- Input: two calls `development_recipe()`.
- Trace: `development_recipe(); development_recipe()` → two constructions from the same constants.
- Assertions: `first == second` (dataclass equality) and `first is not second`;
  `first.gated_stages is not second.gated_stages` (fresh containers — no shared mutable state).
- Sufficiency: pins the "pure and deterministic — every call returns an equal entry" requirement;
  the fresh-container check prevents a shared-list aliasing regression.

### Task 4: `build_development_contribution` — the delivery (TDD coding)

This task implements the second entity of `goga_tool_autonomous/recipe/development`: the pure
transformer `build_development_contribution(recipe, workflow)` at
`goga_tool_autonomous/recipe/development/contribution.py`, plus its re-export on the cell facade.
It carries the package's only runtime platform import —
`from goga.pipeline.workflow import WorkflowDocument, WorkflowExtendStage, WorkflowStage` — which
is safe and mandated by `goga_dependency` (goga imports the facade, so the platform is present
whenever the package runs; declaring goga at runtime would risk resolver conflicts in the goga
image). The relative-import convention does not apply to this third-party import.

**Usages relevant to this task:**
- `conventions`: M1 style + M2 test rules (`tests/recipe/development/test_contribution.py`).
- `workflow_document`: the platform model this routine constructs and reads — per-stage `approve`
  (`str | None`, one of "auto"/"plan"/"dialog", `None` = unset), `manual` (strictly bool,
  three-state: `False` is explicit cancel, distinct from absence), extend-entry positioning
  `before`/`after` (list[str], at least one required) with everything else in the verbatim `body`.
- `recipe_guide` (imported usage): the field semantics of the `recipe` reads.
- `goga_dependency`: the runtime platform-import rule (above).

**CRITICAL: `CODEMANIFEST` files — read-only contract definitions. Do NOT modify them. If
implementation does not match the contract, fix the implementation — never fix the contract. The
`.usages/` files are equally read-only.**

Algorithm (verbatim from the design — the implementation checkboxes follow it):

```
1. Split build_extend into positioning and body:
   extension = WorkflowExtendStage(after = list(build_extend["after"]),
                                   body  = {title, timeout, script, after_script})
   contribution extend map = {"build": extension}
2. gated = {} (ordered by recipe.gated_stages sequence)
3. FOR each stage_name IN recipe.gated_stages:
     IF workflow IS None OR stage_name NOT IN workflow.stages
        OR workflow.stages[stage_name].approve IS None:
       gated[stage_name] = WorkflowStage(approve="auto")
     ELSE: skip (authored approval already present)
4. acceptance = {recipe.accept_stage: WorkflowStage(manual=False)}   (unconditional)
5. RETURN WorkflowDocument(stages = gated + acceptance, extend = {"build": extension})
   (prompt=None, memory=None)
```

Verified code stack trace checkpoints (from the design — each must hold in the implementation):

- `after` is one of the two extracted inline keys (`before`/`after`); everything else stays in
  `body` verbatim (`WorkflowExtendStage` field set: `before, after, agent, loop, approve, body`).
- The `before`/`after` at-least-one rule is satisfied by `after=["commit-changes"]`.
- Extend-entry forbidden keys (`manual`, `notes`, `reflect`, `memory`, `depends_on`, `skip`) are
  absent from the body.
- `WorkflowStage.approve` is `None` exactly when the author left it unset — the read surface of
  the gated decision; a contributed stage sets only the `approve` field (all other fields stay
  `None`, `skip=False` default).
- Inspect-then-fill is consistent with the platform merge (`merge_workflow_overlay._is_set`): the
  merge would fill the slot only when unset anyway; skipping keeps the document minimal ("names
  only the slots it actually fills").
- Three-state `manual`: `False` is explicit cancel, distinct from absence; `accept-result` is
  `trigger: manual` in the pipeline, so the compiler's "manual: false on non-manual stage" error
  can never fire; unconditional contribution is safe — when the author already set `manual`, the
  merge keeps the authored value.
- Never-empty: `extend` always carries `build` and `stages` always carries the acceptance entry —
  the delivery's empty-document discard (with its warning) can never trigger.
- Declarative vocabulary only: stage instructions + one extension entry; no prompt and no memory
  block.
- Determinism: fixed iteration and construction order; no clock, environment, or I/O reads.
- Purity: the authored `workflow` object and its maps are only read, never mutated.
- Errors: none raised by this routine itself (no internal handling, per constraint). A structurally
  impossible input (e.g. `build_extend` missing `"after"`) surfaces as a `KeyError` to the caller
  → the hard action turns it into a clean command error; in practice the recipe is defined
  in-code, so the path is unreachable.

- [x] **STEP 0 (DECLARATION)** — declare this is Task 4: implementing
  `build_development_contribution` in `goga_tool_autonomous/recipe/development/contribution.py`
- [x] **STEP 1 (CONTRACT TESTS)** — create `tests/recipe/development/test_contribution.py` with
  `class TestBuildDevelopmentContributionContract:` — import from the cell facade
  (`from goga_tool_autonomous.recipe.development import build_development_contribution`); assert
  it is in the facade `__all__`; assert via `inspect.signature`: parameters `recipe` (annotation
  `AutonomyRecipe`) and `workflow` (annotation `WorkflowDocument | None`), return annotation
  `WorkflowDocument`. Run the file — failure is expected at this stage (observed: ImportError,
  as designed)
- [x] **STEP 2 (IMPLEMENTATION — REPL cycle)** — open `/opt/goga/project/bin/python -i`; evaluate each
  algorithm step against the real platform models before writing the file: construct
  `WorkflowExtendStage(after=["commit-changes"], body={...})` and inspect its fields; construct
  `WorkflowStage(approve="auto")` / `WorkflowStage(manual=False)` and inspect; build a
  `WorkflowDocument` from them; drive one full call with `workflow=None` and one with the parsed
  reference workflow; verify the authored-instruction read path
  (`workflow.stages[name].approve is None`). Hot-reload the module after each edit and re-run the
  same expressions. Migrate the REPL-verified form into `contribution.py` (runtime platform import
  at the top; Google-style docstring with `Args`/`Returns`; blank-line block separation per M1);
  add the re-export to `goga_tool_autonomous/recipe/development/__init__.py`
  (`__all__ = ["development_recipe", "build_development_contribution"]` — applied in ruff's RUF022
  sorted order `["build_development_contribution", "development_recipe"]`; same names, sorted
  `__all__`)
- [x] **STEP 3 (INTERFACE VERIFICATION)** — run
  `/opt/goga/project/bin/python -m pytest tests/recipe/development/test_contribution.py -v` — all
  contract tests pass (2 passed)
- [x] **STEP 4 (LOGIC TESTS)** — add the seven behavioral scenarios below (positive, negative,
  edge)
- [x] **STEP 5 (DEBUGGING)** — `/opt/goga/project/bin/python -m pytest tests/ -x`; reproduce any
  failure in the REPL (same interpreter session pattern), fix implementation (never tests),
  hot-reload, re-run (20 passed, nothing to debug; the missing-`after` KeyError path verified in
  the REPL as designed)
- [x] **STEP 6 (CONTRACT RE-VERIFICATION)** — facade + API shape + behavior; the algorithm's four
  steps and all checkpoints above hold; no merge/override logic was implemented; no prompt/memory
  entries are contributed
- [x] **STEP 7 (LINT)** — `ruff check` + `ruff format` — clean; decompose if the loop + branches
  approach the complexity threshold (max 10)
- [x] **STEP 8 (COMPLETION)** — mark checkboxes; run the M3 local-commit gate before any commit

Logic test scenarios (verbatim from the design — implement exactly):

**`test_contribution_without_workflow_contributes_everything`** (positive)
- Setup: `entry = development_recipe()`; `workflow = None`.
- Input: `document = build_development_contribution(recipe=entry, workflow=None)`
- Trace:
  ```
  build_development_contribution(entry, None)
    → step 1: extend["build"] = WorkflowExtendStage(after=["commit-changes"], body={title,
      timeout, script, after_script})
    → step 3: workflow is None → all six gated stages → WorkflowStage(approve="auto")
    → step 4: stages["accept-result"] = WorkflowStage(manual=False)
    → step 5: WorkflowDocument(stages=7 entries, extend=1 entry)
  ```
- Assertions:
  ```python
  sorted(document.stages) == sorted([...six gated..., "accept-result"])
  all(document.stages[s].approve == "auto" for s in six gated)
  document.stages["accept-result"].manual is False
  document.extend["build"].after == ["commit-changes"]
  document.extend["build"].body == {"title": "Build implementation", "timeout": "8h",
                                    "script": '...', "after_script": "rm -rf .ralphex"}
  document.prompt is None and document.memory is None
  ```
- Sufficiency: the Scenario-A floor — an unattended run with no authored workflow must receive
  every instruction; this is the tool's core value proposition.

**`test_contribution_with_authored_workflow_never_empty`** (positive)
- Setup: `authored` = `WorkflowDocument(stages={"architecture-review": WorkflowStage(
  approve="auto"), …all six…, "accept-result": WorkflowStage(manual=False)},
  extend={"build": WorkflowExtendStage(after=["commit-changes"], body={…})})` (or the parsed
  reference fixture).
- Input: `document = build_development_contribution(recipe=development_recipe(), workflow=authored)`
- Trace: every gated stage has authored approve → all skipped → only
  `stages["accept-result"] = WorkflowStage(manual=False)` and `extend["build"]` remain
- Assertions:
  ```python
  document.stages.keys() == {"accept-result"}
  document.extend.keys() == {"build"}
  ```
- Sufficiency: the never-empty requirement in its weakest input case — even when the author
  already authored everything, the document still carries the acceptance instruction and the build
  extension (the platform merge then no-ops); prevents an empty document that the delivery would
  discard with a warning.

**`test_contribution_skips_stages_with_authored_approve`** (negative)
- Setup: `authored = WorkflowDocument(stages={"plan-review": WorkflowStage(approve="dialog"),
  "coding-plan": WorkflowStage(approve="auto")})`.
- Input: `document = build_development_contribution(recipe=development_recipe(), workflow=authored)`
- Trace: `plan-review` (dialog) and `coding-plan` (auto) → skipped; remaining four gated stages →
  `approve="auto"`; `accept-result` + `build` as always
- Assertions:
  ```python
  "plan-review" not in document.stages and "coding-plan" not in document.stages
  set(document.stages) == {"architecture-review", "apply-architecture", "code-design",
                           "design-review", "accept-result"}
  ```
- Sufficiency: the inspect-then-fill rule — *any* authored approval instruction (not just `auto`)
  removes the slot from the document; prevents overriding or duplicating authored intent and keeps
  the document naming only the slots it fills.

**`test_contribution_authored_stage_without_approve_still_filled`** (edge)
- Setup: `authored = WorkflowDocument(stages={"code-design": WorkflowStage(prompt="x")})` — the
  stage is authored with another field but approval unset.
- Input: `document = build_development_contribution(recipe=development_recipe(), workflow=authored)`
- Trace: `authored.stages["code-design"].approve is None` → contribute `approve="auto"`; other
  authored fields of that stage untouched (not our vocabulary)
- Assertions: `document.stages["code-design"].approve == "auto"`; all six gated stages present;
  `document.stages["code-design"].prompt is None` (we contribute only the approval instruction)
- Sufficiency: unset-approval detection is field-precise — authorship of *other* fields must not
  suppress the auto-approval fill; also pins that the contributed stage carries nothing but
  `approve`.

**`test_contribution_deterministic_and_pure`** (edge)
- Setup: `authored` = the parsed `reference_workflow` fixture; deep-copied snapshot
  `copy.deepcopy(authored)`.
- Input: `d1 = build_development_contribution(recipe=development_recipe(), workflow=authored)`
  twice.
- Trace: two builds over equal inputs → equal documents; authored object only read
- Assertions: `d1 == d2`; `authored == snapshot` (input not mutated); `d1.stages is not
  authored.stages` and `d1.extend["build"].body is not d2.extend["build"].body` (fresh maps, no
  aliasing of inputs or between results)
- Sufficiency: the determinism/purity requirements — identical facts produce the identical
  contribution and the authored workflow is never mutated; prevents shared-state and
  input-mutation regressions that would corrupt other tools' reads of the same view.

**`test_contribution_with_empty_gated_recipe_contributes_minimum`** (edge)
- Setup: `recipe = AutonomyRecipe(pipeline="development", gated_stages=[],
  accept_stage="accept-result", build_extend={title: "Build implementation",
  after: ["commit-changes"], timeout: "8h", script: <the goga build line>,
  after_script: "rm -rf .ralphex"})` — a hand-built entry with no gated stages.
- Input: `document = build_development_contribution(recipe=recipe, workflow=None)`
- Trace:
  ```
  build_development_contribution(recipe, None)
    → step 3: the loop over the empty gated_stages contributes nothing
    → step 4: stages["accept-result"] = WorkflowStage(manual=False)
    → step 5: WorkflowDocument(stages={accept-result}, extend={build})
  ```
- Assertions:
  ```python
  document.stages.keys() == {"accept-result"}
  document.extend.keys() == {"build"}
  document.stages["accept-result"].manual is False
  ```
- Sufficiency: the never-empty guarantee in its minimal case — the delivery tolerates an empty
  gated list and contributes exactly the acceptance instruction plus the build extension; prevents
  a future refactor that iterates pipeline stages instead of the recipe.

**`test_contribution_duplicate_and_overlapping_gated_names`** (edge)
- Setup: `recipe = AutonomyRecipe(pipeline="p", gated_stages=["code-design", "code-design",
  "accept-result"], accept_stage="accept-result", build_extend={…reference values…})` — a
  duplicated gated name and a gated name equal to the acceptance stage.
- Input: `document = build_development_contribution(recipe=recipe, workflow=None)`
- Trace: `"code-design"` visited twice → the second map assignment collapses the duplicate →
  `stages["accept-result"] = WorkflowStage(manual=False)` overwrites the gated entry
- Assertions:
  ```python
  document.stages.keys() == {"code-design", "accept-result"}
  document.stages["code-design"].approve == "auto"
  document.stages["accept-result"].manual is False
  document.stages["accept-result"].approve is None
  ```
- Sufficiency: pins the documented tolerance of the data carrier's edge inputs (duplicates,
  gated/acceptance overlap) and the deterministic precedence — the unconditional acceptance step
  wins the shared name; prevents validation creeping into the plain-data path.

### Task 5: The recipe zone facade — embeddings (infrastructure)

This task completes the `goga_tool_autonomous/recipe` cell: its facade
`goga_tool_autonomous/recipe/__init__.py` re-exports the three recipe-zone names imported from the
sub-cells (`AutonomyRecipe` from `.model`, `development_recipe` and
`build_development_contribution` from `.development`). The cell declares no own entities — its
contract is exactly the embeddings. Relative imports only (M1); the facade must stay import-clean.

**Usages relevant to this task:**
- `conventions`: M1 style (relative imports, `__all__`, Google-style module docstring).
- `contribution` (imported usage, from
  `goga_tool_autonomous/recipe/development/.usages/contribution.md`): the delivery call form
  (`build_development_contribution(recipe=…, workflow=…)`) re-exported for zone consumers.
- `recipe` (imported usage, from `goga_tool_autonomous/recipe/model/.usages/recipe.md`): the entry
  shape whose consumer import path `from goga_tool_autonomous.recipe import AutonomyRecipe` this
  facade fulfills.

**CRITICAL: `CODEMANIFEST` files — read-only contract definitions. Do NOT modify them. If
implementation does not match the contract, fix the implementation — never fix the contract. The
`.usages/` files are equally read-only.**

- [x] Implement `goga_tool_autonomous/recipe/__init__.py`: relative imports
  `from .model import AutonomyRecipe` and
  `from .development import development_recipe, build_development_contribution`;
  `__all__ = ["AutonomyRecipe", "development_recipe", "build_development_contribution"]`;
  Google-style module docstring (the recipe zone facade — the single contract surface of the zone)
  — applied in ruff's enforced order (isort-sorted import names, RUF022-sorted `__all__`:
  `["AutonomyRecipe", "build_development_contribution", "development_recipe"]`, same three names)
- [x] Verify facade accessibility (per the conventions' facade-check form):
  `/opt/goga/project/bin/python -c "from goga_tool_autonomous.recipe import AutonomyRecipe,
  development_recipe, build_development_contribution"` — exit 0
- [x] Verify the whole suite still passes: `/opt/goga/project/bin/python -m pytest tests/ -x`
  (20 passed)
- [x] Verify the root facade import stays clean: `/opt/goga/project/bin/python -c "import
  goga_tool_autonomous"` — exit 0
- [x] Lint: `/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/` and
  `/opt/goga/project/bin/ruff format goga_tool_autonomous/ tests/` — clean (formatter with
  `--exclude '.usages'` per the M3 adaptation; `--check` confirms 15 files already formatted;
  `goga lint` still `cells: 4 errors: 0`)

### Task 6: `register_hooks` and `autonomy` — the package facade (TDD coding)

This task implements the package-facade cell `goga_tool_autonomous`: both entities share the
declared `location` `goga_tool_autonomous/registration.py` (same location → one task), and the
root facade `goga_tool_autonomous/__init__.py` re-exports `register_hooks`, `autonomy`, and the
three embedded recipe-zone names. `registration.py` imports only from `.recipe` (no platform
import); the module-level registry `_PIPELINE_DOMAINS` maps the exact pipeline name to its
(entry factory, delivery) pair.

**Usages relevant to this task:**
- `conventions`: M1 style + M2 test rules (`tests/test_registration.py` — root-package modules
  are tested directly in `tests/`).
- `hooks_registration`: `register_hooks(hooks)` callback form; `hooks.subscribe(domain, action,
  name, hook)`; the tool identity is assigned by the platform from the package name (this package
  → `autonomous`) — a package never names itself; hook-argument injection by offered names
  (`context`, `self`) — the hook must declare exactly `context`; a broken facade import is the
  platform's single fatal case.
- `pipeline_amendment`: the `pipeline / amend_workflow` semantics — error class `hard`; fires
  after workflow resolution and the runner-skip merge, before compilation, in run and card forms;
  the `WorkflowAmendment` reads `pipeline` (identity — `name` is the discovered file stem,
  `display_name` and `source` never participate), `decision`, `workflow`, `work`;
  `contribute(document)` buffers and commits after a clean return; authored-wins merge per slot.
- `development` (imported usage, from `goga_tool_autonomous/recipe/.usages/development.md`): the
  domain API this facade wires into its registry — the entry factory and the delivery.
- `goga_dependency`: the facade import-cleanliness requirement.

**CRITICAL: `CODEMANIFEST` files — read-only contract definitions. Do NOT modify them. If
implementation does not match the contract, fix the implementation — never fix the contract. The
`.usages/` files are equally read-only.**

Verified code stack traces (from the design):

`register_hooks(hooks)`:
```
1. Input: the platform (a goga command reaching the first hook checkpoint of a run, or
   `goga hooks` inspection) imports the facade module goga_tool_autonomous and calls
   register_hooks(hooks) with the registrar scoped to this tool.
2. The facade import chain executes (__init__.py → .registration, .recipe → .model,
   .development) → import-clean at all times; relative imports only (conventions); the sole
   third-party-touching import is goga.pipeline.workflow inside contribution.py, present by
   construction (goga imports the facade; per goga_dependency). A broken import would be fatal to
   every goga command.
3. hooks.subscribe("pipeline", "amend_workflow", "autonomy", autonomy) → the address exists in
   the action catalog with error class hard; the envelope is valid (non-empty name, callable
   hook, no repeat) → the registrar appends exactly one Subscription.
4. Output: None; one subscription registered. No configuration or file reads; no other addresses,
   no other names (constraint).
```

`autonomy(context)`:
```
1. Input: the platform's amendment walk builds a fresh WorkflowAmendment (pipeline, decision,
   workflow, work) per tool, wraps it in a read-only delivery proxy, and calls the hook by
   injected keyword: autonomy(context=proxy) → the hook declares exactly the offered name
   `context` (positional-or-keyword), so build_hook_arguments delivers it; the proxy passes
   attribute reads and bound-method calls (contribute) and blocks writes.
2. name = context.pipeline.name; look the name up in the module-level registry mapping the exact
   pipeline name to its functional domain (entry factory + delivery) → PipelineIdentity.name is
   the discovered file stem ("development"); display_name ("Development") and source never
   participate; a miss returns None without contributing (the delivery continues silently —
   composition equals a project without the tool); only pipeline.name and workflow are read —
   decision and work are never touched (constraint).
3. document = delivery(entry_factory(), context.workflow) with delivery =
   build_development_contribution, entry_factory = development_recipe → the type flow matches
   (development_recipe() -> AutonomyRecipe feeds recipe; context.workflow is
   WorkflowDocument | None, matching workflow).
4. context.contribute(document) → the single write channel; the buffer replaces whole on
   repeated calls (we call it once); the contribution commits only after the hook returns
   without raising.
5. Output: None; the buffered contribution is the side effect. No state, no cache, no internal
   exception handling — a failure propagates and the platform stops the command with a clean
   error naming the hook, tool, and action (`hook autonomy of tool autonomous failed on
   pipeline.amend_workflow: <reason>`), discarding the whole contribution.
```

Registry form (module-level constant in `registration.py`, documented in
`goga_tool_autonomous/.usages/development.md`):
```
_PIPELINE_DOMAINS = {
    "development": (development_recipe, build_development_contribution),
}
```
keys are exact pipeline names; values are (entry factory, delivery) pairs imported from the zone
facade via relative import (`from .recipe import ...`). Adding a pipeline zone later = one
import, one registry entry, and the domain's embeddings on the facade (per the manifest header
annotation).

- [x] **STEP 0 (DECLARATION)** — declare this is Task 6: implementing `register_hooks` and
  `autonomy` in `goga_tool_autonomous/registration.py` + the root facade re-exports
- [x] **STEP 1 (CONTRACT TESTS)** — create `tests/test_registration.py` with
  `class TestRegistrationContract:` — import from the root facade
  (`from goga_tool_autonomous import register_hooks, autonomy`); assert the facade `__all__`
  contains `register_hooks`, `autonomy`, `AutonomyRecipe`, `development_recipe`,
  `build_development_contribution`; assert via `inspect.signature`: `register_hooks` has exactly
  one parameter `hooks`; `autonomy` has exactly one parameter named `context` (the offered-name
  injection contract — a different name would silently never receive the view). Run the file —
  failure is expected at this stage (observed: ImportError, as designed)
- [x] **STEP 2 (IMPLEMENTATION — REPL cycle)** — open `/opt/goga/project/bin/python -i`; evaluate
  interactively: a recording stub `_Hooks` capturing `subscribe` calls; a fake context
  (`SimpleNamespace(name="development")` + a contribute recorder) driving `autonomy` end-to-end;
  the registry lookup miss for a non-development name. Verify in the REPL that the delivered
  document has exactly the designed shape and that a miss contributes nothing. Hot-reload
  `goga_tool_autonomous.registration` after each edit and re-run. Migrate the verified form into
  `registration.py`: the `_PIPELINE_DOMAINS` constant (relative import
  `from .recipe import development_recipe, build_development_contribution`), then
  `register_hooks(hooks)` and `autonomy(context)` with Google-style docstrings; type the `hooks`
  and `context` parameters with deferred annotations — `from __future__ import annotations` plus
  `if TYPE_CHECKING:` imports of `HookRegistrar` (as `Hooks`) and `WorkflowAmendment` — so
  `registration.py` carries zero runtime platform imports while keeping mandatory type hints
  (M1); update the root
  `goga_tool_autonomous/__init__.py` to re-export `register_hooks`, `autonomy` (relative
  `from .registration import …`) and the three embedded names (relative
  `from .recipe import …`) with `__all__` (5 names) and a Google-style module docstring
  (REPL-verified against the real platform: the real `HookRegistrar(tool="autonomous")` accepted
  exactly one subscription `pipeline/amend_workflow/autonomy` with zero rejections; the real
  `WorkflowAmendment` view and the fake context both received the seven-stage + `build` document;
  the miss and display-name paths contributed nothing; `importlib.reload` confirmed)
- [x] **STEP 3 (INTERFACE VERIFICATION)** — run
  `/opt/goga/project/bin/python -m pytest tests/test_registration.py -v` — all contract tests pass
  (3 passed)
- [x] **STEP 4 (LOGIC TESTS)** — add the six behavioral scenarios below
- [x] **STEP 5 (DEBUGGING)** — `/opt/goga/project/bin/python -m pytest tests/ -x`; reproduce any
  failure in the REPL, fix implementation (never tests), hot-reload, re-run (29 passed, nothing
  to debug)
- [x] **STEP 6 (CONTRACT RE-VERIFICATION)** — facade + API shape + behavior; exactly one
  `subscribe` call with the address `pipeline`/`amend_workflow` and name `autonomy`; the hook
  reads only `pipeline.name`/`workflow`; no try/except, no state, no file/config reads anywhere
  in the package
- [x] **STEP 7 (LINT)** — `ruff check` + `ruff format` — clean (17 files already formatted, no
  edits needed)
- [x] **STEP 8 (COMPLETION)** — mark checkboxes; run the M3 local-commit gate before any commit

Logic test scenarios (verbatim from the design):

**`test_register_hooks_subscribes_single_amendment_hook`** (positive)
- Setup: a recording stub
  `class _Hooks: def subscribe(self, domain, action, name, hook): self.calls.append((domain, action, name, hook))`
  with `calls = []`.
- Input: `register_hooks(_Hooks())`
- Trace: `register_hooks(hooks)` → `hooks.subscribe("pipeline", "amend_workflow", "autonomy",
  autonomy)` → one recorded call; the hook object is the facade-exported `autonomy` function
- Assertions:
  ```python
  len(hooks.calls) == 1
  hooks.calls[0][:3] == ("pipeline", "amend_workflow", "autonomy")
  hooks.calls[0][3] is autonomy   # autonomy imported from the root facade (M2)
  ```
- Sufficiency: the entire subscription contract — exactly one subscription, the correct hard
  address, the correct name, the real hook; prevents any extra subscription or renamed address.

**`test_autonomy_contributes_for_development_pipeline`** (positive)
- Setup: a fake view `pipeline = SimpleNamespace(name="development")`, `workflow = None`; a
  recorder `class _Context: def contribute(self, document): self.contributed = document`
  exposing `pipeline` and `workflow` attributes.
- Input: `autonomy(context=ctx)`
- Trace: `autonomy(ctx)` → `name = ctx.pipeline.name == "development"` → registry hit →
  `document = build_development_contribution(development_recipe(), ctx.workflow=None)` →
  `ctx.contribute(document)`
- Assertions:
  ```python
  ctx.contributed is not None
  ctx.contributed.stages.keys() == {...six gated..., "accept-result"}
  ctx.contributed.extend.keys() == {"build"}
  ```
- Sufficiency: the happy path of the hook — registry hit, correct build inputs, contribution
  delivered; the strongest single guard over the facade wiring.

**`test_autonomy_silent_for_unknown_pipeline`** (negative)
- Setup: fake context with `pipeline = SimpleNamespace(name="review")` (an existing
  non-development pipeline name), `workflow = None`, contribute recorder.
- Input: `autonomy(context=ctx)`
- Trace: `name = "review"` → `_PIPELINE_DOMAINS` miss → return `None` without calling
  `ctx.contribute`
- Assertions: `ctx.contributed is None` (no contribution call)
- Sufficiency: the registry-miss silence contract — any other pipeline must compose exactly as a
  project without the tool; prevents an over-eager default match (e.g. substring or display-name
  matching).

**`test_autonomy_ignores_display_name`** (negative)
- Setup: fake context with `pipeline = SimpleNamespace(name="development-weekly",
  display_name="Development")`, `workflow=None`, recorder.
- Input: `autonomy(context=ctx)`
- Trace: `name = "development-weekly" ≠ "development"` → miss → silent
- Assertions: `ctx.contributed is None`
- Sufficiency: pins "compared verbatim — source and display name never participate"; prevents
  prefix/display matching regressions.

**`test_register_hooks_never_reads_files_or_config`** (edge)
- Setup: run with `cwd=tmp_path` (an empty directory — no `.goga`, no configuration).
- Input: `register_hooks(recorder)`
- Trace: a pure subscribe call; no path is resolved, no file opened
- Assertions: exactly one subscription recorded (same as the positive test); no exception
- Sufficiency: the "no configuration or file reads during registration" constraint — registration
  must succeed in a bare directory; prevents environment sniffing creeping into the facade.

**`test_register_hooks_idempotent_across_calls`** (edge)
- Setup: two independent recorders `r1`, `r2` — each a stub
  `class _Rec: def subscribe(self, domain, action, name, hook): self.calls.append((domain,
  action, name, hook))` with `calls = []`.
- Input: `register_hooks(r1)` then `register_hooks(r2)` — two calls in one process
- Trace: each call performs exactly one subscribe with identical arguments; no accumulated state
- Assertions:
  ```python
  len(r1.calls) == 1 and len(r2.calls) == 1
  r1.calls == r2.calls == [("pipeline", "amend_workflow", "autonomy", autonomy)]
  ```
- Sufficiency: the platform calls `register_hooks` more than once per process (inspection with
  `goga hooks` plus the run itself, each on a fresh registrar) — pins that repeated registration
  neither duplicates nor loses the single subscription.

### Task 7: Integration tests — the real platform merge and compiler (integration tests)

This task verifies the tool end-to-end against the real platform (goga, unpinned `>=2.0` in the
test extra): the contributed document must survive `merge_workflow_overlay` and `compile_flow`
and produce the unattended composition (Scenario A), and the full reference workflow must win
byte-identically (Scenario C — neutrality). Cross-entity by nature: `development_recipe` →
`build_development_contribution` → platform merge → platform compiler. It also runs the final
acceptance checks carried over from the apply-architecture stage.

**Usages relevant to this task:**
- `conventions`: M2 — integration tests covering multiple packages go directly in `tests/`
  (`tests/test_integration.py`); file output uses `tmp_path` exclusively; no mocks (pure logic
  against the real installed platform).
- `goga_dependency`: the test extra declares `goga>=2.0` unpinned — a platform release changing
  the development-pipeline shape must surface here as failures, not silently pass.
- `workflow_document` / `pipeline_amendment`: the merge semantics (authored wins per slot) and the
  compiled vocabulary asserted below.

**CRITICAL: `CODEMANIFEST` files — read-only contract definitions. Do NOT modify them. If
implementation does not match the contract, fix the implementation — never fix the contract. The
`.usages/` files are equally read-only.**

- [x] Create `tests/test_integration.py` (directly in `tests/`, per M2) importing from the root
  facade (`from goga_tool_autonomous import development_recipe,
  build_development_contribution`) and from the platform (`goga.pipeline.compiler.compile_flow`,
  `goga.pipeline.hooks.overlay.merge_workflow_overlay` and `ToolContribution`)
- [x] Implement `test_integration_contribution_only_compiles_unattended` (Scenario A — verbatim
  from the design):
  - Setup: fixtures `development_pipeline_path`, `tmp_path`;
    `document = build_development_contribution(recipe=development_recipe(), workflow=None)`;
    `overlay = merge_workflow_overlay(None, [ToolContribution(tool="autonomous",
    document=document)])`
  - Input: `compile_flow(development_pipeline_path, tmp_path / "flow.yml", workflow=overlay.workflow)`
  - Trace: parse the pipeline → apply the workflow: six × approve auto (interactive suppression),
    accept-result manual cancel, extend build embedded after commit-changes → serialize
  - Assertions (values verified against goga 2.0.0):
    ```python
    flow = yaml.safe_load((tmp_path / "flow.yml").read_text())
    names = [s["name"] for s in flow["stages"]]
    names[-3:] == ["Commit changes", "Build implementation", "Contracts & coverage audit"]
    build = flow["stages"][-2]
    build["script"] == 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"'
    build["script_after"] == "rm -rf .ralphex"
    build["script_timeout"] == "8h"
    build["depends_on"] == ["commit-changes"]
    gated = flow["stages"][1:7]           # the six review stages
    all("interactive" not in s for s in gated)          # approve auto suppressed communication
    "auto_run" not in flow["stages"][-1]                 # accept-result manual cancelled
    overlay.provenance == ["autonomous"]
    ```
  - Sufficiency: end-to-end proof that the contributed document survives the real platform merge
    and compiler and produces the unattended composition — the tool's whole purpose in one test;
    regresses on any vocabulary drift between the package and a future platform release
- [x] Implement `test_integration_authored_reference_wins_byte_identical` (Scenario C — verbatim
  from the design):
  - Setup: fixtures `reference_workflow`, `development_pipeline_path`, `tmp_path`;
    `document = build_development_contribution(recipe=development_recipe(),
    workflow=reference_workflow)`; `overlay = merge_workflow_overlay(reference_workflow,
    [ToolContribution(tool="autonomous", document=document)])`
  - Input: compile twice — `compile_flow(pipe, tmp_path/"authored.yml",
    workflow=reference_workflow)` and `compile_flow(pipe, tmp_path/"merged.yml",
    workflow=overlay.workflow)`
  - Trace: gated slots authored-set → contribution values ignored; accept-result manual
    authored-set (False) → kept; extend.build under authored name → contribution entry dropped →
    `overlay.workflow` field-equal to authored; compile both → two serialized flows
  - Assertions:
    ```python
    (tmp_path/"authored.yml").read_text() == (tmp_path/"merged.yml").read_text()
    overlay.provenance == ["autonomous"]
    ```
  - Sufficiency: the neutrality property — authored intent wins per slot with zero byte drift;
    guards the "do not implement merge or override logic" constraint from the platform side
- [x] REPL-verify the expected compiled values before pinning them: drive
  `merge_workflow_overlay` + `compile_flow` in `/opt/goga/project/bin/python -i` once, confirm the
  stage order and the build fields, then migrate the verified expectations into the test (M4)
- [x] Run validation: `/opt/goga/project/bin/python -m pytest tests/ -x` — the full suite (20
  scenarios) is green
- [x] Final acceptance checks (carried over from the apply-architecture stage): facade import
  check (`/opt/goga/project/bin/python -c "import goga_tool_autonomous"`); full facade surface check
  (`/opt/goga/project/bin/python -c "from goga_tool_autonomous import register_hooks, autonomy,
  AutonomyRecipe, development_recipe, build_development_contribution"`); zone facade check
  (`/opt/goga/project/bin/python -c "from goga_tool_autonomous.recipe import AutonomyRecipe,
  development_recipe, build_development_contribution"`); `test_entry_mirrors_reference_workflow`
  passes; contribution determinism passes; hook silence for non-`development` pipelines passes;
  the `goga>=2.0` test-extra entry is present in `pyproject.toml`
- [x] Lint + format: `/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/` and
  `/opt/goga/project/bin/ruff format goga_tool_autonomous/ tests/` — clean
- [x] Verify the contracts are untouched: `goga lint` still reports `cells: 4 errors: 0`; the
  four CODEMANIFESTs and all `.usages/` files are unmodified (diff against the pre-task state)

---

## Validation Commands

- `/opt/goga/project/bin/python -m pytest tests/ -x`: Run all tests (the full 20-scenario suite)
- `/opt/goga/project/bin/python -m pytest tests/<path>/test_<name>.py -v`: Run a specific test file
- `/opt/goga/project/bin/ruff check goga_tool_autonomous/ tests/`: Lint check (source and tests — exit 0)
- `/opt/goga/project/bin/ruff format --check goga_tool_autonomous/ tests/`: Formatter check (exit 0)
- `/opt/goga/project/bin/python -c "import goga_tool_autonomous"`: Facade import-cleanliness (a broken
  import is fatal to every goga command)
- `/opt/goga/project/bin/python -c "from goga_tool_autonomous import register_hooks, autonomy, AutonomyRecipe, development_recipe, build_development_contribution"`: Verify that all facade entities (2 declared + 3 embedded) are importable
- `/opt/goga/project/bin/python -c "from goga_tool_autonomous.recipe import AutonomyRecipe, development_recipe, build_development_contribution"`: Verify the recipe zone facade embeddings
- `goga lint`: Verify the cells — must stay `cells: 4 errors: 0` (CODEMANIFESTs untouched)

---

## Completion Criteria

- [x] Every contract entity is implemented in the correct `location`
  (`recipe/model/recipe.py`, `recipe/development/entry.py`, `recipe/development/contribution.py`,
  `registration.py`)
- [x] Every contract entity is accessible from the facade (cell facades, the recipe zone facade,
  and the package facade — `__all__` per the Python cell rules)
- [x] Properties and methods match the declared API (four read-only `AutonomyRecipe` properties;
  the five routine signatures, including `autonomy`'s exactly-`context` parameter)
- [x] Descriptions are reflected in behavior (verbatim reference mirroring; never-empty document;
  inspect-then-fill; unconditional acceptance; registry exact-match silence; single subscription)
- [x] Contract dependencies are met (`AutonomyRecipe` imported by the development cell and both
  facades; the platform import confined to `contribution.py`)
- [x] Re-exports are accessible from the facade (3 embedded names on two facades)
- [x] Every coding task followed the TDD workflow (contract tests → code → verification → logic
  tests → debugging → re-verification → lint)
- [x] Contract tests and logic tests cover facade, API, and behavior within each coding task;
  integration tests exist for the cross-entity scenarios (Task 7)
- [x] No package boundary was expanded (no new cells, no new facade-level interfaces, internal
  decomposition only within the existing cells)
- [x] `CODEMANIFEST` files were not modified (contract is read-only); `.usages/` files were not
  modified; `goga lint` reports `cells: 4 errors: 0`
- [x] All validation commands pass (tests, lint, format check, all three facade checks)
- [x] Every Usages entry is mentioned in at least one task (`conventions`, `workflow_document`,
  `hooks_registration`, `pipeline_amendment`, `goga_dependency`; imported: `recipe`/`recipe_guide`,
  `contribution`, `development`)
- [x] The Mandatory Rules were enforced across all development stages: M1 coding style (incl. the
  sanctioned pydantic deviation for `AutonomyRecipe` only), M2 test rules (mirrored tree,
  naming, classification, mock policy), M3 linter/formatter gate at every task **and before every
  local commit**, M4 REPL-cycle workflow (continuous interactive evaluation, hot reloading,
  migration of verified code to source files), M5 contract immutability
- [x] The venv lives outside the project at `/opt/goga/project`; runtime `dependencies = []` is
  untouched; `goga>=2.0` is present in the `test` extra
