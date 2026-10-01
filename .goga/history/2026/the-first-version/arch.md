# Architecture Plan — goga-tool-autonomous

## Topic

**goga-tool-autonomous** — unattended `development` pipeline via a single `amend_workflow` hook contribution.

Plan path: `.goga/history/2026/the-first-version/arch.md` (topic `the-first-version`, year 2026).

Source task: `.goga/history/2026/the-first-version/task.md` (PRD and ADR in the same topic).

## Implementation Order

All cells are **created anew** (Artifact Resolution: greenfield — the cell schema is empty, `goga schema` → `[]`).

| # | Cell | Reason for the order |
|---|---|---|
| 1 | `goga_tool_autonomous/recipe/model` | Leaf — no Imports; defines `AutonomyRecipe`, the type every other cell references |
| 2 | `goga_tool_autonomous/recipe/development` | Depends on `recipe/model` (imports `AutonomyRecipe`); declares the development entry and its delivery |
| 3 | `goga_tool_autonomous/recipe` | Parent zone facade — depends on both sub-cells; re-exports their API and provides the domain usage file from its facade |
| 4 | `goga_tool_autonomous` | Main cell — depends on `recipe` (types + the `development` domain practice); declares the subscription and the registry |

One project-level usage file is created: `.goga/usages/cooks/goga-dependency.md` — the spec for connecting goga as a dependency (referenced by the main cell). The WorkflowDocument surface is consumed through the existing synced platform usages (read-only), referenced by path in the cells' `Usages` headers.

## Artifacts

### Cell 1: `goga_tool_autonomous/recipe/model` (create new)

#### CODEMANIFEST — `goga_tool_autonomous/recipe/model/CODEMANIFEST`

```yaml
Usages:
  conventions: .goga/usages/conventions.md
  workflow_document: .goga/usages/github/goga/pipeline/workflow/parse-workflow.md

Annotations: |
  Use `conventions` for code writing rules and testing.

  Recipe knowledge is plain data: no behavior, no I/O, no state.
  The recipe entity deliberately uses plain Python data structures instead of pydantic — the
  package keeps its runtime dependencies empty; this deviation from `conventions` is accepted
  for this cell.
  Use `workflow_document` for the extend-entry vocabulary the `build_extend` data carries.

---

"AutonomyRecipe(pipeline: str, gated_stages: list[str], accept_stage: str, build_extend: dict[str, str | list[str]])":
  location: recipe.py
  annotations: |
    Immutable data recipe for one pipeline's autonomy contribution — the single source of every
    entry the delivery path contributes for that pipeline.

    `pipeline`: the exact pipeline name the recipe targets; source and display name are ignored
    `gated_stages`: stages receiving the approve instruction auto when the author left the
    approval mode unset
    `accept_stage`: the acceptance stage receiving the unconditional non-manual instruction
    `build_extend`: the build extension entry as data, in the extend-entry vocabulary of
    `workflow_document`

    Requirements:
    - Construction captures all four fields; instances expose them read-only

    Constraints:
    - A data carrier only — no methods, no computed state, no I/O
    - Plain data structures only (no pydantic) — the cell-wide deviation from `conventions`
  properties:
    "pipeline -> str": |
      Exact target pipeline name; compared verbatim against the composing pipeline's name —
      source and display name never participate.
    "gated_stages -> list[str]": |
      Stages receiving the approve instruction auto when their authored entry carries no
      approve instruction; the concrete set is zone knowledge defined by the pipeline's recipe
      entry.
    "accept_stage -> str": |
      The acceptance stage receiving the unconditional non-manual instruction —
      contributed always, unchecked.
    "build_extend -> dict[str, str | list[str]]": |
      The build extension entry as plain data in the extend-entry vocabulary of
      `workflow_document` (title, after, timeout, script, after_script); the delivery path
      places it under the fresh extension name build.

---

Author: Goga
CreatedAt: 01/10/26
Description: |
  The generic recipe shape of the autonomy tool: one pipeline's contribution knowledge as
  plain immutable data.
```

#### Usage file — `goga_tool_autonomous/recipe/model/.usages/recipe.md`

