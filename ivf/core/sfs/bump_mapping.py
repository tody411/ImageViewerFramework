# -*- coding: utf-8 -*-
## @package ivf.core.sfs.bump_mapping
#
#  ivf.core.sfs.bump_mapping utility package.
#  @author      tody
#  @date        2016/02/10

import numpy as np
import cv2

from ivf.cv.normal import normalizeImage


def bumpNormal(D_32F, scale=1.0, sigma=1.0):
    gx = cv2.Sobel(D_32F, cv2.CV_64F, 1, 0, ksize=1)
    gx = cv2.GaussianBlur(gx, (0, 0), sigma)

    gy = -cv2.Sobel(D_32F, cv2.CV_64F, 0, 1, ksize=1)
    gy = cv2.GaussianBlur(gy, (0, 0), sigma)

    h, w = D_32F.shape[:2]
    N_32F = np.zeros((h, w, 3), dtype=np.float32)
    N_32F[:, :, 0] = -scale * gx
    N_32F[:, :, 1] = -scale * gy
    N_32F[:, :, 2] = 1.0
    N_32F = normalizeImage(N_32F, th=1.0)

    return N_32F

def bumpMapping(N_32F, D_32F):
    pass
