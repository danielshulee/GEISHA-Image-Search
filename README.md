# GEISHA-Image-Search

Image search for [GEISHA](http://geisha.arizona.edu/geisha/), an online repository for gene expression in chicken embryos.

<img src='http://geisha.arizona.edu/geisha/photos/R340.TBX4.S19.01.jpg' align="middle" width=300>

## Problem

[GEISHA](http://geisha.arizona.edu/geisha/), a [National Institutes of Health](https://www.nih.gov/) funded project, investigates gene expression patterns in chicken embryos using situ hybridization and provides images of chicken embryos in an online database. By doing so, it is a valuable resource for researchers and students of developmental biology. However, with an abundance of embryo images comes difficulty making sense of all the images, and currently, there are only a couple of esoteric ways to query and filter embryos. These methods are mostly limited to filtering by stage and anatomical location (the blue area in which a gene is expressed), and they pose the problems of being difficult for students to understand, and still returning up to thousands of images for common categories (one anatomical location returns over 6000 results). To address these problems, this project introduces a new way: using an image to search for other images.

<img src='Img/Geisha_early_stage.jpeg' width='500'>

With Geisha Image Search, a researcher or student could find new images by inputting one of their own, and getting out images of similar embryos. Using an embryo image from the [GEISHA](http://geisha.arizona.edu/geisha/) website or another lab or publication, a student or researcher is able to find similar images to compare or learn from. This way, students are able to browse images without a full understanding of their terminology or science, and researchers have a way to quickly search through thousands of photos.

For example, a student in his research might come across this image:

<img src='Img/Geisha_model_input.png' height='350'>

Without Geisha Image Search, if the student wanted to find other embyros like it, he/she would have to identify the features of that image and query them, or scroll through the [GEISHA](http://geisha.arizona.edu/geisha/) database in hopes of finding others like it. With Geisha Image Search, he/she could save that image and upload it to the tool in any size and in any typical format, and receive these images in response:

<img src='Img/Geisha_model_output.jpeg' height='550'>

Given these returned images (in reality, there would be a lot more than 4), the student can choose and analyze the ones that match his/her needs. This method can be applied to any embyro image, and it is an effective introduction to [GEISHA](http://geisha.arizona.edu/geisha/) and developmental biology.

### The Criteria for Similarity

For each image, there are two features that distinguish it from others: the stage of embryo development, and the anatomical locations (the patches stained blue, denoting gene expression). Currently, these are the two primary criteria through which one can query and find images. While this is useful, it requires a "bottom up" approach (understanding before doing), and those who currently have an image of an embryo have no way of finding similar ones. To address this problem, this project seeks to create an engine for [GEISHA](http://geisha.arizona.edu/geisha/) that allows easier browsing through image search.

Stage refers the how far the chicken embryo is in development. Here are two groups of embryos in similar stages.

<img src='Img/Geisha_early_stage.jpeg' width='500'>
<img src='Img/Geisha_later_stage.jpeg' width='500'>

Images of embryos in similar stages will be considered more similar.

Location refers to where the gene is expressed on the embryo, indicated by blue staining. Here is an embryo with staining in only parts of its body.

<img src='Img/hardyCFCSt10.1.jpeg' width='250'>

When comparing images, those with staining in similar places will be considered more similar.

## Solution

As mentioned above, the capability to input an image and find "similar" ones would be useful for students and researchers alike. My proposed solution involves deep learning, through which neural networks can be trained to predict the two most important parameters of every image: stage and anatomical location.

### Deep Learning

Deep learning is a technique that enables a computer to "learn" from data, allowing it to extract patterns and perform tasks, even on complicated inputs that it has not seen. Among the advantages of deep learning is its ability to work with images. It can perform all sorts of analyses, such as classifying the contents of an image (e.g. the anatomical locations in an embryo) or performing regression (e.g. the stage of an embryo). Using deep learning, one can effectively train a computer to recognize chicken embryos and output meaningful information about them.

The mechanism for deep learning is a structure called the "neural network". Based after the biological brain, the neural network is a learned mathematical function that maps inputs— images, in our case— to various outputs— anatomical locations and stage. These functions start with no predictive power, but given data with labels (the "correct answers" for what the stage or locations are), they can "learn" how to recognize patterns in images. Once these networks are trained with sufficient data, they can be deployed to new data that they have not seen— in our case, a new image given by the user in order to find "similar" ones.

The reason that deep learning can find the "similarity" between images is the fact that a network, given an image, returns numerical outputs for whatever task is given. For example, when predicting anatomical locations (of which there are around 140), the network returns 140 numbers, all between 0 and 1, that represent the probability that the image has genes expressed in each location. For example, if the number in the vector corresponding to "Endoderm" is 0.98, the network is 98% sure that the embryo's endoderm has been expressed. Similarly, the network predicting stage would also return a number, although it doesn't symbolize a probability. Instead, it represents what stage the network thinks the image is in.

Because each image can be converted into a set of numbers, we can find the similarity between different images. 

<img src='Img/Concept_map.png' width='400'>

## Computing Similarity

With numbers associated with each image, we can compare the similarity between images. Specifically, each image in the GEISHA database has 4 sets of numbers. For location, each image has 2 vectors: one as the output from the neural network (which are the network's predictions), and one as the actual labels for the image, since we already know the actual locations for any image in the database. For stage, the same applies: there is one number representing the prediction 

One challenge that arises is the problem of computing similarity. Since there are two different measurements (stage and locations), each with a different numerical structure (the output corresponding to location is a 141-dimensional vector, while the stage predctions are single numbers), it is hard to create a single metric that evaluates "similarity" between image. To solve this problem, I calculate separate similarities for location and stage, and normalized them to the same scale in order to combine them into a single metric.

### Overview of my methods

As described above, a difficulty arises in the different mathematical forms that 

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
