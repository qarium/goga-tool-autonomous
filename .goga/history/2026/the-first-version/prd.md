# Autonomous Development Pipeline — goga-tool-autonomous

## Problem

Teams using goga on their projects cannot run the development pipeline autonomously. Two gaps carry equal weight and define this product:

**The autonomy gap.** A developer runs the goga `development` pipeline for a task, but by default the run stops for a human approval at every gated stage, the final `accept-result` stage waits for a manual trigger, and the build is a separate manual step outside the pipeline. A task cannot go from definition to a verified, built result as one unattended run — the pipeline demands continuous human attention at every gate.

**The reuse gap.** The only existing path to autonomy is hand-authoring a project-local workflow file that carries the correct set of amendments: per-stage automatic approval, the acceptance-trigger switch, and the build extension. That configuration is repeated manual work in every project, is easy to get wrong (a missed stage silently reintroduces a manual gate that stalls an unattended run), and drifts between projects as pipelines evolve.

Both gaps must be closed by one product: a run that completes on its own, achieved by installation rather than by authoring.

## Users

**Primary user — the task developer (pipeline runner).** Runs the `development` pipeline for a task in a goga-configured project. Wants the run to complete end-to-end — through acceptance and the build — without attending approval gates or launching the build separately. Today the run halts at each gate, waits for a manual acceptance trigger, and ends before the build.

**Secondary actor — the project setup maintainer.** Installs and configures goga tooling for a project (image, project configuration, tool declarations). Wants every project to obtain an autonomous development pipeline by installing the tool package, without authoring or maintaining workflow boilerplate per project. In small teams this is the same person as the runner.

**Removed actor — the human approver.** Today a person approves each stage gate and manually triggers acceptance. For the development pipeline these interaction points are intentionally removed. No dedicated product obligation replaces them: the standard run output is sufficient feedback (user decision).

**Audience.** Any goga project. The tool is a public, reusable package — `goga-tool-autonomous` — installable into a project's goga image; it is not private to one team's projects.

## Goals

1. **Autonomous end-to-end run.** A developer starts a `development`-pipeline run for a task and receives the completed, verified result — including the build — with every approval gate passed automatically and acceptance triggered as part of the run: no manual stage approvals, no manual acceptance trigger, no separately launched build.
2. **Autonomy by installation.** Any goga project adopts this behavior by installing the tool package into its goga image — with zero per-project workflow authoring or maintenance.
3. **Authored control preserved.** Autonomy only fills what a project left unset. An explicitly authored approval mode, acceptance trigger, or build extension is never overridden or duplicated.

Stage communication is retained by design: autonomy removes gates, the manual trigger, and the separate build — it does not suppress the interviews a stage may legitimately conduct.

## User Experience

**Entry points.**

- *Setup maintainer (one time per project):* install the tool package into the project's goga image as a goga tool. Nothing is authored in the project; no workflow file, no configuration change.
- *Task developer (per task):* run `goga pipeline development` exactly as before — standard command, no new flags or options.

**Primary flow.**

1. The maintainer installs the tool; nothing else in the project changes.
2. The developer starts a development-pipeline run for a task.
3. At composition time the tool's amendments commit: the gated stages compose with automatic approval, acceptance no longer waits for a manual trigger, and a build stage joins the pipeline after `commit-changes`.
4. The run proceeds through every gate without waiting for the user. Feedback is the standard run output: the amendment summary names the committed contributions, the pipeline card names the contributing tool, stages report progress, and the run reports completion with its exit code.
5. The build executes inside the run after `commit-changes`, allowed to run long.
6. Acceptance completes as part of the run; the run finishes and reports its outcome. The developer returns to a finished run and reads the results.

**Alternative flows.**

- *Authored workflow present:* authored values win per slot. The tool fills only what the author left unset; an authored build extension under the same name wins over the tool's. The observable behavior is the project's authored intent, nothing overridden, nothing duplicated.
- *Workflow layer disabled by the runner (`--no-workflow`):* no amendments deliver at all; the run composes raw. An explicit runner decision to disable the workflow layer is respected — autonomy is never forced through it.
- *Different explicit workflow (`-w <name>`):* the amendment layer stays active for the development pipeline; fields the workflow leaves unset still receive the autonomy defaults.
- *Any other pipeline (bugfix, patch, refinement, review, sync):* the tool is silent; composition and behavior are identical to a project without the tool.
- *The tool's own repository:* its hand-authored development workflow already sets everything the tool would contribute, so the contribution commits nothing — a natural no-op. The tool performs no self-detection or special-casing.

