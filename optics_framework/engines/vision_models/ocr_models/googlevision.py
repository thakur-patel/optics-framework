from optics_framework.common.text_interface import TextInterface
from optics_framework.common.logging_config import logger
import cv2
import numpy as np
from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorClient
from typing import Optional, List, Tuple, Union


class GoogleVisionHelper(TextInterface):
    """
    Helper class for Optical Character Recognition (OCR) using EasyOCR.

    This class uses EasyOCR to detect text in images and optionally locate
    specific reference text.
    """

    def __init__(self, language: str = "en"):
        """
        Initializes the EasyOCR reader.

        :param language: Language code for OCR (default: "en").
        :type language: str

        :raises RuntimeError: If EasyOCR fails to initialize.
        """
        pass

    def detect(
        self, input_data: Union[str, np.ndarray], reference_data: Optional[str] = None
    ) -> Optional[List[Tuple[int, int, int, int]]]:
        """
        Detects text in an input image and optionally searches for a specific reference text.

        :param input_data: Path to the image file or a NumPy array of the image.
        :type input_data: Union[str, np.ndarray]
        :param reference_data: Text to search for in the detected results (optional).
        :type reference_data: Optional[str]

        :return: A list of bounding boxes [(x_min, y_min, x_max, y_max)] for the detected text,
                 or None if no match is found.
        :rtype: Optional[List[Tuple[int, int, int, int]]]

        :raises ValueError: If `input_data` is not a valid image path or NumPy array.
        """
        try:
            # Run OCR on the image (path or array)
            if isinstance(input_data, str):
                results = self.reader.readtext(input_data)
            elif isinstance(input_data, np.ndarray):
                results = self.reader.readtext(input_data, detail=1)
            else:
                raise ValueError("Input must be an image path or a NumPy array.")

            detected_boxes = []

            for bbox, text, confidence in results:
                if reference_data:
                    if reference_data.lower() in text.lower():
                        detected_boxes.append(tuple(map(int, bbox[0] + bbox[2])))
                else:
                    detected_boxes.append(tuple(map(int, bbox[0] + bbox[2])))

            if detected_boxes:
                return detected_boxes
            else:
                logger.error(f"No matching text '{reference_data}' found.")
                return None

        except Exception as e:
            logger.error(f"Error during text detection: {e}")
            return None

    def locate(self, frame, text):
        """
        Locate a specific text in the given frame using OCR and return the center coordinates with an optional offset.

        Parameters:
        - frame (np.array): Image data of the frame.
        - text (str): The text to locate in the frame.

        Returns:
        - bool: True if the text is found in the frame, False otherwise.
        - tuple: (x, y) coordinates of the center of the text in the frame or (None, None) if no match is found.
        - tuple: Bounding box coordinates of the detected text.
        - frame (np.array): The frame with the text bounding box and adjusted center dot annotated.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ocr_results = self.detect_text_google(gray_frame)

        # Iterate over each detected text
        for (bbox, detected_text, confidence) in ocr_results:
            detected_text = detected_text.strip()
            if text in detected_text:

                # Get the bounding box coordinates of the detected text
                (top_left, top_right, bottom_right, bottom_left) = bbox
                x, y = int(top_left[0]), int(top_left[1])
                w = int(bottom_right[0] - top_left[0])
                h = int(bottom_right[1] - top_left[1])

                # Calculate the center coordinates
                center_x = x + w // 2
                center_y = y + h // 2

                # Annotation: Draw the bounding box around the text
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw a small circle at the center of the bounding box (optional)
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                bbox = (top_left, bottom_right)
                return True, (center_x, center_y), bbox, frame

        return False, (None, None),bbox, frame
    

    def element_exist(self, input_data, reference_data):
        return super().element_exist(input_data, reference_data)


    def detect_text_google(self,frame: np.ndarray):
        """
        Detects text in a given NumPy array (image frame) using Google Vision API.

        Args:
            frame (np.ndarray): The image frame in NumPy array format.

        Returns:
            list: List of detected text strings.
        """
        if frame is None or not isinstance(frame, np.ndarray):
            raise ValueError("Invalid frame provided. Ensure it's a valid NumPy array.")

        # Convert the NumPy array (OpenCV format) to bytes (JPEG)
        _, encoded_image = cv2.imencode('.jpg', frame)
        image_bytes = encoded_image.tobytes()

        # Initialize Google Vision API client
        client = ImageAnnotatorClient()

        # Create Google Vision API image object
        image = vision.Image(content=image_bytes)

        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations

        # Extract detected text
        detected_text = [text.description for text in texts]
        return detected_text[1:] if detected_text else []
