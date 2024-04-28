"""
A class for the scraping of lecture videos.


"""

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from PyQt6.QtCore import QThread, pyqtSignal

from utils import (
    setup_logger,
    save_list_to_csv,
    login_sso_umich,
    due_2fa_push,
)
import time
import datetime


class Scraper(QThread):
    output = pyqtSignal(str)

    def __init__(
        self,
        username: str,
        password: str,
        num_years_search: int = 6,
        headless: bool = True,
    ) -> None:
        super().__init__()
        setup_logger()
        self.username = username
        self.password = password
        self.num_years_search = num_years_search
        self.headless = headless

    def gui_print(self, text: str) -> None:
        self.output.emit(text + "\n")

    def run(self) -> None:
        cur_year = datetime.date.today().year
        url = f"https://leccap.engin.umich.edu/leccap/{cur_year}"

        options = webdriver.ChromeOptions()
        options.add_argument("--enable-javascript")

        if self.headless:
            options.add_argument("--headless=new")

        # Initialize a Chrome WebDriver
        driver = webdriver.Chrome(options=options)
        # Open the webpage in the Chrome browser
        driver.get(url)

        wait = WebDriverWait(driver, 60)
        time.sleep(2)

        self.gui_print("Logging in to UMich account though single sign on...")
        login_sso_umich(driver, self.username, self.password)
        logger.debug("Logging in to UMich account though single sign on...")

        self.gui_print(
            "IMPORTANT: Check your phone for the DUO push!\n"
            + "This may take a few seconds..."
        )
        duo_res = due_2fa_push(driver, wait)
        if not duo_res:
            self.gui_print(
                "ERROR: DUO push not successful, please try again."
            )
            driver.quit()
            self.finished.emit()
            return

        # --- specific lecap scraping code ---

        self.gui_print("Logged in. Starting Scraping...")
        self.gui_print("This will take a few minutes.")
        # wait for the page to load
        class_links = []
        logger.debug("starting search for classes")
        for i in range(self.num_years_search):
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
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//video"))
                )

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
        logger.debug("Done scraping.")

        self.gui_print("Scraping is complete!")
        self.gui_print("Check all_class_links.csv urls for the video links!")
        # signal that the scraper is done to the GUI
        self.finished.emit()
