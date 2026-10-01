"""Contract and logic tests for the build_development_contribution delivery of the development zone cell."""

import copy
import inspect

import goga_tool_autonomous.recipe.development as development_facade
import pytest
from goga.pipeline.workflow import WorkflowDocument, WorkflowStage
from goga_tool_autonomous.recipe.development import build_development_contribution, development_recipe
from goga_tool_autonomous.recipe.model import AutonomyRecipe


class TestBuildDevelopmentContributionContract:
    """Facade accessibility and public API shape of the development zone delivery."""

    def test_facade_all_exports_contribution_entity(self):
        """The cell facade lists build_development_contribution in __all__."""
        assert "build_development_contribution" in development_facade.__all__

    def test_signature_is_recipe_and_workflow_returning_document(self):
        """The delivery takes recipe and workflow and is annotated to return a WorkflowDocument."""
        signature = inspect.signature(build_development_contribution)

        assert list(signature.parameters) == ["recipe", "workflow"]
        assert signature.parameters["recipe"].annotation is AutonomyRecipe
        assert signature.parameters["workflow"].annotation == WorkflowDocument | None
        assert signature.return_annotation is WorkflowDocument


class TestBuildDevelopmentContributionBehavior:
    """Behavioral requirements of the development zone delivery."""

    def test_contribution_without_workflow_contributes_everything(self):
        """An unattended run with no authored workflow receives every instruction."""
        gated = [
            "architecture-review",
            "apply-architecture",
            "code-design",
            "design-review",
            "coding-plan",
            "plan-review",
        ]

        document = build_development_contribution(recipe=development_recipe(), workflow=None)

        assert sorted(document.stages) == sorted([*gated, "accept-result"])
        assert all(document.stages[stage].approve == "auto" for stage in gated)

        assert document.stages["accept-result"].manual is False
        assert document.extend["build"].after == ["commit-changes"]

        assert document.extend["build"].body == {
            "title": "Build implementation",
            "timeout": "8h",
            "script": 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"',
            "after_script": "rm -rf .ralphex",
        }

        assert document.prompt is None
        assert document.memory is None

    def test_contribution_with_authored_workflow_never_empty(self, reference_workflow):
        """A fully authored workflow still yields the acceptance instruction and the build extension."""
        document = build_development_contribution(recipe=development_recipe(), workflow=reference_workflow)

        assert document.stages.keys() == {"accept-result"}
        assert document.extend.keys() == {"build"}

    def test_contribution_skips_stages_with_authored_approve(self):
        """Any authored approval instruction removes the slot from the document."""
        authored = WorkflowDocument(
            stages={"plan-review": WorkflowStage(approve="dialog"), "coding-plan": WorkflowStage(approve="auto")},
        )

        document = build_development_contribution(recipe=development_recipe(), workflow=authored)

        assert "plan-review" not in document.stages
        assert "coding-plan" not in document.stages
        assert set(document.stages) == {
            "architecture-review",
            "apply-architecture",
            "code-design",
            "design-review",
            "accept-result",
        }

    def test_contribution_authored_stage_without_approve_still_filled(self):
        """A stage authored with another field but approval unset still receives approve auto."""
        authored = WorkflowDocument(stages={"code-design": WorkflowStage(prompt="x")})

        document = build_development_contribution(recipe=development_recipe(), workflow=authored)

        assert document.stages["code-design"].approve == "auto"
        assert document.stages["code-design"].prompt is None
        assert all(document.stages[stage].approve == "auto" for stage in development_recipe().gated_stages)

    def test_contribution_deterministic_and_pure(self, reference_workflow):
        """Equal inputs build equal documents and the authored workflow is never mutated."""
        authored = reference_workflow
        snapshot = copy.deepcopy(authored)

        first = build_development_contribution(recipe=development_recipe(), workflow=authored)
        second = build_development_contribution(recipe=development_recipe(), workflow=authored)

        assert first == second
        assert authored == snapshot
        assert first.stages is not authored.stages
        assert first.extend["build"].body is not second.extend["build"].body

    def test_contribution_with_empty_gated_recipe_contributes_minimum(self):
        """A hand-built entry with no gated stages contributes acceptance plus build only."""
        recipe = AutonomyRecipe(
            pipeline="development",
            gated_stages=[],
            accept_stage="accept-result",
            build_extend={
                "title": "Build implementation",
                "after": ["commit-changes"],
                "timeout": "8h",
                "script": 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"',
                "after_script": "rm -rf .ralphex",
            },
        )

        document = build_development_contribution(recipe=recipe, workflow=None)

        assert document.stages.keys() == {"accept-result"}
        assert document.extend.keys() == {"build"}
        assert document.stages["accept-result"].manual is False

    def test_contribution_duplicate_and_overlapping_gated_names(self):
        """Duplicate gated names collapse and the acceptance step wins the shared name."""
        recipe = AutonomyRecipe(
            pipeline="p",
            gated_stages=["code-design", "code-design", "accept-result"],
            accept_stage="accept-result",
            build_extend={
                "title": "Build implementation",
                "after": ["commit-changes"],
                "timeout": "8h",
                "script": 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"',
                "after_script": "rm -rf .ralphex",
            },
        )

        document = build_development_contribution(recipe=recipe, workflow=None)

        assert document.stages.keys() == {"code-design", "accept-result"}
        assert document.stages["code-design"].approve == "auto"
        assert document.stages["accept-result"].manual is False
        assert document.stages["accept-result"].approve is None

    def test_contribution_recipe_without_after_key_raises_key_error(self):
        """A hand-built recipe lacking the after positioning key fails with a propagated KeyError."""
        recipe = AutonomyRecipe(pipeline="p", gated_stages=[], accept_stage="a", build_extend={"title": "T"})

        with pytest.raises(KeyError):
            build_development_contribution(recipe=recipe, workflow=None)
