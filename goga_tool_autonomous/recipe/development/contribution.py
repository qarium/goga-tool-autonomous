"""The development zone delivery building the never-empty declarative contribution."""

from goga.pipeline.workflow import WorkflowDocument, WorkflowExtendStage, WorkflowStage

from ..model import AutonomyRecipe


def build_development_contribution(recipe: AutonomyRecipe, workflow: WorkflowDocument | None) -> WorkflowDocument:
    """Build the development pipeline's declarative contribution from the recipe and the authored workflow.

    The recipe is the single source of every contributed entry; the authored workflow is read
    (never mutated) only to detect gated stages whose approval instruction the author already
    set — those slots are left to the platform's authored-wins merge, so the document names
    only the slots it actually fills. The result is never empty: the acceptance instruction
    and the build extension are contributed unconditionally. Deterministic — the same recipe
    and workflow always produce the identical document.

    Args:
        recipe: The development pipeline's autonomy recipe carrying the gated stages, the
            acceptance stage, and the build extension entry.
        workflow: The authored workflow document, or None when nothing was resolved.

    Returns:
        The declarative contribution: the build extension under the fresh name "build", the
        approve instruction "auto" for each gated stage lacking an authored approval, and the
        non-manual instruction for the acceptance stage.
    """
    build_extend = recipe.build_extend
    body = {key: value for key, value in build_extend.items() if key != "after"}
    extension = WorkflowExtendStage(after=list(build_extend["after"]), body=body)

    stages: dict[str, WorkflowStage] = {}

    for stage_name in recipe.gated_stages:
        authored = None if workflow is None else workflow.stages.get(stage_name)

        if authored is None or authored.approve is None:
            stages[stage_name] = WorkflowStage(approve="auto")

    stages[recipe.accept_stage] = WorkflowStage(manual=False)

    return WorkflowDocument(stages=stages, extend={"build": extension})