**Failure flows.**

- *Structurally invalid contribution:* the command stops before launch with a clean error naming the tool and the action; nothing partial applies; authored files remain untouched; a re-run after correction works.
- *Project has no build configuration:* the run still composes with the build stage; the build stage fails with a readable error naming the missing configuration. The project owns its configuration (user decision); the failure is visible immediately in the run and follows standard stage-failure semantics.
- *A stage or the build fails mid-run:* standard run behavior — the failing stage is reported, the run exits non-zero, and re-running the pipeline is the recovery path.

**States, consequences, recovery.** No new states: composing → running (unattended) → completed / failed. The tool never modifies authored files; amendments are per-run, in-memory, and deterministic — identical inputs always compose the identical run, so there is nothing to undo and any interruption follows standard run behavior.

## Requirements

**Targeting and boundaries**

1. The tool contributes its workflow amendment only when the composing pipeline is `development`; for every other pipeline it contributes nothing and changes no behavior.
2. All contributions are declarative run-time amendments. The tool must never create or modify any project file.

**Autonomy**

3. For the development pipeline, the gated stages — `architecture-review`, `apply-architecture`, `code-design`, `design-review`, `coding-plan`, `plan-review` — must compose with automatic approval whenever the author left the approval mode unset. (This enumerated set is the gated-stage set of the goga development pipeline as of the supported goga version line.)
4. The `accept-result` stage must compose as not manually triggered whenever the author left it unset, so acceptance runs as part of the unattended run.
5. Authored intent wins per slot: an explicitly authored approval mode, acceptance trigger, or same-named extension entry is never overridden, replaced, or duplicated.

**Build integration**

6. For the development pipeline, a build stage is contributed under a fresh extension name with the reference configuration: title `Build implementation`, placed after `commit-changes`, an 8-hour timeout, invoking the goga build entrypoint with the run's plan artifact, followed by cleanup of the build working directory. The reference workflow (`.goga/workflows/development.yml` in this repository) is the authoritative definition of these values.
7. The build extension is contributed unconditionally for the development pipeline, independent of whether build settings exist in the project configuration.
8. When the effective project configuration lacks build settings, the build stage must fail with a readable error naming the missing configuration; the failure follows standard stage-failure semantics (reported, non-zero, re-runnable) and affects nothing else in the run.
9. The tool must not prevent or conflict with build settings contributed by other tools — the composed run resolves configuration at execution time. A failure in a scenario where the build is configured by another tool is a defect of this tool.

**Adoption and feedback**

10. Adoption is installation of the package as a goga tool in the project's image; no project-file authoring is required for the autonomy effect on the development pipeline.
11. Feedback is limited to the standard run surfaces: the amendment summary naming committed contributions, the pipeline card provenance, and standard stage and completion output. The tool adds no dedicated reports, dashboards, or notifications.

**Failure and robustness**

12. A structurally invalid contribution stops the command before launch with a clean error naming the tool and the action; nothing partial applies; a re-run after correction works.
13. An explicit runner decision to disable the workflow layer (`--no-workflow`) results in no contribution at all.
14. The contribution is a fixed, deterministic document — independent of external state, time, or environment — so identical project state and flags always compose the identical run.
15. The contribution must compose cleanly when development stages are skipped — via an authored workflow `skip` or runner skip flags: the tool's entry for a skipped stage has no effect and never fails the composition.

## Constraints

