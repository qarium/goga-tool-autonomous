# Recipe model

The `goga_tool_autonomous/recipe/model` cell — the `AutonomyRecipe` data shape: how a zone
author defines one pipeline's autonomy knowledge and how consumer code reads it.

Recipe knowledge is plain data: no behavior, no I/O, no state. The recipe entity deliberately
uses plain Python data structures instead of pydantic — the package keeps its runtime
dependencies empty.

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
- The extension entry follows the platform's extend-entry vocabulary; the extension name is
  chosen by the delivery path, not by the entry.

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
