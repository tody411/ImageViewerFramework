# -*- coding: utf-8 -*-
## @package inversetoon.core.lighting
#
#  inversetoon.core.lighting utility package.
#  @author      tody
#  @date        2015/07/31

import numpy as np
import cv2

from ivf.np.norm import normalizeVector
from ivf.core.shader.lambert import diffuse
from ivf.cv.normal import normalizeImage



## Normal sphere image.
def normalSphere(h=256, w=256):
    N_32F = np.zeros((h, w, 3))
    A_32F = np.zeros((h, w))

    for y in xrange(h):
        N_32F[y, :, 0] = np.linspace(-1.05, 1.05, w)

    for x in xrange(w):
        N_32F[:, x, 1] = np.linspace(1.05, -1.05, w)

    r_xy = N_32F[:, :, 0] ** 2 + N_32F[:, :, 1] ** 2
    N_32F[r_xy < 1.0, 2] = np.sqrt(1.0 - r_xy[r_xy < 1.0])
    N_32F[r_xy > 1.0, 2] = 0.0
    N_32F = normalizeImage(N_32F)
    A_32F[r_xy < 1.0] = 1.0 - r_xy[r_xy < 1.0] ** 100
    A_32F = cv2.bilateralFilter(np.float32(A_32F), 0, 0.1, 2)
    return N_32F, A_32F


## Light sphere image for the light direction.
def lightSphere(L, h=256, w=256):
    L = normalizeVector(L)

    N_32F, A_32F = normalSphere(h, w)
    I_32F = diffuse(N_32F, L)
    I_32F = I_32F * A_32F
    return I_32F

