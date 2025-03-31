import pytest
from optics_framework.common.driver_interface import DriverInterface


class TestDriver(DriverInterface):
    def launch_app(self, event_name):
        if not event_name:
            raise ValueError("Event name cannot be empty.")
        return f"App launched with event: {event_name}"


def test_launch_app():
    driver = TestDriver()
    assert driver.launch_app(
        "test_event") == "App launched with event: test_event"


def test_invalid_event():
    driver = TestDriver()
    with pytest.raises(ValueError, match="Event name cannot be empty."):
        driver.launch_app("")
