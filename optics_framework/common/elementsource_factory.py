from typing import Union, List
from optics_framework.common.elementsource_interface import ElementSourceInterface
from optics_framework.common.base_factory import GenericFactory

class ElementSourceFactory(GenericFactory[ElementSourceInterface]):
    """
    Factory class for managing element sources.

    This class extends :class:`GenericFactory` to handle the discovery and
    instantiation of element sources implementing the :class:`ElementSourceInterface`.

    :Methods:
        - :meth:`discover_elementsources` - Discovers available element sources in the specified package.
        - :meth:`get_elementsource` - Retrieves an instance of a specified element source.
    """

    @classmethod
    def discover_elementsources(
        cls, package: str = "optics_framework.engines.elementsources"
    ) -> None:
        """
        Discover and register all available element sources.

        :param package: The package containing element source implementations.
                Defaults to ``"optics_framework.engines.elementsources"``.
        :type package: str
        :return: None
        :rtype: None
        """
        cls.discover(package)

    @classmethod
    def get_driver(cls, name: Union[str, List[Union[str, dict]], None]) -> ElementSourceInterface:
        """
        Retrieve an instance of the specified element source.

        :param name: The name of the element source to retrieve.
        :type name: str
        :return: An instance of the requested element source.
        :rtype: ElementSourceInterface
        :raises ValueError: If the requested element source is not found.
        :raises RuntimeError: If no valid class implementing :class:`ElementSourceInterface` is found.
        """
        return cls.get(name, ElementSourceInterface)


ElementSourceFactory.discover_elementsources()
