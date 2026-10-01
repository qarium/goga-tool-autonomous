"""Contract tests for the recipe zone facade re-exporting the zone's embedded names."""

import goga_tool_autonomous.recipe as zone_facade
import goga_tool_autonomous.recipe.development as development_facade
import goga_tool_autonomous.recipe.model as model_facade


class TestRecipeZoneFacadeContract:
    """Facade accessibility of the recipe zone's embedded re-exports."""

    def test_zone_facade_all_lists_exactly_the_embedded_names(self):
        """The zone facade __all__ is exactly the three embedded recipe-zone names."""
        assert set(zone_facade.__all__) == {
            "AutonomyRecipe",
            "build_development_contribution",
            "development_recipe",
        }

    def test_zone_facade_reexports_the_owning_sub_cell_objects(self):
        """Each embedded name is the identical object re-exported from its owning sub-cell."""
        assert zone_facade.AutonomyRecipe is model_facade.AutonomyRecipe

        assert zone_facade.development_recipe is development_facade.development_recipe
        assert zone_facade.build_development_contribution is development_facade.build_development_contribution
