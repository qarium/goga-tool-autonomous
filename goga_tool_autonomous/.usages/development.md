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
