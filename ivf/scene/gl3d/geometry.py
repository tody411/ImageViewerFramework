# -*- coding: utf-8 -*-
## @package ivf.scene.gl3d.geometry
#
#  ivf.scene.gl3d.geometry utility package.
#  @author      tody
#  @date        2016/02/01


# Numpy modules
import numpy as np

# OpenGL modules
from OpenGL.GL import *
from OpenGL.GLUT import *
from ivf.util.timer import timing_func


def boundingBox(positions):
    p_min = np.min(positions, axis=0)
    p_max = np.max(positions, axis=0)
    return p_min, p_max


class Geometry:
    ## Constructor
    def __init__(self, positions=None, indexArray=None):
        self._vertexArray = positions
        self._normalArray = None
        self._indexArray = indexArray
        self._vertexColors = None
        self._texCoords = None
        self._primitiveType = GL_TRIANGLES

    def setPositions(self, positions):
        self._vertexArray = np.float32(positions)

    def positions(self):
        return self._vertexArray

    def boundingBox(self):
        return boundingBox(self._vertexArray)

    def hasNormals(self):
        return self._normalArray is not None

    def setNormals(self, normals):
        self._normalArray = normals

    def normals(self):
        return self._normalArray

    def setInexArray(self, indexArray):
        self._indexArray = indexArray

    def indexArray(self):
        return self._indexArray

    def setVertexColors(self, vertexColors):
        self._vertexColors = np.float32(vertexColors)

    def vertexColors(self):
        return self._vertexColors

    def hasVertexColors(self):
        return self._vertexColors is not None

    def setTexCoords(self, texCoords):
        self._texCoords = texCoords

    def hasTexCoords(self):
        return self._texCoords is not None

    def setPrimitiveType(self, primitiveType):
        self._primitiveType = primitiveType

    def empty(self):
        return self._vertexArray is None or self._indexArray is None

    def gl(self):
        if self.empty():
            return

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf(self._vertexArray)

        if self.hasTexCoords():
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glTexCoordPointerf(self._texCoords)

        if self.hasNormals():
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointerf(self._normalArray)

        if self.hasVertexColors():
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointerf(self._vertexColors)

        glDrawElementsui(self._primitiveType, self._indexArray)