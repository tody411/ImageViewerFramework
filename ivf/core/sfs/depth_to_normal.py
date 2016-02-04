
# -*- coding: utf-8 -*-
## @package ivf.core.sfs.depth_to_normal
#
#  ivf.core.sfs.depth_to_normal utility package.
#  @author      tody
#  @date        2016/02/04

import numpy as np
import cv2

from ivf.cv.normal import normalizeImage


def depthToNormal(D_32F):
    h, w = D_32F.shape
    gx = cv2.Sobel(D_32F, cv2.CV_64F, 1, 0, ksize=1)
    gy = cv2.Sobel(D_32F, cv2.CV_64F, 0, 1, ksize=1)

    N_32F = np.zeros((h, w, 3), dtype=np.float32)
    N_32F[:, :, 0] = -gx
    N_32F[:, :, 1] = gy
    N_32F[:, :, 2] = 2

    N_32F = normalizeImage(N_32F)
    return N_32F
