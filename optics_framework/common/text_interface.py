from abc import ABC, abstractmethod
from typing import Optional, List, Tuple


class TextInterface(ABC):
    """
    Abstract base class for vision-based detection models.

    This interface enforces the implementation of a :meth:`detect` method,
    which processes input data to identify specific objects, patterns, or text.
    """

    @abstractmethod
    def detect(
        self, input_data, reference_data
    ) -> Optional[List[Tuple[int, int, int, int]]]:
        """
        Perform detection on the given input data.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param reference_data: The reference data used for matching or comparison.
        :type reference_data: Any
        :return: A list of bounding boxes represented as tuples ``(x, y, width, height)``,
                 or ``None`` if no matches are found.
        :rtype: Optional[List[Tuple[int, int, int, int]]]
        """
        pass

    def element_exist(self, input_data, reference_data) -> Optional[Tuple[int, int]]:
        """
        Find the location of a reference image within the input data.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param reference_data: The reference data used for matching or comparison.
        :type reference_data: Any
        :return: A tuple ``(x, y)`` representing the top-left corner of the reference image,
                 or ``None`` if the image is not found.
        :rtype: Optional[Tuple[int, int]]
        """
        pass

    def locate(self, input_data, text) -> Optional[Tuple[int, int]]:
        """
        Find the location of text within the input data.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type
        input_data: Any
        :param text: The text to search for.
        :type text: str
        :return: A tuple ``(x, y)`` representing the centre of the text,
                 or ``None`` if the text is not found.
        :rtype: Optional[Tuple[int, int]]
        """
        pass

    def find_element(self, input_data, text) -> Optional[Tuple[bool, Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Locate a specific text in the given input data using OCR and return the coordinates.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param text: The text to locate in the input data.
        :type text: str
        :return: A tuple containing a boolean indicating if the text was found,
                 the coordinates of the text, and the bounding box of the text.
        :rtype: Optional[Tuple[bool, Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]]
        """
        pass

    def locate_using_index(self, input_data, text, index) -> Optional[Tuple[int, int]]:
        """
        Locate a specific text in the given input data using OCR and return the coordinates.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param text: The text to locate in the input data.
        :type text: str
        :param index: The index of the text to locate.
        :type index: int
        :return: A tuple ``(x, y)`` representing the centre of the text,
                 or ``None`` if the text is not found.
        :rtype: Optional[Tuple[int, int]]
        """
        pass