from optics_framework.common.logging_config import logger, apply_logger_format_to_all
from optics_framework.common import utils
from optics_framework.common.optics_builder import OpticsBuilder
from datetime import datetime
import time
import cv2
from typing import Union, List, Dict

@apply_logger_format_to_all("internal")
class Verifier:
    """
    Provides methods to verify elements, screens, and data integrity.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Verifier, cls).__new__(cls)
        return cls._instance

    def __init__(self, builder: OpticsBuilder):
        self.element_source = builder.get_element_source()
        self.image_detection = builder.get_image_detection()
        self.text_detection = builder.get_text_detection()

    def validate_element(
        self,
        element: str,
        timeout: int = 10,
        rule: str = "all",
        event_name: str | None = None,
    ) -> None:
        """
        Verifies the specified element.

        :param element: The element to be verified (Image template, OCR template, or XPath).
        :type element: str
        :param timeout: The time to wait for verification.
        :type timeout: int
        :param rule: The rule used for verification.
        :type rule: str
        :param event_name: The name of the event associated with the verification.
        :type event_name: str
        """
        logger.debug(f"Validating element: {element}")
        logger.debug(f"Timeout: {timeout} and Rule: {rule}")
        self.assert_presence(element, timeout, rule, event_name)


    def is_element(
        self, element: str, element_state: str, timeout: int, event_name: str
    ) -> None:
        """
        Checks if the specified element is Enabled/Disabled/Visible/Invisible.

        :param element: The element to be checked (Image template, OCR template, or XPath).
        :type element: str
        :param element_state: The state of the element (visible, invisible, enabled, disabled).
        :type element_state: str
        :param timeout: The time to wait for the element.
        :type timeout: int
        :param event_name: The name of the event associated with the check.
        :type event_name: str
        """
        pass

    def assert_equality(self, output, expression) -> None:
        """
        Compares two values for equality.

        :param output: The first value to be compared.
        :type output: any
        :param expression: The second value to be compared.
        :type expression: any
        :param event_name: The name of the event associated with the comparison.
        :type event_name: str
        """
        pass
    
    def vision_search(self, elements: list[str], timeout: int, rule: str) -> bool:
        """
        Vision based search for elements
        """
        rule = rule.lower()
        timeout = int(timeout)
        found_text = False
        found_image = False
        # Group elements by type
        texts = [el for el in elements if utils.determine_element_type(el) == 'Text']
        images = [el for el in elements if utils.determine_element_type(el) == 'Image']

        # Shared resources
        element_status = {
            'texts': {text: {'found': False, 'bbox': None} for text in texts},
            'images': {image: {'found': False, 'bbox': None} for image in images}
        }
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            
            # Capture a screenshot
            timestamp = utils.get_current_time_for_events() # Get timestamp when the screenshot is taken
            frame = self.element_source.capture()

            if frame is None:
                logger.debug("Screenshot capture failed. Skipping iteration.")
                continue

            logger.debug(f"Screenshot captured at {timestamp}.")

            # Search for text elements
            if texts:
                found_text = self.assert_texts_vision(frame, texts, element_status, rule)

            # Search for image elements
            if images:
                found_image = self.assert_images_vision(frame, images, element_status, rule)

            # If rule is 'any' and either text or image is found, stop early
            if rule == 'any' and (found_text or found_image):
                utils.annotate_and_save(frame, element_status)
                return True

            # If rule is 'all' and all elements are found, stop early
            if rule == 'all' and all(
                item['found'] for status in element_status.values() for item in status.values()
            ):
                return True

            time.sleep(0.5)
            # Final annotation before returning
        utils.annotate_and_save(frame, element_status)

        return any(item['found'] for status in element_status.values() for item in status.values())

    def assert_texts_vision(self, frame, texts, element_status, rule):
        """
        Searches for the given texts in a single frame using OCR.
        
        Args:
            frame (numpy.ndarray): The image frame to search in.
            texts (list): List of text elements to search for.
            element_status (dict): Dictionary storing found element statuses.
        Returns:
            bool: True if an element is found (for 'any' rule), False otherwise.
        """
        found_any = False

        for text in texts[:]:  # Iterate over a copy to avoid modification issues
            if element_status['texts'][text]['found']:
                continue  # Skip if already found
            found, _, bbox = self.text_detection.find_element(frame, text)
            
            if found:
                if not element_status['texts'][text]['found']:
                    element_status['texts'][text] = {'found': True, 'bbox': bbox}

                logger.debug(f"Text '{text}' found at bbox: {bbox}.")
                found_any = True

                if rule == 'any':
                    return True  # Stop processing if 'any' rule is met
            else:
                logger.debug(f"Text '{text}' not found in screenshot.")

        return found_any if rule == 'any' else all(
            item['found'] for item in element_status['texts'].values()
        )


    def assert_images_vision(self, frame, images, element_status, rule):
        """
        Searches for the given images in a single frame using template matching.
        
        Args:
            frame (numpy.ndarray): The image frame to search in.
            images (list): List of image templates to search for.
            element_status (dict): Dictionary storing found element statuses.
            rule (str): 'any' (stop when one is found) or 'all' (search all).
        Returns:
            bool: True if an element is found (for 'any' rule), False otherwise.
        """
        found_any = False

        for image in images[:]:  # Iterate over a copy to avoid modification issues
            if element_status['images'][image]['found']:
                continue  # Skip if already found

            result, _, bbox = self.image_detection.find_element(frame, image)

            if result:
                element_status['images'][image] = {'found': True, 'bbox': bbox}

                logger.debug(f"Image '{image}' found at bbox: {bbox}.")
                found_any = True

                if rule == 'any':
                    return True  # Stop processing if 'any' rule is met
            else:
                logger.debug(f"Image '{image}' not found.")

        return found_any if rule == 'any' else all(
            item['found'] for item in element_status['images'].values()
        )

    def assert_presence(self, elements, timeout=30, rule='any', event_name=None) -> bool:
        """
        Asserts the presence of elements.

        :param elements: The elements to be checked (Image template, OCR template, or XPath).
        :type elements: list
        :param timeout: The time to wait for the elements.
        :type timeout: int
        :param rule: The rule used for verification.
        :type rule: str
        :param event_name: The name of the event associated with the assertion.
        :type event_name: str
        """
        element_source_type = type(self.element_source.current_instance).__name__
        rule = rule.lower()
        timeout = int(timeout)
        elements = elements.split(',')
        # Group elements by type
        texts = [el for el in elements if utils.determine_element_type(el) == 'Text']
        xpaths = [el for el in elements if utils.determine_element_type(el) == 'XPath']
        images = [el for el in elements if utils.determine_element_type(el) == 'Image']

        if 'appium' in element_source_type.lower():
            # calls assert presence from appium driver
            if images:
                logger.error("Image search is not supported for Appium based search")
                return False
            texts_xpaths = texts + xpaths
            result = self.element_source.assert_elements(texts_xpaths, timeout, rule)

        else:
            # vision search
            if xpaths:
                logger.error("XPath search is not supported for Vision based search")
                return False
            texts_images = texts + images
            result = self.vision_search(texts_images, timeout, rule)
        if event_name:
            # Trigger event
            pass

        return result
    
    def validate_screen(self, elements, timeout=30, rule='any', event_name=None) -> None:
        """
        Verifies the specified screen.

        :param elements: The elements to be verified (Image template, OCR template, or XPath).
        :type elements: list
        :param timeout: The time to wait for verification.
        :type timeout: int
        :param rule: The rule used for verification.
        :type rule: str
        :param event_name: The name of the event associated with the verification.
        :type event_name: str
        """
        self.assert_presence(elements, timeout, rule, event_name)

