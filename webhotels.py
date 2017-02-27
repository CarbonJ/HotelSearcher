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

    for base in scraper.listings:
        listfix.append(base)
        listing = ''
        for entry in base:
            genconhotels.logger.info(entry)
            listing += '<b>{}</b></br>'.format(entry)
        #     listing += '<i>{}</i>/br>'.format(entry)
        #     listing += 'Price: {}</br>'.format(entry)
        #     listing += 'Miles: {}</br>'.format(entry)
        # listfix.append(listing)
        # genconhotels.logger.info(listing)

        # for subitem in base:
        #     for hotel in subitem:
        #         templist.append(subitem)


        # message += '*{}*\n'.format(entry[0])
        # message += '_{}_\n'.format(entry[1])
        # message += 'Price: {}\n'.format(entry[2])
        # message += 'Miles: {}\n'.format(entry[3])

    return render_template(
        'template.html',
        listing_count=len(scraper.listings),
        my_list=listfix)


if __name__ == '__main__':
    genconhotels.logger.info("Start of flask app.")
    app.run(debug=True, host="0.0.0.0", port=8080)
