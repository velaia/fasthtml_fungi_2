import datetime
from fasthtml.common import *
from icecream import ic
from dotenv import load_dotenv
import os
import piexif
from fasthtml_fungi_2.gps_utils import convert_coordinates_to_geojson


load_dotenv()

headers = (picolink, MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']), )
app, rt = fast_app(hdrs=headers)
setup_toasts(app)
db = database('data/observation2.db')

observations = db.t.observations
if observations not in db.t:
    observations.create(id=int, filename=str, created_at=str, note=str, longitude=float, latitude=float, pk='id')
Observation = observations.dataclass()


@rt("/")
def get():
    return Title("Mushroom 🍄 Map"), Main(
        H1("My Mushroom 🍄 Map"),
        P("The map displays your mushroom observations."),
        P(A(Button("➕ Click to add new observation"), href="/new-observation")),
        P("These are the mushroom observations so far:"),
        Ul(
            *[Li(f"{obs.filename} at {obs.created_at}", A("show on map")) for obs in observations()]
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
def get():
    # return a Title and page for new observation that includes an image upload
    return Title("New Observation"), Main(
        Div(observation_markdown, cls="marked"),
        Form(
            Input(id="photo", type="file", name="photo"),
            Button("Submit", type="submit"),
            action="/new-observation",
            method="POST",
            enctype="multipart/form-data",
            accept="image/*",
        ),
    cls="container")


@rt("/new-observation")
async def post(session, photo: str):
    try:
        add_toast(session, "Photo upload successful", "success")
        photo_content = await photo.read()
        file_path = os.path.join(".", os.getenv('upload_path'), photo.filename)
        with open(file_path, "wb") as output:
            output.write(photo_content)
        ic(type(photo))

        exif_dict = piexif.load(file_path)
        ic(exif_dict)
        assert 'GPS' in exif_dict, "No GPS data in the image metadata"

        geojson = convert_coordinates_to_geojson(exif_dict)
        ic(geojson)

        obs = Observation(filename=photo.filename, created_at=datetime.datetime.now().isoformat(), 
                        note="New observation", longitude=geojson['coordinates'][1], latitude=geojson['coordinates'][0])
        observations.insert(obs)
    except Exception as e:
        add_toast(session, f"Error: {e}", "error")
        return Title("Error"), Main(H1("Error"), P(f"Error: {e}"),
                                    P( A("Back to main page", href="/")),
                                    cls="container")

    return Title("Successful Submission "), Main(
        H1("Information about Uploaded Photo"), Img(src=file_path, width="400")
    )


@rt("/static/uploads/{fname:path}.{ext:static}")
async def get(fname:str, ext:str): 
    return FileResponse(f'static/uploads/{fname}.{ext}')


def main():
    ic("in run")
    serve()
