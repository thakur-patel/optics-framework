from typing import Union, List
from optics_framework.common.text_interface import TextInterface
from optics_framework.common.base_factory import GenericFactory


class TextFactory(GenericFactory[TextInterface]):
    """
    Factory class for managing vision processing engines.

    This class extends :class:`GenericFactory` to handle the discovery and
    instantiation of vision-related detection models that implement
    :class:`TextInterface`.

    :Methods:
        - :meth:`discover_drivers`: Discovers available vision detection engines.
        - :meth:`get_driver`: Retrieves an instance of a specified vision detection engine.
    """

    @classmethod
    def discover_drivers(
        cls, package: str = "optics_framework.engines.vision_models.ocr_models"
    ) -> None:
        """
        Discover and register available vision detection engines.

        :param package: The package containing vision detection implementations.
                        Defaults to ``"optics_framework.engines.vision_models.ocr_models"``.
        :type package: str
        :return: None
        :rtype: None
        """
        cls.discover(package)

    @classmethod
    def get_driver(cls, name: Union[str, List[Union[str, dict]], None]) -> TextInterface:
        """
        Retrieve an instance of the specified vision detection engine.

        :param name: The name of the vision engine to retrieve. Can be a string or a list of strings/dicts.
        :type name: Union[str, List[Union[str, dict]]]
        :return: An instance of the requested vision detection engine.
        :rtype: TextInterface

        :raises ValueError: If the requested vision engine is not found.
        :raises RuntimeError: If no valid class implementing :class:`TextInterface` is found.
        """
        return cls.get(name, TextInterface)


TextFactory.discover_drivers()
