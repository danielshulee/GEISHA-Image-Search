# GEISHA-Image-Search

Image search for [GEISHA](http://geisha.arizona.edu/geisha/), an online repository for gene expression in chicken embryos.

## GEISHA

## Problem

Often times in science, domain knowledge is needed to access or understand many useful resources, creating an annoying barrier in which knowledge is needed to learn. In my experience, developmental biology is no different. For example, [GEISHA](http://geisha.arizona.edu/geisha/) is an online database with images depicting gene expression in chicken embryos. It is a valuable resource for both research and learning, but with embryos in over 40 different stages of development and genes expressed in hundreds of different anatomical locations on the embryos, it can be overwhelming to make sense of the data.

<img src='http://geisha.arizona.edu/geisha/photos/R340.TBX4.S19.01.jpg' align="middle" width=300>

For each image, there are a few important pieces of metadata— the stage of embryo development, and the anatomical location (the patches stained blue). Currently, these two are the primary ways that one can use to query and find images. While this is useful, it requires a "bottom up" approach (understanding before doing), and those who currently have an image of an embryo have no way of finding similar ones. To address this problem, this project seeks to create an engine for [GEISHA](http://geisha.arizona.edu/geisha/) that allows easier browsing through image search.

### The Criteria for Similarity

As stated above, there are two important criteria for comparing embryos— stage and location.

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
