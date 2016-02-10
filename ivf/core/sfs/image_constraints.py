# -*- coding: utf-8 -*-
## @package ivf.core.sfs.image_constraints
#
#  ivf.core.sfs.image_constraints utility package.
#  @author      tody
#  @date        2016/02/09

import numpy as np
import cv2

from ivf.core.solver import image_solver
from ivf.core.sfs.silhouette_normal import silhouetteNormal
from ivf.cv.normal import normalizeImage
from ivf.np.norm import l2NormVectors


def laplacian(image):
    image_L = cv2.Laplacian(image, cv2.CV_64F) / 4.0
    return image_L


def laplacianConstraints(w_c=1.0):
    def func(image):
        image_smooth = laplacian(image) + image
        return w_c, image_smooth
    return func


def brightnessConstraints(L, I_32F, w_c=1.0):
    I_level = image_solver.LevelImage(I_32F)

    def func(N_32F):
        I_32F_level = I_level.level(N_32F)
        h, w = N_32F.shape[:2]
        NL = np.dot(N_32F.reshape(-1, 3), L)
        NL = np.clip(NL, 0.0, 1.0)
        dI = I_32F_level.reshape(h*w) - NL
        dI = dI.reshape(h, w)
        N_I = np.zeros_like(N_32F)
        for i in range(3):
            N_I[:, :, i] = N_32F[:, :, i] + dI[:, :] * L[i]
        return w_c, N_I
    return func


def silhouetteConstraints(A_8U, w_c=1.0, th_alpha=0.2):
    h, w = A_8U.shape
    N0_32F = silhouetteNormal(A_8U)
    W_32F = th_alpha - A_8U / np.float32(np.max(A_8U))
    W_32F *= 1.0 / th_alpha

    return normalConstraints(W_32F, N0_32F, w_c)


def normalConstraints(W_32F, N0_32F, w_c=1.0):
    N0_level = image_solver.LevelImage(N0_32F)
    W_level = image_solver.LevelImage(W_32F)

    def func(N_32F):
        W_32F_level = W_level.level(N_32F)
        N0_32F_level = N0_level.level(N_32F)

        N_new = np.array(N_32F)
        cons_ids = W_32F_level > 0

        for i in xrange(3):
            N_new[cons_ids, i] = N0_32F_level[cons_ids, i] / W_32F_level[cons_ids]

        return w_c, N_new
    return func


def postNormalize(th=0.0):
    def func(N):
        N = normalizeImage(N, th)
        return N
    return func


def NxyToNz(N_32F):
    N = N_32F.reshape(-1, 3)
    Nx, Ny = N[:, 0], N[:, 1]

    Nxy_sq = l2NormVectors(Nx) + l2NormVectors(Ny)
    Nz_sq = 1.0 - Nxy_sq
    Nz_sq = np.clip(Nz_sq, 0.0, 1.0)
    Nz = np.sqrt(Nz_sq)
    Nz = np.clip(Nz, 0.0, 1.0)

    N_new = np.array(N)
    N_new[:, 2] = Nz
    return N_new.reshape(N_32F.shape)