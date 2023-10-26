"""
A Johnware Project
2023

Scrapes amazon S3 links that can then be accessed later (or downloaded using the download script)
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from getpass import getpass
from utils import save_list_to_csv, login_sso_umich, due_2fa_push
import time
import datetime

print(
    "Welcome to the UMich lecture scraper!\n"
    "This program will scrape the video links from a CoE Lecture recordings page\n"
    "and save them to a csv file\n"
    "(process takes ~10-20 minutes depending on number of classes and internet speed).\n"
    "You will need to enter your UMich login credentials and DUO 2FA.\n"
    "This program will never save your password.\n"
    "Please enter your credentials below.\n"
)

num_years_search = 6

cur_year = datetime.date.today().year

url = f"https://leccap.engin.umich.edu/leccap/{cur_year}"
username = input("unique name: ")
password = getpass("Password (never saved!): ")

options = webdriver.ChromeOptions()
options.add_argument("--enable-javascript")
# options.add_argument("--headless=new") # TODO: uncomment if you wish to run headless

# Initialize a Chrome WebDriver
driver = webdriver.Chrome(options=options)
# Open the webpage in the Chrome browser
driver.get(url)

wait = WebDriverWait(driver, 60)
time.sleep(2)

login_sso_umich(driver, username, password)
print("Logging in to UMich account though single sign on...")

due_2fa_push(driver, wait)
print("Requesting DUO 2 auth, CHECK YOUR PHONE!")

time.sleep(15)  # TODO: find a better way

# --- specific lecap scraping code ---

# wait for the page to load
class_links = []
print("starting search for classes")
for i in range(num_years_search):
    if "None of your courses from" in driver.page_source:
        print(f"no recordings for {cur_year-i}")
    else:
        class_link_elts = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.list-group-item"))
        )

        for elt in class_link_elts:
            link = elt.get_attribute("href")

            if link not in class_links:
                class_links.append(link)

    prev_li = driver.find_element(By.CSS_SELECTOR, "li.previous")
    prev_a = prev_li.find_element(By.CSS_SELECTOR, "a")
    prev_a.click()

    time.sleep(4)  # TODO: find a better way


print(class_links)
print("class search ended")

# --- start scraping specific class pages ---

video_srcs = []

for link in class_links:
    # open up a tab to the class page
    driver.execute_script("window.open('{}', '_blank');".format(link))

    # Switch to the newly opened tab
    driver.switch_to.window(driver.window_handles[-1])

    # get the links to each recording
    elems = driver.find_elements(by=By.CSS_SELECTOR, value="a.btn.btn-primary.btn-sm")
    href_links = []

    for elem in elems:
        l = elem.get_attribute("href")
        if l not in href_links:
            href_links.append(l)

    # TODO: print that we downloading videos for X class

    # now go through each recording and get the video link
    for record_link in href_links:
        driver.execute_script("window.open('{}', '_blank');".format(record_link))

        # Switch to the newly opened tab
        driver.switch_to.window(driver.window_handles[-1])

        # print(driver.page_source)

        # Wait until the <video> element is present
        wait.until(EC.presence_of_element_located((By.XPATH, "//video")))

        # Find the video element and extract the "src" attribute
        video = driver.find_elements(by=By.XPATH, value="//video")
        print(video)

        video_src = video[0].get_attribute("src")

        print(video_src)
        video_srcs.append(video_src)

        # Close the current tab
        driver.close()

        driver.switch_to.window(driver.window_handles[1])

    # Close the current tab
    driver.close()

    driver.switch_to.window(driver.window_handles[0])

driver.quit()

save_list_to_csv(video_srcs, "all_class_links.csv")

print("Done scraping links.")
