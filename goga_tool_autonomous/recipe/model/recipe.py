"""The immutable AutonomyRecipe shape carrying one pipeline's autonomy knowledge."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class AutonomyRecipe:
    """Immutable data recipe for one pipeline's autonomy contribution.

    The single source of every entry the delivery path contributes for that pipeline. Recipe
    knowledge is plain data by the cell-wide sanctioned deviation from ``conventions``: the
    package keeps its runtime dependencies empty, so no pydantic — a frozen data carrier with
    no methods, no computed state, and no I/O.

    Args:
        pipeline: Exact target pipeline name; compared verbatim against the composing
            pipeline's name — source and display name never participate.
        gated_stages: Stages receiving the approve instruction auto when their authored entry
            carries no approve instruction.
        accept_stage: The acceptance stage receiving the unconditional non-manual instruction.
        build_extend: The build extension entry as plain data in the extend-entry vocabulary
            of ``workflow_document`` (title, after, timeout, script, after_script).
    """

    pipeline: str
    gated_stages: list[str]
    accept_stage: str
    build_extend: dict[str, str | list[str]]
