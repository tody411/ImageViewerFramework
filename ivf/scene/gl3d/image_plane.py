
# Numpy modules
import numpy as np

# OpenGL modules
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from mesh import Mesh

from ivf.cv.image import to32F, to8U
from ivf.util.timer import timing_func


class ImagePlane:
    ## Constructor
    def __init__(self, image):
        self._image = to32F(image)
        self._geometry = Mesh()
        self._initGeometry()

    def gl(self):
        self._geometry.gl()

    def boundingBox(self):
        return self._geometry.boundingBox()

    def setDepth(self, D_32F):
        D_flat = D_32F.ravel()
        self._points[:, 2] = D_flat
        self._geometry.setPositions(self._points)

    @timing_func
    def _initPoints(self, h, w):
        ys = np.linspace(h-1, 0, h)
        xs = np.linspace(0, w-1, w)
        px, py = np.meshgrid(xs, ys, sparse=False)
        px = px.ravel()
        py = py.ravel()
        pz = np.zeros(len(py))

        return np.array([px, py, pz]).T

    @timing_func
    def _initIndexArray(self, h, w):
        ys = np.arange(h - 1)
        xs = np.arange(w - 1)

        fx, fy = np.meshgrid(xs, ys, sparse=False)
        fx = fx.ravel()
        fy = fy.ravel()

        f1 = w * fy + fx
        f2 = f1 + 1
        f3 = f2 + w
        f4 = f3 - 1

        return np.array([f1, f2, f3, f4]).T

    @timing_func
    def _initGeometry(self):
        h, w = self._image.shape[:2]

        self._points = self._initPoints(h, w)
        colors = self._image.reshape(-1, self._image.shape[2])

        index_array = self._initIndexArray(h, w)

        self._geometry.setPositions(self._points)
        self._geometry.setVertexColors(colors)
        self._geometry.setInexArray(index_array)


class TexturePlane:
    ## Constructor
    def __init__(self, image):
        self._image = to8U(image)
        self._geometry = Mesh()
        self._initGeometry()
        self._texture_id = None

    def gl(self):
        glEnable( GL_TEXTURE_2D )

        if self._texture_id is None:
            self._texture_id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, self._texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, self._image.shape[1], self._image.shape[0], GL_RGBA, GL_UNSIGNED_BYTE, self._image)

        self._geometry.gl()

    def boundingBox(self):
        return self._geometry.boundingBox()

    @timing_func
    def _initGeometry(self):
        h, w = self._image.shape[:2]

        points = np.array([(0.0, 0.0, 0.0), (w - 1.0, 0.0, 0.0), (w - 1.0, h - 1.0, 0.0),  (0.0, h - 1.0, 0.0)])

        index_array = np.array([(0, 1, 2, 3)])

        tex_coords = np.array([(0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)])

        self._geometry.setPositions(points)
        self._geometry.setInexArray(index_array)
        self._geometry.setTexCoords(tex_coords)