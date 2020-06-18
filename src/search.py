"""
File: search.py
Author: Daniel Lee <danielslee@email.arizona.edu>
Purpose: Imports and creates all of the objects needed for live image search.

The following libraries are imported:
- fastai (used for model evaluation)
- urllib (to download images)
- pickle (to load data objects)

The following data objects are loaded:
- Trained stage and location models
- Saved results for existing images in the database (filename, stage predictions, anatomical locations predictions)

Functions are defined for the image search process. In general, functions have the following purpose:
- To wrap the input image in deep learning objects for prediction
- To predict on input embryos using trained models
- To retrieve save information on database images
- To compute similarity given an input embryo and database embryos, and return the most similar images
"""

## Libraries
from fastai.vision import *
import urllib
import pickle

## Data
# Load trained models
stage_model = load_learner("models/","stage-prediction-model.pkl")
locations_model = load_learner("models/","locations-prediction-model.pkl")
locations_model.model.eval()
stage_model.model.eval()

# Load saved results for existing images
with open("data/database-image-predictions.pkl", "rb") as inp:
    public_filenames, public_stages, public_locations = pickle.load(inp)
    
## Functions

# To create an ImageDataBunch object to run inference on and find similar images to 
def grab_image(image_in:str, *args, **kwargs) -> ImageDataBunch:
    """
    Given a filename or string that corresponds to an image, returns a fastai databunch containing just that
    image. Typcially, an input embyro image is fed to this function as a first step in the image search process.

    A DataBunch is the basic fastai wrapper for a machine learning data object that can be used for inference
    (prediction). In this case, the DataBunch will  be fed into the trained models to predict on the image's
    stage and anatomical locations.

    Arguments:
    - image_in: A string indicating the input image. This can be a path to a local image file (absolute or
    relative to the main repository), or the filename of an image on the Geisha website (upon which it will
    be downloaded directly). Anything else will result in an error.
    
    Returns:
    An ImageDataBunch containing the following image.  The databunch resizes the image to 300 (w) x 400 (h)
    """
    # Check for image locally
    if os.path.exists(image_in):
        return _create_databunch(image_in)
    # Check the Geisha website for the image
    else:
        try:
            image_url = "http://geisha.arizona.edu/geisha/photos/" + image_in
            urllib.request.urlretrieve(image_url, "src/temporary-images/" + image_in)
            return _create_databunch("src/temporary-images/" + image_in) 
        except urllib.error.HTTPError:
            raise FileNotFoundError("Image not found locally or on the Geisha database")

def _create_databunch(image_fn:str) -> ImageDataBunch:
    """
    Given the filename of a image on disk, creates a fastai ImageDataBunch with that image.

    The DataBunch returned will resize the image to 300 (w) x 400 (h). It contains no other data transforms.
    """
    return (ImageList([image_fn], path="../Images/")
            .split_none()
            .label_empty()
            .transform(tfms=([],[]), size=(400,300))
            .databunch(bs=1)
            .normalize(imagenet_stats))

# Helpers
def run_inference(image_db:DataBunch, do_stage=True, do_locations=True):
    """
    Given an image in data bunch form, runs inference on that image by predicting on its stage and
    locations (via the trained models).

    Arguments:
    - image_db: A DataBunch created by `grab_image` which contains an input image.
    - do_stage: Whether to predict on an image's stage
    - do_locations: Whether to predict on an image's anatomical locations
    
    Returns:
    The predictions in the form of a tuple. By default contains (stage prediction, locations prediction),
    unless instructed to not predict on either feature. Both predictions are in the form of a PyTorch tensor.
    """
    res = []
    # Get data and predict using models
    xb, yb = image_db.one_item(image_db.train_ds[0][0])
    if do_stage:
        stage_pred = stage_model.model(xb).cpu()
        res.append(stage_pred.detach())
    if do_locations:
        locations_pred = locations_model.model(xb).sigmoid().cpu()
        res.append(locations_pred.detach())
    return tuple(res)
def retrieve_predictions():
    """
    Retrieves the saved information on the public images in the Geisha database. This includes the stage and
    anatomical locations predictions for each image. This information will be returned in a tuple of PyTorch
    tensors in the form (stages, locations).
    """
    return (public_stages, public_locations)
def normalize_z_score(tensors:List[Tensor]):
    """
    Given a list of tensors, normalizes them to mean 0 and standard deviation 1, in essence returning z-scores.
    In similarity calculations, this technique is used to combine measures of similarity of an embryo's stage and
    anatomical locations (which are represented by different mathematical objects, and therefore will have
    differences in scale in whatever metric is used to measure their similarity)

    Argments:
    - tensors: a list of PyTorch tensors to be normalize into z-scores

    Returns:
    - The same list of tensors, with each individual tensor normalized into z-scores
    """
    for i in range(len(tensors)):
        tensors[i] = (tensors[i] - tensors[i].mean())/tensors[i].std()
    return tensors
