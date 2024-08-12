import datetime
from fasthtml.common import *
from icecream import ic
from dotenv import load_dotenv
import os
import piexif
from fasthtml_fungi_2.gps_utils import convert_coordinates_to_geojson


load_dotenv()

headers = (picolink, MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']), 
           Script(type="text/javascript", src="https://unpkg.com/maplibre-gl@4.0.2/dist/maplibre-gl.js"),
           Link(rel="stylesheet", href="https://unpkg.com/maplibre-gl@4.0.2/dist/maplibre-gl.css"),
           Link(rel="stylesheet", href="/static/style.css"),
           Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
           Meta(name="color-scheme", content="dark light"),
           Meta(name="charset", content="utf-8"),)
app, rt = fast_app(hdrs=headers)
setup_toasts(app)
db = database('data/observation2.db')

observations = db.t.observations
if observations not in db.t:
    observations.create(id=int, filename=str, species=str, created_at=str, note=str, longitude=float, latitude=float, pk='id')
Observation = observations.dataclass()


@rt("/")
def get(session):
    return Title("Mushroom 🍄 Map"), Main(
        H1("My Mushroom 🍄 Map"),
        P("The map displays your mushroom observations."),
        P(A(Button("➕ Click to add new observation"), href="/new-observation")),
        P("These are the mushroom observations so far:"),
        Ul(
            *[Li(f"{obs.species} - {obs.created_at}", 
                 A("Show on map", href=f"/observation/{obs.id}"), 
                 A("❌ Delete", href=f"/observation/delete/{obs.id}")) 
                for obs in observations()]
            ),
    cls="container")


observation_markdown = """
# Add 🍄 Observation

Please select the mushroom image for the observation. The photo should come with the GPS location where it has been taken in the metadata.

After uploading:
- The image will be displayed on the page.
- The GPS coordinates will be extracted from the image metadata and stored in a database containing your observations.
- A map will be displayed with the location of the observation.
"""

@rt("/new-observation")
async def get(session):
    # return a Title and page for new observation that includes an image upload
    return Title("New Observation"), Main(
        Div(observation_markdown, cls="marked"),
        Form(
            Input(id="species", type="text", name="species", placeholder="Species name"),
            Input(id="photo", type="file", name="photo"),
            Button("Submit", type="submit"),
            action="/new-observation",
            method="POST",
            enctype="multipart/form-data",
            accept="image/*",
        ),
    cls="container")


@rt("/new-observation")
async def post(session, photo: str, species: str):
    try:
        photo_content = await photo.read()
        file_path = os.path.join(".", os.getenv('upload_path'), photo.filename)
        with open(file_path, "wb") as output:
            output.write(photo_content)

        exif_dict = piexif.load(file_path)
        assert 'GPS' in exif_dict, "No GPS data in the image metadata"

        geojson = convert_coordinates_to_geojson(exif_dict)
        ic(geojson["coordinates"])

        # TODO: set created_at to date from EXIF data
        exif_date = exif_dict['Exif'][36867].decode()
        # parse exif_date
        exif_date_parsed = datetime.datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")

        obs = Observation(filename=photo.filename, created_at=exif_date_parsed, species=species,
                        note="New observation", longitude=geojson['coordinates'][1], latitude=geojson['coordinates'][0])
        observations.insert(obs)
        add_toast(session, "Photo upload successful", "success")
    except Exception as e:
        add_toast(session, f"Error: {e}", "error")
        return Title("Error"), Main(H1("Error"), P(f"Error: {e}"),
                                    P( A("Back to main page", href="/")),
                                    cls="container")

    return RedirectResponse("/", status_code=303)


@rt("/static/uploads/{fname:path}.{ext:static}")
async def get(fname:str, ext:str): 
    return FileResponse(f'static/uploads/{fname}.{ext}')

@rt("/observation/{id}")
def get(id:int):
    obs = observations[id]

    observation_js = f"""
var map = new maplibregl.Map({{
    container: 'map',
    style: 'https://tiles.stadiamaps.com/styles/stamen_terrain.json',  // Style URL; see our documentation for more options
    center: [{obs.longitude}, {obs.latitude}],  // Initial focus coordinate
    zoom: 14
}});

maplibregl.setRTLTextPlugin('https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.2.3/mapbox-gl-rtl-text.min.js');
map.addControl(new maplibregl.NavigationControl());

var markerCollection = {{
    "type": "FeatureCollection",
    "features": [{{
        "type": "Feature",
        "geometry": {{
            "type": "Point",
            // NOTE: in GeoJSON notation, LONGITUDE comes first. GeoJSON 
            // uses x, y coordinate notation
            "coordinates": [{obs.longitude}, {obs.latitude}]
        }},
        "properties": {{
            "title": "Observation 1"
        }}
    }}]
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

    return Titled(f"Observation: {obs.species}",
                  
        Div(A("Back to main page", href="/"), style="margin-bottom: 20px;"),
        Main(
        Div(H2("Map"), P( Div(id="map", style="height:650px; width:800px; position:relative;"), cls="grid",), ), 
        Div(H2("Details"), P(
            P(f"Made at: ", Strong(f"{obs.created_at}")), 
            P(f"Coordinates (latitude, longitude): ", Strong(f"{obs.latitude:.4f}, {obs.longitude:.4f}")),
            P(Img(src=f"/static/uploads/{obs.filename}", width="400")), cls="grid",),),
        Script(type="text/javascript", code=observation_js),
    style="display:flex; justify-content:space-between; "))

@rt("/observation/delete/{id}")
def get(session, id: int):
    observations.delete(id)
    add_toast(session, "Observation deleted", "success")
    return RedirectResponse("/")


def main():
    ic("in run")
    serve(host="localhost")


if __name__ == "__main__":
    main()