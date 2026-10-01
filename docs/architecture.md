# Architecture

The tool is organized as a directed hierarchy of cells — each a directory with a `CODEMANIFEST`
contract and consumer-facing practices in `.usages/`. Contracts are read-only: when
implementation and contract disagree, the implementation is what gets fixed.

## Cell map

| Cell | Role |
|---|---|
| [`goga_tool_autonomous`](api/facade.md) | Package facade — the platform subscription (one hook) and the single API surface |
| [`goga_tool_autonomous/recipe`](api/recipe-zone.md) | Recipe zone facade — re-exports the zone's sub-cell contracts |
| [`goga_tool_autonomous/recipe/development`](api/development-domain.md) | Development functional domain — the pipeline's recipe entry and its delivery |
| [`goga_tool_autonomous/recipe/model`](api/recipe-model.md) | Recipe model — the `AutonomyRecipe` data shape |

## Import graph

```
goga_tool_autonomous            (package facade, the hook + subscription)
└── goga_tool_autonomous/recipe         (zone facade, re-exports)
    ├── goga_tool_autonomous/recipe/model          (AutonomyRecipe shape)
    └── goga_tool_autonomous/recipe/development    (development domain)
```

The package facade imports the recipe-zone facade only; the zone facade aggregates the model
cell and the per-pipeline domain cells. Cross-imports between cells never form a cycle.

## Amendment data flow

The amendment action fires after workflow resolution and the runner-skip merge, before
compilation — in the run form and the card form alike:

1. goga calls `register_hooks(hooks)` when a command first reaches a hook checkpoint.
2. The registration subscribes exactly one hook: address `pipeline` / `amend_workflow`, name
   `autonomy`.
3. The platform delivers a `WorkflowAmendment` context to the hook.
4. The hook resolves the functional domain for the exact pipeline name of the context — the
   `development` pipeline maps to the development domain; a miss returns silently and
   composition is identical to a project without the tool.
5. The delivery `build_development_contribution` builds the contribution document from the
   recipe entry and the authored workflow (or `None` when no workflow resolved).
6. The hook contributes the document through the context. The platform merge keeps authored
   values per slot — nothing is overridden, nothing is duplicated.

## Extension point — adding the next pipeline domain

One pipeline zone — one facade usage file. To add a domain:

1. Create the zone sub-cell `goga_tool_autonomous/recipe/<pipeline>` with its recipe entry
   (plain data, shaped by `AutonomyRecipe`) and its delivery.
2. Register it in the facade registry — one registry entry.
3. Re-export its entry and delivery on the facade via embeddings.
4. Document it in its own facade usage file.

The facade declares no new types for a new zone — the domain's contract arrives through
embeddings.

## Runtime properties

- The package runs inside a goga-provided interpreter: runtime dependencies stay empty — goga
  is provided by the ecosystem and is declared only in the test extra, unpinned above the
  supported line.
- The facade module stays import-clean — a broken import is fatal to every goga command.
- The hook and the delivery are pure functions of their inputs: no state, no cache, no clock or
  environment reads; identical facts produce the identical contribution.
- Failures propagate as clean command errors through the hard action — no internal exception
  handling.
