from optics_framework.common.logging_config import logger, apply_logger_format_to_all


@apply_logger_format_to_all("user")
class KeywordRegistry:
    """
    Manages a mapping of keyword function names to their methods.

    This class maintains a registry of callable methods extracted from given
    instances. It maps public method names to their corresponding method functions.
    """

    def __init__(self):
        """
        Initialize a new instance of KeywordRegistry.

        Sets up an empty dictionary to store the mapping between keyword function
        names and their methods.
        """
        self.keyword_map = {}

    def register(self, instance):
        """
        Register all public callable methods of an instance.

        Iterates over all attributes of the provided instance and registers those that are
        callable and do not have a name starting with an underscore. If a duplicate method
        name is encountered, a warning is logged.

        :param instance: The instance whose methods are to be registered.
        :type instance: object
        """
        for method_name in dir(instance):
            if not method_name.startswith("_"):
                method = getattr(instance, method_name)
                if callable(method):
                    if method_name in self.keyword_map:
                        logger.warning(
                            f"Warning: Duplicate method name '{method_name}'"
                        )
                    self.keyword_map[method_name] = method

    def get_method(self, func_name):
        """
        Retrieve a method by its function name.

        Returns the callable method associated with the specified function name from the registry.
        If no such method exists, None is returned.

        :param func_name: The name of the function to retrieve.
        :type func_name: str
        :return: The callable method if found; otherwise, None.
        :rtype: callable or None
        """
        return self.keyword_map.get(func_name)
