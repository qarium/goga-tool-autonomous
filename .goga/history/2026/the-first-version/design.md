# Design Document: `the-first-version`

Topic path: `.goga/history/2026/the-first-version/design.md` (topic `the-first-version`, year 2026).
Source architecture plan: `.goga/history/2026/the-first-version/arch.md` (materialized by the
apply-architecture stage — `goga lint`: `cells: 4 errors: 0`).
Platform verified against: installed `goga 2.0.0` (`/opt/goga`), ref `2.0.x` per `.goga/config.yml`.

## Contract Changes

### Changed CODEMANIFEST Files

- `goga_tool_autonomous/recipe/model/CODEMANIFEST`: **new** — the recipe shape cell (leaf, no
  Imports). Declares the `AutonomyRecipe` entity at `recipe.py` with four read-only properties.
- `goga_tool_autonomous/recipe/development/CODEMANIFEST`: **new** — the development functional
  domain. Imports `AutonomyRecipe` + the `recipe` practice from `recipe/model`. Declares the
  routines `development_recipe` (`entry.py`) and `build_development_contribution`
  (`contribution.py`).
- `goga_tool_autonomous/recipe/CODEMANIFEST`: **new** — the recipe zone facade. Imports from both
  sub-cells; embeds `AutonomyRecipe`, `development_recipe`, `build_development_contribution`.
- `goga_tool_autonomous/CODEMANIFEST`: **new** — the package facade. Imports the three types + the
  `development` practice from `recipe`. Declares `register_hooks` and `autonomy` (`registration.py`)
  and embeds the three recipe-zone types.

All four are greenfield creations (the cell schema was empty before the apply-architecture stage);
there are no modifications of, or deletions from, any pre-existing manifest.

### New Entities

- `AutonomyRecipe(pipeline: str, gated_stages: list[str], accept_stage: str, build_extend: dict[str, str | list[str]])`
  — immutable plain-data recipe of one pipeline's autonomy contribution; Entity with four
  properties, no methods; location `goga_tool_autonomous/recipe/model/recipe.py`.
- `development_recipe() -> entry: AutonomyRecipe` — the development zone entry (pure factory);
  location `goga_tool_autonomous/recipe/development/entry.py`.
- `build_development_contribution(recipe: AutonomyRecipe, workflow: WorkflowDocument | None) -> document: WorkflowDocument`
  — the development delivery (pure transformer recipe + authored workflow → contribution
  document); location `goga_tool_autonomous/recipe/development/contribution.py`.
- `register_hooks(hooks: Hooks)` — subscribes the single `autonomy` hook to
  `pipeline / amend_workflow`; location `goga_tool_autonomous/registration.py`.
- `autonomy(context: WorkflowAmendment)` — the amendment hook: resolves the pipeline's domain,
  builds the contribution, contributes it through the view; location
  `goga_tool_autonomous/registration.py`.

### Changed Entities

- None (greenfield).

### Deleted Entities

- None.

### Usages and Annotations Changes

- New project-level practices referenced by path: `conventions`
  (`.goga/usages/conventions.md`), `workflow_document`
  (`.goga/usages/github/goga/pipeline/workflow/parse-workflow.md`), `hooks_registration`
  (`.goga/usages/github/goga/hooks/registering-hooks.md`), `pipeline_amendment`
  (`.goga/usages/github/goga/pipeline/registering-hooks.md`), `goga_dependency`
  (`.goga/usages/cooks/goga-dependency.md`).
- New imported practices: `recipe` (from `recipe/model`, aliased `recipe_guide` inside
  `recipe/development`), `contribution` (from `recipe/development`), `development` (from
  `recipe`).
- New cell-level consumer documentation: `recipe/model/.usages/recipe.md`,
  `recipe/development/.usages/contribution.md`, `recipe/.usages/development.md`,
  `goga_tool_autonomous/.usages/development.md`.

## Applied Fixes

### Fixed CODEMANIFEST Defects

- None. Phase 3 static validation and the four-dimension consistency audit found no defects:
  `goga lint` reports `cells: 4 errors: 0`; every backtick reference resolves in its document
  context; every connected practice (own `Usages` and `Imports.Usages`) is referenced in at least
  one annotation; all usage paths exist on disk; no import cycles (dependency tree confirmed via
  `goga schema`); `location` values are flat, extension-bearing filenames; casing and the
  Header/Body/Footer document structure conform to the DSL.

  The consistency audit was performed against the **actual installed platform API** (goga 2.0.0):
  `HookRegistrar.subscribe(domain, action, name, hook)` (`goga/hooks/tools/registration.py`),
  the declared hard action `pipeline/amend_workflow` (`goga/hooks/catalog/catalog.py:43`),
  `WorkflowAmendment` with reads `pipeline` / `decision` / `workflow` / `work` and the single
  write channel `contribute(document)` (`goga/pipeline/hooks/amendments.py`), the
  `WorkflowDocument` / `WorkflowStage` / `WorkflowExtendStage` models
  (`goga/pipeline/workflow/`), the authored-wins merge (`goga/pipeline/hooks/overlay.py`), and
  the fixed-name hook-argument injection offering exactly `context` and `self`
  (`goga/hooks/dispatch/delivery.py`). All contract-level expectations match the platform.

## Entity Interaction and Data Flow

### Interaction Diagram

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

### Data Flows

**Scenario A — unattended run, no authored workflow** (decision `disabled` or `silent-miss`, or
an authored workflow resolving to `None`):
`context.workflow is None` → the delivery contributes `approve: auto` for **all six** gated
stages, `manual: false` for `accept-result`, and the `build` extension. The merge starts from the
unset shape (no authored entry per name); the compiled flow runs with every review gate
non-interactive, acceptance non-manual, and the build stage after `commit-changes`.

**Scenario B — partially authored workflow** (the author set `approve` on some stages only):
the delivery skips the stages whose authored entry carries an `approve` instruction and fills the
rest; the acceptance instruction and the build extension are contributed regardless; authored
values win per slot in the platform merge.

**Scenario C — the full reference workflow** (`.goga/workflows/development.yml` authored):
every gated stage already carries `approve: auto`, `accept-result` already carries
`manual: false`, and the authored `extend` already owns the name `build` → the contribution
carries only the `accept-result` stage entry, and the merge drops the contributed `build`
extension under the authored name. **Verified experimentally on goga 2.0.0**: the merged workflow
is field-equal to the authored one, and `compile_flow` output is byte-identical with and without
the contribution — the tool is neutral exactly when the author already authored its knowledge.

**Scenario D — any other pipeline** (name ≠ `development`): the registry lookup misses,
`autonomy` returns without contributing; the delivery sees `None` and continues silently;
composition is identical to a project without the tool.

### Entity Dependencies

