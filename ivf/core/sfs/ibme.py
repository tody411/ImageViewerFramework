# -*- coding: utf-8 -*-
## @package npr_sfs.core.sfs.ibme
#
#  Image-Based Material Editing [Kahn et al. 2006].
#  @author      tody
#  @date        2015/07/30

import numpy as np
import cv2

import matplotlib.pyplot as plt
from ivf.cv.normal import normalizeImage


def computeGradientNormals(D_32F, sigma=1.0):
    h, w = D_32F.shape

    gx = cv2.Sobel(D_32F, cv2.CV_64F, 1, 0, ksize=1)
    gx = cv2.GaussianBlur(gx, (0, 0), sigma)

    gy = cv2.Sobel(D_32F, cv2.CV_64F, 0, 1, ksize=1)
    gy = cv2.GaussianBlur(gy, (0, 0), sigma)

    g_max = max(np.max(gx), np.max(gy))
    g_scale = 100.0 / g_max

    T_32F = np.zeros((h, w, 3), dtype=np.float32)
    T_32F[:, :, 0] = 1.0
    T_32F[:, :, 2] = g_scale * gx

    B_32F = np.zeros((h, w, 3), dtype=np.float32)
    B_32F[:, :, 1] = 1.0
    B_32F[:, :, 2] = -g_scale * gy

    T_flat = T_32F.reshape(-1, 3)
    B_flat = B_32F.reshape(-1, 3)

    N_flat = np.cross(T_flat, B_flat)
    N_32F = N_flat.reshape(h, w, 3)
    N_32F = normalizeImage(N_32F)

    return N_32F


def depthRecovery(I_32F, sigma_range=0.1, sigma_space=10,
                  w_base=0.9, w_detail=0.1):
    BL = cv2.bilateralFilter(I_32F, -1, sigma_range, sigma_space)
    DL = I_32F - BL
    D_32F = w_base * BL + w_detail * DL
    h, w = I_32F.shape[:2]
    d_scale = 0.5 * 0.5 * (h+w)
    D_32F = d_scale * D_32F
    return D_32F


def estimateNormal(I_32F):
    D_32F = depthRecovery(I_32F)
    N_32F = computeGradientNormals(D_32F)
    return N_32F, D_32F
