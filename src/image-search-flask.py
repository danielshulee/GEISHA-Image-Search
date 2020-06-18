"""
File: image-search-flask.py
Author: Daniel Lee <danielslee@email.arizona.edu>
Description: Creates the web app which implements the live search engine for embryo images. It accepts two parameters,
which are given as query parameters in the app's url:

- filename (required): the filename of an image to find similar images to. This can be a path to a local image file
(absolute or relative to this repository), or the filename of an image on the Geisha website (upon which it will be
downloaded directly). Anything else will result in an error.
- num_images: the number of similar images to return. The default is 50.

Given these inputs, the web app searches through the publicly available images within the Geisha database, and finds and returns
the most similar images. Similarity is computed based on an image's stage and anatomical locations- images with embryos of a
similar stage, with staining in similar anatomical locations, are considered most similar. A sorted list of the most similar filenames
are returned, separated the newline character "\n". On a browser, this will display as a list of filenames separated by spaces.

Example Usage:
Input link: http://localhost:8080/?filename=R449.CDH5.S17.001.jpg&n=10
Displayed Output (with new lines instead of spaces):
R449.CDH5.S17.001.jpg
R449.CDH5.S16.001.jpg
R361.EGFL7.S17D.004.jpg
R467.CDH5.S14002.jpg
R208.TGFBR2.S16.01.jpg
R445.VEGFR3.S15.001.jpg
R380.LMOD1.S16.001.jpg
R299.TGFBR3.S17.01.jpg
R361.EGFL7.S15D.002.jpg
R445.VEGFR3.S13.001.jpg
...
"""
from flask import Flask, request
from search import *

app = Flask(__name__)

@app.route("/")

def main():
    """
    Executes the image search engine.

    Given a filename and number of images to return (uses the 'n' argument; defaults to 50), the app downloads the image locally, predicts
    on its features using the trained models, compares it with the public database images, and returns the results.
    """
    # Parse arguments (filename and n)
    fname = request.args.get("filename", None)
    # Need more than a link: filenames should be supported too
    if fname is None: raise TypeError("Missing filename of image to compare to.")
    n = request.args.get("n", None)
    n = int(ifnone(n, 50))
    # Retrieve image, find similar image filenames, display top results
    image_in = grab_image(fname)
    similar_images = embryo_similarity(image_in)  # Using euclidean similarity with equal weight
    similar_images = [Path(fn).name for fn in similar_images[:n]]
    return "\n".join(similar_images)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