```md
# Recipe entries — defining and consuming pipeline autonomy knowledge

Domain: the `AutonomyRecipe` data shape of the `goga_tool_autonomous/recipe` cell — how a zone
author defines one pipeline's autonomy knowledge and how consumer code reads it.
Audience: contributors adding a pipeline zone (a new `recipe/<pipeline>` sub-cell) and code that
delivers recipes into workflow contributions.

## The shape

`AutonomyRecipe(pipeline, gated_stages, accept_stage, build_extend)` — an immutable, plain-data
carrier. All four fields are captured at construction and exposed read-only:

| Field | Meaning |
|---|---|
| `pipeline` | the exact pipeline name the recipe targets; compared verbatim (source and display name ignored) |
| `gated_stages` | stages receiving `approve: auto` when the authored workflow leaves the approval mode unset |
| `accept_stage` | the acceptance stage receiving the unconditional non-manual instruction |
| `build_extend` | the build extension entry as data, in the workflow extend-entry vocabulary (title, after, timeout, script, after_script) |

## Defining an entry (a new pipeline zone)

```python
from goga_tool_autonomous.recipe import AutonomyRecipe

my_recipe = AutonomyRecipe(
    pipeline="my-pipeline",
    gated_stages=["first-review", "second-review"],
    accept_stage="accept-result",
    build_extend={
        "title": "Build implementation",
        "after": ["commit-changes"],
        "timeout": "8h",
        "script": "python3 -P -m goga.build \"$(python3 -m goga history path -f plan.md)\"",
        "after_script": "rm -rf .ralphex",
    },
)
```

- Construct with keyword arguments; capture all four fields at once.
- Use plain data structures only — lists, strings, dicts; no models, no behavior.
- The extension entry follows the platform's extend-entry vocabulary; the extension name is chosen
  by the delivery path, not by the entry.

## Reading an entry

```python
recipe.pipeline        # "my-pipeline"
recipe.gated_stages    # ["first-review", "second-review"]
recipe.accept_stage    # "accept-result"
recipe.build_extend    # {"title": ..., "after": [...], ...}
```

- Fields are read-only; nothing is computed on read.
- Consumers decide how an entry maps into a contribution; the entry itself performs no action.

## Preconditions and side effects

- Constructing an entry performs no I/O and touches no project files.
- Entries are inert data: holding one changes nothing until a delivery path contributes it.
- Keep one entry per pipeline; the composing registry keys entries by `pipeline`.
```

### Cell 2: `goga_tool_autonomous/recipe/development` (create new)

#### CODEMANIFEST — `goga_tool_autonomous/recipe/development/CODEMANIFEST`

