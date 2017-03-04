from flask import Flask, render_template, request
import genconhotels
import config
import threading

app = Flask(__name__)


def search(guests):
    genconhotels.logger.info("---START OF SEARCH AND SCRAPE.---")
    scraper = genconhotels.Scraper(config.url, config.slacktoken,
                                   'Test')  # 'Live', 'Test', 'Other'
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
            listing_count=len(scraper.listings),
            my_list=listfix)
    else:
        return 'No results'


@app.route('/hotels', methods=['POST'])
def hotels():
    genconhotels.logger.info('Flask: request received by slack command.')
    #channel = request.form.get('channel_name')
    username = request.form.get('user_name')
    text = request.form.get('text')
    genconhotels.logger.info('Slack: {} searching for {} rooms.'.format(username, text))

    try:
        if isinstance(int(text), int):
            if 1 <= int(text) <= 6:
                genconhotels.logger.info('GOOD')
                return 'Good'
            else:
                return 'Please enter a number between 1 and 6.'
    except ValueError as e:
        genconhotels.logger.info('Flask: error "{}" received.'.format(e))
        return 'Please enter a number between 1 and 6.'



    # if int(text) % 1 == 0 and int(text) <= 6:
    #     genconhotels.logger.info('Flask: Room search value in proper range.')
    #     return 'Getting hotel information...'
    # else:
    #     genconhotels.logger.info('Flask: Room search value not in range.')
    #     return 'Please enter a number between 1 and 6.'

    #genconhotels.logger.info("Slack: received".format(inbound_message))

    # if type(text) is int and int(text) <= 6:
    #     threads = []
    #     t = threading.Thread(target=search, args=(text, ))
    #     threads.append(t)
    #     t.start()
    #     genconhotels.logger.info('Flask: submiting to search.')

    #     return 'Getting hotel information...'
    # else:
    #     return 'Please enter a number between 1 and 6.'



if __name__ == '__main__':
    genconhotels.logger.info("Start of flask app.")
    app.run(debug=True, host="0.0.0.0", port=8080)
