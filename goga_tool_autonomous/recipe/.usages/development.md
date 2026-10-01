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
