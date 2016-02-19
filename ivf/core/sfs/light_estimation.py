# -*- coding: utf-8 -*-
## @package ivf.core.sfs.light_estimation
#
#  ivf.core.sfs.light_estimation utility package.
#  @author      tody
#  @date        2016/02/12

import numpy as np
import cv2
from ivf.np.norm import normalizeVector


def lightEstimation(I_32F, N_32F, A_8U=None):
    I = I_32F.flatten()
    N = N_32F.reshape(-1, 3)
    if A_8U is not None:
        I = I_32F[A_8U > 0.5 * np.max(A_8U)]
        N = N_32F[A_8U > 0.5 * np.max(A_8U), :]

    num_samples = 2000
    sample_ids = np.random.randint(len(I) - 1, size=num_samples)

    I = I[sample_ids]
    N = N[sample_ids]

    I_avg = np.average(I)
    N_avg = np.average(N, axis=0)

    #I = I - 0.8 * I_avg
    #N = N - 0.8 * N_avg

    A = np.dot(N.T, N)
    b = np.dot(N.T, I)

    L = np.linalg.solve(A, b)

    L = normalizeVector(L)

    return L


def lightEstimationLaplacian(I_32F, N_32F, A_8U=None):
    sigma = 3.0
    I_lap = cv2.Laplacian(I_32F, cv2.CV_32F, ksize=1)
    I_lap = cv2.GaussianBlur(I_lap, (0, 0), sigma)
    N_lap = cv2.Laplacian(N_32F, cv2.CV_32F, ksize=1)
    N_lap = cv2.GaussianBlur(N_lap, (0, 0), sigma)

    return lightEstimation(I_lap, N_lap, A_8U)


def lightEstimationByVoting(W_32F, N_32F, A_8U=None):
    W = W_32F.flatten()

    N = N_32F.reshape(-1, 3)
    if A_8U is not None:
        W = W_32F[A_8U > 0.5 * np.max(A_8U)]
        N = N_32F[A_8U > 0.5 * np.max(A_8U), :]

    num_samples = 2000
    sample_ids = np.random.randint(len(W) - 1, size=num_samples)

    W = W[sample_ids]
    N = N[sample_ids]

    W /= np.max(W)
    W = W ** 1.0

    L = np.dot(N.T, W)
    L = normalizeVector(L)
    return L
