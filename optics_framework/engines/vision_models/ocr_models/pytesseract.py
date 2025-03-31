from optics_framework.common.text_interface import TextInterface
from optics_framework.common import utils
from optics_framework.common.logging_config import logger
import pytesseract
import numpy as np
import cv2
from typing import Optional, List, Tuple, Union


class PytesseractHelper(TextInterface):
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
        self.pytesseract_config = "--oem 3 --psm 6"
        # logger.debug(f"Pytesseract initialized with config: {self.pytesseract_config}")

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
                # logger.debug(f"Detected text '{reference_data}' at: {detected_boxes}")
                return detected_boxes
            else:
                logger.error(f"No matching text '{reference_data}' found.")
                return None

        except Exception as e:
            logger.error(f"Error during text detection: {e}")
            return None

    def locate(self, frame, text):
        """
        Find the location of text within the input data.
        """
        result, coor, bbox = self.find_element(frame, text)
        if not result:
            logger.exception(f"Text '{text}' not found in the frame.")
            raise Exception(f"Text '{text}' not found in the frame.")
        # annotate the frame
        annotated_frame = utils.annotate_element(frame, coor, bbox)
        utils.save_screenshot(annotated_frame, name='annotated_frame')
        return coor
        
    def locate_using_index(self, frame, text, index):
        result, coor, bbox = self.find_element_index(frame, text, index)
        if not result:
            logger.exception(f"Text '{text}' not found at index {index} in the frame.")
            raise Exception(f"Text '{text}' not found at index {index} in the frame.")
        # annotate the frame
        annotated_frame = utils.annotate_element(frame, coor, bbox)
        utils.save_screenshot(annotated_frame, name='annotated_frame')
        return coor
    
    def find_element(self, frame, text):
        """
        Locate a specific text in the given frame using OCR and return the center coordinates.

        Parameters:
            - frame (np.array): Image data of the frame.
            - text (str): The text to locate in the frame.

        Returns:
            - tuple: (x, y) coordinates of the center of the text in the frame or (None, None) if not found.
            - tuple: Bounding box coordinates of the detected text.
            - frame (np.array): The frame with the annotated text bounding box and center dot.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ocr_results = self.detect_text_pytesseract(gray_frame)

        # logger.debug("Text Detection Results:", ocr_results)

        for detected_text, (x, y, w, h), confidence in ocr_results:
            if detected_text.strip().lower() == text.lower():  # Case-insensitive match
                # logger.debug(f"MATCHED: {detected_text} at ({x}, {y}, {w}, {h})")

                # Calculate center of the bounding box
                center_x = x + w // 2
                center_y = y + h // 2

                bbox = ((x, y), (x + w, y + h))  # Top-left and bottom-right

                # Save the annotated frame
                utils.save_screenshot(frame, name='annotated_frame')

                # logger.debug("Returning values:", center_x, center_y, bbox)
                return True,(center_x, center_y),bbox

        # If no match is found, return None values
        # logger.debug(f"Text '{text}' not found in frame.")
        return False,(None, None),None

    def find_element_index(self, frame, text, index=0):
        """
        Locate a specific occurrence of a text in the given frame using OCR and return the center coordinates.

        Parameters:
            - frame (np.array): Image data of the frame.
            - text (str): The text to locate in the frame.
            - index (int): The occurrence index (0-based) to select if multiple matches exist.

        Returns:
            - tuple: (x, y) coordinates of the center of the selected text in the frame or (None, None) if not found.
            - tuple: Bounding box coordinates of the detected text.
            - frame (np.array): The frame with the annotated text bounding box and center dot.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ocr_results = self.detect_text_pytesseract(gray_frame)

        # logger.debug("Text Detection Results:", ocr_results)

        matches = []
        for detected_text, (x, y, w, h), confidence in ocr_results:
            if detected_text.strip().lower() == text.lower():  # Case-insensitive match
                center_x = x + w // 2
                center_y = y + h // 2
                bbox = ((x, y), (x + w, y + h))  # Top-left and bottom-right
                matches.append(((center_x, center_y), bbox))

        if matches and index < len(matches):
            selected_center, selected_bbox = matches[index]

            # Save the annotated frame
            utils.save_screenshot(frame, name='annotated_frame')

            # logger.debug("Returning values:", selected_center, selected_bbox)
            return True, selected_center, selected_bbox

        # If no match is found or the index is out of range
        return False, (None, None), None

    def detect_text_pytesseract(self, image):
        _, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        data = pytesseract.image_to_data(binary_image, config=self.pytesseract_config, output_type=pytesseract.Output.DICT)
        detected_texts = []
        for i in range(len(data["text"])):
            text = data["text"][i].strip()
            if text:  # Filter out empty results
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                conf = data["conf"][i]  # Get confidence score
                detected_texts.append((text, (x, y, w, h), conf))
        return binary_image, detected_texts

    def element_exist(self, input_data, reference_data):
        # dummy implementation
        return super().element_exist(input_data, reference_data)