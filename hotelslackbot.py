from flask import Flask, render_template
import genconhotels
import config
import threading


app = Flask(__name__)


# @app.route("/")
def search(guests):
    genconhotels.logger.info("---START OF SEARCH AND SCRAPE.---")
    scraper = genconhotels.Scraper(
        config.url, config.slacktoken, 'Test')  # 'Live', 'Test', 'Other'
    scraper.scrap(1, guests)  # # of rooms, # of guests
    genconhotels.logger.info("---END OF SEARCH AND SCRAPE.---")

    listfix = []

    for base in scraper.listings:
        listfix.append(base)
        listing = ''
        for entry in base:
            listing += '<b>{}</b></br>'.format(entry)

    if listfix:
        return render_template(
            'template.html',
            listing_count=len(scraper.listings), my_list=listfix)
    else:
        return 'No results'


@app.route('/hotels', methods=['POST'])
def hotels():
    genconhotels.logger.info('Flask: request received by slack command.')

    threads = []
    t = threading.Thread(target=search, args=(4,))
    threads.append(t)
    t.start()
    genconhotels.logger.info('Flask: submiting to search.')

    return 'Getting hotel information...'


if __name__ == '__main__':
    genconhotels.logger.info("Start of flask app.")
    app.run(debug=True, host="0.0.0.0", port=8080)
