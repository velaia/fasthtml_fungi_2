from fasthtml.common import *
from icecream import ic
from dotenv import load_dotenv
import os
import piexif
from fasthtml_fungi_2.gps_utils import convert_coordinates_to_geojson


load_dotenv()

headers = (MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']), )
app, rt = fast_app(hdrs=headers)
setup_toasts(app)
db = database('data/observations.db')

observations = db.t.observations
if observations not in db.t:
    observations.create(id=int, filename=str, created_at=str, note=str, pk='id')
Observation = observations.dataclass()


@rt("/")
def get():
    return Title("Mushroom 🍄 Map"), Main(
        H1("Mushroom 🍄 Map"),
        P("The map displays your mushroom observations."),
        A("Click to add new observation", href="/new-observation"),
    )


observation_markdown = """
# Add a new observation

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
    )


@rt("/new-observation")
async def post(session, photo: str):
    add_toast(session, "Photo upload successful", "success")
    photo_content = await photo.read()
    file_path = os.path.join(".", os.getenv('upload_path'), photo.filename)
    with open(file_path, "wb") as output:
        output.write(photo_content)
    ic(type(photo))

    exif_dict = piexif.load(file_path)
    ic(exif_dict)

    geojson = convert_coordinates_to_geojson(exif_dict)
    ic(geojson)

    return Title("Successful Submission "), Main(
        H1("Information about Uploaded Photo"), Img(src=file_path, width="400")
    )


@rt("/static/uploads/{fname:path}.{ext:static}")
async def get(fname:str, ext:str): 
    return FileResponse(f'static/uploads/{fname}.{ext}')


def main():
    ic("in run")
    serve()
