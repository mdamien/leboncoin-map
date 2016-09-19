import requests, json, os, functools
from bs4 import BeautifulSoup

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
geolocator = Nominatim()

if 'DYNO' in os.environ:
    debug = False
else:
    debug = True

import flask
from flask_cache import Cache
app = flask.Flask(__name__)

config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache'
}
if not debug:
    config = {
        'CACHE_TYPE:': 'simple',
    }
cache = Cache(app, config=config)


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
    url_with_page = url + '&o=' + str(page)
    print('fetch items', url_with_page)

    items = []
    proxies = None
    if debug:
        proxies = {
            'https': '37.235.82.186:80',
        }
    resp = requests.get(url_with_page, proxies=proxies)
    soup = BeautifulSoup(resp.text, 'lxml')

    if soup.find(id='last') and 'href' in soup.find(id='last').attrs:
        pages = int(soup.find(id='last').attrs['href'].split('o=')[-1].split('&')[0])
    else:
        pages = page
    has_next = soup.find(id='next') is not None and 'href' in soup.find(id='next').attrs

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
        return """<html style='background-color: #333; color: #eee'><br/><br/><br/>a<center>
                <h2 style='font-family:sans'>Ce site s'utilise avec l'extension 'Carte - Leboncoin'</h2>
            </center></html>"""


@app.route('/main.js')
def send_js():
    return app.send_static_file('hello.js')


if __name__ == "__main__":
    app.run(debug=debug)
