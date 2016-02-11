# -*- coding: utf-8 -*-
## @package ivf.core.sfs.bump_mapping
#
#  ivf.core.sfs.bump_mapping utility package.
#  @author      tody
#  @date        2016/02/10

import numpy as np
import cv2

from ivf.cv.normal import normalizeImage
from ivf.np.norm import normVectors


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


def rotateVectors(A, N, cos_theta, sin_theta):
    p = np.dot(A, N) * A
    q = N - p
    r = np.cross(N, A)
    N_new = p + cos_theta * q + sin_theta * r
    return N_new


def tangentCoordinates(N_32F):
    N = N_32F.reshape(-1, 3)

    v_z = np.array([0.0, 0.0, 1.0])
    A = np.cross(N, v_z)

    sin_theta = normVectors(A)
    cos_theta = np.dot(N, v_z)

    v_x = np.array([1.0, 0.0, 0.0])
    v_y = np.array([0.0, 1.0, 0.0])

    T = np.zeros_like(N)
    T[:, :] = np.array([1.0, 0.0, 0.0])
    B = np.zeros_like(N)
    B[:, :] = np.array([0.0, 1.0, 0.0])

    sin_valid = sin_theta > 1e-4

    T[sin_valid, :] = rotateVectors(A, T[sin_valid, :], cos_theta[sin_valid], sin_theta[sin_valid])
    B[sin_valid, :] = rotateVectors(A, B[sin_valid, :], cos_theta[sin_valid], sin_theta[sin_valid])

    return T, B


def bumpMapping(N_32F, N_b_32):
    N_32F[:, :, 0] += N_b_32[:, :, 0]
    N_32F[:, :, 1] += N_b_32[:, :, 1]
    return N_32F
