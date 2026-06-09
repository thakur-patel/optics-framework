"""Unit tests for scaling interactive-element bounds into screenshot pixel space.

Ensures get_interactive_elements / get_screen_elements / workspace consumers
receive bounds already aligned to the returned screenshot, so no client-side
scaling is needed. Gated to Appium sources; other platforms unchanged.
"""
import numpy as np

from optics_framework.common import utils


class _FakeWebDriver:
    def __init__(self, width, height):
        self._size = {"width": width, "height": height}

    def get_window_size(self):
        return self._size


class _AppiumSource:
    REQUIRED_DRIVER_TYPE = "appium"

    def __init__(self, wd):
        self.driver = wd


class _SeleniumSource:
    REQUIRED_DRIVER_TYPE = "selenium"

    def __init__(self, wd):
        self.driver = wd


class _InstanceFallback:
    """Mimics base_factory.InstanceFallback: holds .instances and .current_instance."""

    def __init__(self, instances):
        self.instances = list(instances)
        self.current_instance = instances[0] if instances else None


def _elements():
    return [
        {"text": "A", "bounds": {"x1": 20, "y1": 96, "x2": 355, "y2": 140}, "xpath": "//a"},
        {"text": "B", "bounds": {"x1": 0, "y1": 0, "x2": 100, "y2": 50}, "xpath": "//b"},
    ]


def _screenshot(width=1080, height=2340):
    return np.zeros((height, width, 3), dtype=np.uint8)


class TestScaleInteractiveElementBounds:
    def test_appium_window_smaller_than_screenshot_scales(self):
        src = _AppiumSource(_FakeWebDriver(375, 812))
        out = utils.scale_interactive_element_bounds(_elements(), src, _screenshot())
        # ~2.88x / ~2.881x
        assert out[0]["bounds"] == {"x1": 57, "y1": 276, "x2": 1022, "y2": 403}
        assert out[1]["bounds"] == {"x1": 0, "y1": 0, "x2": 288, "y2": 144}

    def test_resolves_instance_fallback(self):
        src = _InstanceFallback([_AppiumSource(_FakeWebDriver(375, 812))])
        out = utils.scale_interactive_element_bounds(_elements(), src, _screenshot())
        assert out[0]["bounds"] == {"x1": 57, "y1": 276, "x2": 1022, "y2": 403}

    def test_android_window_equals_screenshot_is_noop(self):
        src = _AppiumSource(_FakeWebDriver(1080, 2340))
        original = _elements()
        out = utils.scale_interactive_element_bounds(_elements(), src, _screenshot())
        assert out[0]["bounds"] == original[0]["bounds"]
        assert out[1]["bounds"] == original[1]["bounds"]

    def test_non_appium_source_is_left_unchanged(self):
        # Selenium driver exposes get_window_size, but its space is unrelated to the
        # screenshot's; scaling must NOT touch it.
        src = _SeleniumSource(_FakeWebDriver(375, 812))
        original = _elements()
        out = utils.scale_interactive_element_bounds(_elements(), src, _screenshot())
        assert out[0]["bounds"] == original[0]["bounds"]

    def test_no_screenshot_is_noop(self):
        src = _AppiumSource(_FakeWebDriver(375, 812))
        original = _elements()
        out = utils.scale_interactive_element_bounds(_elements(), src, None)
        assert out[0]["bounds"] == original[0]["bounds"]

    def test_missing_window_size_is_noop(self):
        class _NoWinSource:
            REQUIRED_DRIVER_TYPE = "appium"
            driver = object()

        original = _elements()
        out = utils.scale_interactive_element_bounds(_elements(), _NoWinSource(), _screenshot())
        assert out[0]["bounds"] == original[0]["bounds"]

    def test_elements_without_bounds_preserved(self):
        src = _AppiumSource(_FakeWebDriver(375, 812))
        els = [{"text": "x", "xpath": "//x"}, {"text": "y", "bounds": None}]
        out = utils.scale_interactive_element_bounds(els, src, _screenshot())
        assert out[0] == {"text": "x", "xpath": "//x"}
        assert out[1]["bounds"] is None

    def test_malformed_bounds_skipped(self):
        src = _AppiumSource(_FakeWebDriver(375, 812))
        els = [{"bounds": {"x1": 1, "y1": 2}}]  # missing x2/y2
        out = utils.scale_interactive_element_bounds(els, src, _screenshot())
        assert out[0]["bounds"] == {"x1": 1, "y1": 2}

    def test_empty_list(self):
        src = _AppiumSource(_FakeWebDriver(375, 812))
        assert utils.scale_interactive_element_bounds([], src, _screenshot()) == []
