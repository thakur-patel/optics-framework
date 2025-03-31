# Global variable to store the Appium driver instance
_driver = None

def set_appium_driver(driver):
    """Set the global Appium driver instance."""
    global _driver
    _driver = driver

def get_appium_driver():
    """Retrieve the global Appium driver instance."""
    if _driver is None:
        raise RuntimeError("Appium driver has not been initialized. Call set_driver() after starting the session.")
    return _driver

def quit_appium_driver():
    """Quit the global Appium driver instance."""
    global _driver
    if _driver is not None:
        _driver.quit()
        _driver = None