```yaml
Imports:
  - Types:
      - AutonomyRecipe
    Usages:
      - recipe AS recipe_guide
    From: goga_tool_autonomous/recipe/model

Usages:
  conventions: .goga/usages/conventions.md
  workflow_document: .goga/usages/github/goga/pipeline/workflow/parse-workflow.md
  goga_dependency: .goga/usages/cooks/goga-dependency.md

Annotations: |
  Use `conventions` for code writing rules and testing.

  This cell is the development zone: the pipeline-specific autonomy knowledge of the
  development pipeline and its delivery into a contribution document.
  The zone entry `development_recipe` is plain data defined in this cell; its values mirror
  the reference workflow .goga/workflows/development.yml — the reference is authoritative
  documentation, never read at runtime.
  Use `recipe_guide` from Imports for the entry shape and field semantics.
  Use `workflow_document` for the platform model this cell constructs and reads.
  Use `goga_dependency` for acquiring the platform model at runtime — the package declares
  no runtime goga dependency.

---

"development_recipe() -> entry: AutonomyRecipe":
  location: entry.py
  annotations: |
    The development zone entry — the recipe data of the development pipeline; the single
    source of every value the zone's delivery contributes.

    `entry`: the development recipe — the gated-stage set, the acceptance stage, and the
    build extension

    Requirements:
    - Values mirror the reference workflow .goga/workflows/development.yml verbatim:
      gated_stages is exactly architecture-review, apply-architecture, code-design,
      design-review, coding-plan, plan-review; accept_stage is accept-result; build_extend
      carries title Build implementation, after commit-changes, timeout 8h, the goga build
      entrypoint invoked with the run's plan artifact, and the after_script cleanup
    - Pure and deterministic — every call returns an equal entry; the reference file is
      never read at runtime

    Constraints:
    - Data only — the entry performs no action beyond construction

"build_development_contribution(recipe: AutonomyRecipe, workflow: WorkflowDocument | None) -> document: WorkflowDocument":
  location: contribution.py
  annotations: |
    Build the development autonomy contribution — the never-empty declarative document the
    hook delivers for the development pipeline.

    `recipe`: the development recipe entry — the source of every contributed entry
    `workflow`: the authored workflow after the decision and the runner-skip merge; None when
    no workflow resolved
    `document`: the WorkflowDocument-shaped contribution — stage instructions plus the build
    extension

    Algorithm:
    1. Place the build extension: put the build extension entry of `recipe` under the fresh
       extension name build
    2. Fill the gated stages: for each gated stage of `recipe` — contribute the approve
       instruction auto when `workflow` is None, the stage has no authored entry, or its
       authored entry carries no approve instruction; skip a stage whose authored entry
       already carries one
    3. Set the acceptance trigger: contribute the manual instruction false for the acceptance
       stage of `recipe` — always, unchecked
    4. Assemble the document from the collected stage instructions and the build extension,
       and return it

    Requirements:
    - The result is never empty: at minimum the acceptance-stage instruction and the build
      extension
    - Deterministic: the same recipe and workflow always produce the identical document
    - Use `workflow_document` for both the construction and the authored-instruction reads

    Constraints:
    - Contribute stage instructions and the build extension only — never prompt or memory
      entries
    - Do not implement merge or override logic — the platform owns authored-wins semantics
    - No I/O, no state, no time or environment dependence

---

Author: Goga
CreatedAt: 01/10/26
Description: |
  The development functional domain: the development pipeline's recipe entry (plain data) and
  its delivery into a WorkflowDocument-shaped contribution.
```

#### Usage file — `goga_tool_autonomous/recipe/development/.usages/contribution.md`

```md
# Building the development contribution

Domain: the development zone's delivery — building the workflow-amendment contribution document
for the development pipeline from a recipe entry and a delivered authored workflow.
Audience: consumers wiring the delivery (the package facade and its hook) and test authors
asserting the contribution against the real platform merge and compiler.

## The call

```python
from goga_tool_autonomous.recipe.development import development_recipe, build_development_contribution

document = build_development_contribution(recipe=development_recipe(), workflow=authored)
```

- `recipe` — a recipe entry for the development pipeline (pipeline name `development`); the
  zone exposes its own entry through `development_recipe`.
- `workflow` — the authored workflow as delivered by the platform amendment view, or `None` when
  no workflow resolved.
- Returns the contribution document: stage instructions plus the `build` extension entry.

## What comes out

The document is never empty and always carries:

- the acceptance-stage instruction — the acceptance stage becomes non-manually triggered
- the build extension under the fresh name `build` — title `Build implementation`, placed after
  `commit-changes`, an 8-hour timeout, the goga build entrypoint invoked with the run's plan
  artifact, and `.ralphex` cleanup after the script

Additionally, for every gated stage whose approval mode the author left unset:

- the automatic-approval instruction (`architecture-review`, `apply-architecture`, `code-design`,
  `design-review`, `coding-plan`, `plan-review`)

With `workflow=None`, all six gated stages receive the automatic-approval instruction.

## Inspect-then-fill behavior

A gated stage whose authored entry already carries an approval instruction is omitted from the
contribution — the document names only the slots it actually fills. The acceptance instruction and
the build extension are contributed unconditionally; the platform merge still lets authored values
win per slot.

```python
# authored approval present on one stage:
authored.stages["plan-review"]["approve"] = "dialog"

