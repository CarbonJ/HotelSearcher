from selenium import webdriver
from bs4 import BeautifulSoup
import re
import logging
import time
from slackclient import SlackClient
import config

# Basic variables out of config.py
url = config.url
slacktoken = config.slacktoken

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
    """Performs scraping and Slack notifications"""
    def __init__(self, url, slacktoken, env):
        self.url = url
        self.listings = []
        self.token = slacktoken
        self.slack_client = SlackClient(self.token)
        self.slack_send = True
        self.channel = ''

        if env == 'Live':
            self.channel = config.livechannel
            logger.info("Results to be sent to '{}'.".format(self.channel))
        elif env == 'Test':
            self.channel = config.testchannel
            logger.info("Results to be sent to '{}'.".format(self.channel))
        else:
            self.slack_send = False
            logger.info("Results not sent to Slack ")

    def send_message(self, channel_id, message):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username='Gencon Hotels',
            icon_emoji=':hotel:')

    def scrap(self, rooms, guests):
        logger.info("Starting URL: {}".format(self.url))
        logger.info(
            "Searching for - Rooms: {}, Guests: {}".format(rooms, guests))

        # Selenium getting page
        driver = webdriver.PhantomJS()
        driver.set_window_size(1120, 550)
        driver.get(self.url)

        # Input calendar parameters
        try:
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
        # DEFECT: Not getting proper values submitted via selenium
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
                logger.info("Search complete.")
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
                logger.info("Unknown website information. Getting "
                            "temp.html and screenshot")
                driver.save_screenshot('unknown_screenshot.png')
                with open("temp.html", "w") as temp:
                    temp.write(driver.page_source)

            driver.quit()

            if self.slack_send:
                if self.listings:
                    logger.info(
                        "Found {} listings.".format(len(self.listings)))
                    message = "\nSearch Parameters: " \
                              "Rooms - {}, Guests - {} "\
                              "_(Currently wrong, is 1 & 1)_ " \
                              "\n".format(rooms, guests)
                    for entry in self.listings:
                        logger.info(entry)
                        message += '*{}*\n'.format(entry[0])
                        message += '_{}_\n'.format(entry[1])
                        message += 'Price: {}\n'.format(entry[2])
                        message += 'Miles: {}\n'.format(entry[3])
                        self.send_message(self.channel, message)
                        print(self.channel)
                        message = ""
                logger.info("Slack message sent to {}".format(self.channel))
            else:
                logger.info("SOMETHING HERE")
                if self.listings:
                    logger.info(
                        "Found {} listings.".format(len(self.listings)))


if __name__ == "__main__":
    logger.info("Start of scraper.")
    scraper = Scraper(url, slacktoken, 'Test')  # 'Live', 'Test', 'Other'
    scraper.scrap(1, 3)  # # of rooms, # of guests
    logger.info("End of scraper.")
