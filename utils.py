from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def save_list_to_csv(list_of_values, csv_file_path):
    """Saves a list of values to a CSV file, with one entry per row.

    Args:
      list_of_values: A list of values to save to the CSV file.
      csv_file_path: The path to the CSV file to save the values to.
    """

    # Import the csv module.
    import csv

    # Open the CSV file for writing.
    with open(csv_file_path, "w", newline="") as csvfile:
        # Create a CSV writer object.
        writer = csv.writer(csvfile)

        # Write the list of values to the CSV file, one entry per row.
        for value in list_of_values:
            writer.writerow([value])


def login_sso_umich(driver, username: str, password: str):
    """
    logins into umich account using single sign on
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


def due_2fa_push(driver, wait):
    """
    gets the push notification from DUO 2FA to your phone
    """
    wait.until(EC.presence_of_element_located((By.ID, "duo_iframe")))
    # Click the "Send Me a Push" button
    driver.switch_to.frame("duo_iframe")
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button.auth-button.positive"))
    )
    auth_button = driver.find_element(By.CSS_SELECTOR, "button.auth-button.positive")
    auth_button.click()