document = build_development_contribution(recipe=entry, workflow=authored)
# the document has no approve instruction for plan-review; the other five are present
```

## Preconditions and side effects

- The call is pure: no I/O, no state, no clock or environment reads; identical inputs produce an
  identical document.
- Failures are not handled here — an invalid recipe or workflow surfaces to the caller as a clean
  error (the amendment action is hard).
- The document uses only stage instructions and extension entries — no prompt or memory content.
```

### Cell 3: `goga_tool_autonomous/recipe` (create new — parent zone facade)

#### CODEMANIFEST — `goga_tool_autonomous/recipe/CODEMANIFEST`

```yaml
Imports:
  - Types:
      - AutonomyRecipe
    Usages:
      - recipe
    From: goga_tool_autonomous/recipe/model
  - Types:
      - development_recipe
      - build_development_contribution
    Usages:
      - contribution
    From: goga_tool_autonomous/recipe/development

Usages:
  conventions: .goga/usages/conventions.md

Annotations: |
  Use `conventions` for code writing rules and testing.

  This cell is the recipe zone facade: the single contract surface of the zone — the recipe
  shape and every pipeline domain's entry and delivery, re-exported from the sub-cells.
  Use `recipe` and `contribution` from Imports for the re-exported sub-cell APIs.

---

->AutonomyRecipe: {}

->development_recipe: {}

->build_development_contribution: {}

---

Author: Goga
CreatedAt: 01/10/26
Description: |
  The recipe zone facade: aggregates the zone's sub-cells — the recipe shape and the pipeline
  domain entries and deliveries — into one contract surface with functional-domain usage files.
```

#### Usage file — `goga_tool_autonomous/recipe/.usages/development.md`

```md
# The development domain of the recipe zone

Domain: the development functional domain provided from the `goga_tool_autonomous/recipe`
facade — the development recipe entry and its delivery into a workflow contribution.
Audience: consumers of the recipe zone facade (the package facade and its subscription logic)
and test authors asserting the development contribution.

## The domain API

```python
from goga_tool_autonomous.recipe import AutonomyRecipe, development_recipe, build_development_contribution
```

The domain aggregates the zone's development knowledge as two artifacts: the entry —
`development_recipe`, the immutable plain-data recipe of the development pipeline — and the
delivery — building the contribution document from the entry and a delivered authored
workflow.

## The development entry

```python
entry = development_recipe()
```

The entry is defined by the zone; its values mirror the reference workflow of the tool's
repository — pipeline `development`, the six gated stages (architecture-review,
apply-architecture, code-design, design-review, coding-plan, plan-review), the acceptance
stage `accept-result`, and the build extension in the workflow extend-entry vocabulary
(title, after, timeout, script, after_script). `AutonomyRecipe` remains the shape for
hand-built entries in tests and future zones.

## Delivering the contribution

```python
document = build_development_contribution(recipe=entry, workflow=authored)
```

- `workflow` — the authored workflow as delivered by the platform amendment view, or `None`
  when no workflow resolved
- The document is never empty: it always carries the acceptance-stage instruction (non-manual
  acceptance) and the build extension under the fresh name `build`; for every gated stage whose
  approval mode the author left unset it adds the automatic-approval instruction — with
  `workflow=None`, all six are present
- A gated stage whose authored entry already carries an approval instruction is omitted — the
  document names only the slots it fills; authored values win per slot in the platform merge

## Preconditions and side effects

- The delivery is a pure function of the entry and the workflow: identical inputs produce an
  identical document; no I/O, no state, no clock reads.
- Only stage instructions and extension entries — no prompt or memory content.
```

### Cell 4: `goga_tool_autonomous` (create new — the main cell)

#### CODEMANIFEST — `goga_tool_autonomous/CODEMANIFEST`

