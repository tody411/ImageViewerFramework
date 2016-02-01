
# -*- coding: utf-8 -*-
## @package npr_sfs.scene.light
#
#  npr_sfs.scene.light utility package.
#  @author      tody
#  @date        2015/11/17

import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Light:
    ## Constructor
    def __init__(self, light_no=0, L=None):
        self._L = np.array([0.0, 0.0, 1.0, 0.0])
        if L is not None:
            self._L = L
        self._light_no = light_no
        self._ambient = np.array([0.0, 0.0, 0.0, 1.0])
        self._diffuse = np.array([1.0, 1.0, 1.0, 1.0])
        self._specular = np.array([0.0, 0.0, 0.0, 1.0])

    def setLightNo(self, light_no):
        self._light_no = light_no

    def setLightDirection(self, L):
        self._L[:3] = L[:3]
        self._L[3] = 0.0

    def setAmbient(self, ambient):
        self._ambient = ambient

    def setDiffuse(self, diffuse):
        self._diffuse = diffuse

    def setSpecular(self, specular):
        self._specular = specular

    def gl(self):
        glEnable(GL_LIGHT0 + self._light_no)
        glLightfv(GL_LIGHT0 + self._light_no, GL_AMBIENT, self._ambient)
        glLightfv(GL_LIGHT0 + self._light_no, GL_DIFFUSE, self._diffuse)
        glLightfv(GL_LIGHT0 + self._light_no, GL_SPECULAR, self._specular)
        glLightfv(GL_LIGHT0 + self._light_no, GL_POSITION, self._L)