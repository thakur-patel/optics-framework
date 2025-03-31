from abc import ABC, abstractmethod

class ElementSourceInterface(ABC):
    """
    Abstract base class for application drivers.

    This interface enforces the implementation of essential methods
    for interacting with applications.
    """

    @abstractmethod
    def capture(self):
        """
        Capture the current screen state.

        :return: None
        :rtype: None
        """ 


    @abstractmethod
    def locate(self, element) -> tuple:
        """
        Locate a template image within a larger image.

        :param image: The image to search.
        :param template: The template to search for.
        :return: A tuple containing the coordinates of the located template.
        :rtype: tuple
        """
        pass

    @abstractmethod
    def assert_elements(self, elements, timeout=30, rule='any') -> None:
        """
        Assert the presence of elements on the screen.
        :param elements: The elements to be asserted.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    def locate_using_index(self, element, index) -> tuple:
        """
        Locate an element by index.
        :param element: The element to locate.
        :param index: The index of the element.
        :return: A tuple containing the coordinates of the located element.
        :rtype: tuple
        """
        pass