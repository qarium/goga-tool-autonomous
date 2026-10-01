"""The package facade's registration wiring the autonomy hook into the pipeline amendment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .recipe import build_development_contribution, development_recipe

if TYPE_CHECKING:
    from goga.hooks.tools.registration import HookRegistrar as Hooks
    from goga.pipeline.hooks.amendments import WorkflowAmendment

_PIPELINE_DOMAINS = {
    "development": (development_recipe, build_development_contribution),
}


def register_hooks(hooks: Hooks) -> None:
    """Subscribe the single autonomy hook to the pipeline amend_workflow action.

    Exactly one subscription, unconditional: the hook routine ``autonomy`` under domain
    ``pipeline``, action ``amend_workflow``, hook name ``autonomy``. The tool identity is
    assigned by the platform from the package name — a package never names itself. No
    configuration or file is read during registration; the facade imports cleanly at all
    times (a broken import is fatal to every goga command).

    Args:
        hooks: The platform registrar scoped to this tool, exposing
            ``subscribe(domain, action, name, hook)``.
    """
    hooks.subscribe("pipeline", "amend_workflow", "autonomy", autonomy)


def autonomy(context: WorkflowAmendment) -> None:
    """Contribute the resolved pipeline domain's autonomy document through the amendment view.

    The composing pipeline's exact name (the discovered stem — display name and source never
    participate) is looked up in the registry of pipeline domains; a miss returns silently, so
    composition is identical to a project without the tool. A hit builds the contribution from
    the domain's entry and the authored workflow of the view, then contributes it through the
    view's single write channel. Only the pipeline identity and the authored workflow are
    read; no state, no cache, no internal exception handling — a failure propagates to the
    platform's hard action as a clean command error.

    Args:
        context: The read-and-contribute view of this tool at the amendment checkpoint.
    """
    domain = _PIPELINE_DOMAINS.get(context.pipeline.name)

    if domain is None:
        return

    entry_factory, delivery = domain

    context.contribute(delivery(entry_factory(), context.workflow))
