import pytest
import cv2
from pathlib import Path
from optics_framework.engines.vision_models.ocr_models.easyocr_helper import EasyOCRHelper


@pytest.fixture
def easyocr_instance():
    """Fixture to initialize EasyOCRHelper."""
    return EasyOCRHelper(language="en")


@pytest.fixture
def sample_image():
    """Loads a sample test image as a NumPy array."""
    test_file_path = Path(__file__).resolve()  # Get the test file's absolute path
    image_path = test_file_path.parent.parent.parent.parent / "assets" /  \
    "sample_text_image.png"  # Construct absolute path
    image = cv2.imread(str(image_path))
    assert image is not None, "Test image not found or failed to load"
    return image


def test_detect_text(easyocr_instance, sample_image):
    """Test that detect method correctly identifies text in an image."""
    reference_text = "Connected"

    result = easyocr_instance.detect(sample_image, reference_text)

    assert result is not None, "Text should be detected in the image"
    assert isinstance(
        result, list), "Result should be a list of bounding boxes"
    assert all(isinstance(box, tuple) and len(
        box) == 4 for box in result), "Each box should be a tuple of four integers"


def test_detect_text_not_found(easyocr_instance, sample_image):
    """Test that detect returns None if reference text is not found."""
    reference_text = "NonexistentText"

    result = easyocr_instance.detect(sample_image, reference_text)

    assert result is None, "No bounding box should be returned for missing text"
