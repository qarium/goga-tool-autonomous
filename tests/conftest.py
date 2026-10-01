"""Shared fixtures for the goga-tool-autonomous test suite."""

import importlib.resources
from pathlib import Path

import pytest
from goga.pipeline.workflow import WorkflowDocument, parse_workflow


@pytest.fixture
def development_pipeline_path() -> Path:
    """Deliver the development pipeline file of the installed goga platform."""
    return Path(importlib.resources.files("goga") / "assets" / "pipelines" / "development.yml")


@pytest.fixture(scope="session")
def reference_workflow() -> WorkflowDocument:
    """Deliver the parsed reference workflow of this project (read-only)."""
    return parse_workflow(Path(__file__).resolve().parents[1] / ".goga" / "workflows" / "development.yml")
