'use strict';

function getQueryStrings() { 
  var assoc  = {};
  var decode = function (s) { return decodeURIComponent(s.replace(/\+/g, " ")); };
  var queryString = location.search.substring(1); 
  var keyValues = queryString.split('&'); 

  for(var i in keyValues) { 
    var key = keyValues[i].split('=');
    if (key.length > 1) {
      assoc[decode(key[0])] = decode(key[1]);
    }
  } 

  return assoc; 
}

var GEOCODE_URL = '/locate';

var qs = getQueryStrings();

L.mapbox.accessToken = 'pk.eyJ1IjoicG93ZXJzaG9wcyIsImEiOiJhYUdRR0t3In0.oTz8RJqED2YEcDRfJYNAOQ';
var map = L.mapbox.map('map', 'powershops.1ebg8klg', {
  maxZoom: 12,
});

var markers = new L.MarkerClusterGroup({
  animate: false,
  spiderfyDistanceMultiplier: 2.5,
});

map.addLayer(markers);

$('#msg h1').html('Chargement des annonces... ');

var all_items = [];

function add_to_map(data) {
  data.forEach(function(a) {
    if (a.place) {
      $.getJSON(GEOCODE_URL, {
        q: a.place,
      }).then(function(coords) {
        if (coords && coords.lat) {
          var marker = new L.Marker([
            coords.lat,
            coords.lng,
          ], {
            icon: new L.DivIcon({
              className: 'ad-icon',
              html: '<h2>' + a.title + (a.price ? (' - ' + a.price) : '') + '</h2>'
            })
          });
          marker.on('click', function(e) {
            window.open(a.link, '_blank');
          });
          markers.addLayer(marker);
          map.fitBounds(markers.getBounds());
        } else {
          console.log('ignoring', a.title, a.link)
        }
      });
    }
  });
};

function get_page(page) {
  $.getJSON('/items', {url: qs['url'], page: page}).then(function(response) {
    add_to_map(response.data)

    $('#msg').show();

    if (response.has_next) {
      $('#msg h1').html('Chargement des annonces... ' + (page + 1) + '/' + response.pages);
      get_page(page + 1);
    } else {
      $('#msg').hide();
    }
  }).catch(err => {
    $('#msg').hide();
    $('#msg h1').html('Oops, une erreur est arrivée :(' + 
      (err.status ? ('<br/><br/>' + err.status + ' - ' + err.statusText) : ''));
    $('#msg').show();
  })
}

get_page(1);
