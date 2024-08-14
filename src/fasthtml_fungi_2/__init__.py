import datetime
from fasthtml.common import *
from icecream import ic
from dotenv import load_dotenv
import os
import piexif
from fasthtml_fungi_2.utils import convert_coordinates_to_geojson, get_map_js, get_long_lat_bnds


load_dotenv()


# Website setup, including scripts and styles
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


# Database
observations = db.t.observations
if observations not in db.t:
    observations.create(id=int, filename=str, species=str, created_at=str, note=str, longitude=float, latitude=float, pk='id')
Observation = observations.dataclass()


# Routes
@rt("/")
async def get(session, request: Request):
    observation_entities = observations(order_by="created_at desc")
    # if no observations, redirect to new observation page
    if(len(observation_entities) == 0):
        return RedirectResponse("/new-observation", status_code=303)
    
    long_lat_bnds = get_long_lat_bnds(observation_entities)

    map_js = get_map_js(observation_entities, long_lat_bnds)

    return Title("🍄 Mushroom Map 🍄"), Main(
        H1("🍄 My Mushroom Map 🍄"),
        P("The map displays your mushroom observations."),
        Div(
            Div(
                P(A(Button("➕ Click to add new observation"), href="/new-observation"), style="margin-bottom: 3em;"),
                Ul(
                    *[Li(f"{obs.species} - {datetime.datetime.strptime(obs.created_at, '%Y-%m-%dT%H:%M:%S').strftime('%B %d, %Y %I:%M %p')} ", 
                        A("✍ Details", href=f"/observation/{obs.id}"), 
                        A("❌ Delete", href=f"/observation/delete/{obs.id}")) 
                        for obs in observation_entities]
                    ),),
            Div(id="map", style="height:650px; width:800px;"), 
            style="display:flex; justify-content:space-between; "),
        Script(type="text/javascript", code=map_js),
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
async def post(photo: str, species: str, sess):
    try:
        photo_content = await photo.read()
        file_path = os.path.join(".", "static/uploads", photo.filename)
        with open(file_path, "wb") as output:
            output.write(photo_content)

        exif_dict = piexif.load(file_path)
        assert 'GPS' in exif_dict, "No GPS data in the image metadata"

        geojson = convert_coordinates_to_geojson(exif_dict)
        ic(geojson["coordinates"])

        # set created_at to date from EXIF data
        exif_date = exif_dict['Exif'][36867].decode()
        # parse exif_date
        exif_date_parsed = datetime.datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")

        obs = Observation(filename=photo.filename, created_at=exif_date_parsed, species=species,
                        note="New observation", longitude=geojson['coordinates'][1], latitude=geojson['coordinates'][0])
        observations.insert(obs)
        add_toast(sess, "Photo upload successful", "success")
    except Exception as e:
        add_toast(sess, f"Error: {e}", "error")
        sess['error'] = "something went wrong"
        # return Title("Error"), Main(H1("Error"), P(f"Error: {e}"),
        #                             P( A("Back to main page", href="/")),
        #                             cls="container")

    return RedirectResponse("/", status_code=303)


@rt("/static/uploads/{fname:path}.{ext:static}")
async def get(fname:str, ext:str): 
    return FileResponse(f'static/uploads/{fname}.{ext}')

@rt("/observation/{id}")
async def get(id:int, sess):
    obs = observations[id]
    observation_js = get_map_js(obs)

    return Main(H1(f"🍄 {obs.species} 🍄", id="title"),
                  
        Div(A("Back to main page", href="/"), style="margin-bottom: 20px;"),
        Main(
        Div(H2("Map"), P( Div(id="map", style="height:650px; width:800px; position:relative;"), cls="grid",), ), 
        Div(H2("Details"), P(
            P(Label("Species: "), Input(type="text", id="species", name="species",
                                         value=obs.species, hx_post=f"/observation/{obs.id}",
                                         hx_target="#title", hx_swap="innerHTML")),
            P(f"Made at: ", Strong(f"{datetime.datetime.strptime(obs.created_at, '%Y-%m-%dT%H:%M:%S').strftime('%B %d, %Y %I:%M %p')}")),
            P(f"Coordinates (latitude, longitude): ", Strong(f"{obs.latitude:.4f}, {obs.longitude:.4f}")),
            P(Img(src=f"/static/uploads/{obs.filename}", width="400")), cls="grid",), ),
        Script(type="text/javascript", code=observation_js),
    style="display:flex; justify-content:space-between; "), cls="container")

@rt("/observation/{id}")
async def post(id:int, species:str, session):
    ic(f"adjusting species name to {species}")
    obs = observations.get(id)
    ic(obs)
    obs.species = species
    observations.update(obs)
    return f"🍄 {species} 🍄"


@rt("/observation/delete/{id}")
async def get(session, id: int):
    observations.delete(id)
    add_toast(session, "Observation deleted", "success")
    return RedirectResponse("/")


def main():
    ic("in run")
    serve(host="localhost")


if __name__ == "__main__":
    main()