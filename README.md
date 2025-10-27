# t4gpd
Set of tools based on Python, GeoPandas and Shapely to achieve urban geoprocessing

## Pre-requisites
To be able to use the **t4gpd** plugin, perform geoprocessing and display your own maps, you need a Python3 interpreter and recent versions of the geopandas, matplotlib, numpy, and shapely libraries. One possibility is to install a [Miniconda3](https://docs.conda.io/en/latest/miniconda.html) environment, in which you will first create and then configure a new environment (we will call it gpd):
> conda create -n gpd

> conda activate gpd

> conda config --env --add channels conda-forge

> conda config --env --set channel_priority strict

> conda install python=3.10 geopandas=0.12.2 contextily geocube imageio jupyterlab mapclassify matplotlib matplotlib-scalebar meshio networkx notebook openpyxl overpy plotly pvlib Pyarrow pymap3d pyogrio pysolar pyvista pywavelets rasterio scikit-learn scipy seaborn windrose xlrd xlwt

> pip install dijkstar pythermalcomfort suntimes

## Installation instructions
As **t4gpd** is now on [PyPI](https://pypi.org/project/t4gpd/), the easiest way to install the latest version is to use the pip command as follows:
> pip install t4gpd

Alternatively, you can download the **t4gpd** latest version from the [PyPI](https://pypi.org/project/t4gpd/#files). Then, install the Python3 plugin you downloaded:
> pip install t4gpd-0.9.9.tar.gz

## Read the documentation
Go to [https://t4gpd-docs.readthedocs.io](https://t4gpd-docs.readthedocs.io) to consult the documentation.

