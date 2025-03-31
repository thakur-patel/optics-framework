from typing import Union, List
from optics_framework.common.image_interface import ImageInterface
from optics_framework.common.base_factory import GenericFactory


class ImageFactory(GenericFactory[ImageInterface]):
    """
    Factory class for managing image processing engines.

    This class extends :class:`GenericFactory` to handle the discovery and
    instantiation of image-related detection models that implement
    :class:`ImageInterface`.

    :Methods:
        - :meth:`discover_drivers`: Discovers available image detection engines.
        - :meth:`get_driver`: Retrieves an instance of a specified image detection engine.
    """

    @classmethod
    def discover_drivers(
        cls, package: str = "optics_framework.engines.vision_models.image_models"
    ) -> None:
        """
        Discover and register available image detection engines.

        :param package: The package containing vision detection implementations.
                        Defaults to ``"optics_framework.engines.vision_models.image_models"``.
        :type package: str
        :return: None
        :rtype: None
        """
        cls.discover(package)

    @classmethod
    def get_driver(cls, name: Union[str, List[Union[str, dict]], None]) -> ImageInterface:
        """
        Retrieve an instance of the specified vision detection engine.

        :param name: The name of the vision engine to retrieve. Can be a string or a list of strings/dicts.
        :type name: Union[str, List[Union[str, dict]]]
        :return: An instance of the requested vision detection engine.
        :rtype: ImageInterface

        :raises ValueError: If the requested vision engine is not found.
        :raises RuntimeError: If no valid class implementing :class:`ImageInterface` is found.
        """
        return cls.get(name, ImageInterface)


ImageFactory.discover_drivers()
