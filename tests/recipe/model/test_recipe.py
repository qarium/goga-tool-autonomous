"""Contract and logic tests for the AutonomyRecipe entity of the recipe model cell."""

import inspect
from dataclasses import FrozenInstanceError

import goga_tool_autonomous.recipe.model as model_facade
import pytest
from goga_tool_autonomous.recipe.model import AutonomyRecipe


class TestAutonomyRecipeContract:
    """Facade accessibility and public API shape of the recipe entity."""

    def test_facade_all_exports_recipe_entity(self):
        """The cell facade lists AutonomyRecipe in __all__."""
        assert "AutonomyRecipe" in model_facade.__all__

    def test_constructor_signature_is_four_keyword_only_fields(self):
        """The constructor takes exactly four keyword-only fields without defaults."""
        parameters = inspect.signature(AutonomyRecipe).parameters

        assert list(parameters) == ["pipeline", "gated_stages", "accept_stage", "build_extend"]

        for parameter in parameters.values():
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
            assert parameter.default is inspect.Parameter.empty

        assert parameters["pipeline"].annotation is str
        assert parameters["gated_stages"].annotation == list[str]
        assert parameters["accept_stage"].annotation is str
        assert parameters["build_extend"].annotation == dict[str, str | list[str]]

    def test_instance_surface_is_the_four_fields_only(self):
        """A constructed instance exposes the four fields and no public methods."""
        recipe = AutonomyRecipe(pipeline="p", gated_stages=["s"], accept_stage="a", build_extend={"title": "T"})
        public = {name for name in dir(recipe) if not name.startswith("_")}

        assert public == {"pipeline", "gated_stages", "accept_stage", "build_extend"}

    def test_properties_readable_on_constructed_instance(self):
        """Each property is readable on a constructed instance, verbatim."""
        recipe = AutonomyRecipe(
            pipeline="my-pipeline",
            gated_stages=["first-review"],
            accept_stage="accept-result",
            build_extend={"title": "T", "after": ["commit-changes"]},
        )

        assert recipe.pipeline == "my-pipeline"
        assert recipe.gated_stages == ["first-review"]
        assert recipe.accept_stage == "accept-result"
        assert recipe.build_extend == {"title": "T", "after": ["commit-changes"]}


class TestAutonomyRecipeBehavior:
    """Behavioral requirements of the recipe data carrier."""

    def test_recipe_construction_captures_all_fields(self):
        """Construction with four values exposes each captured value verbatim."""
        recipe = AutonomyRecipe(
            pipeline="my-pipeline",
            gated_stages=["first-review"],
            accept_stage="accept-result",
            build_extend={
                "title": "T",
                "after": ["commit-changes"],
                "timeout": "1h",
                "script": "make",
                "after_script": "rm -rf tmp",
            },
        )

        assert recipe.pipeline == "my-pipeline"
        assert recipe.gated_stages == ["first-review"]
        assert recipe.accept_stage == "accept-result"

        assert recipe.build_extend["title"] == "T"
        assert recipe.build_extend["after"] == ["commit-changes"]

    def test_recipe_fields_are_read_only(self):
        """Field assignment on a frozen instance raises FrozenInstanceError."""
        recipe = AutonomyRecipe(pipeline="p", gated_stages=[], accept_stage="a", build_extend={})

        with pytest.raises(FrozenInstanceError):
            recipe.pipeline = "other"

    def test_recipe_empty_collections(self):
        """Construction with empty list and dict captures them verbatim without defaults."""
        recipe = AutonomyRecipe(pipeline="p", gated_stages=[], accept_stage="a", build_extend={})

        assert recipe.gated_stages == []
        assert recipe.build_extend == {}
        assert recipe.accept_stage == "a"