```
goga_tool_autonomous (register_hooks, autonomy; embeddings)
  └─ goga_tool_autonomous/recipe (embeddings; Imports: 3 types + `development` practice)
       ├─ goga_tool_autonomous/recipe/development (development_recipe,
       │    build_development_contribution; Imports: AutonomyRecipe + `recipe` practice)
       │    └─ goga_tool_autonomous/recipe/model (AutonomyRecipe) — leaf
       └─ goga_tool_autonomous/recipe/model
```

Implementation order (bottom-up, matching the dependency order): `recipe/model` →
`recipe/development` → `recipe` facade → package facade. Runtime platform imports
(`goga.pipeline.workflow`) occur only inside `recipe/development/contribution.py`; per
`goga_dependency` this is safe (goga imports the facade, so the platform is present whenever the
package runs) and keeps the runtime dependency list empty.

## Code Stack Trace

### Trace: `AutonomyRecipe(...)` (constructor)

#### Chain

1. **Input**: a consumer (test, future zone, or `development_recipe`) constructs the entity with
   four values: `pipeline: str`, `gated_stages: list[str]`, `accept_stage: str`,
   `build_extend: dict[str, str | list[str]]`.
2. **Step**: the constructor captures all four fields at once (keyword-only per the conventions'
   `kw_only` rule) → checkpoint: four properties exist, each returning the captured value
   verbatim; instances are frozen — field assignment raises `FrozenInstanceError` (read-only
   exposure). **Passed** (frozen dataclass semantics; Python 3.10+ `kw_only` support).
3. **Step**: no validation, no coercion, no I/O occurs — the entity is inert data → checkpoint:
   the cell-wide deviation from `conventions` (no pydantic) is explicitly sanctioned by the
   manifest header annotation (empty runtime dependencies). **Passed.**
4. **Output**: an immutable `AutonomyRecipe` instance held by the consumer; nothing else happens
   until a delivery path contributes it.

#### Checkpoint Summary

- Field capture and read-only exposure: **passed** (frozen dataclass).
- Plain-data constraint (no pydantic, no methods, no computed state): **passed**.
- Type shapes (`dict[str, str | list[str]]` etc.): **passed** — Python 3.10+ union syntax,
  matches the extend-entry vocabulary (str scalars, `after` as `list[str]`).

### Trace: `development_recipe()`

#### Chain

1. **Input**: called with no arguments by `autonomy` (per-run) or by consumers/tests.
2. **Step**: constructs and returns `AutonomyRecipe(pipeline="development", gated_stages=[...],
   accept_stage="accept-result", build_extend={...})` → checkpoint: values mirror
   `.goga/workflows/development.yml` **verbatim** — verified against the file:
   - `gated_stages` is exactly `["architecture-review", "apply-architecture", "code-design",
     "design-review", "coding-plan", "plan-review"]` — the six stages carrying `approve: auto`
     in the reference, in file order. **Passed.**
   - `accept_stage` is `"accept-result"` — the stage carrying `manual: false` in the reference;
     the stage exists in the development pipeline file with `trigger: manual`, so the explicit
     cancel always has something to cancel. **Passed.**
   - `build_extend` carries `title="Build implementation"`, `after=["commit-changes"]`,
     `timeout="8h"`,
     `script="python3 -P -m goga.build \"$(python3 -m goga history path -f plan.md)\""`,
     `after_script="rm -rf .ralphex"` — verbatim from the reference `extend.build` entry.
     **Passed.**
3. **Step**: nothing is read from disk — the reference file is documentation only → checkpoint:
   "the reference is authoritative documentation, never read at runtime". **Passed.**
4. **Output**: a fresh, equal-on-every-call `AutonomyRecipe` (determinism; fresh mutable
   containers per call so no caller can mutate shared state).

#### Checkpoint Summary

- Verbatim mirroring of the reference workflow: **passed** (checked key by key).
- Purity/determinism: **passed** (constant construction; equal instances on every call).
- Stage-name validity against the real development pipeline: **passed** (all six gated stages,
   `commit-changes`, and `accept-result` exist in `goga/assets/pipelines/development.yml`).

### Trace: `build_development_contribution(recipe, workflow)`

#### Chain

