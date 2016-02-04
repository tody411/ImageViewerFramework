
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

#     N_32F = np.zeros((h, w, 3), dtype=np.float32)
#     N_32F[:, :, 0] = -gx
#     N_32F[:, :, 1] = gy
#     N_32F[:, :, 2] = 1

    T_32F = np.zeros((h, w, 3), dtype=np.float32)
    T_32F[:, :, 0] = 1.0
    T_32F[:, :, 2] = gx

    B_32F = np.zeros((h, w, 3), dtype=np.float32)
    B_32F[:, :, 1] = 1.0
    B_32F[:, :, 2] = -gy

    T_flat = T_32F.reshape(-1, 3)
    B_flat = B_32F.reshape(-1, 3)

    N_flat = np.cross(T_flat, B_flat)
    N_32F = N_flat.reshape(h, w, 3)

    N_32F = normalizeImage(N_32F)
    return N_32F