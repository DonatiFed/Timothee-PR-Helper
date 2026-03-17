"""Shared pytest fixtures and configuration."""

import os
import pytest


def pytest_collection_modifyitems(config, items):
    """Auto-skip integration & API-dependent tests when no API key is set."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return
    skip_api = pytest.mark.skip(reason="ANTHROPIC_API_KEY not set")
    for item in items:
        if "test_integration" in str(item.fspath):
            item.add_marker(skip_api)
        elif "test_scenarios" in str(item.fspath) and "SyntheticParserOnly" not in item.nodeid:
            item.add_marker(skip_api)
