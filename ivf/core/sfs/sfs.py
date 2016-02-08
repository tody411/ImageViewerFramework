# -*- coding: utf-8 -*-
## @package ivf.cmds.sfs.sfs
#
#  ivf.cmds.sfs.sfs utility package.
#  @author      tody
#  @date        2016/02/05

import numpy as np
from ivf.cv.image import luminance
from ivf.np.norm import normVectors


class ShapeFromShading(object):
    def __init__(self, name, L=None, C_32F=None, A_8U=None):
        super(ShapeFromShading, self).__init__()
        self._name = name
        self._L = L
        self._C0_32F = C_32F
        self._C_32F = np.array(C_32F)
        self._I0_32F = self._computeBrightness(C_32F)
        self._I_32F = np.array(self._I0_32F)
        self._A_8U = A_8U
        self._N_32F = None

    def name(self):
        return self._name

    def setAlpha(self, A_8U):
        self._A_8U = A_8U

    def setImage(self, C_32F):
        self._C0_32F = C_32F

    def shading(self):
        return self._C_32F

    def shadingError(self):
        C_diff = self._C_32F - self._C0_32F
        h, w = C_diff.shape[:2]
        C_diff = C_diff.reshape(-1, 3)
        C_diff = normVectors(C_diff)
        C_diff = C_diff.reshape(h, w)
        return C_diff

    def normal(self):
        return self._N_32F

    def brightness(self):
        return self._I_32F

    def brightnessError(self):
        return np.abs(self._I_32F - self._I0_32F)

    def run(self):
        self._runImp()

    def _runImp(self):
        pass

    def _computeBrightness(self, C_32F):
        return luminance(np.float32(C_32F))
