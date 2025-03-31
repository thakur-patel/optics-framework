import pytest
from optics_framework.api.app_management import AppManagement  # Example import


def test_launch_app():
    app_management = AppManagement("appium_helper")
    app_management.launch_app("launch")
    assert True

