import level
import msgport
import numpy as np
from level import Block
from math import acos, hypot, sqrt

YCONST = 0

def centeroid(arr):
	length = arr.shape[0]
	sum_x = np.sum(arr[:, 0])
	sum_y = np.sum(arr[:, 1])
	return sum_x/length, sum_y/length
def getDistance(p1,p2):
	dist = sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
	return dist

globpiv = []
class Triformer(level.Transformer):
	def __init__(self, *blocks):
		super().__init__(*blocks)
		self.lineLength = 0

		self.triA = 0
		self.triB = 0
		self.triC = 0

		self.triab = 0
	def rotateBeginning(self, degrees=90, modifier=1):
		global globpiv
		#self.blocks.sort(key=lambda b:b.coords()[0])
		if modifier==-1:
			self.blocks.reverse()
		globpiv = (self.blocks[0].coords()[0]-(14.6*modifier), self.blocks[0].coords()[1]+YCONST)
		#print(globpiv)
		self.rotate(degrees, pivot=globpiv)
		if modifier==-1:
			self.blocks.reverse()
		return self
	@classmethod
	def createLine(cls, x, y, length, end=False):
		blocks = []
		x+=15
		y-=YCONST
		if end:
			x-=length
		fullturns = int(length//30)
		for i in range(fullturns):
			blocks.append(Block(blockid=579, x_position=x+(30*i), y_position=y))

		if length%30!=0:
			blocks.append(Block(blockid=579, x_position=x+(30*(fullturns-1)+(length%30)), y_position=y))
		
		if end:
			blocks.reverse()
			pass
		retvalue = cls(*blocks)
		retvalue.lineLength = length
		return retvalue
	def attachLineAtStart(self, length, clear=False):
		global globpiv
		globpiv = [self.blocks[0].coords()[0], self.blocks[0].coords()[1]+YCONST]

		globpiv[0] -= np.cos(np.deg2rad(float(self.blocks[0]['rotation'])))*15
		globpiv[1] += np.sin(np.deg2rad(float(self.blocks[0]['rotation'])))*15

		line = Triformer.createLine(globpiv[0], globpiv[1], length, end=False)

		if clear:
			self.clear()
		self.appendTransformer(line)
		self.lineLength = line.lineLength
		return self

	def attachLineAtEnd(self, length, clear=False):
		global globpiv
		globpiv = [self.blocks[-1].coords()[0], self.blocks[-1].coords()[1]]

		globpiv[0] += (np.cos(np.deg2rad(float(self.blocks[-1]['rotation'])))*15)
		globpiv[1] -= (np.sin(np.deg2rad(float(self.blocks[-1]['rotation'])))*15)-YCONST

		line = Triformer.createLine(globpiv[0], globpiv[1], length, end=False)
		#globpiv = [line.blocks[0].coords()[0]-15, line.blocks[0].coords()[1]+(YCONST)]
		if clear:
			self.clear()
		self.appendTransformer(line)
		self.lineLength = line.lineLength
		return self

	def findTriCenter(self):
		global globpiv
		start = (self.blocks[0].coords()[0]-14.6, self.blocks[0].coords()[1]+YCONST)

		pointA = start

		pointC = [start[0]+self.triA, start[1]]

		pointB = [start[0], start[1]]

		pointB[0] += np.cos(np.deg2rad(self.triab))*(self.triB-0.6)
		pointB[1] -= np.sin(np.deg2rad(self.triab))*(self.triB-0.6)

		globpiv = centeroid(np.array([pointA,pointB,pointC]))

		return centeroid(np.array([pointA,pointB,pointC]))

	def scaleTri(self, X=2, origin='d'):
		if origin=='d':
			Px, Py = self.findTriCenter()
		else:
			Px, Py = origin
		for b in self.blocks:
			Ax, Ay = b.coords()

			sx = X * (Ax - Px) + Px
			sy = X * (Ay - Py) + Py

			if b['size']=='0':
				b['size']=1
			print(b['size'])
			b['size'] = float(b['size'])*X
			b.setCoords(sx,sy)
		return self
	def fillTri(self):
		x1, y1 = self.findTriCenter()
		x2, y2 = (self.blocks[0].coords()[0]-14.6, self.blocks[0].coords()[1]+YCONST)
		dist = int((hypot(x2 - x1, y2 - y1)//4)+2)

		i=1
		while min(self.triA, self.triB, self.triC)/i>30:
			tr = self.__class__.createTri(x2, y2, self.triA/i, self.triB/i, self.triC/i)

			x3 = (1/i)*(x2 - (x2+self.triA)) + self.triA
			tr2 = self.__class__.createTri(x3+x2, y2, self.triA/i, self.triB/i, self.triC/i)
			self.appendTransformer(tr).appendTransformer(tr2)
			i+=0.25/dist
		return self
	@classmethod
	def createTri(cls, x, y, A=30, B=40, C=50):
		try:
			ab = np.rad2deg(acos((A * A + B * B - C * C)/(2.0 * A * B)))
			ac = np.rad2deg(acos((A * A + C * C - B * B)/(2.0 * A * C)))
		except ValueError:
			raise ValueError("Invalid triangle with A=%d B=%d C=%d"%(A,B,C))

		triA = cls.createLine(x, y, A)
		triB = triA.duplicate().attachLineAtStart(B, clear=True).rotateBeginning(ab)
		triC = triA.duplicate().attachLineAtEnd(C, clear=True).move(x=-1).rotateBeginning(180+(-1*ac))
		out = triA.appendTransformer(triC).appendTransformer(triB)

		out.triA, out.triB, out.triC = triA.lineLength, triB.lineLength, triC.lineLength
		out.triab = ab
		return out
	@classmethod
	def fromPoints(cls, vertices):
		pointAB, pointAC, pointBC = vertices

		blks = level.Transformer(Block(blockid=916, x_position=pointAB[0],y_position=pointAB[1], size=0.2, color1=3, group_parent=1),
								 Block(blockid=916, x_position=pointAC[0],y_position=pointAC[1], size=0.2, color1=3, group_parent=1),
								 Block(blockid=916, x_position=pointBC[0],y_position=pointBC[1], size=0.2, color1=3, group_parent=1))

		pointAC, pointBC = pointBC, pointAC

		lineA = getDistance(pointAB, pointAC)
		lineB = getDistance(pointAB, pointBC)
		lineC = getDistance(pointAC, pointBC)

		relativeToOrigin = pointAC-pointAB

		dgs = np.rad2deg(np.arctan2(relativeToOrigin[1],relativeToOrigin[0]))

		if min(lineA, lineB, lineC)>=14:
			tri = cls.createTri(pointAB[0],pointAB[1], A=lineA, B=lineB, C=lineC).rotateBeginning(-dgs)
		else:
			tri = level.Transformer()
			print("unpog")

		#tri.appendTransformer(blks)
		return tri