```yaml
Imports:
  - Types:
      - AutonomyRecipe
      - development_recipe
      - build_development_contribution
    Usages:
      - development
    From: goga_tool_autonomous/recipe

Usages:
  conventions: .goga/usages/conventions.md
  workflow_document: .goga/usages/github/goga/pipeline/workflow/parse-workflow.md
  hooks_registration: .goga/usages/github/goga/hooks/registering-hooks.md
  pipeline_amendment: .goga/usages/github/goga/pipeline/registering-hooks.md
  goga_dependency: .goga/usages/cooks/goga-dependency.md

Annotations: |
  Use `conventions` for code writing rules and testing.

  This cell is the package facade: the single API surface of the tool and its goga-platform
  subscription entry. The facade module must stay import-clean — a broken import is fatal to
  every goga command.
  The package runs inside a goga-provided interpreter: per `goga_dependency`, the runtime
  dependencies stay empty — goga is provided by the ecosystem and is declared only in the test
  extra, unpinned above the supported line.
  The subscription maps each exact pipeline name to its functional domain of the recipe zone:
  the development pipeline is served by the `development` domain from Imports — the
  `development_recipe` entry and the `build_development_contribution` delivery; a new pipeline
  zone adds its domain imports, one registry entry, and the domain's embeddings here — the
  facade declares no new types for it.
  Use `hooks_registration` for the facade and subscription contract.
  Use `pipeline_amendment` for the amendment view semantics the hook consumes.

---

"register_hooks(hooks: Hooks)":
  location: registration.py
  annotations: |
    Subscribe the single autonomy hook to the pipeline workflow-amendment action.

    `hooks`: the goga subscription surface delivered at registration — exposes
    subscribe(domain, action, name, hook) per `hooks_registration`

    Algorithm:
    1. Subscribe the hook routine `autonomy` under domain pipeline, action amend_workflow,
       hook name autonomy — exactly one subscription, unconditional

    Requirements:
    - The facade imports cleanly at all times — an import failure stops every goga command
    - No other facades exist: no CLI entry, no install lifecycle

    Constraints:
    - Never subscribe any other address or hook name
    - No configuration or file reads during registration

"autonomy(context: WorkflowAmendment)":
  location: registration.py
  annotations: |
    The amendment hook — deliver the autonomy contribution for the composing pipeline.

    `context`: the per-tool amendment view delivered by the platform

    Algorithm:
    1. Resolve the functional domain for the exact pipeline name of `context` — the
       development pipeline maps to the `development` domain from Imports; a miss returns
       silently
    2. Build the contribution document with the delivery of the resolved domain —
       `build_development_contribution` applied to the domain entry `development_recipe` —
       and the authored workflow of `context` (a `workflow_document`, or none when
       unresolved)
    3. Contribute the document through `context`

    Requirements:
    - A pure function of the delivered facts — identical facts produce the identical
      contribution
    - Read only the pipeline identity and the authored workflow from the view

    Constraints:
    - No state, no cache, no internal exception handling — failures propagate as clean
      command errors through the hard action
    - No project-file or configuration reads; contribute nothing beyond the built document

->AutonomyRecipe: {}

->development_recipe: {}

->build_development_contribution: {}

---

Author: Goga
CreatedAt: 01/10/26
Description: |
  The goga-tool-autonomous package facade: the platform subscription (one hook on the pipeline
  workflow-amendment action) and the re-exported recipe-zone API, mapping each exact pipeline
  name to its functional domain.
```

#### Usage file — `goga_tool_autonomous/.usages/development.md`

```md
# The development domain — unattended development runs via the facade

Domain: the development functional domain of the `goga_tool_autonomous` facade — the platform
subscription, the contributed amendments, and the delivery API for the development pipeline.
Audience: maintainers reasoning about unattended development runs, integrators embedding the
package in a goga image, and test authors asserting the contribution against the real platform
merge and compiler.

## Platform subscription

```python
from goga_tool_autonomous import register_hooks

register_hooks(hooks)  # goga calls this when a command first reaches a hook checkpoint
```

The registration subscribes exactly one hook: address `pipeline` / `amend_workflow`, name
`autonomy`. No CLI entry, no install lifecycle. The amendment action fires after workflow
resolution and the runner-skip merge, before compilation — in the run form and the card form
alike.

## What the domain contributes

For a composing pipeline named exactly `development`:

- automatic approval for every gated stage whose approval mode the author left unset
  (`architecture-review`, `apply-architecture`, `code-design`, `design-review`, `coding-plan`,
  `plan-review`)
- non-manual acceptance for the acceptance stage
- the build extension after `commit-changes` with the reference configuration

For any other pipeline the tool contributes nothing — composition is identical to a project
without the tool.

## Building the contribution directly

```python
from goga_tool_autonomous import development_recipe, build_development_contribution

