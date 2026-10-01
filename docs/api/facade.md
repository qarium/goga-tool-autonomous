# Package facade

The `goga_tool_autonomous` cell — the platform subscription and the single API surface of the
tool. The facade must stay import-clean: a broken import is fatal to every goga command.

## Platform subscription

```python
from goga_tool_autonomous import register_hooks

register_hooks(hooks)  # goga calls this when a command first reaches a hook checkpoint
```

The registration subscribes exactly one hook: address `pipeline` / `amend_workflow`, name
`autonomy`. No CLI entry, no install lifecycle. The amendment action fires after workflow
resolution and the runner-skip merge, before compilation — in the run form and the card form
alike.

### `register_hooks(hooks: Hooks)`

Subscribe the single autonomy hook to the pipeline workflow-amendment action.

- `hooks`: the goga subscription surface delivered at registration — exposes
  `subscribe(domain, action, name, hook)`
- Subscribes the hook routine `autonomy` under domain `pipeline`, action `amend_workflow`,
  hook name `autonomy` — exactly one subscription, unconditional
- No configuration or file reads during registration; never subscribes any other address or
  hook name

### `autonomy(context: WorkflowAmendment)`

The amendment hook — deliver the autonomy contribution for the composing pipeline.

- `context`: the per-tool amendment view delivered by the platform

Algorithm:

1. Resolve the functional domain for the exact pipeline name of `context` — the `development`
   pipeline maps to the development domain; a miss returns silently
2. Build the contribution document with the delivery of the resolved domain —
   `build_development_contribution` applied to the domain entry `development_recipe` — and the
   authored workflow of `context` (a workflow document, or none when unresolved)
3. Contribute the document through `context`

A pure function of the delivered facts — identical facts produce the identical contribution.
Failures propagate as clean command errors through the hard action; no state, no cache, no
internal exception handling.

## Re-exported API

The facade re-exports the recipe-zone API through embeddings:

- [`development_recipe`](development-domain.md#development_recipe) — the development recipe entry
- [`build_development_contribution`](development-domain.md#build_development_contribution) — the
  development delivery
- [`AutonomyRecipe`](recipe-model.md) — the recipe shape

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
extension under the fresh name `build` — title `Build implementation`, after `commit-changes`,
an 8-hour timeout, the goga build entrypoint invoked with the run's plan artifact, and
`.ralphex` cleanup after the script. A gated stage whose authored entry already carries an
approval instruction is omitted; with `workflow=None` all six are present. Authored values win
per slot in the platform merge — nothing overridden, nothing duplicated.

## The facade registry

The facade keeps a module-level registry mapping the pipeline name to the zone's domain API —
the entry factory and the delivery. The hook resolves the composing pipeline's name against it
— an exact match; source and display names never participate.

## Adding the next domain

One pipeline zone — one facade usage file. To add a domain: create the zone sub-cell
`goga_tool_autonomous/recipe/<pipeline>`, register it in the facade registry, re-export its
entry and delivery on the facade via embeddings, and document it in its own facade usage file.

## Preconditions and side effects

- The hook and the delivery are pure functions of their inputs: no state, no cache, no clock or
  environment reads; identical facts produce the identical contribution.
- No project file is ever created or modified; contributions are per-run, in-memory, and
  deterministic.
- Failures surface as clean command errors through the hard action; the whole contribution is
  discarded. A broken package import is fatal to every goga command — the facade stays
  import-clean.
