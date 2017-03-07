# HotelSearcher

Something I've written together to help get housing information for some friends to find housing for some convention.  It started as a small script and added as a small module and Slackbot.

The config.example.py would need to be renamed (config.py) updated with the proper tokens and slack channels to be used.  It was written with Python 3.6 (though 3.x will work).  It also requires Selenium, BeautifulSoup 4, and slackclient.

The script will produce a pile of files while running:
* two driver logs
* a results.html
* a screenshot of the site being scrapped
* a running process log
* and other files if there's a failure

As of now, it's feature complete.  I may change more based on defect found or some proper refactoring, but otherwise it is complete.
- [x] Fix room/guest input in selenium
- [x] Make addresses more 'readable'
- [x] Maybe: convert to stand-alone Flask app (vs running via cron) to have page displaying most recent finds
