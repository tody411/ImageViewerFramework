# -*- coding: utf-8 -*-
## @package inversetoon.core.lighting
#
#  inversetoon.core.lighting utility package.
#  @author      tody
#  @date        2015/07/31

import numpy as np

from ivf.np.norm import normalizeVector
from ivf.core.shader.lambert import diffuse



## Normal sphere image.
def normalSphere(h=256, w=256):
    N_32F = np.zeros((h, w, 3))
    A_32F = np.zeros((h, w))

    for y in xrange(h):
        N_32F[y, :, 0] = np.linspace(-1.0, 1.0, w)

    for x in xrange(w):
        N_32F[:, x, 1] = np.linspace(1.0, -1.0, w)

    r_xy = N_32F[:, :, 0] ** 2 + N_32F[:, :, 1] ** 2
    N_32F[r_xy < 1.0, 2] = np.sqrt(1.0 - r_xy[r_xy < 1.0])
    A_32F[r_xy < 1.0] = 1.0 - r_xy[r_xy < 1.0] ** 100

    return N_32F, A_32F


## Light sphere image for the light direction.
def lightSphere(L, h=256, w=256):
    L = normalizeVector(L)

    N_32F, A_32F = normalSphere(h, w)
    I_32F = diffuse(N_32F, L)
    I_32F = I_32F * A_32F
    return I_32F

