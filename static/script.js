//find a way to assing colors on the fly!
function setColors(listNames) {
    result = {};
    for(var propt in listNames){
        result[propt] = "red";
    }
    return result;
}

function getName(listName, name) {
    if (name in listName) {
        return listName[name];
    }
    return name;
}

function getLeader(data) {
    var votes = data['votos'];
    var leader = "";
    var leaderVotes = 0;
    var leaderMargin = 0;
    var secondLeaderVotes = 0;
    for(var propt in votes) {
        if(!leader) {
            leader = propt;
            leaderVotes = votes[propt];
            leaderMargin = leaderVotes;
        }
        if(votes[propt] > leaderVotes) {
            leader = propt;
            secondLeaderVotes = leaderVotes;
            leaderVotes = votes[propt];
        }
        else if(votes[propt] > secondLeaderVotes && leader !== propt) {
            secondLeaderVotes = votes[propt];
        }
        leaderMargin = leaderVotes - secondLeaderVotes;
    }
    return [leader, leaderVotes, leaderMargin];
}

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
    if (!str) {
        return "";
    }
    result = str.toLowerCase();
    return result.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

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

colorList = setColors(listNames);
// Fire off to get our GeoJSON
$.getJSON(geoJsonUrl, function(response) {

    //get parties and assign colors

    // Pull in the circle layer from GeoJSON
    var circleLayer = L.geoJson(response, {
        pointToLayer: function (feature, latlng) {
            var leaderData = getLeader(feature['properties']);
            var marker = new L.circleMarker(latlng, {
                fillColor: colorList[leaderData[0]],
                color: colorList[leaderData[0]],
                fillOpacity: 0.5,
                weight: 1
        })
        .setRadius(getRadius(leaderData[2]))
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