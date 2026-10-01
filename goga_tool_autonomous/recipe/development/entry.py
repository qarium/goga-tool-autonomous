"""The development zone entry building the development pipeline's autonomy recipe."""

from ..model import AutonomyRecipe


def development_recipe() -> AutonomyRecipe:
    """Build the development pipeline's autonomy recipe from mirrored reference constants.

    The values mirror the reference workflow ``.goga/workflows/development.yml`` verbatim.
    The reference is authoritative documentation, never read at runtime — every value is a
    compile-time constant of the zone, so nothing touches the disk. Pure and deterministic:
    every call returns an equal entry built from fresh mutable containers, so no caller can
    mutate shared autonomy knowledge.

    Returns:
        A recipe targeting the exact pipeline name "development": the six gated review
        stages carrying ``approve: auto`` in the reference (in file order), the acceptance
        stage carrying ``manual: false``, and the build extension entry in the
        extend-entry vocabulary (title, after, timeout, script, after_script).
    """
    return AutonomyRecipe(
        pipeline="development",
        gated_stages=[
            "architecture-review",
            "apply-architecture",
            "code-design",
            "design-review",
            "coding-plan",
            "plan-review",
        ],
        accept_stage="accept-result",
        build_extend={
            "title": "Build implementation",
            "after": ["commit-changes"],
            "timeout": "8h",
            "script": 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"',
            "after_script": "rm -rf .ralphex",
        },
    )
