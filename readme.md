# HotelSearcher

Something I've whipped together to help get information for my Slack group to find housing for some convention.  It is not pretty or even fully functional, but it is 'something'.

The config.example.py would need to be renamed (config.py) updated with the proper tokens and slack channels to be used.  It was written with Python 3.6 (though 3.x will work).  It also requires Selenium, BeautifulSoup 4, and slackclient.

The script will produce a pile of files while running:
* two driver logs
* a results.html
* a screenshot of the site being scrapped
* a running process log
* and other files if there's a failure

Right now the biggest issue is Selenium.  When trying to set the room number and guest number, it is defaulting to 1 (vs the numbers I want).  My choices work fine in the Selenium IDE, but don't work when run via my script.

TBD
- [ ] Fix room/guest input in selenium
- [ ] Make addresses more 'readable'
- [ ] Maybe: convert to stand-alone Flas app (vs running via cron) to have page displaying most recent finds
