# 3d Model to GD
A set of python scripts that allow you to draw 3d model wireframes into the geometry dash editor.

___
## Setup
___
First, make sure you have [Python 3](https://www.python.org/downloads/release/python-386/) installed. If you don't already have [Blender](https://www.blender.org/download/), you should download that as well. You also need to install `numpy` as a python module, via `python3 -m pip install numpy` for mac and `py -m pip install numpy` for windows.

___
## How to run
___
The first thing you need to do is open blender, open the text editor in the project, and paste in the contents of the `blend.py` file. Before you continue to the next steps make sure to apply all modifiers. 

Then, enable top perspective mode (you can do that by pressing '75'), enter edit mode, and select all of the visible faces. Make sure to triangulate all of the faces. Scale down the model until all dimensions are around 1m or less. Press the "Run Script" button in the text editor

Next, make sure GD is in the editor and that the live editor library is injected. Run the `draw.py` file and you should get the wireframe of the model in the gd editor!

