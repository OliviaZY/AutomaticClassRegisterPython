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
from datetime import datetime
import os
import sys
import time

BANNER_WEB_URL = "https://prod11gbss8.rose-hulman.edu/BanSS/twbkwbis.P_WWWLogin"
dataMapUserName_Key = "username"
dataMapPassword_Key = "password"
dataMapPin_Key = "pin"
dataMapCRN_Key = "crn"
attempt_time_key = "attempt_start"

def main():
    # Ensure a data file path is given.
    if (len(sys.argv) < 2):
        print("AutoRegister.py <dataFile> <opt:browser>")
        return
    setup_directory()

    # Initialize Data.
    dataMap = getData(sys.argv[1])
    # Initialize Webdriver.
    driver = getDriver(sys.argv[2].lower())

    # try to auto registerate, retry if there is an exception
    while True:
        try:
            AutoRegister(driver, dataMap)
            break
        except NoSuchElementException as e:
            print("NoSuchElementException happened :" + str(e))
            pass

    # quiting the program
    if (isinstance(driver, webdriver.PhantomJS)):
        driver.close()
    else:
        print("Waiting For User to terminate (Ctrl-C)")
        while(True):
            pass

def AutoRegister(driver, dataMap):
    # login into banner and navigate to registeration page
    login(driver, dataMap[dataMapUserName_Key], dataMap[dataMapPassword_Key])
    enterRegisterationPage(driver, dataMap[dataMapPin_Key])

    # Take picture of the waiting page
    driver.save_screenshot("../img/waitPage.jpg")

    startTime = datetime.strptime(dataMap[attempt_time_key][0], "%H:%M:%S-%m/%d/%Y")

    # Refresh page until crnFields are found.
    while True:
        # Prevent refreshing until two minutes before opening time
        currentTime = datetime.now()
        if currentTime < startTime:
            print(currentTime)
            continue
        break

    # attempt to registerate
    if not attemptToRegisterate(driver, dataMap[dataMapCRN_Key]):
        login(driver, dataMap[dataMapUserName_Key], dataMap[dataMapPassword_Key])
        enterRegisterationPage(driver, dataMap[dataMapPin_Key])
        # active trying
        while True:
            # Enter CRN info and registerate
            if attemptToRegisterate(driver, dataMap[dataMapCRN_Key]):
                break;

    # Take picture and close driver.
    driver.save_screenshot("../img/confirmation.jpg")
    return True

def getDriver(browser):
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


def login(driver, userName, password):
    # Navigate to BannerWeb.
    driver.get(BANNER_WEB_URL)

    # Login to Bannerweb.
    driver.find_element_by_name("sid").send_keys(userName)
    driver.find_element_by_name("PIN").send_keys(password)
    clickTagWithValue(driver, "input", "Login")


def enterRegisterationPage(driver, pin):
    # Navigate to Registeration page and enter PIN.
    driver.get("https://prod11gbss8.rose-hulman.edu/BanSS/bwskfreg.P_AltPin")
    clickTagWithValue(driver, "input", "Submit")
    driver.find_element_by_name("pin").send_keys(pin)
    clickTagWithValue(driver, "input", "Submit")


def attemptToRegisterate(driver, crnInput):
    """
        Gets the CRN text box and fills it in with crn numbers.

        Arguments:
            :type driver :    webdriver
                Selenium Webdriver.
            :type crnInput :  list
                List of CRN numbers.

        Returns a list of CRN text box.
        Raises Selenium.NoSuchElementException
    """
    try:
        for identifier in range(1, len(crnInput)+1):
            element = driver.find_element_by_id("crn_id" + str(identifier))
            element.send_keys(crnInput[identifier - 1])
            identifier += 1
        clickTagWithValue(driver, "input", "Submit Changes")
    except(NoSuchElementException):
        print("Page Not Ready.")
        driver.refresh()
        if (isinstance(driver, webdriver.Firefox)):
            Alert(driver).accept()
        return False
    driver.find_element_by_id("crn_id1")
    return True

def getData(dataFile):
    """
        Pulls user data from data.txt.

        Returns a dictionary of relevant data.
    """
    dataFile = open(dataFile, "r")
    dataMap = {}

    for line in dataFile:
        lineList = line.split()
        dataMap[lineList[0]] = lineList[1:len(lineList)]

    dataFile.close()

    return dataMap


def clickTagWithValue(driver, tagName, value):
    """
       Attempts to click on a button with a specific tag name and value.
       It will click the first button with specified value.

       Arguments:
           :type driver :     webdriver
               Selenium Webdriver.
           :type tagName :    str
               Specified HTML tag name.
           :type value :      str
               Specified HTML value related to tag name.

        Returns nothing.
    """
    inputList = driver.find_elements_by_tag_name(tagName)

    for element in inputList:
        if (element.get_attribute("value") == value):
            element.click()
            break


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
                Rose-Hulman password.
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
