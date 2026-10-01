"""Contract and logic tests for the development_recipe entry of the development zone cell."""

import inspect

import goga_tool_autonomous.recipe.development as development_facade
from goga_tool_autonomous.recipe.development import development_recipe
from goga_tool_autonomous.recipe.model import AutonomyRecipe


class TestDevelopmentRecipeContract:
    """Facade accessibility and public API shape of the development zone entry."""

    def test_facade_all_exports_entry_entity(self):
        """The cell facade lists development_recipe in __all__."""
        assert "development_recipe" in development_facade.__all__

    def test_signature_is_zero_parameters_returning_recipe(self):
        """The factory takes no parameters and is annotated to return an AutonomyRecipe."""
        signature = inspect.signature(development_recipe)

        assert signature.parameters == {}
        assert signature.return_annotation is AutonomyRecipe


class TestDevelopmentRecipeBehavior:
    """Behavioral requirements of the development zone entry factory."""

    def test_entry_mirrors_reference_workflow(self, reference_workflow):
        """The entry values mirror the reference workflow verbatim, in file order."""
        entry = development_recipe()

        assert entry.pipeline == "development"

        authored_auto = [s for s in reference_workflow.stages if reference_workflow.stages[s].approve == "auto"]

        assert entry.gated_stages == authored_auto
        assert entry.gated_stages == [
            "architecture-review",
            "apply-architecture",
            "code-design",
            "design-review",
            "coding-plan",
            "plan-review",
        ]

        assert entry.accept_stage == "accept-result"
        assert entry.build_extend == {
            "title": "Build implementation",
            "after": ["commit-changes"],
            "timeout": "8h",
            "script": 'python3 -P -m goga.build "$(python3 -m goga history path -f plan.md)"',
            "after_script": "rm -rf .ralphex",
        }

        reference_build = reference_workflow.extend["build"]

        assert entry.build_extend == {"after": reference_build.after, **reference_build.body}

        authored_manual = [s for s in reference_workflow.stages if reference_workflow.stages[s].manual is False]

        assert authored_manual == [entry.accept_stage]

    def test_entry_deterministic(self):
        """Every call returns an equal entry built from fresh mutable containers."""
        first = development_recipe()
        second = development_recipe()

        assert first == second
        assert first is not second
        assert first.gated_stages is not second.gated_stages
        assert first.build_extend is not second.build_extend