1. **Input**: `recipe` — an `AutonomyRecipe` (normally `development_recipe()`); `workflow` — the
   authored `WorkflowDocument` after the decision and the runner-skip merge, or `None` when no
   workflow resolved (both verified as the platform's contract for `WorkflowAmendment.workflow`).
2. **Step** (Algorithm 1 — build extension): split `recipe.build_extend` into the extracted
   positioning field and the verbatim body:
   `WorkflowExtendStage(after=list(build_extend["after"]), body={"title": ..., "timeout": ...,
   "script": ..., "after_script": ...})`, placed in the contribution's `extend` map under the
   name `"build"` → checkpoints:
   - Platform model conformance: `after` is one of the two extracted inline keys
     (`before`/`after`), everything else stays in `body` verbatim — **passed**
     (`WorkflowExtendStage` field set `before, after, agent, loop, approve, body`).
   - `before`/`after` at-least-one rule satisfied by `after=["commit-changes"]` — **passed.**
   - Extend-entry forbidden keys (`manual`, `notes`, `reflect`, `memory`, `depends_on`, `skip`)
     are absent from the body — **passed.**
   - Fresh name rule: `"build"` is the extension name the delivery path chooses; when the author
     already owns the name the platform merge drops the contributed entry (authored wins) —
     **passed.**
3. **Step** (Algorithm 2 — gated stages): for each name in `recipe.gated_stages` decide:
   contribute `WorkflowStage(approve="auto")` when `workflow is None`, or the name is absent
   from `workflow.stages`, or `workflow.stages[name].approve is None`; skip when the authored
   entry carries any `approve` instruction → checkpoints:
   - Read surface: `WorkflowStage.approve` exists and is `None` exactly when the author left it
     unset — **passed** (verified in the model: `approve: str | None = None`).
   - Contributed stage shape: only the `approve` field is set; all other fields stay `None`
     (`skip=False` default) — **passed.**
   - Inspect-then-fill consistency with the platform merge: the merge would fill the slot only
     when unset anyway; skipping keeps the document minimal ("names only the slots it actually
     fills") — **passed** (semantics verified against `merge_workflow_overlay._is_set`).
4. **Step** (Algorithm 3 — acceptance trigger): unconditionally add
   `WorkflowStage(manual=False)` under `recipe.accept_stage` → checkpoints:
   - Three-state `manual`: `False` is *explicit cancel*, distinct from absence (`None`);
     `accept-result` is `trigger: manual` in the pipeline, so the compiler's
     "manual: false on non-manual stage" error can never fire here — **passed.**
   - Unconditional contribution is safe: when the author already set `manual`, the merge keeps
     the authored value (False is "set" per the SET table) — **passed.**
5. **Step** (Algorithm 4 — assemble): `WorkflowDocument(stages={...gated contributions...,
   accept_stage: manual-False}, extend={"build": entry})` with `prompt=None` and `memory=None`;
   return it → checkpoints:
   - Never-empty: `extend` always carries `build` and `stages` always carries the acceptance
     entry — the delivery's empty-document discard (with its warning) can never trigger —
     **passed.**
   - Declarative vocabulary only: stage instructions + one extension entry; no prompt and no
     memory block (explicit constraint; verified the merge/compiler treat those as separate
     slots) — **passed.**
   - Determinism: fixed iteration and construction order; no clock, environment, or I/O reads —
     **passed** (verified experimentally: identical inputs → field-equal documents; the merged
     output compiles byte-identically across repeats).
   - Purity: the authored `workflow` object and its maps are only read, never mutated —
     **passed.**
6. **Output**: the contribution `WorkflowDocument`, returned to `autonomy`, which hands it to
   `context.contribute`.

#### Checkpoint Summary

- Extend-entry construction vs `workflow_document` vocabulary: **passed** (compiles cleanly
  through the real `compile_flow`; the build stage lands with `depends_on: ["commit-changes"]`).
- Gated-stage inspect-then-fill vs the authored-wins merge: **passed**.
- Acceptance `manual=False` vs the compiler's three-state manual semantics: **passed** (the
  compiled `Contracts & coverage audit` stage loses its `auto_run: false` key).
- Never-empty vs the delivery's empty-document warning: **passed**.
- No prompt/memory contributions vs the manifest constraint: **passed**.

### Trace: `register_hooks(hooks)`

#### Chain

1. **Input**: the platform (a goga command reaching the first hook checkpoint of a run, or
   `goga hooks` inspection) imports the facade module `goga_tool_autonomous` and calls
   `register_hooks(hooks)` with the registrar scoped to this tool.
2. **Step**: the facade import chain executes (`goga_tool_autonomous/__init__.py` →
   `.registration`, `.recipe` → `.model`, `.development`) → checkpoint: import-clean at all
   times; relative imports only (conventions); the sole third-party-touching import is
   `goga.pipeline.workflow` inside `contribution.py`, which is present by construction (the
   platform imports the facade; per `goga_dependency`). A broken import would be fatal to every
   goga command — the platform raises a clean `ImportError` naming the package
   (`call_register_hooks`). **Passed.**
3. **Step**: call `hooks.subscribe("pipeline", "amend_workflow", "autonomy", autonomy)` →
   checkpoints:
   - Address declared: `pipeline/amend_workflow` exists in the action catalog with error class
     `hard` — **passed** (verified `goga/hooks/catalog/catalog.py:43`).
   - Envelope valid: non-empty name, callable hook, no repeat — the registrar appends exactly
     one `Subscription` — **passed.**
   - `hooks` typing: the manifest's free-form `Hooks` denotes the platform registrar
     (`HookRegistrar.subscribe(domain, action, name, hook)`); only `subscribe` is used —
     **passed** (documented by `hooks_registration`).
4. **Output**: `None`; one subscription registered. No configuration or file reads; no other
   addresses, no other names (constraint).

#### Checkpoint Summary

- Subscription address/name vs the platform catalog: **passed.**
- Facade import cleanliness vs the fatal-import rule: **passed.**
- Constraint "no configuration or file reads during registration": **passed** (registration
  touches nothing beyond the one `subscribe` call).

### Trace: `autonomy(context)`

#### Chain

1. **Input**: the platform's amendment walk builds a fresh `WorkflowAmendment`
   (`pipeline`, `decision`, `workflow`, `work`) per tool, wraps it in a read-only delivery proxy,
   and calls the hook by injected keyword: `autonomy(context=proxy)` → checkpoint: the hook
   declares exactly the offered name `context` (positional-or-keyword), so
   `build_hook_arguments` delivers it; the proxy passes attribute reads and bound-method calls
   (`contribute`) and blocks writes. **Passed** (verified `goga/hooks/dispatch/delivery.py`).
2. **Step** (Algorithm 1 — resolve the domain): `name = context.pipeline.name`; look the name up
   in the module-level registry mapping the exact pipeline name to its functional domain
   (entry factory + delivery) → checkpoints:
   - Exact-match keying: `PipelineIdentity.name` is the discovered file stem (`"development"`);
     `display_name` (`"Development"`) and `source` never participate — **passed.**
   - Miss path: any other name → return `None` without contributing; the delivery sees
     `amendment._contribution is None` and continues silently — composition equals a project
     without the tool — **passed.**
   - Read discipline: only `pipeline.name` and `workflow` are read; `decision` and `work` are
     never touched (constraint) — **passed.**
3. **Step** (Algorithm 2 — build): `document = delivery(entry_factory(), context.workflow)` with
   `delivery = build_development_contribution`, `entry_factory = development_recipe` →
   checkpoint: type flow — `development_recipe() -> AutonomyRecipe` matches
   `build_development_contribution`'s `recipe` parameter; `context.workflow` is
   `WorkflowDocument | None`, matching the `workflow` parameter — **passed** (both verified
   against the platform view type).
4. **Step** (Algorithm 3 — contribute): `context.contribute(document)` → checkpoints:
   - The single write channel; the buffer replaces whole on repeated calls (we call it once) —
     **passed.**
   - The contribution commits only after the hook returns without raising; the walk then
     validates the buffered document's facts and merges it via `merge_workflow_overlay` —
     **passed.**
5. **Output**: `None`; the buffered contribution is the side effect. No state, no cache, no
   internal exception handling — a failure propagates and the platform stops the command with a
   clean error naming the hook, tool, and action (`hook autonomy of tool autonomous failed on
   pipeline.amend_workflow: <reason>`), discarding the whole contribution — exactly the
   manifest's constraint. **Passed.**

#### Checkpoint Summary

- Hook-argument injection vs the offered-name set: **passed.**
- Registry keying vs `PipelineIdentity` semantics: **passed.**
- Type flow `development_recipe() → build_development_contribution(recipe=…, workflow=…)`:
  **passed.**
- Error propagation vs the hard action: **passed.**

## Algorithm Design

### `AutonomyRecipe`

**Responsibility**: carry one pipeline's autonomy knowledge as immutable plain data — the single
source of every entry the delivery path contributes for that pipeline.

**Algorithm:**
```
1. Construct with four keyword-only fields (pipeline, gated_stages, accept_stage, build_extend)
   → frozen instance; every field exposed as a read-only property of the same name
```

**Implementation form**: `@dataclass(frozen=True, kw_only=True)` in
`goga_tool_autonomous/recipe/model/recipe.py`, with a Google-style docstring covering the four
`Args` and the plain-data deviation. No methods, no `__post_init__` validation, no defaults
(conventions' "empty defaults" rule is superseded by the cell's plain-data deviation: an entry
without all four fields is meaningless, and the constructors are few and internal).

**Errors:**
- `FrozenInstanceError` → any field assignment on an instance → consumers treat the entry as
  read-only forever.

**Edge Cases:**
- duplicate names inside `gated_stages`, or a `gated_stages` entry equal to `accept_stage` →
  not validated here (data carrier); the delivery tolerates both — a duplicate collapses in the
  stages map, and an overlap would contribute both instructions for that name.

### `development_recipe`

**Responsibility**: produce the development pipeline's recipe entry — the zone's own knowledge,
mirroring the reference workflow verbatim.

**Algorithm:**
```
1. Construct AutonomyRecipe with the constant development values:
   - pipeline = "development"
   - gated_stages = ["architecture-review", "apply-architecture", "code-design",
                     "design-review", "coding-plan", "plan-review"]
   - accept_stage = "accept-result"
   - build_extend = {title: "Build implementation", after: ["commit-changes"],
                     timeout: "8h",
                     script: python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)",
                     after_script: rm -rf .ralphex}
   → fresh equal instance on every call (fresh list/dict per call)
```

**Errors:**
- none — pure constant construction; nothing can fail.

**Edge Cases:**
- none (no inputs). The values are compile-time constants of the zone.

### `build_development_contribution`

**Responsibility**: build the never-empty declarative contribution document for the development
pipeline from the recipe entry and the delivered authored workflow.

**Algorithm:**
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

**Runtime imports** (the only runtime platform dependency of the package, per `goga_dependency`):
`from goga.pipeline.workflow import WorkflowDocument, WorkflowExtendStage, WorkflowStage` —
relative-import conventions do not apply (third-party/stdlib absolute imports are the rule).

**Errors:**
- none raised by this routine itself (no internal handling, per constraint). A structurally
  impossible input (e.g. `build_extend` missing `"after"`) would surface as a `KeyError` to the
  caller → the hard action turns it into a clean command error. In practice the recipe is
  defined in-code, so the path is unreachable.

**Edge Cases:**
- `workflow=None` → all six gated stages contributed.
- authored `approve` present on every gated stage → zero gated contributions; the document
  still carries the acceptance entry and the build extension (never empty).
- authored workflow naming a gated stage with other fields set but `approve` absent
  (e.g. only `reflect`) → the stage still receives `approve: auto` from the contribution.
- authored `extend.build` already present → the contributed entry is dropped by the platform
  merge (authored name wins); the document itself remains as built.

### `register_hooks`

**Responsibility**: subscribe the single autonomy hook to the pipeline workflow-amendment
action.

**Algorithm:**
```
1. hooks.subscribe(domain="pipeline", action="amend_workflow", name="autonomy", hook=autonomy)
   → exactly one subscription, unconditional
```

**Errors:**
- an invalid envelope would be *rejected as data with a log warning* by the platform (never
  raised) — our envelope is structurally valid, so this path does not occur.
- a broken facade import is the platform's single fatal case — mitigated by design (clean
  relative-import chain, no runtime third-party imports on the facade path except the sanctioned
  `goga.pipeline.workflow` inside `contribution.py`).

