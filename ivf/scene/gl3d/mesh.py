
# -*- coding: utf-8 -*-
## @package npr_sfs.scene.mesh
#
#  npr_sfs.scene.mesh utility package.
#  @author      tody
#  @date        2015/10/17

# Numpy modules
import numpy as np

# OpenGL modules
from OpenGL.GL import *
from OpenGL.GLUT import *

from geometry import Geometry


class Mesh:
    ## Constructor
    def __init__(self, positions=None, indexArray=None):
        self._geometry = Geometry(positions)
        self.setInexArray(indexArray)

    def setPositions(self, positions):
        self._geometry.setPositions(positions)

    def boundingBox(self):
        return self._geometry.boundingBox()

    def setNormals(self, normals):
        self._geometry.setNormals(normals)

    def setInexArray(self, indexArray):
        if indexArray is None:
            return

        indexArray = np.array(indexArray)

        if len(indexArray.shape) == 1:
            self._geometry.setInexArray(indexArray.ravel())
            return

        elif indexArray.shape[1] == 3:
            self._geometry.setPrimitiveType(GL_TRIANGLES)

        elif indexArray.shape[1] == 4:
            self._geometry.setPrimitiveType(GL_QUADS)

        self._geometry.setInexArray(indexArray.ravel())

    def setVertexColors(self, vertexColors):
        self._geometry.setVertexColors(vertexColors)

    def setTexCoords(self, texCoords):
        self._geometry.setTexCoords(texCoords)

    def gl(self):
        self._geometry.gl()
