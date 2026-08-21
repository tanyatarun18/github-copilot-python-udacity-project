"""
Pytest configuration and fixtures for the Sudoku Flask app.
"""
import pytest
import sys
import os

# Add the starter directory to the path so we can import app and sudoku_logic
sys.path.insert(0, os.path.dirname(__file__))

import app as app_module


@pytest.fixture
def app():
    """Create and configure a test app."""
    test_app = app_module.app
    test_app.config['TESTING'] = True
    # Attach CURRENT to app so tests can access it
    test_app.CURRENT = app_module.CURRENT
    return test_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for CLI commands."""
    return app.test_cli_runner()
