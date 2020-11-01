#import matplotlib.pyplot as plt
import numpy as np
import random
#import matplotlib.pyplot as plt
from render import * 
import os.path
import sys

try:
	blend_data = np.load(os.path.join(os.path.expanduser('~'),'.blend.npz'), allow_pickle=True)
except FileNotFoundError:
	sys.stderr.write("\033[0;31m[Error] Make sure to run the blender script before the drawing script\033[0m\n")
	exit(1)

faces = blend_data['arr_0']
camera_mat = blend_data['arr_1']
inverse = np.linalg.inv(camera_mat)
def to2D(x,y,z, width=7, height=12):
	vector = np.array([[x],[y],[z], [1]])
	step1 = inverse @ vector

	x,y,z,w = step1[0,0], step1[1,0], step1[2,0], step1[3,0]

	x/=w
	y/=w
	z/=w

	x = (x+1)*width/2.
	y = (y+1)*height/2.
	return np.array([x,y])

tris = []
colors = []
faces = faces.tolist()
faces.sort(key=lambda x:x[0][2])
faces.reverse()

faces = np.array(faces)
for face in faces:
	tri = []
	_12dist = abs(face[1][2]-face[2][2])
	_10dist = abs(face[1][2]-face[0][2])
	colors.append((_12dist+_10dist)/3.)
	for indx in range(3):
		verts = face[indx]
		tri.append(to2D(*verts.tolist()[:3]))
	tris.append(tri)

tris = np.array(tris)

print("lol")
print(len(tris))
c = 0

a = np.array(colors)
colors = (150*(a - np.min(a))/np.ptp(a)).astype(int)+70

test = level.Level("test")

pogs = level.Transformer()
for tri in tris:
	#if c>800:
	#	break

	#plt.scatter(*tri.T, s=1)

	mult = 255-colors[c]
	hexcol = '#%02x%02x%02x' % (round(mult),round(mult),round(mult))

	#pol = plt.Polygon(tri)
	pogs.appendTransformer(Triformer.fromPoints((tri*4000)))
	#plt.gca().add_patch(pol)
	c+=1

pogs.scale(0.25) \
	.moveTo(x=500, y=500) \
	.addToLevel(test)
msgport.uploadToGD(test,per=7000)