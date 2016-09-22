if (document.getElementById('searchbutton')) { // verify user is doing a search
    var container = document.querySelector('.list .tabsHeader');

    var btn_html = '<input id="map-btn" value="🌍 Carte" type="submit" class="button-blue full" style="background-color: #666;min-height: initial;line-height: 13px;width: auto;padding: 0px 5px;float: right;margin-left: 10px;">';
    container.insertAdjacentHTML('afterbegin', btn_html);
    var btn = container.querySelector('#map-btn');
    
    btn.onclick = function (e) {
        e.preventDefault();
        var url = 'https://lbc.dam.io/?url=' + encodeURIComponent(window.location.href);
        window.open(url, '_blank');
    }
}
