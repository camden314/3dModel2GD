import numpy as np
import random
from render import *
import os.path
import sys

try:
    blend_data = np.load(os.path.join(os.path.expanduser('~'), '.blend.npz'),
                         allow_pickle=True)
except FileNotFoundError:
    sys.stderr.write("\033[0;31m[Error] Make sure to run the blender script"
                     "before the drawing script\033[0m\n")
    exit(1)

faces = blend_data['arr_0']
camera_mat = blend_data['arr_1']
inverse = np.linalg.inv(camera_mat)


def to2D(x, y, z, width=7, height=12):  # Project 3d points onto a 2d plane
    vector = np.array([[x], [y], [z], [1]])
    step1 = inverse @ vector

    x, y, z, w = step1[0, 0], step1[1, 0], step1[2, 0], step1[3, 0]

    x /= w
    y /= w
    z /= w

    x = (x + 1) * width / 2.
    y = (y + 1) * height / 2.
    return np.array([x, y])

tris = []

for face in faces:
    tri = []
    for indx in range(3):
        verts = face[indx]
        tri.append(to2D(*verts.tolist()[:3]))
    tris.append(tri)

tris = np.array(tris)
test = level.Level("test")
pogs = level.Transformer()
c = 0
for tri in tris:
    pogs.appendTransformer(Triformer.fromPoints((tri * 4000)))
    c += 1

pogs.scale(0.25) \
    .moveTo(x=500, y=500) \
    .addToLevel(test)
msgport.uploadToGD(test, per=7000)
