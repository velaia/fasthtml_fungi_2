# fasthtml-fungi-2 - Personal Fungi

Pet project to explore a couple of tools I wanted to explore (for  a while) in combination with 🍄 mushrooms🍄:
* [Answer.ai's FastHTML](https://fastht.ml/)
* [Rye: a Hassle-Free Python Experience](https://rye.astral.sh/)
* [GitHub Copilot](https://github.com/features/copilot)
* [🍦icecream](https://github.com/gruns/icecream) & [dotenv](https://github.com/theskumar/python-dotenv)
* [🗺 Stadia Maps](https://www.stadiamaps.com)

## Description

This application allows users to upload photos of mushrooms they have found. Upon uploading, the app will automatically extract the GPS coordinates from the EXIF data embedded in the photos. Using these coordinates, the app will then display a map highlighting the locations of all the mushroom observations. This feature enables users to easily visualize where different types of mushrooms have been found.

## Installation

### Using Rye

* Clone this git repository
* Make sure to [have rye installed](https://rye.astral.sh/guide/installation/) (together with `uv` it's pip on steroids (and more)!)
* `cd fasthtml_fungi_2` into the cloned repository
* `rye sync`
* Active the newly created virtualenv (e.g. `source .venv/bin/activate`)
* Run the program with `rye run fasthtml-fungi-2` and open the [displayed URL](http://localhost:5001) in your browser to add your first mushroom observation

### Using pip


### Using Docker

## Configuration
You can adjust settings in the `.env` file, e.g. [choose a different Stadia Maps theme](https://docs.stadiamaps.com/themes/).


## TODOs
* [ ] Motivation
* [ ] pip installation instructions
* [ ] Dockerfile & instructions
* [ ] What (else) to put in dotfile? Clean up uploads directory config.
* [ ] Create demo online using railway.app
* [x] Add LICENSE
* [ ] Complete pyproject.toml with relevant meta data
* [ ] Add footer
