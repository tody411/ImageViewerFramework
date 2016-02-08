# -*- coding: utf-8 -*-
## @package npr_sfs.core.sfs.lumo
#
#  Lumo [Johnston et al. 2002].
#  @author      tody
#  @date        2015/07/29


import numpy as np
import cv2
import pyamg
from pyamg.gallery import laplacian

from ivf.core.sfs.silhouette_normal import silhouetteNormal
from ivf.np.norm import normalizeVectors, l2NormVectors
from ivf.core.solver import amg_solver


## Normal constraints from the alpha mask and the initial normal.
def normalConstraints(A_8U, N0_32F, alpha_th=20, w_sil=1e+10):
    h, w = A_8U.shape

    L = laplacian.poisson((h, w))
    L_lil = L.tolil()

    A_flat = A_8U.flatten()
    sil_ids = np.where(A_flat < alpha_th)

    for sil_id in sil_ids:
        L_lil[sil_id, sil_id] = w_sil

    A = L_lil.tocsr()

    N0_flat = N0_32F.reshape(h * w, 3)
    N0_flat[A_flat > alpha_th, :] = 0.0

    b_all = w_sil * N0_flat
    b = np.zeros(b_all.shape)
    b[A_flat < alpha_th, :] = b_all[A_flat < alpha_th, :]

    return A, b


def computeNz(N):
    Nx, Ny = N[:, 0], N[:, 1]

    Nxy_sq = l2NormVectors(Nx) + l2NormVectors(Ny)
    Nz_sq = 1.0 - Nxy_sq
    Nz_sq = np.clip(Nz_sq, 0.0, 1.0)
    Nz = np.sqrt(Nz_sq)
    Nz = np.clip(Nz, 0.0, 1.0)

    N_new = np.array(N)
    N_new[:, 2] = Nz
    return N_new


def estimateNormal(A_8U):
    h, w = A_8U.shape
    N0_32F = silhouetteNormal(A_8U)
    A, b = normalConstraints(A_8U, N0_32F)

    N_flat = amg_solver.solve(A, b)
    N_flat = computeNz(N_flat)
    N_flat = normalizeVectors(N_flat)
    N_32F = N_flat.reshape(h, w, 3)

    return N0_32F, N_32F