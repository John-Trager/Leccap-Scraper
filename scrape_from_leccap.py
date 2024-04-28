"""
A Johnware Project
2023

Scrapes amazon S3 links that can then be accessed later (or downloaded using the download script)
"""

from loguru import logger
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from getpass import getpass
from utils import (
    setup_logger,
    print_welcome,
    save_list_to_csv,
    login_sso_umich,
    due_2fa_push,
)
import time
import datetime

if __name__ == "__main__":
    setup_logger()
    print_welcome()

    num_years_search = 6
    cur_year = datetime.date.today().year
    url = f"https://leccap.engin.umich.edu/leccap/{cur_year}"

    username = input("unique name: ")
    password = getpass("Password (never saved!): ")

    options = webdriver.ChromeOptions()
    options.add_argument("--enable-javascript")
    # NOTE: comment if you wish to run and see whats happening
    options.add_argument("--headless=new")

    # Initialize a Chrome WebDriver
    driver = webdriver.Chrome(options=options)
    # Open the webpage in the Chrome browser
    driver.get(url)

    wait = WebDriverWait(driver, 60)
    time.sleep(2)

    login_sso_umich(driver, username, password)
    logger.debug("Logging in to UMich account though single sign on...")

    due_2fa_push(driver, wait)

    # --- specific lecap scraping code ---

    # wait for the page to load
    class_links = []
    logger.debug("starting search for classes")
    for i in range(num_years_search):
        if "None of your courses from" in driver.page_source:
            logger.warning(f"no recordings for {cur_year-i}")
        else:
            class_link_elts = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a.list-group-item")
                )
            )

            for elt in class_link_elts:
                link = elt.get_attribute("href")

                if link not in class_links:
                    class_links.append(link)

        prev_li = driver.find_element(By.CSS_SELECTOR, "li.previous")
        prev_a = prev_li.find_element(By.CSS_SELECTOR, "a")
        prev_a.click()

        time.sleep(4)  # TODO: find a better way

    logger.debug(class_links)
    logger.debug("class search ended")

    # --- start scraping specific class pages ---

    video_srcs = []

    for link in class_links:
        # open up a tab to the class page
        driver.execute_script("window.open('{}', '_blank');".format(link))

        # Switch to the newly opened tab
        driver.switch_to.window(driver.window_handles[-1])

        # get the links to each recording
        elems = driver.find_elements(
            by=By.CSS_SELECTOR, value="a.btn.btn-primary.btn-sm"
        )
        href_links = []

        for elem in elems:
            l = elem.get_attribute("href")
            if l not in href_links:
                href_links.append(l)

        # now go through each recording and get the video link
        for record_link in href_links:
            driver.execute_script(
                "window.open('{}', '_blank');".format(record_link)
            )

            # Switch to the newly opened tab
            driver.switch_to.window(driver.window_handles[-1])

            # print(driver.page_source)

            # Wait until the <video> element is present
            wait.until(EC.presence_of_element_located((By.XPATH, "//video")))

            # Find the video element and extract the "src" attribute
            video = driver.find_elements(by=By.XPATH, value="//video")
            logger.debug(video)

            video_src = video[0].get_attribute("src")

            logger.debug(video_src)
            video_srcs.append(video_src)

            # Close the current tab
            driver.close()

            driver.switch_to.window(driver.window_handles[1])

        # Close the current tab
        driver.close()

        driver.switch_to.window(driver.window_handles[0])

    driver.quit()

    save_list_to_csv(video_srcs, "all_class_links.csv")

    logger.debug("Done scraping links.")
