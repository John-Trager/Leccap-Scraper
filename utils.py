import time
import sys

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

DEBUG = True


def setup_logger():
    # Define log level based on debug mode
    logger.remove()
    if DEBUG:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")


def print_welcome():
    print(
        "\033[1mWelcome to the UMich lecture scraper!\n"
        "This program will scrape the video links from a CoE Lecture recordings page\n"
        "and save them to a csv file\n"
        "(process takes ~10-20 minutes depending on number of classes and internet speed).\n"
        "You will need to enter your UMich login credentials and DUO 2FA.\n"
        "This program will never save your password.\n"
        "Please enter your credentials below.\n\033[0m"
    )


def save_list_to_csv(list_of_values, csv_file_path):
    """Saves a list of values to a CSV file, with one entry per row.

    Args:
      list_of_values: A list of values to save to the CSV file.
      csv_file_path: The path to the CSV file to save the values to.
    """

    # Import the csv module.
    import csv

    # Open the CSV file for writing.
    with open(csv_file_path, "a+", newline="") as csvfile:
        # Create a CSV writer object.
        writer = csv.writer(csvfile)

        # Write the list of values to the CSV file, one entry per row.
        for value in list_of_values:
            writer.writerow([value])


def login_sso_umich(driver, username: str, password: str):
    """
    logins into umich account using single sign on.

    Returns if successfully logged in or not
    """
    # Find the username and password input fields and the login button
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.ID, "loginSubmit")

    # Fill in the username and password fields
    username_field.send_keys(username)
    password_field.send_keys(password)
    # get rid of username and password data (for safety)
    username = None
    password = None

    # Click the login button
    login_button.click()

    # TODO: may need to sleep here

    # Check if login failed
    # see if word "incorrect" is on page anywhere
    try:
        res = driver.find_element(
            By.XPATH, "//*[contains(text(), 'incorrect')]"
        )
        if res:
            logger.error(
                "Failed to login to UMich account, please check your username and password."
            )

            return False
    except Exception as _:
        logger.debug(
            "Did not find word 'incorrect' on page - login must have succeeded"
        )

    return True


def due_2fa_push(driver, wait) -> bool:
    """
    gets the push notification from DUO 2FA to your phone.

    Returns if successfully pressed the DUO button or not
    """
    wait.until(EC.presence_of_element_located((By.ID, "auth-view-wrapper")))
    logger.critical("Requesting DUO push auth, CHECK YOUR PHONE!")
    # case where they ask if this is a public computer
    # check if button id="trust-browser-button" exists
    # check for up to 10 seconds
    time.sleep(8)
    pressed_btn = False
    for _ in range(10):
        try:
            trust_button = driver.find_element(By.ID, "trust-browser-button")
            trust_button.click()
            pressed_btn = True
            break
        except Exception as e:
            logger.warning("trust button not found... trying again")
        time.sleep(2)

    if not pressed_btn:
        logger.error(
            "Was unable to find the DUO trust browser button, please file an issue on github",
            "or possible try to approve the duo notification on your phone faster.",
        )

    return pressed_btn
