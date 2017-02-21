from selenium import webdriver
from bs4 import BeautifulSoup
import re
from decimal import Decimal

url = "https://aws.passkey.com/reg/32X3LVML-G0EF/"

driver = webdriver.PhantomJS()
driver.set_window_size(1120, 550)
driver.get(url)

# First, navigate date range

try:
    driver.find_element_by_css_selector("h5.accordion").click()
    driver.find_element_by_link_text("16").click()
    driver.find_element_by_css_selector("#check-out > h5.accordion").click()
    driver.find_element_by_xpath("(//a[contains(text(),'20')])[2]").click()
except Exception as e:
    raise e
    print(e)

try:
    driver.find_element_by_id("spinner-room").clear()
    driver.find_element_by_id("spinner-room").click()
    driver.find_element_by_id("spinner-room").send_keys("2")

    driver.find_element_by_id("spinner-guest").clear()
    driver.find_element_by_id("spinner-guest").send_keys("4")
except Exception as e:
    raise e
    print(e)

try:
    driver.find_element_by_link_text("FIND").click()
    #driver.find_element_by_css_selector("label.event-tooltip-filename.devtools-monospace").click()
    delay = 5  # seconds
except driver.NoSuchElementException as e:
    driver.save_screenshot('screenshot.png')
    raise e
    print(e)

# print(driver.current_url)

html = driver.page_source

if "Please select one" in html:
    print('Getting Results')
    totallist = []
    soup = BeautifulSoup(driver.page_source, "lxml")

    hclass = soup.find_all("div", {"class": "h-content"})

    for tag1 in hclass:
        htag = tag1.find_all("p", {"class": "name"})
        atag = tag1.find_all("p", {"class": "address"})
        ptag = tag1.find_all("div", {"class": "price"})
        # dtag = tag1.find_all("", {"class": "mi"})
        for hotel, addy, price, in zip(htag, atag, ptag):
            print(hotel.contents[0])
            print(addy.get_text().strip())
            # print(price.get_text().strip())
            x = re.findall('[0-9]{1,10}', price.get_text())
            print(int(x[0]))

            # re.findall('£{1}[,0-9]{1,10}','The little £250,000 brown fox jumped over the lazy dog')

            # print(address.contents[0])
            # print(price)
        # print(atag)
        # print(ptag)
        # print(dtag)

    with open("results.html", "w") as temp:
        temp.write(soup.prettify())
        driver.save_screenshot('screenshot.png')


elif "TERMS OF SERVICE" in html:
    print('On main page')
elif "Sorry..." in html:
    print('Bad page')
else:
    print("Don't know")
    with open("temp.html", "w") as temp:
        temp.write(driver.page_source)

driver.quit()

