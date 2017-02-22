from selenium import webdriver
from bs4 import BeautifulSoup
import re
import logging
import time

# Basic variables
url = "https://aws.passkey.com/reg/32X3LVML-G0EF/"

# Logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler('scraper.log')
handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)


class Scraper(object):
    """docstring for scraper"""

    def __init__(self, url):
        self.url = url
        self.listings = []

    def scrap(self, rooms, guests):
        logger.info("Starting URL: {}".format(self.url))
        logger.info("Rooms: {}, Guests: {}".format(rooms, guests))

        # Selenium getting page
        driver = webdriver.PhantomJS()
        driver.set_window_size(1120, 550)
        driver.get(self.url)

        # Input calendar parameters
        try:
            # DEFECT: Not getting proper values submitted via selenium
            driver.find_element_by_css_selector("h5.accordion").click()
            driver.find_element_by_link_text("16").click()
            driver.find_element_by_css_selector(
                "#check-out > h5.accordion").click()
            driver.find_element_by_xpath(
                "(//a[contains(text(),'20')])[2]").click()
        except (TypeError, Exception) as e:
            raise e
            logger.info(e)

        # Input room parameters
        try:
            driver.find_element_by_id("spinner-room").click()
            driver.find_element_by_id("spinner-room").clear()
            driver.find_element_by_id("spinner-room").send_keys(rooms)
            driver.find_element_by_id("spinner-guest").click()
            driver.find_element_by_id("spinner-guest").clear()
            driver.find_element_by_id("spinner-guest").send_keys(guests)
        except Exception as e:
            raise e
            logger.info(e)

        try:
            driver.find_element_by_link_text("FIND").click()
            time.sleep(5)  # sleep 5 seconds to allow transaction
        except driver.NoSuchElementException as e:
            driver.save_screenshot('screenshot.png')
            raise e
            logger.info(e)

        if driver.page_source:
            self.page = driver.page_source

            if "Please select one" in self.page:
                logger.info("Found hotels in search")
                soup = BeautifulSoup(self.page, "lxml")
                hclass = soup.find_all("div", {"class": "h-content"})

                for tag1 in hclass:
                    templist = []
                    htag = tag1.find_all("p", {"class": "name"})
                    atag = tag1.find_all("p", {"class": "address"})
                    ptag = tag1.find_all("div", {"class": "price"})
                    dtag = tag1.find_all("", {"class": "mi"})
                    for hotel, addy, price, mi in zip(htag, atag, ptag, dtag):
                        temp_price = re.findall('[0-9]{1,10}',
                                                price.get_text())
                        temp_mi = re.findall('[0-9]{1,10}', mi.get_text())
                        templist.append(hotel.contents[0])
                        templist.append(
                            addy.get_text().strip().replace(u'\xa0', u' '))
                        templist.append('.'.join(temp_price))
                        templist.append('.'.join(temp_mi))
                        self.listings.append(templist)

                with open("results.html", "w") as temp:
                    temp.write(soup.prettify())
                    driver.save_screenshot('screenshot.png')

            elif "TERMS OF SERVICE" in self.page:
                logger.info("Still on main page, nothing found or failed.")
                driver.save_screenshot('unknown_screenshot.png')
                with open("temp.html", "w") as temp:
                    temp.write(driver.page_source)
            elif "Sorry..." in self.page:
                logger.info("Website or navigation failed.")
            else:
                logger.info(
                    "Unknown website information. Getting temp.html and screenshot"
                )
                driver.save_screenshot('unknown_screenshot.png')
                with open("temp.html", "w") as temp:
                    temp.write(driver.page_source)

            driver.quit()


if __name__ == "__main__":
    logger.info("Start of scraper.")
    scraper = Scraper(url)
    scraper.scrap(1, 3)  # # of rooms, # of guests
    logger.info(scraper.listings)
    logger.info("End of scraper.")
