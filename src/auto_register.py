"""
Class Register using Selenium.

Default driver is PhantomJS.

Supported drivers:
    PhantomJS
    Chrome
    Mozilla Firefox (unrealiable since marionette update)
Created on Jan 28, 2016

@author: David Lam
@edited: Fred Zhang
"""

from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import os
import sys
import time
import argparse

# Global Constants.
BANNER_WEB_URL = "https://prod11gbss8.rose-hulman.edu/BanSS/twbkwbis.P_WWWLogin"
username_KEY = "username"
PASSWORD_KEY = "password"
PIN_KEY = "pin"
CRN_KEY = "crn"
START_KEY = "start"


def get_driver(browser):
    """
        Gets the driver for the specified browser

        Arguments:
            :type browser       String
                browser webdriver to return.

        Returns the Webdriver for the specified browser.
    """
    if (browser == "chrome"):
        return webdriver.Chrome(
            "../drivers/chromedriver.exe", service_log_path="../logs/chrome.log")
    elif (browser == "phantom"):
        return webdriver.PhantomJS(
            "../drivers/phantomjs.exe", service_log_path="../logs/phantom.log")
    elif (browser == "firefox"):
        return webdriver.Firefox(
            executable_path="../drivers/geckodriver.exe", log_path="../logs/firefox.log")
    else:
        print("Invalid option...using PhantomJS")
        return webdriver.PhantomJS(
            "../drivers/phantomjs.exe", service_log_path="../logs/phantom.log")


def click_tag_with_value(driver, tag_name, value):
    """
       Attempts to click on a button with a specific tag name and value.
       It will click the first button with specified value.

       Arguments:
           :type driver :     webdriver
               Selenium Webdriver.
           :type tag_name :    str
               Specified HTML tag name.
           :type value :      str
               Specified HTML value related to tag name.

        Returns nothing.
    """
    inputList = driver.find_elements_by_tag_name(tag_name)

    for element in inputList:
        if (element.get_attribute("value") == value):
            element.click()
            break


def attempt_to_register(driver, crn_input):
    """
        Gets the CRN text box and fills it in with crn numbers.

        Arguments:
            :type driver :    webdriver
                Selenium Webdriver.
            :type crn_input :  list
                List of CRN numbers.

        Returns a list of CRN text box.

        Raises Selenium.NoSuchElementException
    """
    try:
        firstElement = None
        for identifier in range(1, len(crn_input) + 1):
            element = driver.find_element_by_id("crn_id" + str(identifier))
            element.send_keys(crn_input[identifier - 1])
            if (identifier == 1):
                firstElement = element

        # Old way: Look up all input tags (about 100+)
        # Then, linearly scan for an input with value "Submit Changes"
        # click_tag_with_value(driver, "input", "Submit Changes")

        # Hard coded the offset from Chrome experimentation.
        # Use WebElement.location to find proper offset values.
        action = ActionChains(driver)
        action.move_to_element_with_offset(firstElement, 0, 43)
        action.click()
        action.perform()

    except (NoSuchElementException):
        print("Page Not Ready.")
        driver.refresh()
        if (isinstance(driver, webdriver.Firefox)):
            Alert(driver).accept()
        return False
    return True


def parse_arguments():
    """
        Returns the arguments parsed from the command line.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--data", help="Data text file file path", required=True)
    parser.add_argument(
        "-b", "--browser", help="Webdriver to use", default="phantom", required=True)

    return parser.parse_args()


def get_data(data_file):
    """
        Pulls user data from data.txt.

        Arguments:
            :type data_file     String
                Path String to data text.

        Returns a dictionary of relevant data.
    """
    data_file = open(data_file, "r")
    dataMap = {}

    for line in data_file:
        lineList = line.split()
        dataMap[lineList[0]] = lineList[1:len(lineList)]

    data_file.close()

    return dataMap


def setup_directory():
    """
        Creates the logs and img files if not created.
    """
    # Make directory for logs and images if necessary.
    if (not os.path.isdir("../logs/")):
        os.makedirs("../logs/")
    if (not os.path.isdir("../img/")):
        os.makedirs("../img/")


def login(driver, username, password):
    """
        Login to BannerWeb.

        Arguments:
            :type driver :        webdriver
                Selenium Webdriver.
            :type username :      String
                Rose-Hulman username.
            :type password :      String
                Rose-Hulman passwordpop.
    """
    # Navigate to BannerWeb.
    driver.get(BANNER_WEB_URL)

    # Login to Bannerweb.
    driver.find_element_by_name("sid").send_keys(username)
    driver.find_element_by_name("PIN").send_keys(password)
    click_tag_with_value(driver, "input", "Login")


def navigate_to_registration_page(driver, pin):
    """
        Navigates to the registration page and enters the given pin.

        Arguments:
            :type driver        webdriver
                Selenium Webdriver.
            :type pin           String
                Rose-Hulman user PIN.
    """
    # Navigate to Registeration page and enter PIN.
    driver.get("https://prod11gbss8.rose-hulman.edu/BanSS/bwskfreg.P_AltPin")
    click_tag_with_value(driver, "input", "Submit")
    driver.find_element_by_name("pin").send_keys(pin)
    click_tag_with_value(driver, "input", "Submit")


def auto_register(driver, data_map):
    """
        Arguments:
            :type driver        webdriver
                Selenium webdriver.
            :type data_map      Dictionary
                Data dictionary of input data.
    """
    # login into banner and navigate to registeration page
    login(driver, data_map[username_KEY], data_map[PASSWORD_KEY])
    navigate_to_registration_page(driver, data_map[PIN_KEY])

    # Take picture of the waiting page
    driver.save_screenshot("../img/waitPage.jpg")

    # Grab the start time if available.
    start_time = datetime.strptime(data_map[START_KEY][0], "%H:%M:%S-%m/%d/%Y")

    # Wait until specified start_time if provided.
    while True:
        # Prevent refreshing until start_time.
        currentTime = datetime.now()
        if currentTime < start_time:
            print(currentTime)
            continue
        break

    # Attempt to register.
    if not attempt_to_register(driver, data_map[CRN_KEY]):
        login(driver, data_map[username_KEY], data_map[PASSWORD_KEY])
        navigate_to_registration_page(driver, data_map[PIN_KEY])
        # Actively attempt to register.
        while True:
            # Enter CRN info and registerate
            if attempt_to_register(driver, data_map[CRN_KEY]):
                break

    # Take picture and close driver.
    driver.save_screenshot("../img/confirmation.jpg")
    return True


def main():
    """
        Driver Function.
    """
    # Get arguments and setup.
    arguments = parse_arguments()
    setup_directory()

    # Initialize Data.
    data_map = get_data(arguments.data)

    # Initialize Webdriver.
    driver = get_driver(arguments.browser.lower())

    # Try to Auto Register, retry if there is an exception
    while (True):
        try:
            auto_register(driver, data_map)
            break
        except NoSuchElementException as e:
            print("NoSuchElementException: " + str(e))
            pass

    # Close the driver if it is the PhantomJS driver.
    # Otherwise, leave the webdriver open for user manual overrides.
    if (isinstance(driver, webdriver.PhantomJS)):
        driver.close()
    else:
        print("Waiting For User to terminate (Ctrl-C)")
        while(True):
            pass

if __name__ == "__main__":
    main()
