from typing import Union, List
from optics_framework.common.driver_interface import DriverInterface
from optics_framework.common.base_factory import GenericFactory

class DeviceFactory(GenericFactory[DriverInterface]):
    """
    Factory class for managing device drivers.

    This class extends :class:`GenericFactory` to handle the discovery and
    instantiation of drivers implementing the :class:`DriverInterface`.

    :Methods:
        - :meth:`discover_drivers` - Discovers available drivers in the specified package.
        - :meth:`get_driver` - Retrieves an instance of a specified driver.
    """

    @classmethod
    def discover_drivers(
        cls, package: str = "optics_framework.engines.drivers"
    ) -> None:
        """
        Discover and register all available drivers.

        :param package: The package containing driver implementations.
                        Defaults to ``"optics_framework.engines.drivers"``.
        :type package: str
        :return: None
        :rtype: None
        """
        cls.discover(package)

    @classmethod
    def get_driver(cls, name: Union[str, List[Union[str, dict]], None]) -> DriverInterface:
        """
        Retrieve an instance of the specified driver.

        :param name: The name of the driver to retrieve.
        :type name: str or List[str]
        :return: An instance of the requested driver.
        :rtype: DriverInterface
        :raises ValueError: If the requested driver is not found.
        :raises RuntimeError: If no valid class implementing :class:`DriverInterface` is found.
        """
        return cls.get(name, DriverInterface)

DeviceFactory.discover_drivers()
