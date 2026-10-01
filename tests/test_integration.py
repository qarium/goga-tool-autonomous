"""Integration tests: the contribution against the real platform merge and compiler."""

import yaml
from goga.hooks.tools.registration import HookRegistrar
from goga.pipeline.compiler import compile_flow
from goga.pipeline.hooks import PipelineHooks, PipelineIdentity, WorkflowDecision, WorkIdentity
from goga.pipeline.hooks.overlay import ToolContribution, merge_workflow_overlay
from goga_tool_autonomous import autonomy, build_development_contribution, development_recipe, register_hooks


class TestPlatformIntegration:
    """End-to-end scenarios driving the delivery through the installed goga platform."""

    def test_integration_contribution_only_compiles_unattended(self, development_pipeline_path, tmp_path):
        """The contribution alone survives merge and compile into the unattended composition."""
        document = build_development_contribution(recipe=development_recipe(), workflow=None)

        overlay = merge_workflow_overlay(None, [ToolContribution(tool="autonomous", document=document)])

        compile_flow(development_pipeline_path, tmp_path / "flow.yml", workflow=overlay.workflow)

        flow = yaml.safe_load((tmp_path / "flow.yml").read_text())
        names = [stage["name"] for stage in flow["stages"]]

        assert names[-3:] == ["Commit changes", "Build implementation", "Contracts & coverage audit"]

        build = flow["stages"][-2]
        expected_script = 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"'

        assert build["script"] == expected_script
        assert build["script_after"] == "rm -rf .ralphex"
        assert build["script_timeout"] == "8h"
        assert build["depends_on"] == ["commit-changes"]

        gated = flow["stages"][1:7]

        assert all("interactive" not in stage for stage in gated)
        assert "auto_run" not in flow["stages"][-1]
        assert overlay.provenance == ["autonomous"]

    def test_integration_authored_reference_wins_byte_identical(
        self, reference_workflow, development_pipeline_path, tmp_path
    ):
        """The authored reference workflow compiles byte-identically with and without the contribution."""
        document = build_development_contribution(recipe=development_recipe(), workflow=reference_workflow)

        overlay = merge_workflow_overlay(reference_workflow, [ToolContribution(tool="autonomous", document=document)])

        compile_flow(development_pipeline_path, tmp_path / "authored.yml", workflow=reference_workflow)
        compile_flow(development_pipeline_path, tmp_path / "merged.yml", workflow=overlay.workflow)

        assert (tmp_path / "authored.yml").read_text() == (tmp_path / "merged.yml").read_text()
        assert overlay.provenance == ["autonomous"]

    def test_integration_registration_accepted_by_real_registrar(self):
        """register_hooks registers exactly one valid subscription on the real platform registrar."""
        registrar = HookRegistrar(tool="autonomous")

        register_hooks(registrar)

        assert len(registrar.subscriptions) == 1

        subscription = registrar.subscriptions[0]

        assert (subscription.domain, subscription.action, subscription.name) == (
            "pipeline",
            "amend_workflow",
            "autonomy",
        )
        assert subscription.hook is autonomy
        assert registrar.rejections == []

    def test_integration_amendment_delivery_contributes_for_development(self):
        """The real amendment delivery commits the autonomy contribution for a development composition."""
        hooks = PipelineHooks()

        overlay = hooks.amend_workflow(
            pipeline=PipelineIdentity(
                name="development",
                display_name="Development",
                description="The development pipeline",
                source="project",
            ),
            decision=WorkflowDecision(kind="disabled", workflow_name=None),
            workflow=None,
            work=WorkIdentity(branch="the-first-version"),
        )

        assert overlay.provenance == ["autonomous"]

        gated = [name for name in overlay.workflow.stages if name != "accept-result"]

        assert all(overlay.workflow.stages[name].approve == "auto" for name in gated)
        assert overlay.workflow.stages["accept-result"].manual is False
        assert overlay.workflow.extend.keys() == {"build"}

    def test_integration_amendment_delivery_silent_for_other_pipeline(self):
        """The real amendment delivery stays neutral for a non-development composition."""
        hooks = PipelineHooks()

        overlay = hooks.amend_workflow(
            pipeline=PipelineIdentity(name="review", display_name="", description="", source="project"),
            decision=WorkflowDecision(kind="disabled", workflow_name=None),
            workflow=None,
            work=WorkIdentity(branch="the-first-version"),
        )

        assert overlay.provenance == []
        assert overlay.workflow is None
