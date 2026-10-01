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
authored.stages["plan-review"].approve = "dialog"

document = build_development_contribution(recipe=entry, workflow=authored)
# the document has no approve instruction for plan-review; the other five are present
```

## Preconditions and side effects

- The call is pure: no I/O, no state, no clock or environment reads; identical inputs produce an
  identical document.
- Failures are not handled here — an invalid recipe or workflow surfaces to the caller as a clean
  error (the amendment action is hard).
- The document uses only stage instructions and extension entries — no prompt or memory content.
