function getName(listName, name) {
    if (name in listName) {
        return listName[name][0];
    }
    return name;
}

function getColor(listName, name) {
    if (name in listName) {
        return listName[name][1];
    }
    return "red";
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

function getTotalData(schools, listNames) {
    result = {};
    resultList = [];
    total = 0;
    for(var propt in listNames){
        result[propt] = [0, 0];
    }
    
    // XXX: only process last school that has the total numbers:
    //for(i=0; i < schools.length; i++) {
    for(i=schools.length-1; i < schools.length; i++) {
        var school = schools[i]['properties'];
        for(var prop in listNames) {
            if(school['votos'][prop]) {
                result[prop][0] += school['votos'][prop];
            }
        }
        total += school['overall_total'];
    }

    for(var prope in listNames) {
        result[prope][1] = getPercentage(result[prope][0], total);
        resultList.push([prope, result[prope][0], result[prope][1]]);
    }

    resultList.sort(function(a, b) {
        return b[1]-a[1];
    });
    return resultList;
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
    return ((value/total)*100).toFixed(2);
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
var mapquestLayer = new L.TileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
});
map.addLayer(mapquestLayer);

// Styling tricks
var radiusConstant = 0.5;
var getRadius = function(value) {
    return Math.sqrt(value)*radiusConstant;
};

// Fire off to get our GeoJSON
$.getJSON(geoJsonUrl, function(response) {
    //MAP STUFF
    // Pull in the circle layer from GeoJSON
    var circleLayer = L.geoJson(response, {
        pointToLayer: function (feature, latlng) {
            var leaderData = getLeader(feature['properties']);
            var marker = new L.circleMarker(latlng, {
                fillColor: getColor(listNames, leaderData[0]),
                color: getColor(listNames, leaderData[0]),
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


    //Modal Stuff
    var schools = response["features"];
    var result = getTotalData(schools, listNames);
    var i = 0;

    for(i=0; i<result.length; i++) {
        if(i < 6) {
            var party = result[i];
            var html = "<div class='party'>" +"<div style='background-color:"+getColor(listNames, party[0]) +"' class='name "+party[0]+"'>" + (i+1) +" " + getName(listNames, party[0])+"</div>" +
                "<div class='percent'>&nbsp;&nbsp;"+party[2]+"%</div>" +
                "<div class='votes'>"+ addCommas(party[1]) +" votes</div></div>";
            $(".legend").append(html);
        }
    }

});
