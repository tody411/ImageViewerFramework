
# -*- coding: utf-8 -*-
## @package ivf.scene.3d.camera
#
#  ivf.scene.3d.camera utility package.
#  @author      tody
#  @date        2016/02/01



# Numpy module
import numpy as np

# OpenGL modules
from OpenGL.GL import *
from OpenGL.GLU import *


## Perspective camera
class PerspectiveCamera:

    ## Constructor
    def __init__(self, fov=45.0, aspect=1.0, near=1.0, far=100.0):
        self._fov = fov
        self._aspect = aspect
        self._near = near
        self._far = far

    def gl(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self._fov, self._aspect, self._near, self._far)
        glMatrixMode(GL_MODELVIEW)


## Orthographic camera
class OrthographicCamera:

    ## Constructor
    def __init__(self, left=-1.0, right=1.0, top=-1.0, bottom=1.0, near=-1.0, far=1.0):
        self._left = left
        self._right = right
        self._top = top
        self._bottom = bottom
        self._near = near
        self._far = far

    def gl(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self._left, self._right, self._top, self._bottom, self._near, self._far)
        glMatrixMode(GL_MODELVIEW)


def lookAtPositions(vertices):
    x_mean = 0.5 * (np.max(vertices[:, 0]) + np.min(vertices[:, 0]))
    y_mean = 0.5 * (np.max(vertices[:, 1]) + np.min(vertices[:, 1]))
    z_mean = 0.5 * (np.max(vertices[:, 2]) + np.min(vertices[:, 2]))

    xRange = np.max(vertices[:,0]) - np.min(vertices[:,0])
    yRange = np.max(vertices[:,1]) - np.min(vertices[:,1])
    zRange = np.max(vertices[:,2]) - np.min(vertices[:,2])

    boundingRange = np.linalg.norm( np.array([xRange, yRange, zRange]) )

    translate = [-x_mean, -y_mean, -z_mean]
    scale = 2.0 / boundingRange

    def gl():
        glScale(scale, scale, scale)
        glTranslate(translate[0], translate[1], translate[2])

    return gl


def lookAtBoundingBox(bb):
    p_mean = 0.5 * (bb[0] + bb[1])
    p_range = bb[1] - bb[0]

    scale = 2.0 / np.linalg.norm(p_range)
    translate = -p_mean

    def gl():
        glScale(scale, scale, scale)
        glTranslate(translate[0], translate[1], translate[2])

    return gl