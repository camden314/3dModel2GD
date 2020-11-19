"""
Render file.

its the render part
"""

from math import acos, hypot, sqrt

import level

from level import Block

import msgport

import numpy as np


def centeroid(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x / length, sum_y / length


def getDistance(p1, p2):
    dist = sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    return dist


class Triformer(level.Transformer):
    def __init__(self, *blocks):
        super().__init__(*blocks)
        self.lineLength = 0

        self.triA = 0
        self.triB = 0
        self.triC = 0

        self.triab = 0

    def rotateBeginning(self, degrees=90, modifier=1):
        if modifier == -1:
            self.blocks.reverse()
        piv = self.blocks[0].coords()
        piv[0] -= (14.6 * modifier)

        self.rotate(degrees, pivot=piv)
        if modifier == -1:
            self.blocks.reverse()
        return self

    @classmethod
    def createLine(cls, x, y, length, end=False):
        blocks = []
        x += 15
        if end:
            x -= length
        fullturns = int(length // 30)
        for i in range(fullturns):
            blocks.append(Block(blockid=579, x_position=x + (30 * i),
                                y_position=y))
        if length % 30 != 0:
            x += (30 * (fullturns - 1) + (length % 30))
            blocks.append(Block(blockid=579, x_position=x, y_position=y))
        if end:
            blocks.reverse()
            pass
        retvalue = cls(*blocks)
        retvalue.lineLength = length
        return retvalue

    def attachLineAtStart(self, length, clear=False):
        piv = list(self.blocks[0].coords())

        piv[0] -= np.cos(np.deg2rad(float(self.blocks[0]['rotation']))) * 15
        piv[1] += np.sin(np.deg2rad(float(self.blocks[0]['rotation']))) * 15

        line = Triformer.createLine(piv[0], piv[1], length, end=False)

        if clear:
            self.clear()
        self.appendTransformer(line)
        self.lineLength = line.lineLength
        return self

    def attachLineAtEnd(self, length, clear=False):
        piv = list(self.blocks[-1].coords())

        piv[0] += np.cos(np.deg2rad(float(self.blocks[-1]['rotation']))) * 15
        piv[1] -= np.sin(np.deg2rad(float(self.blocks[-1]['rotation']))) * 15

        line = Triformer.createLine(piv[0], piv[1], length, end=False)

        if clear:
            self.clear()
        self.appendTransformer(line)
        self.lineLength = line.lineLength
        return self

    def findTriCenter(self):
        start = (self.blocks[0].coords()[0] - 14.6, self.blocks[0].coords()[1])

        pointA = start

        pointC = [start[0] + self.triA, start[1]]

        pointB = [start[0], start[1]]

        pointB[0] += np.cos(np.deg2rad(self.triab)) * (self.triB - 0.6)
        pointB[1] -= np.sin(np.deg2rad(self.triab)) * (self.triB - 0.6)

        return centeroid(np.array([pointA, pointB, pointC]))

    def scaleTri(self, X=2, origin='d'):
        if origin == 'd':
            Px, Py = self.findTriCenter()
        else:
            Px, Py = origin
        for b in self.blocks:
            Ax, Ay = b.coords()

            sx = X * (Ax - Px) + Px
            sy = X * (Ay - Py) + Py

            if b['size'] == '0':
                b['size'] = 1
            print(b['size'])
            b['size'] = float(b['size']) * X
            b.setCoords(sx, sy)
        return self

    def fillTri(self):
        x1, y1 = self.findTriCenter()
        x2, y2 = self.blocks[0].coords()
        x2 -= 14.6

        dist = int((hypot(x2 - x1, y2 - y1) // 4) + 2)

        i = 1
        while min(self.triA, self.triB, self.triC) / i > 30:
            x3 = (1 / i) * (x2 - (x2 + self.triA)) + self.triA

            tr = Triformer.createTri(x2, y2, self.triA / i, self.triB / i,
                                     self.triC / i)
            tr2 = Triformer.createTri(x3 + x2, y2, self.triA / i,
                                      self.triB / i, self.triC / i)

            self.appendTransformer(tr).appendTransformer(tr2)
            i += 0.25 / dist
        return self

    @classmethod
    def createTri(cls, x, y, A=30, B=40, C=50):
        try:
            ab = np.rad2deg(acos((A * A + B * B - C * C) / (2.0 * A * B)))
            ac = np.rad2deg(acos((A * A + C * C - B * B) / (2.0 * A * C)))
        except ValueError:
            raise ValueError("Invalid triangle with A=%d B=%d C=%d" % (A, B, C))

        triA = cls.createLine(x, y, A)
        triB = triA.duplicate().attachLineAtStart(B, clear=True) \
                               .rotateBeginning(ab)

        triC = triA.duplicate().attachLineAtEnd(C, clear=True) \
                               .move(x=-1) \
                               .rotateBeginning(180 + (-1 * ac))
        out = triA.appendTransformer(triC).appendTransformer(triB)

        out.triA = triA.lineLength
        out.triB = triB.lineLength
        out.triC = triC.lineLength

        out.triab = ab
        return out

    @classmethod
    def fromPoints(cls, vertices):
        pointAB, pointAC, pointBC = vertices

        pointAC, pointBC = pointBC, pointAC

        lineA = getDistance(pointAB, pointAC)
        lineB = getDistance(pointAB, pointBC)
        lineC = getDistance(pointAC, pointBC)

        relativeToOrigin = pointAC - pointAB

        dgs = np.rad2deg(np.arctan2(relativeToOrigin[1], relativeToOrigin[0]))

        if min(lineA, lineB, lineC) >= 14:
            tri = cls.createTri(pointAB[0], pointAB[1], lineA, lineB, lineC) \
                     .rotateBeginning(-dgs)
        else:
            tri = level.Transformer()
        return tri