- The tool operates exclusively through the published goga hooks mechanism: a `register_hooks` facade subscribing to the pipeline workflow-amendment action, contributing declarative workflow documents built from the authored workflow vocabulary (stages, extend). No goga code changes.
- The platform rule "authored intent wins per slot" is inviolable: stage fields fill only what the author left unset; extension entries add only under fresh names; an authored memory block is unbeatable. The tool cannot override authored values even where it might want to.
- The amendment action is hard: a failing hook stops the command with a clean error naming the tool and the action, and the whole contribution is discarded. The package facade must stay import-clean — an import failure stops every goga command naming the package.
- The pipeline card form and the run form compose identically through the same amendment layer: the same flags must produce the same composition and the same provenance in both forms.
- The merged workflow passes the same compilation validation as an authored one — a contribution naming an unknown stage surfaces as a structural composition error.
- The tool must not subscribe to the configuration-amendment action; the project configuration answers for itself (user decision).
- The repository's reference workflow `.goga/workflows/development.yml` remains as-is: it is a reference, not an artifact to regenerate, and the tool performs no self-application special-casing.
- The contribution carries autonomy mechanics only — no `reflect`, `prompt`, or `memory` content; those remain project-authored (user decision).
- Pipeline-shape coupling: the enumerated stage set is tied to the development-pipeline shape of the supported goga version line (2.0.x). If a future goga release adds or renames gated development stages, the tool must be updated to cover them — otherwise runs stall at the uncovered gate.
- Stage communication is retained: autonomy means the removal of approval gates and the manual acceptance trigger plus the integrated build, not the suppression of stage interviews.
- The tool depends on the goga 2.0.x hooks API surface and must remain a pure subscriber of it.
- The package is public and reusable, installable into any goga project's image, and supports Python 3.10 and above.

## Scope

### In Scope

- The `goga-tool-autonomous` package as an installable goga tool: hooks registration and the declarative workflow amendment for the `development` pipeline.
- The autonomy contribution itself: automatic approval on the six gated stages, non-manual acceptance, and the build extension after `commit-changes` with the reference configuration.
- Boundary behavior: silence on all other pipelines, no configuration amendments, no project-file modification, authored-wins semantics, deterministic contribution, clean composition under skipped stages.
- Failure behavior: clean pre-launch failure on an invalid contribution; readable build failure when build settings are missing; non-interference with build settings contributed by other tools.
- The install-only adoption experience.

### Out of Scope

- Amendments to any pipeline other than `development` (bugfix, patch, refinement, review, sync).
- Any configuration-domain contribution (`amend_config` is not subscribed).
- `reflect`, `prompt`, or `memory` content in the contribution — project-authored material stays project-authored.
- Modifying, regenerating, or removing this repository's reference `.goga/workflows/development.yml`.
- Transparency or reporting features beyond the standard run output.
- Configurability of the tool itself (opt-in/opt-out switches, per-project settings) — an authored workflow is the override mechanism.
- Changes to the goga platform.
- Distribution infrastructure beyond the package itself being installable.

## Success Criteria

1. In a project with the tool installed and no authored development workflow, the composed `development` run contains no stage that waits for a human approval: the six gated stages compose with automatic approval, `accept-result` composes as non-manual, and the build stage is present after `commit-changes`. Verifiable on the pipeline card, with the tool named in provenance.
2. In a project with build configuration, a `development` run completes from start to finish — including execution of the build stage — without human interaction at any gate, and reports its exit code.
3. Adopting the behavior in a fresh goga project requires only installing the package as a goga tool: no workflow file authored, no configuration change — the first composed run after installation is already autonomous.
4. Authored project files are byte-identical before and after runs with the tool installed.
5. In a project with an authored development workflow that explicitly sets an approval mode (for example `approve: dialog`) or a same-named build extension, the composed run reflects the authored values exactly — nothing overridden, no duplicate extension added.
6. With `--no-workflow`, the composed development run contains none of the tool's amendments.
7. Composing any non-development pipeline in a project with the tool installed yields exactly the same composition as without the tool, with the tool absent from provenance.
8. When the project configuration lacks build settings, the development run composes with the build stage, the build stage fails with a readable error naming the missing configuration, and nothing else in the run is affected by the tool.
9. Composing the same project with the same flags twice yields identical compositions — same stages, same provenance.
10. A development composition with a gated stage skipped (for example `-s plan-review`) composes cleanly with the tool installed — no structural error, and the tool's entry for the skipped stage has no effect.
