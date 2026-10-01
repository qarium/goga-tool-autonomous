"""Integration tests: the contribution against the real platform merge and compiler."""

import yaml
from goga.pipeline.compiler import compile_flow
from goga.pipeline.hooks.overlay import ToolContribution, merge_workflow_overlay
from goga_tool_autonomous import build_development_contribution, development_recipe


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
