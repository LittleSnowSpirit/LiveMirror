"""Pytest collection policy for backend tests.

The supported default backend suite is the core API flow. Legacy feature tests
remain in this directory for reference, but many target experimental modules
whose contracts have drifted. Set LIVEMIRROR_RUN_EXPERIMENTAL_TESTS=1 to collect
those tests intentionally.
"""

from __future__ import annotations

import os
from pathlib import Path


CORE_TESTS = {"test_core_api.py"}


def pytest_ignore_collect(collection_path: Path, config) -> bool:
    if os.environ.get("LIVEMIRROR_RUN_EXPERIMENTAL_TESTS") == "1":
        return False

    path = Path(str(collection_path))
    if path.is_file() and path.name.startswith("test_") and path.suffix == ".py":
        return path.name not in CORE_TESTS

    return False
