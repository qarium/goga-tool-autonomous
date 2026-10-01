# Autonomy by fixed workflow amendment on the development pipeline

## Status

accepted (2026-10-01)

`goga-tool-autonomous` delivers an unattended `development` run by subscribing — through the package facade's `register_hooks` — to the single hard action `pipeline.amend_workflow` (one hook, name `autonomy`, taking only `context`). When the composing pipeline name is exactly `development` (source and display name ignored), the hook contributes one document built at each call as a pure function of the delivered facts: `approve: auto` for each gated stage (`architecture-review`, `apply-architecture`, `code-design`, `design-review`, `coding-plan`, `plan-review`) whose authored entry in `context.workflow` carries no `approve`, plus — always, unchecked — `accept-result` with `manual: false` and the `build` extend entry verbatim from the reference workflow (`.goga/workflows/development.yml`). Nothing else: no `prompt`, no `memory`, no other pipelines, no config amendments, no project-file writes. The platform, not the tool, owns the authored-wins-per-slot merge, the `--no-workflow` silence (the checkpoint never fires on a disabled decision), and clean composition over runner-skipped stages (skip flags merge into the authored workflow before the amendment).

## Considered Options

- **Blind contribution vs inspect-then-fill.** A fully blind document is behaviorally identical (authored-set slots never yield in the platform merge), but we keep one narrow inspect rule — skip the `approve` entry when the authored stage already carries one — so the committed contribution names only the slots it actually fills. `manual` and the build entry are contributed unconditionally; checking them buys nothing. When no authored workflow resolved, every entry is contributed.
- **Guard against a custom `development` pipeline missing some gated stages.** Rejected: the amendment view exposes no pipeline stage list, a guard would need project-file reads (duplicating platform discovery and breaking determinism), and the compiler's structural error already is the clean pre-launch failure naming the tool. The tool targets the development-pipeline shape of the goga 2.0.x line.
- **Declaring `goga` as a runtime dependency.** Rejected: `[project.dependencies]` stays empty. The tool is installed into a goga image — the ecosystem provides goga, and declaring it risks resolver conflicts. The model import (`goga.pipeline.workflow`) is safe because goga itself imports the facade. Tests declare `goga>=2.0` (no upper bound) in the test extra and verify the hook against the real merge and compiler.

## Consequences

- Any failure inside the hook surfaces through the hard action as a clean error (`hook autonomy of tool autonomous failed on pipeline.amend_workflow: …`) with the whole contribution discarded — the hook adds no internal exception handling, keeps no state and no cache, and the facade must stay import-clean (a broken import is fatal to every goga command).
- The contributed document is never empty (at minimum the `manual` entry and the build extension), so the platform's empty-contribution warning path is unreachable.
- Extensibility direction: the pipeline→contribution knowledge stays shaped as data (a recipe keyed by pipeline name) behind one generic delivery path, so adding another pipeline later is one more entry — but no other pipeline is named or exposed today; the scope remains `development` only.
- When a future goga release changes the development-pipeline shape, the tool must be revised (the enumerated gated set); tests running against unpinned `goga>=2.0` surface that drift as test failures rather than as stalled unattended runs.
