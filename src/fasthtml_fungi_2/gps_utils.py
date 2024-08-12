import json

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