**Edge Cases:**
- called multiple times per process (inspection + run) — idempotent: each call registers the
  same one subscription on a fresh registrar.

### `autonomy`

**Responsibility**: the amendment hook — deliver the autonomy contribution for the composing
pipeline.

**Algorithm:**
```
1. name = context.pipeline.name
2. domain = _PIPELINE_DOMAINS.get(name)          (exact, verbatim match)
   IF domain IS None: RETURN                     (miss — silent, no contribution)
3. entry_factory, delivery = domain
4. document = delivery(entry_factory(), context.workflow)
5. context.contribute(document)
   RETURN
```

**Registry form** (module-level constant in `registration.py`, documented in
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

**Errors:**
- any exception propagates unchanged (constraint: no internal handling, no state) → the
  platform's hard action stops the command with a clean error naming the hook, tool, and
  action, and discards this tool's whole contribution.

**Edge Cases:**
- non-`development` pipeline (including display-name collisions like a hypothetical pipeline
  whose *display* name is "Development") → silent no-op.
- `context.workflow is None` (workflow disabled, silent-miss) → full contribution (Scenario A).
- read-only proxy: the routine only reads `pipeline.name` / `workflow` and calls `contribute`;
  attribute writes are impossible by construction.

## Cross-cutting Concerns

- **Error handling**: no `try/except` anywhere in the package. Every failure propagates to the
  platform boundary, where the hard `amend_workflow` action converts it into a clean command
  error naming the tool (`autonomous`), the hook (`autonomy`), and the reason; the tool's whole
  contribution is discarded. Contract boundary isolation (cookbook): the platform's failure
  modes are facts about the platform, not obligations of this contract.
- **Logging**: none in the package. The routines are pure functions without operational events
  of their own; the platform already logs the meaningful moments (registration rejections,
  empty-contribution discards, hook failures) with tool context. `conventions`' logging rules
  therefore have no application surface here — recorded as a deliberate decision, not an
  oversight.
- **Validation**: none in the package. The authored `workflow` arrives pre-validated by
  `parse_workflow`; the merged result (authored + contribution) passes the same compilation
  validation as an authored workflow (`compile_flow`), so a malformed contribution would surface
  as the compiler's structural error at the platform boundary. The recipe data is defined
  in-code and trusted.
- **Caching**: none (constraint). `development_recipe()` rebuilds its (small) value on every
  call; registration state lives in the platform, which already builds it once per run.
- **Concurrency**: stateless by design — no module mutable state, frozen data carriers, fresh
  containers per call. No thread-synchronization requirements.
- **Configuration**: no reads (constraints on both `register_hooks` and `autonomy`). All
  knowledge is code.

## Usages Analysis

### `conventions` (all four cells)
- **What it provides**: mandatory Python rules — 3.10+ compatibility, `pyproject.toml`
  configuration, relative intra-package imports, pydantic data models, logging standards,
  formatting, Google-style docstrings, and the full testing standard (structure, naming, mocks,
  venv).
- **Where used**: every entity of every cell (global annotation in each manifest).
- **Why chosen**: the project-wide code and test law; every file the implementation writes
  follows it.
- **How exactly**: relative imports inside `goga_tool_autonomous`; `pyproject.toml` as the
  configuration surface; Google docstrings on all public callables; tests mirroring
  `goga_tool_autonomous/…` under `tests/…` with `__init__.py` and `conftest.py` per the test
  structure rules. **Sanctioned deviation** (manifest headers): the recipe cell uses a frozen
  dataclass instead of pydantic to keep runtime dependencies empty.

### `workflow_document` (model, development, main cells)
- **What it provides**: the workflow-file parser contract — the `WorkflowDocument` shape, the
  per-stage instruction vocabulary (`approve`, `manual`, …), and the extend-entry vocabulary
  (positioning `before`/`after`, inline `agent`/`loop`/`approve`, verbatim `body`, forbidden
  keys).
- **Where used**: `AutonomyRecipe.build_extend` (vocabulary of the carried data);
  `build_development_contribution` (construction of the document and authored-instruction
  reads); `autonomy` (reading `context.workflow`).
- **Why chosen**: the contribution is a declarative `WorkflowDocument` — the same vocabulary an
  authored workflow-file uses; this practice is the platform's own specification of that
  vocabulary.
- **How exactly**: `WorkflowExtendStage(after=[...], body={title, timeout, script,
  after_script})`; `WorkflowStage(approve="auto")` for gated stages; `WorkflowStage(manual=
  False)` for the acceptance stage; reads limited to `workflow.stages[name].approve`.

### `goga_dependency` (development, main cells)
- **What it provides**: the rule connecting the goga platform as a dependency — runtime
  dependencies stay empty; importing platform modules inside the package is safe (goga imports
  the facade); the test extra declares `goga>=2.0` unpinned.
- **Where used**: `build_development_contribution` (the runtime `goga.pipeline.workflow`
  import); the facade cells' import-cleanliness requirement.
- **Why chosen**: the package runs inside a goga-provided interpreter; declaring goga at runtime
  risks resolver conflicts in the goga image.
- **How exactly**: `dependencies = []` in `pyproject.toml` (already true); add `"goga>=2.0"` to
  the `test` extra (see Additional Instructions — the entry is currently missing and is part of
  this design's deliverables); tests import
  `goga.pipeline.{workflow,hooks,compiler}` under that extra.

### `hooks_registration` (main cell)
- **What it provides**: the facade/subscription contract — `register_hooks(hooks)` callback,
  `hooks.subscribe(domain, action, name, hook)`, hook-argument injection by offered names
  (`context`, `self`), failure behavior (broken import fatal, hard-action errors).
- **Where used**: `register_hooks`, `autonomy`.
- **Why chosen**: the subscription is the package's only platform entry point.
- **How exactly**: one `subscribe("pipeline", "amend_workflow", "autonomy", autonomy)` call;
  the hook declares only `context`.

### `pipeline_amendment` (main cell)
- **What it provides**: the pipeline domain's amendment action semantics — when it fires (post
  decision + runner-skip merge, pre-compilation; run and card forms), the `WorkflowAmendment`
  reads (`pipeline`, `decision`, `workflow`, `work`), `contribute(document)` buffering, and the
  authored-wins merge rules per slot.
- **Where used**: `autonomy`.
- **Why chosen**: the hook consumes exactly this view; the merge rules justify the
  inspect-then-fill algorithm and the unconditional acceptance/build contributions.
- **How exactly**: read `context.pipeline.name` and `context.workflow`; build via the domain
  delivery; call `context.contribute(document)` once.

### Imported Usages
- `recipe` (aliased `recipe_guide`) from `goga_tool_autonomous/recipe/model` — the entry shape
  and field semantics for the development zone's entry construction and for the delivery's reads.
  Path: `goga_tool_autonomous/recipe/model/.usages/recipe.md`. Referenced in the development
  manifest's global annotation.
- `contribution` from `goga_tool_autonomous/recipe/development` — the delivery call form
  (`build_development_contribution(recipe=…, workflow=…)`) for zone consumers.
  Path: `goga_tool_autonomous/recipe/development/.usages/contribution.md`. Referenced in the
  recipe facade manifest's global annotation.
- `development` from `goga_tool_autonomous/recipe` — the domain API (entry + delivery) the
  package facade wires into its registry.
  Path: `goga_tool_autonomous/recipe/.usages/development.md`. Referenced in the main manifest's
  global annotation.

All imported-usage files exist and match the current CODEMANIFESTs (verified read).

## `.usages/` Update

### Cell: `goga_tool_autonomous/recipe/model`

#### Existing Files — Consistency
- **`recipe.md`** → `goga_tool_autonomous/recipe/model/.usages/recipe.md`
  - Status: **current** — describes `AutonomyRecipe(pipeline, gated_stages, accept_stage,
    build_extend)` matching the manifest signature and properties; the defining/reading examples
    match the designed frozen-dataclass form; the import path
    `from goga_tool_autonomous.recipe import AutonomyRecipe` matches the zone facade design.
  - Additions needed: none.
  - Updates needed: none.

### Cell: `goga_tool_autonomous/recipe/development`

#### Existing Files — Consistency
- **`contribution.md`** → `goga_tool_autonomous/recipe/development/.usages/contribution.md`
  - Status: **current** — the call form, the never-empty guarantee, the gated-stage listing, the
    inspect-then-fill behavior with the `plan-review` example, and the purity preconditions all
    match the traced algorithm.
  - Additions needed: none.
  - Updates needed: none.

### Cell: `goga_tool_autonomous/recipe`

#### Existing Files — Consistency
- **`development.md`** → `goga_tool_autonomous/recipe/.usages/development.md`
  - Status: **current** — the domain API import line, the entry description, and the delivery
    semantics match the facade embeddings and the traced behavior.
  - Additions needed: none.
  - Updates needed: none.

### Cell: `goga_tool_autonomous`

#### Existing Files — Consistency
- **`development.md`** → `goga_tool_autonomous/.usages/development.md`
  - Status: **current** — the `register_hooks(hooks)` subscription (one hook, address
    `pipeline`/`amend_workflow`, name `autonomy`), the contributed amendments, the direct
    delivery call, the registry description (module-level, exact pipeline name → entry factory +
    delivery), and the adding-the-next-domain recipe all match this design.
  - Additions needed: none.
  - Updates needed: none.

No new `.usages/` files are required: each cell's files already partition by functional domain
(the shape / the delivery / the zone domain / the facade domain), matching the cookbook's
category organization.

## Test Stack Trace

### General Setup

- **Environment**: a virtualenv **outside the project at `/opt/project`** (per the run
  requirements; conventions: all code executes in a venv, created if missing) with the package
  installed editable plus the `test` extra: `pytest>=8.0`, `pytest-cov>=5.0`, `pytest-mock>=3.10`,
  `ruff>=0.15.0`, `goga>=2.0`.
- **Layout** (conventions — tests mirror the source tree, root-package modules directly in
  `tests/`, integration tests directly in `tests/`, `__init__.py` in every test directory):
  ```
  tests/
  ├── __init__.py
  ├── conftest.py                      # shared fixtures
  ├── test_registration.py             # ← goga_tool_autonomous/registration.py
  ├── test_integration.py              # cross-package: platform merge + compiler
  └── recipe/
      ├── __init__.py
      ├── model/
      │   ├── __init__.py
      │   └── test_recipe.py           # ← recipe/model/recipe.py
      └── development/
          ├── __init__.py
          ├── test_entry.py            # ← recipe/development/entry.py
          └── test_contribution.py     # ← recipe/development/contribution.py
  ```
- **Shared fixtures** (`tests/conftest.py`):
  - `development_pipeline_path` — the real installed pipeline file, located via
    `importlib.resources.files("goga") / "assets" / "pipelines" / "development.yml"` (verified
    resolvable; a platform release changing the development pipeline shape must surface as test
    failures — that is the unpinned-`goga` rationale of `goga_dependency`).
  - `reference_workflow` — `parse_workflow(Path(__file__).resolve().parents[1] / ".goga" /
    "workflows" / "development.yml")`; session-scoped, read-only. For `tests/conftest.py`,
    `parents[1]` is the project root (verified: the reference file parses cleanly on goga 2.0.0).
- **Mock policy**: none needed — pure logic is tested mock-free per conventions; file I/O uses
  `tmp_path` only.

### Source File Registry

| File under test | Entities |
|---|---|
| `goga_tool_autonomous/recipe/model/recipe.py` | `AutonomyRecipe` |
| `goga_tool_autonomous/recipe/development/entry.py` | `development_recipe` |
| `goga_tool_autonomous/recipe/development/contribution.py` | `build_development_contribution` |
| `goga_tool_autonomous/registration.py` | `register_hooks`, `autonomy` |

---

### Positive Tests

#### `test_recipe_construction_captures_all_fields`

**Setup**: none (pure construction).

**Input**: `AutonomyRecipe(pipeline="my-pipeline", gated_stages=["first-review"],
accept_stage="accept-result", build_extend={"title": "T", "after": ["commit-changes"],
"timeout": "1h", "script": "make", "after_script": "rm -rf tmp"})`

**Trace**:
```
AutonomyRecipe(pipeline=..., gated_stages=..., accept_stage=..., build_extend=...)
  → frozen dataclass __init__ captures the four keyword-only fields
  → property reads return each captured value verbatim
```

**Assertions**:
```
recipe.pipeline == "my-pipeline"
recipe.gated_stages == ["first-review"]
recipe.accept_stage == "accept-result"
recipe.build_extend["title"] == "T" and recipe.build_extend["after"] == ["commit-changes"]
```

**Sufficiency**: pins the four-property contract — construction captures everything, reads
return it verbatim; prevents a future refactor from dropping or renaming a field.

#### `test_entry_mirrors_reference_workflow`

**Setup**: fixture `reference_workflow` (parsed repo `.goga/workflows/development.yml`).

**Input**: `entry = development_recipe()`

**Trace**:
```
development_recipe()
  → AutonomyRecipe(pipeline="development", gated_stages=[six], accept_stage="accept-result",
                   build_extend={title, after, timeout, script, after_script})
  → compared against parse_workflow(reference).stages / .extend
```

**Assertions**:
```
entry.pipeline == "development"
entry.gated_stages == [s for s in reference.stages if reference.stages[s].approve == "auto"]
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

**Sufficiency**: enforces the verbatim-mirroring requirement against the authoritative reference;
any drift (either side edited alone) fails here instead of silently changing unattended runs.

#### `test_entry_deterministic`

**Setup**: none.

**Input**: two calls `development_recipe()`.

**Trace**:
```
development_recipe(); development_recipe()
  → two constructions from the same constants
```

**Assertions**: `first == second` (dataclass equality) and `first is not second`;
`first.gated_stages is not second.gated_stages` (fresh containers — no shared mutable state).

**Sufficiency**: pins the "pure and deterministic — every call returns an equal entry"
requirement; the fresh-container check prevents a shared-list aliasing regression.

#### `test_contribution_without_workflow_contributes_everything`

**Setup**: `entry = development_recipe()`; `workflow = None`.

**Input**: `document = build_development_contribution(recipe=entry, workflow=None)`

**Trace**:
```
build_development_contribution(entry, None)
  → step 1: extend["build"] = WorkflowExtendStage(after=["commit-changes"], body={title,
    timeout, script, after_script})
  → step 3: workflow is None → all six gated stages → WorkflowStage(approve="auto")
  → step 4: stages["accept-result"] = WorkflowStage(manual=False)
  → step 5: WorkflowDocument(stages=7 entries, extend=1 entry)
```

**Assertions**:
```
sorted(document.stages) == sorted([...six gated..., "accept-result"])
all(document.stages[s].approve == "auto" for s in six gated)
document.stages["accept-result"].manual is False
document.extend["build"].after == ["commit-changes"]
document.extend["build"].body == {"title": "Build implementation", "timeout": "8h",
                                  "script": '...', "after_script": "rm -rf .ralphex"}
document.prompt is None and document.memory is None
```

**Sufficiency**: the Scenario-A floor — an unattended run with no authored workflow must receive
every instruction; this is the tool's core value proposition.

#### `test_contribution_with_authored_workflow_never_empty`

**Setup**: `authored` = `WorkflowDocument(stages={"architecture-review": WorkflowStage(
approve="auto"), …all six…, "accept-result": WorkflowStage(manual=False)},
extend={"build": WorkflowExtendStage(after=["commit-changes"], body={…})})` (or the parsed
reference fixture).

**Input**: `document = build_development_contribution(recipe=development_recipe(), workflow=authored)`

**Trace**:
```
build_development_contribution(entry, authored)
  → every gated stage has authored approve → all skipped
  → only stages["accept-result"] = WorkflowStage(manual=False) and extend["build"] remain
```

**Assertions**:
```
document.stages.keys() == {"accept-result"}
document.extend.keys() == {"build"}
```

**Sufficiency**: the never-empty requirement in its weakest input case — even when the author
already authored everything, the document still carries the acceptance instruction and the build
extension (the platform merge then no-ops); prevents an empty document that the delivery would
discard with a warning.

#### `test_register_hooks_subscribes_single_amendment_hook`

**Setup**: a recording stub
`class _Hooks: def subscribe(self, domain, action, name, hook): self.calls.append((domain, action, name, hook))`
with `calls = []`.

**Input**: `register_hooks(_Hooks())`

**Trace**:
```
register_hooks(hooks)
  → hooks.subscribe("pipeline", "amend_workflow", "autonomy", autonomy)
  → one recorded call; the hook object is the module's autonomy function
```

**Assertions**:
```
len(hooks.calls) == 1
hooks.calls[0][:3] == ("pipeline", "amend_workflow", "autonomy")
hooks.calls[0][3] is goga_tool_autonomous.registration.autonomy
```

**Sufficiency**: the entire subscription contract — exactly one subscription, the correct hard
address, the correct name, the real hook; prevents any extra subscription or renamed address.

#### `test_autonomy_contributes_for_development_pipeline`

**Setup**: a fake view
`pipeline = SimpleNamespace(name="development")`, `workflow = None`; a recorder
`class _Context: def contribute(self, document): self.contributed = document` exposing
`pipeline` and `workflow` attributes.

**Input**: `autonomy(context=ctx)`

**Trace**:
```
autonomy(ctx)
  → name = ctx.pipeline.name == "development" → registry hit
  → document = build_development_contribution(development_recipe(), ctx.workflow=None)
  → ctx.contribute(document)
```

**Assertions**:
```
ctx.contributed is not None
ctx.contributed.stages.keys() == {...six gated..., "accept-result"}
ctx.contributed.extend.keys() == {"build"}
```

**Sufficiency**: the happy path of the hook — registry hit, correct build inputs, contribution
delivered; the strongest single guard over the facade wiring.

#### `test_integration_contribution_only_compiles_unattended`

**Setup**: fixtures `development_pipeline_path`, `tmp_path`; `document =
build_development_contribution(recipe=development_recipe(), workflow=None)`;
`overlay = merge_workflow_overlay(None, [ToolContribution(tool="autonomous", document=document)])`.

**Input**: `compile_flow(development_pipeline_path, tmp_path / "flow.yml", workflow=overlay.workflow)`

**Trace**:
```
compile_flow(pipeline, flow, workflow=contribution-only overlay)
  → parse_dsl(pipeline) → body of the nine real stages
  → apply workflow: six × approve auto (interactive suppression), accept-result manual cancel,
    extend build embedded after commit-changes
  → serialize to tmp_path/"flow.yml"
```

**Assertions** (values verified against goga 2.0.0):
```
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

**Sufficiency**: end-to-end proof that the contributed document survives the real platform merge
and compiler and produces the unattended composition — the tool's whole purpose in one test;
regresses on any vocabulary drift between the package and a future platform release.

#### `test_integration_authored_reference_wins_byte_identical`

**Setup**: fixtures `reference_workflow`, `development_pipeline_path`, `tmp_path`; `document =
build_development_contribution(recipe=development_recipe(), workflow=reference_workflow)`;
`overlay = merge_workflow_overlay(reference_workflow, [ToolContribution(tool="autonomous",
document=document)])`.

**Input**: compile twice —
`compile_flow(pipe, tmp_path/"authored.yml", workflow=reference_workflow)` and
`compile_flow(pipe, tmp_path/"merged.yml", workflow=overlay.workflow)`.

**Trace**:
```
merge_workflow_overlay(authored, [our contribution])
  → gated slots authored-set → contribution values ignored
  → accept-result manual authored-set (False) → kept
  → extend.build under authored name → contribution entry dropped
  → overlay.workflow field-equal to authored
compile both → two serialized flows
```

**Assertions**:
```
(tmp_path/"authored.yml").read_text() == (tmp_path/"merged.yml").read_text()
overlay.provenance == ["autonomous"]
```

**Sufficiency**: the neutrality property (Scenario C) — authored intent wins per slot with zero
byte drift; guards the "do not implement merge or override logic" constraint from the platform
side.

---

### Negative Tests

#### `test_autonomy_silent_for_unknown_pipeline`

**Setup**: fake context with `pipeline = SimpleNamespace(name="review")` (an existing
non-development pipeline name), `workflow = None`, contribute recorder.

**Input**: `autonomy(context=ctx)`

**Trace**:
```
autonomy(ctx)
  → name = "review" → _PIPELINE_DOMAINS miss
  → return None without calling ctx.contribute
```

**Assertions**: `ctx.contributed is None` (no contribution call).

**Sufficiency**: the registry-miss silence contract — any other pipeline must compose exactly as
a project without the tool; prevents an over-eager default match (e.g. substring or
display-name matching).

#### `test_autonomy_ignores_display_name`

**Setup**: fake context with `pipeline = SimpleNamespace(name="development-weekly",
display_name="Development")`, `workflow=None`, recorder.

**Input**: `autonomy(context=ctx)`

**Trace**:
```
autonomy(ctx)
  → name = "development-weekly" ≠ "development" → miss → silent
```

**Assertions**: `ctx.contributed is None`.

**Sufficiency**: pins "compared verbatim — source and display name never participate"; prevents
prefix/display matching regressions.

#### `test_contribution_skips_stages_with_authored_approve`

**Setup**: `authored = WorkflowDocument(stages={"plan-review": WorkflowStage(approve="dialog"),
"coding-plan": WorkflowStage(approve="auto")})`.

**Input**: `document = build_development_contribution(recipe=development_recipe(), workflow=authored)`

**Trace**:
```
build_development_contribution(entry, authored)
  → plan-review (dialog) and coding-plan (auto) → skipped
  → remaining four gated stages → approve="auto"
  → accept-result + build as always
```

**Assertions**:
```
"plan-review" not in document.stages and "coding-plan" not in document.stages
set(document.stages) == {"architecture-review", "apply-architecture", "code-design",
                         "design-review", "accept-result"}
```

**Sufficiency**: the inspect-then-fill rule — *any* authored approval instruction (not just
`auto`) removes the slot from the document; prevents overriding or duplicating authored intent
and keeps the document naming only the slots it fills.

---

### Edge Case Tests

#### `test_recipe_fields_are_read_only`

**Setup**: `recipe = AutonomyRecipe(pipeline="p", gated_stages=[], accept_stage="a",
build_extend={})`.

**Input**: `recipe.pipeline = "other"` (assignment).

**Trace**:
```
attribute assignment on a frozen dataclass instance
  → dataclasses.FrozenInstanceError raised
```

**Assertions**: `with pytest.raises(FrozenInstanceError): recipe.pipeline = "other"`.

**Sufficiency**: the read-only exposure requirement — prevents a mutable-recipe refactor that
would let a consumer (or a hook bug) mutate shared autonomy knowledge.

#### `test_recipe_empty_collections`

**Setup/Input**: `AutonomyRecipe(pipeline="p", gated_stages=[], accept_stage="a",
build_extend={})`.

**Trace**:
```
construction with empty list/dict → fields captured verbatim
```

**Assertions**: `recipe.gated_stages == [] and recipe.build_extend == {} and
recipe.accept_stage == "a"`.

**Sufficiency**: the shape stays a dumb carrier at the empty boundary — no defaults injected, no
validation errors; a hand-built test entry with no gated stages is legal and the delivery must
cope (it would contribute only acceptance + build).

#### `test_contribution_authored_stage_without_approve_still_filled`

**Setup**: `authored = WorkflowDocument(stages={"code-design": WorkflowStage(prompt="x")})` —
the stage is authored with another field but approval unset.

**Input**: `document = build_development_contribution(recipe=development_recipe(), workflow=authored)`

**Trace**:
```
authored.stages["code-design"].approve is None → contribute approve="auto"
other authored fields of that stage untouched (not our vocabulary)
```

**Assertions**: `document.stages["code-design"].approve == "auto"`; all six gated stages
present; `document.stages["code-design"].prompt is None` (we contribute only the approval
instruction).

**Sufficiency**: unset-approval detection is field-precise — authorship of *other* fields must
not suppress the auto-approval fill; also pins that the contributed stage carries nothing but
`approve`.

#### `test_contribution_deterministic_and_pure`

**Setup**: `authored` = the parsed `reference_workflow` fixture; deep-copied snapshot
`copy.deepcopy(authored)`.

**Input**: `d1 = build_development_contribution(recipe=development_recipe(), workflow=authored)`
twice.

**Trace**:
```
two builds over equal inputs → equal documents; authored object only read
```

**Assertions**: `d1 == d2`; `authored == snapshot` (input not mutated); `d1.stages is not
authored.stages` and `d1.extend["build"].body is not d2.extend["build"].body` (fresh maps, no
aliasing of inputs or between results).

**Sufficiency**: the determinism/purity requirements — identical facts produce the identical
contribution and the authored workflow is never mutated; prevents shared-state and
input-mutation regressions that would corrupt other tools' reads of the same view.

#### `test_contribution_with_empty_gated_recipe_contributes_minimum`

**Setup**: `recipe = AutonomyRecipe(pipeline="development", gated_stages=[],
accept_stage="accept-result", build_extend={title: "Build implementation",
after: ["commit-changes"], timeout: "8h", script: <the goga build line>,
after_script: "rm -rf .ralphex"})` — a hand-built entry with no gated stages.

**Input**: `document = build_development_contribution(recipe=recipe, workflow=None)`

**Trace**:
```
build_development_contribution(recipe, None)
  → step 3: the loop over the empty gated_stages contributes nothing
  → step 4: stages["accept-result"] = WorkflowStage(manual=False)
  → step 5: WorkflowDocument(stages={accept-result}, extend={build})
```

**Assertions**:
```
document.stages.keys() == {"accept-result"}
document.extend.keys() == {"build"}
document.stages["accept-result"].manual is False
```

**Sufficiency**: the never-empty guarantee in its minimal case — the delivery tolerates an
empty gated list and contributes exactly the acceptance instruction plus the build extension;
prevents a future refactor that iterates pipeline stages instead of the recipe.

#### `test_contribution_duplicate_and_overlapping_gated_names`

**Setup**: `recipe = AutonomyRecipe(pipeline="p", gated_stages=["code-design", "code-design",
"accept-result"], accept_stage="accept-result", build_extend={…reference values…})` — a
duplicated gated name and a gated name equal to the acceptance stage.

**Input**: `document = build_development_contribution(recipe=recipe, workflow=None)`

**Trace**:
```
build_development_contribution(recipe, None)
  → step 3: "code-design" visited twice → the second map assignment collapses the duplicate
  → step 4: stages["accept-result"] = WorkflowStage(manual=False) overwrites the gated entry
```

**Assertions**:
```
document.stages.keys() == {"code-design", "accept-result"}
document.stages["code-design"].approve == "auto"
document.stages["accept-result"].manual is False
document.stages["accept-result"].approve is None
```

**Sufficiency**: pins the documented tolerance of the data carrier's edge inputs (duplicates,
gated/acceptance overlap) and the deterministic precedence — the unconditional acceptance step
wins the shared name; prevents validation creeping into the plain-data path.

