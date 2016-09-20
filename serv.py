import requests, json, os, functools
from bs4 import BeautifulSoup
from furl import furl

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
geolocator = Nominatim()

debug = 'gunicorn' not in os.environ.get('SERVER_SOFTWARE', '')

import flask
from flask_cache import Cache
app = flask.Flask(__name__)

config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache'
}
cache = Cache(app, config=config)

MAX_PAGES = 5

@cache.memoize(1000)
def geolocate(place):
    if place:
        print('geolocate', place)
        try:
            location = geolocator.geocode(place)
            if location:
                return {
                    'lat': location.latitude,
                    'lng': location.longitude,
                }
        except GeocoderTimedOut:
            print('geocoder timeout')
    return {}


@cache.memoize(1000)
def fetch_items(url, page):
    assert url.startswith('https://www.leboncoin.fr/')
    url_with_page = furl(url).add({'o': str(page)})
    print('fetch items', url_with_page)

    items = []
    resp = requests.get(url_with_page)
    soup = BeautifulSoup(resp.text, 'lxml')

    if soup.find(id='last') and 'href' in soup.find(id='last').attrs:
        pages = int(furl(soup.find(id='last').attrs['href']).args['o'])
    else:
        pages = page
    pages = min(pages, MAX_PAGES)
    has_next = page < pages

    for item in soup.select('.list_item'):
        data = {}
        data['link'] = item.attrs['href']
        data['title'] = item.select('.item_title')[0].text.strip()
        img = item.select('.item_imagePic span')
        if img:
            data['thumbnail'] = img[0].attrs['data-imgsrc']
        if item.select('.item_supp'):
            data['category'] = item.select('.item_supp')[0].text \
                                    .replace('(pro)', '').strip()
            place = item.select('.item_supp')[1].text
            place = ' '.join(x.strip() for x in place.strip().split(' ') if x.strip())
            data['place'] = place
        price = item.find(class_='item_price')
        if price:
            data['price'] = price.text.replace('\xa0', ' ').strip()
        if item.find(class_='item_absolute'):
            data['date'] = item.find(class_='item_absolute').text.strip()
        items.append(data)

    return items, has_next, pages


@app.route("/locate")
def geocoder():
    return flask.jsonify(**geolocate(flask.request.args.get('q')))


@app.route("/items")
def fetch():
    items, has_next, pages = fetch_items(flask.request.args.get('url'), int(flask.request.args.get('page', '1')))
    resp = {
        'data': items,
        'has_next': has_next,
        'pages': pages,
    }
    return flask.jsonify(**resp)


@app.route("/")
def index():
    if flask.request.args.get('url'):
        return app.send_static_file('hello.html')
    else:
        return """<html style='background-color: #333; color: #eee'><br/><br/><br/><center>
                <h2 style='font-family:sans'>Ce site s'utilise avec l'extension 'Carte - leboncoin.fr'</h2>
            </center></html>"""


@app.route('/main.js')
def send_js():
    return app.send_static_file('hello.js')


@app.route('/favicon.ico')
def send_favicon():
    return app.send_static_file('favicon.ico')


if __name__ == "__main__":
    app.run(debug=debug)
