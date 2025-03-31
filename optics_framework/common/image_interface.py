from abc import ABC, abstractmethod
from typing import Optional, List, Tuple


class ImageInterface(ABC):
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

    def locate(self, input_data, image) -> Optional[Tuple[int, int]]:
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

    def find_element(self, input_data, image) -> Optional[Tuple[bool, Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Find the location of an image within the input data.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param image: The image to search for.
        :type image: Any
        :return: A tuple containing a boolean indicating whether the image was found,
                 the center coordinates of the image, and the bounding box coordinates.
        :rtype: Optional[Tuple[bool, Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]]
        """
        pass

    def locate_using_index(self, input_data, reference_data, index) -> Optional[Tuple[int, int]]:
        """
        Find the location of an element using the specified index.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param reference_data: The reference data used for matching or comparison.
        :type reference_data: Any
        :param index: The index of the element to locate.
        :type index: int
        :return: A tuple ``(x, y)`` representing the center of the element,
                 or ``None`` if the element is not found.
        :rtype: Optional[Tuple[int, int]]
        """
        pass