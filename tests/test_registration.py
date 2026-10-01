"""Contract and logic tests for the register_hooks and autonomy routines of the package facade."""

import inspect
from types import SimpleNamespace

import goga_tool_autonomous as root_facade
from goga_tool_autonomous import autonomy, register_hooks


class TestRegistrationContract:
    """Facade accessibility and public API shape of the package facade routines."""

    def test_facade_all_exports_routines_and_embedded_names(self):
        """The root facade lists both routines and the three embedded recipe-zone names."""
        assert set(root_facade.__all__) == {
            "AutonomyRecipe",
            "autonomy",
            "build_development_contribution",
            "development_recipe",
            "register_hooks",
        }

    def test_register_hooks_signature_is_single_hooks_parameter(self):
        """register_hooks offers exactly one positional-or-keyword parameter named hooks."""
        signature = inspect.signature(register_hooks)

        assert list(signature.parameters) == ["hooks"]
        assert signature.parameters["hooks"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD

    def test_autonomy_signature_is_single_context_parameter(self):
        """autonomy offers exactly one positional-or-keyword parameter named context."""
        signature = inspect.signature(autonomy)

        assert list(signature.parameters) == ["context"]
        assert signature.parameters["context"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


class _Hooks:
    """Recording stub of the platform registrar capturing subscribe calls."""

    def __init__(self):
        self.calls = []

    def subscribe(self, domain, action, name, hook):
        self.calls.append((domain, action, name, hook))


class _Context:
    """Fake amendment view exposing the pipeline identity, the workflow, and a contribute recorder."""

    def __init__(self, name, workflow=None, display_name=""):
        self.pipeline = SimpleNamespace(name=name, display_name=display_name)
        self.workflow = workflow
        self.contributed = None

    def contribute(self, document):
        self.contributed = document


class TestRegistrationBehavior:
    """Behavioral requirements of the registration and the amendment hook."""

    def test_register_hooks_subscribes_single_amendment_hook(self):
        """Registration performs exactly one subscribe with the designed address, name, and hook."""
        hooks = _Hooks()

        register_hooks(hooks)

        assert len(hooks.calls) == 1
        assert hooks.calls[0][:3] == ("pipeline", "amend_workflow", "autonomy")
        assert hooks.calls[0][3] is autonomy

    def test_autonomy_contributes_for_development_pipeline(self):
        """A development-pipeline view receives the full never-empty contribution document."""
        context = _Context(name="development", workflow=None)

        autonomy(context=context)

        assert context.contributed is not None
        assert context.contributed.stages.keys() == {
            "architecture-review",
            "apply-architecture",
            "code-design",
            "design-review",
            "coding-plan",
            "plan-review",
            "accept-result",
        }
        assert context.contributed.extend.keys() == {"build"}

    def test_autonomy_silent_for_unknown_pipeline(self):
        """An existing non-development pipeline name contributes nothing."""
        context = _Context(name="review", workflow=None)

        autonomy(context=context)

        assert context.contributed is None

    def test_autonomy_ignores_display_name(self):
        """A pipeline whose display name is Development but whose stem differs stays silent."""
        context = _Context(name="development-weekly", workflow=None, display_name="Development")

        autonomy(context=context)

        assert context.contributed is None

    def test_register_hooks_never_reads_files_or_config(self, tmp_path, monkeypatch):
        """Registration succeeds in a bare directory and records exactly one subscription."""
        monkeypatch.chdir(tmp_path)
        hooks = _Hooks()

        register_hooks(hooks)

        assert len(hooks.calls) == 1
        assert hooks.calls[0][:3] == ("pipeline", "amend_workflow", "autonomy")

    def test_register_hooks_idempotent_across_calls(self):
        """Repeated registration on fresh registrars neither duplicates nor loses the subscription."""
        first = _Hooks()
        second = _Hooks()

        register_hooks(first)
        register_hooks(second)

        assert len(first.calls) == 1
        assert len(second.calls) == 1
        assert first.calls == second.calls == [("pipeline", "amend_workflow", "autonomy", autonomy)]