#### `test_register_hooks_never_reads_files_or_config`

**Setup**: run with `cwd=tmp_path` (an empty directory — no `.goga`, no configuration).

**Input**: `register_hooks(recorder)`.

**Trace**:
```
register_hooks(hooks)
  → pure subscribe call; no path is resolved, no file opened
```

**Assertions**: exactly one subscription recorded (same as the positive test); no exception.

**Sufficiency**: the "no configuration or file reads during registration" constraint —
registration must succeed in a bare directory; prevents environment sniffing creeping into the
facade.

#### `test_register_hooks_idempotent_across_calls`

**Setup**: two independent recorders `r1`, `r2` — each a stub
`class _Rec: def subscribe(self, domain, action, name, hook): self.calls.append((domain,
action, name, hook))` with `calls = []`.

**Input**: `register_hooks(r1)` then `register_hooks(r2)` — two calls in one process.

**Trace**:
```
register_hooks(r1) → r1.subscribe("pipeline", "amend_workflow", "autonomy", autonomy)
register_hooks(r2) → r2.subscribe("pipeline", "amend_workflow", "autonomy", autonomy)
  → each call performs exactly one subscribe with identical arguments; no accumulated state
```

**Assertions**:
```
len(r1.calls) == 1 and len(r2.calls) == 1
r1.calls == r2.calls == [("pipeline", "amend_workflow", "autonomy", autonomy)]
```

