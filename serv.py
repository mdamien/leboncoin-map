import requests, json, os, functools
from bs4 import BeautifulSoup

from geopy.geocoders import Nominatim
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
        location = geolocator.geocode(place)
        if location:
            return {
                'lat': location.latitude,
                'lng': location.longitude,
            }


@cache.memoize(1000)
def fetch_items(url):
    print('fetch items', url)
    all_found = []

    page = 1
    while True:
        print(url)
        resp = requests.get(url + '&o=' + str(page))
        print(resp)
        soup = BeautifulSoup(resp.text, 'lxml')

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
            data['coords'] = geolocate(place)
            price = item.find(class_='item_price')
            if price:
                data['price'] = price.text.replace('\xa0', ' ').strip()
            if item.find(class_='item_absolute'):
                data['date'] = item.find(class_='item_absolute').text.strip()
            all_found.append(data)
        next = soup.find(id='last')

        break

        if next:
            page += 1
        else:
            break

    return all_found


@app.route("/items")
def fetch():
    items = fetch_items(flask.request.args.get('url'))
    return flask.jsonify(*items)


@app.route("/")
def index():
    return app.send_static_file('hello.html')


@app.route('/main.js')
def send_js():
    return app.send_static_file('hello.js')


if __name__ == "__main__":
    app.run(debug=debug)
