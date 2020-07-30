"""
File: image-search-flask.py
Author: Daniel Lee <danielslee@email.arizona.edu>
Description: Launches the web app which implements the live search engine for embryo images.

This script accepts two optional command-line parameters:
- port: specifies the port to run the app. This defaults to 8081 (8080 is used for the main Geisha page).
- image home directory: a local directory containing embryo images. If left empty, this will default to the
directory that this script is run from, and images will most likely be pulled from the internet.

Example Script Usage:
python src/image-search-flask.py # Run app, keep defaults
python src/image-search-flask.py 8080 # Run app on port 8080
python src/image-search-flask.py /home/geisha/images # Run app and look for local images at /home/geisha/images
python src/image-search-flask.py 8080 /home/geisha/images # Combine above settings

The app accepts two parameters, which are given as query parameters in the app's url:

- filename (required): the filename of an image to find similar images to. This can be a local image file in
the image home directory, or the filename of an image on the Geisha website (upon which it will be downloaded).
Anything else will result in an error.
- num_images: the number of similar images to return. The default is 50.

Given the input embryo, the web app searches through the publicly available embryo images within the Geisha
database, and finds and returns the most similar images. A sorted list of the most similar filenames are
returned, separated the newline character "\n". On a browser, this will display as a list of filenames separated
by spaces.

Example App Usage:
python src/image-search-flask.py 8080 /home/geisha/images

Input link: http://localhost:8080/?filename=R449.CDH5.S17.001.jpg&n=10
Displayed Output (with new lines instead of spaces):
R449.CDH5.S17.001.jpg
R449.CDH5.S16.001.jpg
...

Input link: http://localhost:8080/?filename=local-embryo.jpg&n=10
Displayed Output (with new lines instead of spaces):
similar-image-one.jpg
similar-image-two.jpg
...
"""
from flask import Flask, request
from search import *
import sys

app = Flask(__name__)

@app.route("/")

def main():
    """
    Executes the image search engine.

    Given a filename and number of images to return (uses the 'n' argument; defaults to 50), the app
    finds or downloads the image locally, predicts on its features using the trained models, compares it
    with the public database images, and returns the filenames of the most similar ones.
    """
    # Parse app arguments (filename and n)
    fname = request.args.get("filename", None)
    # Need more than a link: filenames should be supported too
    if fname is None: raise TypeError("Missing filename of image to compare to.")
    n = request.args.get("n", None)
    n = int(ifnone(n, 50))
    # Retrieve image, find similar image filenames, display top results
    image_in = grab_image(fname, image_home_dir = app.config.get('image_home_dir'))
    similar_images = embryo_similarity(image_in)  # Using euclidean similarity with equal weight
    similar_images = [Path(fn).name for fn in similar_images[:n]]
    return "\n".join(similar_images)

if __name__ == "__main__":
    # No command line arguments
    if len(sys.argv) == 1:
        port = 8081
        app.config['image_home_dir'] = "."
    # One command line argument
    elif len(sys.argv) == 2:
        # Figure out whether the port of image home directory is specified
        try:
            int(sys.argv[1])
            port = int(sys.argv[1])
            app.config['image_home_dir'] = "."
        except:
            port = 8081
            app.config['image_home_dir'] = sys.argv[1]
    # Two command line arguments
    elif len(sys.argv) == 3:
        port = int(sys.argv[1])
        app.config['image_home_dir'] = sys.argv[2]
    else:
        raise TypeError("Too many command line arguments (two allowed)")
    app.run(debug=True, port=port)