document = build_development_contribution(recipe=development_recipe(), workflow=authored)
```

- `recipe` — the development recipe entry, built by the zone's `development_recipe` and
  re-exported by the facade
- `workflow` — the authored workflow as delivered by the amendment view, or `None` when no
  workflow resolved
- Returns the contribution document: stage instructions plus the `build` extension entry

The document is never empty and always carries the acceptance-stage instruction and the build
extension under the fresh name `build` — title `Build implementation`, after `commit-changes`, an
8-hour timeout, the goga build entrypoint invoked with the run's plan artifact, and `.ralphex`
cleanup after the script. A gated stage whose authored entry already carries an approval
instruction is omitted; with `workflow=None` all six are present. Authored values win per slot in
the platform merge — nothing overridden, nothing duplicated.

## The development entry

```python
from goga_tool_autonomous import development_recipe

entry = development_recipe()
```

The entry is defined by the development zone and re-exported by the facade; its values mirror
the reference workflow of the tool's repository — pipeline `development`, the six gated stages
(`architecture-review`, `apply-architecture`, `code-design`, `design-review`, `coding-plan`,
`plan-review`), the acceptance stage `accept-result`, and the build extension in the workflow
extend-entry vocabulary. An immutable, plain-data carrier; `AutonomyRecipe` (also re-exported)
is the shape for hand-built entries in tests and future zones.

The facade keeps a module-level registry mapping the pipeline name to the zone's domain API —
the entry factory and the delivery; the hook resolves the composing pipeline's name against it
— an exact match; source and display names never participate.

## Adding the next domain

One pipeline zone — one facade usage file (this file is the development one). To add a domain:
create the zone sub-cell `goga_tool_autonomous/recipe/<pipeline>`, register it in the facade
registry, re-export its entry and delivery on the facade via embeddings, and document it in its
own facade usage file.

## Preconditions and side effects

- The hook and the delivery are pure functions of their inputs: no state, no cache, no clock or
  environment reads; identical facts produce the identical contribution.
- No project file is ever created or modified; contributions are per-run, in-memory, and
  deterministic.
- Failures surface as clean command errors through the hard action; the whole contribution is
  discarded. A broken package import is fatal to every goga command — the facade stays
  import-clean.
```

### Project usage (create new) — `.goga/usages/cooks/goga-dependency.md`

```md
# goga as a dependency — how this package connects the platform

Domain: declaring (and not declaring) the goga platform as a dependency of the
`goga-tool-autonomous` package. Audience: maintainers of the package and contributors updating
the dependency manifest.

## The rule

- **Runtime: never declare goga.** The package's runtime dependencies stay empty. A goga tool is
  installed into a goga-provided interpreter (the project's goga image) — the ecosystem provides
  goga, and declaring it again risks resolver conflicts inside that image.
- **Import safety without a declaration.** Importing platform modules inside the package (for
  example the workflow model from `goga.pipeline.workflow`) is safe because goga itself imports
  the package facade — the platform is present in the interpreter whenever the package runs.
- **Tests: declare goga unpinned.** The test extra declares `goga>=2.0` with no upper bound, so a
  future platform release that changes the development-pipeline shape surfaces as test failures
  instead of silently passing or stalling unattended runs.

## Manifest shape

```toml
[project]
dependencies = []          # runtime — stays empty

[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.10",
    "ruff>=0.15.0",
    "goga>=2.0",           # test-only, no upper bound
]
```

## What this means in practice

- Never add goga to the runtime dependencies — not even with a lower bound.
- Keep the test-extra entry unpinned above (`>=2.0`, no upper bound).
- Installing the package into a plain (non-goga) environment is out of scope: the package only
  runs inside a goga-provided interpreter.
```

## Dependency Map

