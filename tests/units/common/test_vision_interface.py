import pytest
import numpy as np
from unittest.mock import patch
from optics_framework.common.vision_interface import VisionInterface
from typing import Optional, List, Tuple

class MockVisionModel(VisionInterface):
    """
    Mock implementation of VisionInterface for testing.
    """

    def detect(self, input_data, reference_data) -> Optional[List[Tuple[int, int, int, int]]]:
        """
        Simulated detection method that returns fixed bounding boxes for testing.
        """
        if isinstance(input_data, np.ndarray) and isinstance(reference_data, np.ndarray):
            return [(10, 20, 30, 40), (50, 60, 70, 80)]
        return None

@pytest.fixture
def mock_images():
    """
    Fixture to create mock image data.
    """
    mock_input = np.zeros((100, 100, 3), dtype=np.uint8)  # Black 100x100 image
    mock_reference = np.ones(
        (50, 50, 3), dtype=np.uint8) * 255  # White 50x50 image
    return mock_input, mock_reference

def test_vision_interface_instantiation():
    """
    Test that an instance of VisionInterface cannot be created directly.
    """
    with pytest.raises(TypeError):
        VisionInterface() # type: ignore

def test_mock_vision_model_with_mocked_images(mock_images):
    """
    Test the mock vision model with mocked images.
    """
    model = MockVisionModel()
    input_data, reference_data = mock_images

    result = model.detect(input_data, reference_data)

    expected_result = [(10, 20, 30, 40), (50, 60, 70, 80)]
    assert result == expected_result, "Detection result does not match expected bounding boxes."

def test_mock_vision_model_no_images():
    """
    Test that the mock vision model returns None when no images are provided.
    """
    model = MockVisionModel()

    assert model.detect(None, None) is None
    assert model.detect("invalid_data", "invalid_data") is None
