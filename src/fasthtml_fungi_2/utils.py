import json, os


def convert_coordinates_to_geojson(data):
    if 'GPS' not in data:
        # throw exception
        raise ValueError("No GPS data in the image metadata") 
    elif len(data['GPS'].keys()) < 1:
        raise ValueError("No GPS data in the image metadata") 
    
    coordinates = {
        "type": "Point",
        "coordinates": [
            data['GPS'][2][0][0] + data['GPS'][2][1][0] / 60 + data['GPS'][2][2][0] / data['GPS'][2][2][1] / 3600,
            data['GPS'][4][0][0] + data['GPS'][4][1][0] / 60 + data['GPS'][4][2][0] / data['GPS'][4][2][1] / 3600,
        ]
    }
    return coordinates


def get_long_lat_bnds(points):
    # Get the bounding box of the points (longitude, latitude per point)
    longitudes = [point.longitude for point in points]
    latitudes = [point.latitude for point in points]
    long_lat_bnds = {
        "min_lon": min(longitudes),
        "max_lon": max(longitudes),
        "min_lat": min(latitudes),
        "max_lat": max(latitudes),
    }
    return long_lat_bnds


def get_map_js(obs, long_lat_bnds=None):
    bounds = ""

    # center on the observation or first observation in a list of observations
    if isinstance(obs, list):
        center = obs[0]
        features = obs
    else:
        center = obs
        features = [obs]

    if len(features) > 1:
        long_lat_bnds = get_long_lat_bnds(features)

    js = f"""
var map = new maplibregl.Map({{
    container: 'map',
    style: 'https://tiles.stadiamaps.com/styles/{os.getenv('map_style')}.json',  // Style URL; see our documentation for more options
    center: [{center.longitude}, {center.latitude}],  // Initial focus coordinate
    zoom: 13,
    bounds: [[7.200780555555555, 44.18025], [8.21453611111111, 45.98447222222222]],
    <!-- add 70 pixels of padding to the map -->
    fitBoundsOptions: {{ padding: 50, }}
    }});
"""

    js += f"""


maplibregl.setRTLTextPlugin('https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.2.3/mapbox-gl-rtl-text.min.js');
map.addControl(new maplibregl.NavigationControl());

var markerCollection = {{
    "type": "FeatureCollection",
    "features": ["""


    # Add markers for the features to the map
    for feature in features:
        js += f"""
    {{
        "type": "Feature",
        "geometry": {{
            "type": "Point",
            // NOTE: in GeoJSON notation, LONGITUDE comes first. GeoJSON 
            // uses x, y coordinate notation
            "coordinates": [{feature.longitude}, {feature.latitude}]
        }},
        "properties": {{
            "title": "<a href='/observation/{feature.id}'>{feature.species}</a> - {feature.created_at}"
        }}
    }},"""

    js += f"""
    ]
}};

markerCollection.features.forEach(function (point) {{
    // Since these are HTML markers, we create a DOM element first, which we will later
    // pass to the Marker constructor.
    var elem = document.createElement('div');
    elem.className = 'marker';

    // Now, we construct a marker and set it's coordinates from the GeoJSON. Note the coordinate order.
    var marker = new maplibregl.Marker(elem);
    marker.setLngLat(point.geometry.coordinates);

    // You can also create a popup that gets shown when you click on a marker. You can style this using
    // CSS as well if you so desire. A minimal example is shown. The offset will depend on the height of your image.
    var popup = new maplibregl.Popup({{ offset: 24, closeButton: false }});
    popup.setHTML('<div>' + point.properties.title + '</div>');

    // Set the marker's popup.
    marker.setPopup(popup);

    // Finally, we add the marker to the map.
    marker.addTo(map);
}});
    """

    return js

# Example usage
data = {
    'GPS': {
        0: (2, 2, 0, 0),
        1: b'N',
        2: ((45, 1), (59, 1), (2536.2, 100)),
        3: b'E',
        4: ((7, 1), (13, 1), (1807.8, 100)),
        5: 0,
        6: (2040, 1),
        7: ((8, 1), (26, 1), (58, 1)),
        16: b'M',
        17: (102, 1),
        29: b'2024:08:08'
    }
}

#  geojson = convert_coordinates_to_geojson(data)
