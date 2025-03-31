from optics_framework.common.elementsource_interface import ElementSourceInterface
from optics_framework.engines.drivers.appium_driver_manager import get_appium_driver
from optics_framework.common.logging_config import logger
from optics_framework.common import utils
from appium.webdriver.common.appiumby import AppiumBy
from optics_framework.engines.drivers.appium_UI_helper import UIHelper
from lxml import etree
import time
import re

class AppiumPageSource(ElementSourceInterface):
    """
    Appium Find Element Class
    """

    def __init__(self):
        """
        Initialize the Appium Find Element Class.

        Args:
            driver: The Appium driver instance.
        """
        self.driver = None
        self.ui_helper = UIHelper()
        self.tree = None
        self.root = None

    def _get_appium_driver(self):
        if self.driver is None:
            self.driver = get_appium_driver()
        return self.driver  
    
    def capture(self):
        """
        Capture the current screen state.

        return """
        logger.exception('Appium Find Element does not support capturing the screen state.')
        raise NotImplementedError(
            'Appium Find Element does not support capturing the screen state.')

    def get_page_source(self) -> str:
        """
        Get the page source of the current page.

        Returns:
            str: The page source.
        """
        time_stamp = utils.get_current_time_for_events()

        driver = self._get_appium_driver()
        page_source = driver.page_source

        self.tree = etree.ElementTree(etree.fromstring(page_source.encode('utf-8')))
        self.root = self.tree.getroot()

        logger.debug('\n\n========== PAGE SOURCE FETCHED ==========\n')
        logger.debug(f'Page source fetched at: {time_stamp}')
        logger.debug('\n==========================================\n')
        return page_source
    

    def locate(self, element: str):
        """
        Find the specified element on the current page.

        Args:
            element: The element to find on the page.

        Returns:
            bool: True if the element is found, False otherwise.
        """
        """
        Find the specified element on the current page using the Appium driver.
        """
        driver = self._get_appium_driver()
        element_type = utils.determine_element_type(element)

        if element_type == 'Image':
            # Find the element by image
            logger.debug('Appium Find Element does not support finding images.')
            return None
        else:
            if element_type == 'Text':
                # Find the element by text
                xpath = self.find_xpath_from_text(element)
                try:
                    element = driver.find_element(AppiumBy.XPATH, xpath)
                except Exception as e:
                    logger.exception(f"Error finding element by text: {e}")
                    raise Exception (f"Error finding element by text: {e}")
                return element
            elif element_type == 'XPath':
                xpath, _ = self.ui_helper.find_xpath(element)
                try:
                    element = driver.find_element(AppiumBy.XPATH, xpath)
                except Exception as e:
                    logger.exception(f"Error finding element by xpath: {e}")
                    raise Exception (f"Error finding element by xpath: {e}")
                return element
            

    def locate_using_index(self, element, index, strategy=None) -> dict:
        locators = self.get_locator_and_strategy_using_index(element, index, strategy)
        if locators:
            strategy = locators['strategy']
            locator = locators['locator']
            xpath = self.ui_helper.get_view_locator(strategy=strategy, locator=locator)
            try:
                element = self.driver.find_element(AppiumBy.XPATH, xpath)
            except Exception as e:
                logger.exception(f"Error finding element by index: {e}")
                raise Exception (f"Error finding element by index: {e}")
            return element
        return {}


    def assert_elements(self, elements, timeout=30, rule='any'):
        """
        Assert the presence of elements on the current page.

        Args:
            elements (list): List of elements to assert on the page.
            timeout (int): Maximum time to wait for the elements to appear.
            rule (str): Rule to apply ("any" or "all").
            polling_interval (float): Interval between retries in seconds.

        Returns:
            bool: True if the elements are found.

        Raises:
            Exception: If elements are not found based on the rule within the timeout.
        """
        if rule not in ["any", "all"]:
            raise ValueError("Invalid rule. Use 'any' or 'all'.")

        start_time = time.time()

        while time.time() - start_time < timeout:
            texts = [el for el in elements if utils.determine_element_type(el) == 'Text']
            xpaths = [el for el in elements if utils.determine_element_type(el) == 'XPath']

            self.get_page_source()  # Refresh page source before checking

            # Check text-based elements
            if texts:
                text_found = self.ui_text_search(texts, rule)
                if rule == "all" and not text_found:
                    time.sleep(0.3)
                    continue
                if rule == "any" and text_found:
                    return True  # Early exit if any text is found

            # Check XPath-based elements
            xpath_found = False
            for xpath in xpaths:
                xpath_result,_ = self.ui_helper.find_xpath(xpath)
                if rule == "all" and not xpath_result:
                    xpath_found = False
                    break  # Stop checking further if one is missing
                if rule == "any" and xpath_result:
                    return True  # Early exit if any XPath is found
                xpath_found = True  # If all xpaths found in "all" mode

            if rule == "all" and text_found and xpath_found:
                return True  # All required elements are found

            time.sleep(0.3)  # Wait before retrying

        # Timeout reached, raise an exception based on rule
        if rule == "all":
            raise TimeoutError(f"Timeout reached: Not all elements were found: {elements}")

        if rule == "any":
            raise TimeoutError("Timeout reached: None of the specified elements were found.")

        return False  # This should never be reached due to exceptions


    def find_xpath_from_text(self, text):
        """
        Find the XPath of an element based on the text content.

        Args:
            text (str): The text content to search for in the UI tree.

        Returns:
            str: The XPath of the element containing the
            text content, or None if not found.
        """
        locators = self.ui_helper.get_locator_and_strategy(text)
        if locators:
            strategy = locators['strategy']
            locator = locators['locator']
            xpath = self.ui_helper.get_view_locator(strategy=strategy, locator=locator)
            return xpath
        return None
    

    def ui_text_search(self, texts, rule='any'):
        """
        Checks if any or all given texts exist in the UI tree.
        
        Args:
            texts (list): List of text strings to search for.
            rule (str): Rule for matching ('any' or 'all').

        Returns:
            bool: True if the condition is met, otherwise False.
        """
        strategies = ["text", "resource-id", "content-desc", "name", "value", "label"]
        
        found_texts = set()

        for text in texts:
            logger.debug(f'Searching for text: {text}')
            
            for attrib in strategies:
                matching_elements = self.tree.xpath(f"//*[@{attrib}]")
                
                for elem in matching_elements:
                    attrib_value = elem.attrib.get(attrib, '').strip()
                    
                    if attrib_value and utils.compare_text(attrib_value, text):
                        logger.debug(f"Match found using {attrib} for '{text}'")
                        found_texts.add(text)  # Mark this text as found
                        break  # Stop searching other elements for this text
                
                if text in found_texts:  # Stop checking other strategies if already found
                    break
            
            if rule == 'any' and text in found_texts:
                return True  # Early exit if at least one match is found
        
        return len(found_texts) == len(texts) if rule == 'all' else False


    def get_locator_and_strategy_using_index(self, element, index, strategy=None) -> dict:
        """
        Perform a linear search across all strategies (resource-id, text, content-desc, etc.) in the UI tree,
        match against the input, and index the found matches.

        Args:
            element (str): The element identifier to search for.
            index (int): zero indexing
            strategy (str): supported attributes in string, 'resource-id', 'text', 'content-desc', 'name', 'value', 'label'

        Returns:
            list: A list of dictionaries, each containing the strategy, value, and index of the match.
        """
        self.get_page_source()
        tree = self.tree

        # Collect all elements in positional order
        all_strategies = ['resource-id', 'text', 'content-desc', 'name', 'value', 'label']  # Supported attributes
        all_elements = []

        strategies = [strategy] if strategy else all_strategies

        # If a specific strategy is provided, ensure it's valid
        if strategy and strategy not in strategies:
            raise ValueError(f"Invalid strategy '{strategy}'. Supported strategies: {strategies}")

        for strategy in strategies:
            elements = tree.xpath(f"//*[@{strategy}]")
            for elem in elements:
                attr_value = elem.attrib.get(strategy, '').strip()
                bounds = elem.attrib.get('bounds', '')  # Parse bounds if available
                position = self.parse_bounds(bounds)
                all_elements.append({
                    "strategy": strategy,
                    "value": attr_value,
                    "position": position
                })

        # Perform a linear match against all elements
        matches = []
        for idx, elem in enumerate(all_elements):
            if utils.compare_text(elem["value"], element):
                matches.append({
                    "index": idx,
                    "strategy": elem["strategy"],
                    "value": elem["value"],
                    "position": elem["position"]
                })

        # Log matches
        logger.debug(f"Found {len(matches)} matches for '{element}': {matches}")

        if index >= len(matches):
            raise   IndexError(f"Index {index} is out of range for the matches found. Total matches: {len(matches)}.")

        desired_match = matches[index]
        logger.debug(f'Found the matches for {element} and returning {index} index match: {desired_match} ')

        strategy = desired_match["strategy"]
        locator = desired_match["value"]
        
        logger.debug(f"Returning strategy: {strategy}, locator: {locator}")
        return {"strategy": strategy, "locator": locator}

    def parse_bounds(self, bounds):
        """
        Parse the 'bounds' attribute to extract position information.
        Args:
            bounds (str): Bounds string in the format "[x1,y1][x2,y2]".
        Returns:
            dict: A dictionary with coordinates {x1, y1, x2, y2}.
        """
        try:
            numbers = re.findall(r'\d+', bounds)  # Extract all numbers from the string
            if len(numbers) == 4:
                x1, y1, x2, y2 = map(int, numbers)
                return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            else:
                raise ValueError(f"Unexpected bounds format: {bounds}")
        except Exception as e:
            logger.debug(f"Error parsing bounds: {bounds} - {e}")
            return {"x1": 0, "y1": 0, "x2": 0, "y2": 0}
