from abc import ABC, abstractmethod
import inspect
from typing import Union, Tuple, Generator, Set
from optics_framework.common.base_factory import FallbackProxy
from optics_framework.common.elementsource_interface import ElementSourceInterface
from optics_framework.common import utils
from optics_framework.common.logging_config import logger

# Locator Strategy Interface
class LocatorStrategy(ABC):
    @property
    @abstractmethod
    def element_source(self) -> ElementSourceInterface:
        """The element source this strategy operates on."""
        pass

    @abstractmethod
    def locate(self, element) -> Union[object, Tuple[int, int]]:
        """Locate an element and return either an element object or coordinates (x, y)."""
        pass

    @staticmethod
    @abstractmethod
    def supports(element_type: str, element_source: ElementSourceInterface) -> bool:
        """Determine if this strategy supports the given element type and source."""
        pass

    @staticmethod
    def _is_method_implemented(element_source, method_name: str) -> bool:
        """Check if the method is implemented and not a stub."""
        method = getattr(element_source, method_name)
        if inspect.isabstract(method):
            return False
        try:
            source = inspect.getsource(method)
            return "raise NotImplementedError" not in source
        except (OSError, TypeError):
            return True

# Concrete Strategies


class XPathStrategy(LocatorStrategy):
    def __init__(self, element_source: ElementSourceInterface):
        self._element_source = element_source

    @property
    def element_source(self) -> ElementSourceInterface:
        return self._element_source

    def locate(self, element):
        return self.element_source.locate(element)

    @staticmethod
    def supports(element_type: str, element_source: ElementSourceInterface) -> bool:
        return element_type == "XPath" and LocatorStrategy._is_method_implemented(element_source, "locate")


class TextElementStrategy(LocatorStrategy):
    def __init__(self, element_source: ElementSourceInterface):
        self._element_source = element_source

    @property
    def element_source(self) -> ElementSourceInterface:
        return self._element_source

    def locate(self, element):
        return self.element_source.locate(element)

    @staticmethod
    def supports(element_type: str, element_source: ElementSourceInterface) -> bool:
        return element_type == "Text" and LocatorStrategy._is_method_implemented(element_source, "locate")


class TextDetectionStrategy(LocatorStrategy):
    def __init__(self, element_source: ElementSourceInterface, text_detection):
        self._element_source = element_source
        self.text_detection = text_detection

    @property
    def element_source(self) -> ElementSourceInterface:
        return self._element_source

    def locate(self, element):
        screenshot = self.element_source.capture()
        return self.text_detection.locate(screenshot, element)

    @staticmethod
    def supports(element_type: str, element_source: ElementSourceInterface) -> bool:
        return element_type == "Text" and LocatorStrategy._is_method_implemented(element_source, "capture")


class ImageDetectionStrategy(LocatorStrategy):
    def __init__(self, element_source: ElementSourceInterface, image_detection):
        self._element_source = element_source
        self.image_detection = image_detection

    @property
    def element_source(self) -> ElementSourceInterface:
        return self._element_source

    def locate(self, element):
        screenshot = self.element_source.capture()
        return self.image_detection.locate(screenshot, element)

    @staticmethod
    def supports(element_type: str, element_source: ElementSourceInterface) -> bool:
        return element_type == "Image" and LocatorStrategy._is_method_implemented(element_source, "capture")

# Strategy Factory


class StrategyFactory:
    def __init__(self, text_detection, image_detection):
        self.text_detection = text_detection
        self.image_detection = image_detection
        self._strategy_registry = [
            (XPathStrategy, "XPath", {}),
            (TextElementStrategy, "Text", {}),
            (TextDetectionStrategy, "Text", {
             "text_detection": self.text_detection}),
            (ImageDetectionStrategy, "Image", {
             "image_detection": self.image_detection}),
        ]

    def create_strategies(self, element_source: ElementSourceInterface) -> list:
        """Create strategies compatible with the given element source using the registry."""
        strategies = []
        for strategy_cls, element_type, extra_args in self._strategy_registry:
            if strategy_cls.supports(element_type, element_source):
                strategies.append(strategy_cls(element_source, **extra_args))
        return strategies

# Result Wrapper


class LocateResult:
    def __init__(self, value: Union[object, Tuple[int, int]], strategy: LocatorStrategy):
        self.value = value
        self.strategy = strategy
        self.is_coordinates = isinstance(value, tuple)

# Strategy Manager


class StrategyManager:
    def __init__(self, element_source: ElementSourceInterface, text_detection, image_detection):
        self.element_source = element_source
        self.factory = StrategyFactory(text_detection, image_detection)
        self.strategies = self._build_strategies()
        logger.debug(f"Built strategies: {self.strategies}")

    def _build_strategies(self) -> Set[LocatorStrategy]:
        """Build a set of all strategies from the element source."""
        all_strategies = set()
        if isinstance(self.element_source, FallbackProxy):
            for instance in self.element_source.instances:
                all_strategies.update(self.factory.create_strategies(instance))
        else:
            all_strategies.update(
                self.factory.create_strategies(self.element_source))

        if not all_strategies:
            raise ValueError(
                "No strategies available for the given element source")
        return all_strategies

    def locate(self, element) -> Generator[LocateResult, None, None]:
        """Yield applicable strategies' results in order of attempt."""
        element_type = utils.determine_element_type(element)
        applicable_strategies = {s for s in self.strategies if s.supports(
            element_type, s.element_source)}

        for strategy in applicable_strategies:
            try:
                result = strategy.locate(element)
                if result:
                    yield LocateResult(result, strategy)
            except Exception as e:
                logger.error(
                    f"Strategy {strategy.__class__.__name__} failed: {e}")