# Framework for creating similarity algorithms
def similarity(image:DataBunch, stage_sim_func:Callable[[DataBunch], tensor], locations_sim_func:Callable, \
               alpha:int=0.5, *args, **kwargs) -> List[str]:
    """
    After models predict the stage and anatomical locations of an input embryo image, the next step in the image
    search involves comparing those results with the existing database and computing similarity. This function
    creates a framework for ranking similarities between Geisha images and the input image.

    The basic framework for comparing images is as such: an input embryo's stage and anatomical locations are 
    compared separately, with all the embryos in the database. Comparison happens mathematically via some
    score, with a higher number corresponding to more similarity. After comparison, two separate vectors of scores
    will exist: one representing the similarity between an embryo's stage with the stages of embryos in the database,
    and one for the anatomical locations. These two separate similarity scores are then normalized into z-scores, and
    then combined together (through linear combination). Normalization is required because stage and locations are
    fundamentally different objects– stage is a single number, while locations are one-hot encoded by a vector with
    dimensionality equal to the number of existing locations. Normalization ignores the scale of whatever comparison
    mechanism the two use, and put them on equal footing (as long as a higher number indicates more similarity).

    To implement the framework, this function accepts an image and arbitrary functions to compute similarity. Two
    functions/algorithms are needed: one that accepts the input image and returns a vector of stage similarity scores
    (one for each image in the database), and another that does the same for locations. Again, similarity scores must
    be scalar numbers– example algorithms include negative absolute difference for stage, and euclidean distance between
    vectors for locations. Given the two functions, this function uses them to compute similarities, normalizes them,
    combines then, then ranks and returns a sorted list of the images in the database, from most similar to the least similar.
    The most effective way of using this is wrapping the two similarity functions via `partial`. That way, only an image
    needs to be given to then receive all geisha image filenames, ranked in order of similarity.

    Arguments:
    - image: an input image in DataBunch form
    - stage_sim_func: a stage similarity function. This accepts the input image and returns a tensor of stage similarity
    scores (one for each item in the database).*
    - location_sim_func: a locations similarity function in the same manner.*
    - alpha: determines the percent weight given to the stage similarity. Must be a float between 0 and 1. A value of 0.4
    means that stage similarity is weighted at 40% and locations similarity 60%.
    * See the functions/algorithms I use below. They have been tested and are found to deliver the best results.

    Returns: A list of filenames images in the Geisha database, ranked in order of similarity to the input image. 
    """
    # Compute similarities using functions given
    stage_sims = stage_sim_func(image, **kwargs)
    locations_sims = locations_sim_func(image, **kwargs)
    assert stage_sims.shape[0] == locations_sims.shape[0]
    # Normalize similarity scores into z-scores
    (stage_sims, locations_sims) = normalize_z_score([stage_sims, locations_sims])
    combined_sims = alpha*stage_sims + (1-alpha)*locations_sims
    # Sort filenames in order of similarity, return
    sim_order = combined_sims.topk(len(combined_sims), dim=0)[1].squeeze()
    return public_filenames[sim_order].tolist()
def stage_sim_absolute(image:DataBunch, **kwargs) -> Tensor:
    """
    The default function for computing stage similarity between embryos. Predicts the stage of the input image, and
    then returns the negative absolute stage difference between the input image's stage and the stages of the database
    embryos.

    Arguments:
    - image: The input image DataBunch

    Returns:
    A tensor of similarity values (one for each database image). Each similarity score is the negative absolute difference
    in stage.
    """
    stage_pred = run_inference(image, do_locations=False)[0]
    public_stages, _ = retrieve_predictions()
    return -1*(stage_pred - public_stages).abs()

def locations_sim_euclidean(image:DataBunch, **kwargs):
    """
    A locations similarity function that uses euclidean similarity between vectors. Predicts the anatomical locations of
    the input image, and then returns the eucliean similarity between the input embryo's locations vector and the
    locations vectors of the database embryos.

    Euclidean similarity and distance are computed between unnormalized, one-hot locations vectors. The euclidean
    similarity between two locations vectors is defined as 1/(1 + euclidean distance).

    Arguments:
    - image: The input image DataBunch

    Returns:
    A tensor of similarity values (one for each database image). Each similarity score is the euclidean similarity between
    locations vectors.
    """
    locations_pred = run_inference(image, do_stage=False)[0]
    _, public_locations = retrieve_predictions()
    euclidean_distance = torch.norm(public_locations-locations_pred, dim=1).unsqueeze(1)
    return 1/(1+euclidean_distance)
def _create_similarity_func(stage_sim_func:Callable[[DataBunch], tensor], locations_sim_func:Callable, **kwargs):
    """
    Helper function to wrap the `similarity` function with stage and locations similarity functions. Uses partial.
    After using this function, the resulting similarity function only needs an image parameter to return similar
    image filenames.
    """
    return partial(similarity, stage_sim_func = stage_sim_func, locations_sim_func = locations_sim_func, **kwargs)
# Define the similarity algorithm I will use. I use negative absolute stage difference and euclidean locations similarity,
# and weight stage and locations equally.
embryo_similarity = _create_similarity_func(stage_sim_absolute, locations_sim_euclidean, alpha=0.5)