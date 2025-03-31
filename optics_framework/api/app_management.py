from optics_framework.common.logging_config import logger, apply_logger_format_to_all
from optics_framework.common.optics_builder import OpticsBuilder

@apply_logger_format_to_all("internal")
class AppManagement:
    """
    A high-level API for managing applications.

    This class provides functionality for launching, terminating,
    and modifying app settings.

    Attributes:
        driver (object): The driver instance for managing applications.
    """
    def __init__(self, builder: OpticsBuilder):
        self.driver = builder.get_driver()
        if self.driver is None:
            logger.exception(f"Driver '{builder.driver_config}' could not be initialized.")

    def initialise_setup(self):
        """
        Set up the environment for the driver module.

        This method should be called before performing any application
        management operations.
        """
        logger.debug("Initialising setup for AppManagement.")

    def launch_app(self, event_name: str | None = None):
        """
        Launch the specified application.

        :param event_name: The event triggering the app launch.
        :type event_name: str
        """
        self.driver.launch_app(event_name)

    def start_appium_session(self, event_name: str | None = None):
        """
        Start an Appium session.

        :param event_name: The event triggering the session start.
        :type event_name: str
        """
        self.driver.launch_app(event_name)

    def start_other_app(self, package_name: str, event_name: str):
        """
        Start another application.

        :param package_name: The package name of the application.
        :type package_name: str
        :param event_name: The event triggering the app start.
        :type event_name: str
        """
        pass

    def close_and_terminate_app(self, package_name: str, event_name: str):
        """
        Close and terminate a specified application.

        :param package_name: The package name of the application.
        :type package_name: str
        :param event_name: The event triggering the app termination.
        :type event_name: str
        """
        pass

    def force_terminate_app(self, event_name: str):
        """
        Forcefully terminate the specified application.

        :param event_name: The event triggering the forced termination.
        :type event_name: str
        """
        pass

    def get_app_version(self):
        """
        Get the version of the application.

        :return: The version of the application.
        :rtype: str
        """
        self.driver.get_app_version()
