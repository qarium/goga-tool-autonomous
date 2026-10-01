# Development domain

The `goga_tool_autonomous/recipe/development` cell — the pipeline-specific autonomy knowledge
of the development pipeline and its delivery into a contribution document.

## `development_recipe`

```python
from goga_tool_autonomous.recipe.development import development_recipe, build_development_contribution

entry = development_recipe()
```

The development zone entry — the recipe data of the development pipeline; the single source of
every value the zone's delivery contributes. Plain data, no behavior:

- `pipeline` — `development`
- `gated_stages` — exactly `architecture-review`, `apply-architecture`, `code-design`,
  `design-review`, `coding-plan`, `plan-review`
- `accept_stage` — `accept-result`
- `build_extend` — title `Build implementation`, after `commit-changes`, timeout `8h`, the goga
  build entrypoint invoked with the run's plan artifact, and the `after_script` cleanup

The values mirror the reference workflow `.goga/workflows/development.yml` verbatim — the
reference is authoritative documentation, never read at runtime. Pure and deterministic: every
call returns an equal entry.

## `build_development_contribution`

```python
document = build_development_contribution(recipe=development_recipe(), workflow=authored)
```

Build the development autonomy contribution — the never-empty declarative document the hook
delivers for the development pipeline.

- `recipe` — a recipe entry for the development pipeline (pipeline name `development`); the
  zone exposes its own entry through `development_recipe`
- `workflow` — the authored workflow as delivered by the platform amendment view, or `None`
  when no workflow resolved
- Returns the contribution document: stage instructions plus the `build` extension entry

Algorithm:

1. Place the build extension: put the build extension entry of `recipe` under the fresh
   extension name `build`
2. Fill the gated stages: for each gated stage of `recipe` — contribute the `approve: auto`
   instruction when `workflow` is `None`, the stage has no authored entry, or its authored
   entry carries no approve instruction; skip a stage whose authored entry already carries one
3. Set the acceptance trigger: contribute the `manual: false` instruction for the acceptance
   stage of `recipe` — always, unchecked
4. Assemble the document from the collected stage instructions and the build extension, and
   return it

## What comes out

The document is never empty and always carries:

- the acceptance-stage instruction — the acceptance stage becomes non-manually triggered
- the build extension under the fresh name `build` — title `Build implementation`, placed after
  `commit-changes`, an 8-hour timeout, the goga build entrypoint invoked with the run's plan
  artifact, and `.ralphex` cleanup after the script

Additionally, for every gated stage whose approval mode the author left unset: the
automatic-approval instruction. With `workflow=None`, all six gated stages receive it.

## Inspect-then-fill behavior

A gated stage whose authored entry already carries an approval instruction is omitted from the
contribution — the document names only the slots it actually fills. The acceptance instruction
and the build extension are contributed unconditionally; the platform merge still lets authored
values win per slot. The delivery implements no merge or override logic of its own — the
platform owns authored-wins semantics.

```python
# authored approval present on one stage:
authored.stages["plan-review"].approve = "dialog"

document = build_development_contribution(recipe=entry, workflow=authored)
# the document has no approve instruction for plan-review; the other five are present
```

## Preconditions and side effects

- The call is pure: no I/O, no state, no clock or environment reads; identical inputs produce an
  identical document.
- Failures are not handled here — an invalid recipe or workflow surfaces to the caller as a
  clean error (the amendment action is hard).
- The document uses only stage instructions and extension entries — no prompt or memory
  content.
