from flask import Flask, render_template
import genconhotels
import config

app = Flask(__name__)


@app.route("/")
def template_test():
    genconhotels.logger.info("Start of scraper.")
    scraper = genconhotels.Scraper(
        config.url, config.slacktoken, 'Test')  # 'Live', 'Test', 'Other'
    scraper.scrap(1, 3)  # # of rooms, # of guests
    genconhotels.logger.info("End of scraper.")

    listfix = []

    for item in scraper.listings:
        templist = []
        for subitem in item:
            templist.append(subitem)
        listfix.append(templist)

        # message += '*{}*\n'.format(entry[0])
        # message += '_{}_\n'.format(entry[1])
        # message += 'Price: {}\n'.format(entry[2])
        # message += 'Miles: {}\n'.format(entry[3])

    return render_template(
        'template.html',
        listing_count=len(scraper.listings),
        my_list=[listfix])


if __name__ == '__main__':
    genconhotels.logger.info("Start of flask app.")
    app.run(debug=True, host="0.0.0.0", port=8080)
