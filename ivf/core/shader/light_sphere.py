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


## Light sphere image for the light direction.
def lightSphereWithBG(L, h=256, w=256, bg_color=np.array([1.0, 0.0, 0.0])):
    L = normalizeVector(L)

    N_32F, A_32F = normalSphere(h, w)
    I_32F = diffuse(N_32F, L)

    C_32F = np.zeros(N_32F.shape)
    C_32F[:, :] = bg_color

    for ci in xrange(3):
        C_32F[:, :, ci] = I_32F * A_32F + (1.0 - A_32F) * C_32F[:, :, ci]

    return np.clip(C_32F, 0.0, 1.0)


def lightSphereColorMap(L, h=256, w=256, v=0.0, v_min=0.0, v_max=1.0):
    t = (v - v_min) / (v_max - v_min)

    r = np.array([1.0, 0.0, 0.0])
    g = np.array([0.0, 1.0, 0.0])
    b = np.array([0.0, 0.0, 1.0])

    t1 = np.clip(2.0 * t, 0.0, 1.0)
    bg_color = (1.0 - t1) * b + t1 * g

    t2 = np.clip(2.0 * (t - 0.5), 0.0, 1.0)
    bg_color = (1.0 - t2) * bg_color + t2 * r

    return lightSphereWithBG(L, h, w, bg_color)
