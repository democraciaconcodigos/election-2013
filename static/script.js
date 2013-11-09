var addCommas = function (nStr) {
        nStr += '';
        x = nStr.split('.');
        x1 = x[0];
        x2 = x.length > 1 ? '.' + x[1] : '';
        var rgx = /(\d+)(\d{3})/;
        while (rgx.test(x1)) {
            x1 = x1.replace(rgx, '$1' + ',' + '$2');
        }
        return x1 + x2;
    };
    function titleCase(str) {
        var str = str.toLowerCase();
        return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
    };
    function getPercentage(value, total) {
        return ((value/total)*100).toFixed(1);
    }

    var $width = $(window).width();
    var center = [initialLat, initialLon];
    var zoom = 8;

    if ($width <= 767) {
        center = [initialLat, initialLon];
        zoom = 7;
    }

    if ($width <= 479) {
        zoom = 7;
    }

    var map = L.map('map', {
        zoomControl: false,
        minZoom: 8
    }).setView(center, zoom);
    // Base tiles
    var mapquestLayer = new L.TileLayer('http://{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: 'Data, imagery and map information provided by <a href="http://open.mapquest.co.uk" target="_blank">MapQuest</a>,<a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> and contributors.',
        subdomains: ['otile1','otile2','otile3','otile4']
    });
    map.addLayer(mapquestLayer);

    // Styling tricks
    var radiusConstant = 0.5;
    var getRadius = function(value) {
        return Math.sqrt(value)*radiusConstant;
    };

    var list2color = {
        '501': '#50ade6', // light blue
        '502': '#6eb440', // green
        '503': '#ffda00'  // yellow
    }

    var list2abbrev = {
        '501': 'FpV',
        '502': 'UNEN',
        '503': 'Pro'
    };

    // Fire off to get our GeoJSON
    $.getJSON(geoJsonUrl, function(response) {

        // Pull in the circle layer from GeoJSON
        var circleLayer = L.geoJson(response, {
            pointToLayer: function (feature, latlng) {
                var marker = new L.circleMarker(latlng, {
                    fillColor: list2color[feature.properties['leader']],
                    color: list2color[feature.properties['leader']],
                    fillOpacity: 0.5,
                    weight: 1
                })
                .setRadius(getRadius(feature.properties['margin_of_victory']))
                .bindPopup(_.template($("#template-popup").html(), feature.properties)
                );
                return marker;
            }
        });

        // Set the default data layer that will load with the map
        map.addLayer(circleLayer);

        // Add a little headline in there too
        $(".leaflet-control-layers-list").prepend("<h3>Data styles</h3>");

        // Add the zoom control in the upper right
        new L.Control.Zoom({position: "topright"}).addTo(map);
    });