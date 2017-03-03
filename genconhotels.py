# Third Party
from selenium import webdriver
from bs4 import BeautifulSoup
from slackclient import SlackClient
# Built-in
import re
import logging
import time
# Custom
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
            logger.info("Parameters: results to be sent to '{}'.".format(self.channel))
        elif env == 'Test':
            self.channel = config.testchannel
            logger.info("Parameters: results to be sent to '{}'.".format(self.channel))
        else:
            self.slack_send = False
            logger.info("Parameters: results not sent to Slack ")

    def send_message(self, channel_id, message):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username='Gencon Hotels',
            icon_emoji=':hotel:')

    def scrap(self, rooms, guests):
        logger.info("Parameters: starting URL: {}".format(self.url))
        logger.info(
            "Parameters:  Room# {}, Guest# {}".format(rooms, guests))

        # Selenium getting page
        driver = webdriver.PhantomJS()
        # driver = webdriver.Chrome('/Users/justin/Documents/Projects/GenconHotel/chromedriver')  # Here for troubleshooting only
        driver.set_window_size(1120, 550)
        driver.get(self.url)

        # Input calendar parameters
        try:
            logger.info('Search: locating calendar selections.')
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
            # DEFECT: Room # gets wiped out when doing the guest portion
            # for not good reason.
            # rselect = driver.find_element_by_id("spinner-room")

            # if rselect:
            #     logger.info('Located room web field.')
            #     driver.find_element_by_id("spinner-room").click()
            #     driver.find_element_by_id("spinner-room").clear()
            #     driver.find_element_by_id("spinner-room").send_keys('\b')
            #     logger.info("Sending room value {}".format(rooms))
            #     driver.find_element_by_id("spinner-room").send_keys(rooms)

            gselect = driver.find_element_by_id("spinner-guest")

            if gselect:
                logger.info('Search: locating guest web field.')
                driver.find_element_by_id("spinner-guest").click()
                driver.find_element_by_id("spinner-guest").clear()
                driver.find_element_by_id("spinner-guest").send_keys('\b')
                logger.info("Search: sending guest value {}".format(guests))
                driver.find_element_by_id("spinner-guest").send_keys(guests)
                #logger.info('Search: guest value on form: {}'.format(gselect.get_attribute('aria-valuenow')))

            time.sleep(1)
        except (Exception) as e:
            raise e
            logger.info(e)

        try:
            logger.info('Search: submitting webform')
            driver.find_element_by_link_text("FIND").click()
            time.sleep(3)  # sleep 5 seconds to allow transaction
        except driver.NoSuchElementException as e:
            driver.save_screenshot('screenshot.png')
            raise e
            logger.info(e)

        if driver.page_source:
            logger.info("Scrape: web page found and now being scraped.")
            self.page = driver.page_source

            if "Please select one" in self.page:
                logger.info("Scrape: hotels found.")
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

                with open("Scrape.html", "w") as temp:
                    temp.write(soup.prettify())
                    driver.save_screenshot('screenshot.png')

            elif "TERMS OF SERVICE" in self.page:
                logger.info("Scrape: main page detected, something failed.")
                driver.save_screenshot('unknown_screenshot.png')
                with open("temp.html", "w") as temp:
                    temp.write(driver.page_source)
            elif "Sorry..." in self.page:
                logger.info("Scrape: error page detected, something failed")
            elif "No hotel matched your search criteria" in self.page:
                logger.info("Scrape: 0 hotels found with that criteria.")
                # DEFECT NEEDS OUTPUT
            else:
                logger.info("Scrape: unknown website information. Getting "
                            "temp.html and screenshot")
                driver.save_screenshot('unknown_screenshot.png')
                with open("temp.html", "w") as temp:
                    temp.write(driver.page_source)

            driver.quit()

            if self.slack_send:
                if self.listings:
                    logger.info(
                        "Slack: formating {} listings.".format(len(self.listings)))
                    message = "\nSearch Parameters: " \
                              "Rooms - {}, Guests - {} "\
                              "\n".format(rooms, guests)
                    for entry in self.listings:
                        logger.info(entry)
                        message += '*{}*\n'.format(entry[0])
                        message += '_{}_\n'.format(entry[1])
                        message += 'Price: {}\n'.format(entry[2])
                        message += 'Miles: {}\n'.format(entry[3])
                        self.send_message(self.channel, message)
                        message = ""
                logger.info("Slack: message sent to {}".format(self.channel))
            else:
                # DEPRECATED
                logger.info("SOMETHING HERE")
                if self.listings:
                    logger.info(
                        "Found {} listings.".format(len(self.listings)))


if __name__ == "__main__":
    logger.info("---START OF SEARCH AND SCRAPE.---")
    scraper = Scraper(url, slacktoken, 'Live')  # 'Live', 'Test', 'Other'
    scraper.scrap(1, 4)  # # of rooms, # of guests
    logger.info("---END OF SEARCH AND SCRAPE.---")