```
                    ┌──────────────────────────────────────────────┐
                    │  goga_tool_autonomous          (main cell)   │
                    │  register_hooks(hooks), autonomy(context)    │
                    │  registry {pipeline name → domain API}       │
                    │  Imports: recipe (Types ×3 + Usages[development])
                    │  Embeds: AutonomyRecipe,                     │
                    │           development_recipe,                │
                    │           build_development_contribution     │
                    └────────────────────▲─────────────────────────┘
                                         │ Types + Usages[development]
                ┌────────────────────────┴───────────────────────┐
                │  goga_tool_autonomous/recipe     (parent zone) │
                │  facade: embeddings of the sub-cell types      │
                │  .usages/development.md (domain from facade)   │
                └───────▲──────────────────────────▲──────────────┘
                        │ Types + Usages[recipe]   │ Types + Usages[contribution]
      ┌─────────────────┴──────────┐   ┌───────────┴─────────────────────┐
      │ recipe/model    (sub-cell) │   │ recipe/development (sub-cell)   │
      │ AutonomyRecipe             │◄──┤ Imports: AutonomyRecipe from    │
      │ .usages/recipe.md          │   │          recipe/model           │
      │                            │   │ development_recipe (the entry)  │
      │                            │   │ build_development_contribution  │
      │                            │   │ .usages/contribution.md         │
      └────────────────────────────┘   └─────────────────────────────────┘

External (read-only): goga platform specs consumed via the synced usages — the WorkflowDocument
vocabulary via .goga/usages/github/goga/pipeline/workflow/parse-workflow.md (referenced by the
model, development, and main cells); hooks/amendment semantics via
.goga/usages/github/goga/hooks/registering-hooks.md and
.goga/usages/github/goga/pipeline/registering-hooks.md (referenced by the main cell).
Project spec (created): .goga/usages/cooks/goga-dependency.md — connecting goga as a dependency
(referenced by the development and main cells).
```

Connection list:

| Source cell | Imported types | Imported usages | Target cell |
|---|---|---|---|
| `goga_tool_autonomous/recipe/model` | `AutonomyRecipe` | `recipe AS recipe_guide` | `goga_tool_autonomous/recipe/development` |
| `goga_tool_autonomous/recipe/model` | `AutonomyRecipe` | `recipe` | `goga_tool_autonomous/recipe` |
| `goga_tool_autonomous/recipe/development` | `development_recipe`, `build_development_contribution` | `contribution` | `goga_tool_autonomous/recipe` |
| `goga_tool_autonomous/recipe` | `AutonomyRecipe`, `development_recipe`, `build_development_contribution` | `development` | `goga_tool_autonomous` |

## Verification Checklist

After implementing each artifact, check:

- [ ] `goga lint` passes with zero errors across the project (all four CODEMANIFESTs parse; imports resolve; references resolve)
- [ ] `goga schema` shows the four cells with their types, usages, and dependency edges exactly as in the Dependency Map
- [ ] Facade import check: `python -c "from goga_tool_autonomous import register_hooks, autonomy, AutonomyRecipe, development_recipe, build_development_contribution"` succeeds (import-clean facade; `__all__` exposes exactly these five names)
- [ ] Sub-cell facades: `from goga_tool_autonomous.recipe import AutonomyRecipe, development_recipe, build_development_contribution`, `from goga_tool_autonomous.recipe.development import development_recipe, build_development_contribution`, and `from goga_tool_autonomous.recipe.model import AutonomyRecipe` all succeed
- [ ] The development entry `development_recipe()` equals the reference `.goga/workflows/development.yml` values (six gated stages, `accept-result`, verbatim `extend.build`) — asserted by tests against the file
- [ ] The contribution is never empty and deterministic: repeated builds over identical inputs produce identical documents
- [ ] Hook behavior: silence for a non-`development` pipeline name; full contribution for `development` with `workflow=None`; authored-`approve` stages omitted — verified against the real `merge_workflow_overlay` and `compile_flow` (tests)
- [ ] No cell writes project files at runtime; no `prompt`/`memory` entries in the contribution; per `goga_dependency` the runtime dependencies stay empty and goga appears only in the test extra, unpinned above the supported line