**Sufficiency**: the platform calls `register_hooks` more than once per process (inspection
with `goga hooks` plus the run itself, each on a fresh registrar) — pins that repeated
registration neither duplicates nor loses the single subscription.

## Additional Instructions for the Implementation Agent

- **Environment**: create/use the virtualenv outside the project at `/opt/project`; install the
  package editable with the `test` extra there and run everything from it
  (`pytest tests/ -x`, `ruff check goga_tool_autonomous/`).
- **`pyproject.toml`**: add `"goga>=2.0"` (unpinned above) to `[project.optional-dependencies].test`
  — currently missing; mandated by `goga_dependency`. Keep `dependencies = []` untouched. The
  stray `[tool.setuptools.package-data] swax = []` entry may be dropped as dead configuration.
- **Module map to create** (all `__init__.py` files re-export the cell surface with `__all__`,
  Google docstrings on every public callable, relative imports for intra-package references):
  | File | Contents |
  |---|---|
  | `goga_tool_autonomous/recipe/model/recipe.py` | `AutonomyRecipe` frozen kw_only dataclass |
  | `goga_tool_autonomous/recipe/model/__init__.py` | `from .recipe import AutonomyRecipe` |
  | `goga_tool_autonomous/recipe/development/entry.py` | `development_recipe` |
  | `goga_tool_autonomous/recipe/development/contribution.py` | `build_development_contribution` (imports `goga.pipeline.workflow`) |
  | `goga_tool_autonomous/recipe/development/__init__.py` | re-export both routines |
  | `goga_tool_autonomous/recipe/__init__.py` | re-export `AutonomyRecipe`, `development_recipe`, `build_development_contribution` (the embeddings) |
  | `goga_tool_autonomous/registration.py` | `_PIPELINE_DOMAINS`, `register_hooks`, `autonomy` |
  | `goga_tool_autonomous/__init__.py` | re-export `register_hooks`, `autonomy` + the three embedded recipe-zone names |
- **Import discipline**: `registration.py` imports only from `.recipe` (no platform import);
  the only runtime platform import in the package is
  `from goga.pipeline.workflow import WorkflowDocument, WorkflowStage, WorkflowExtendStage`
  inside `contribution.py`. Tests import `goga.pipeline.{workflow,hooks,compiler}` freely under
  the test extra.
- **Keep the facade import-clean at all times** — a broken import is fatal to every goga
  command; verify with `python -c "import goga_tool_autonomous"` after every change.
- **No logging, no validation, no caching, no state** anywhere in the package (see
  Cross-cutting Concerns) — do not add "defensive" try/except around the platform calls; the
  hard action owns error conversion.
- **Acceptance checks carried over from the apply-architecture stage** (verify at the end):
  facade import check; `development_recipe()` vs the reference workflow equality
  (`test_entry_mirrors_reference_workflow`); contribution determinism; hook silence for
  non-`development` pipelines; the `goga>=2.0` test-extra entry.
- **Do not modify** the four CODEMANIFESTs or the `.usages/` files — this design implements
  them as-is (Phase 3 audit found no defects).
