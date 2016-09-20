var search = document.getElementById('searchbutton');
if (search) {
    var container = search.parentNode;
    container.innerHTML += search.outerHTML;

    var mapBtn = container.lastChild;
    mapBtn.value = 'Carte';
    mapBtn.id = '';
    mapBtn.style.marginTop = '10px';
    mapBtn.style.backgroundColor = '#999';
    delete mapBtn.attributes['data-info'];

    mapBtn.onclick = function (e) {
        e.preventDefault();
        var url = 'https://lbc.dam.io/?url=' + encodeURIComponent(window.location.href);
        window.open(url, '_blank');
        return false;
    }
}
