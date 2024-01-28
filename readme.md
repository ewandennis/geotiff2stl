# GeoTIFF -> STL

Given a geoTIFF (a TIFF with floating point height field in channel 0), build a printable model.

The model is composed of a rectangular box whose top face is the relief map made from the TIFF height field.

# Dependencies
 - python 3
 - gdal
 - see requirements.txt for python deps

# Usage

Note: this tool needs an available GeoTIFF file to convert.
 
1. git clone this repo: `git clone $THIS_REPO`
1. `cd $THIS_REPO`
1. optional - make a virtual env for this repo: `python -m venv .`
1. install deps: `pip install -r requirements.txt`
1. `python tiff2stl.py $GEOTIFF.tif $OUTPUT.stl`

# Config Options
At the top of tiff2stl.py are several useful config options:

 - HSCALE - the amount to scale the model in X/Y (east/west, north/south) (defaults to 50 since I'm using OS Terrain-50 data to test)
 - VSCALE - the amount to scale the model in Z (elevation) 
 - BOXHEIGHT - the dimensions of the box under the model_

