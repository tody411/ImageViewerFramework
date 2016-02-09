# -*- coding: utf-8 -*-
## @package ivf.core.sfs.depth_from_gradient
#
#  ivf.core.sfs.depth_from_gradient utility package.
#  @author      tody
#  @date        2016/02/08

import numpy as np
import scipy.sparse
import cv2

from ivf.core.sfs.constraints import l2Regularization, laplacianMatrix
from ivf.core.solver import amg_solver


def gradientConstraints(I_32F, w_cons=1.0):
    epsilon = 0.01

    gx = cv2.Sobel(I_32F, cv2.CV_32F, 1, 0, ksize=1)
    gx = cv2.GaussianBlur(gx, (0, 0), 5.0)
    #gx = smoothGradient(gx)
    gxx = cv2.Sobel(gx, cv2.CV_32F, 1, 0, ksize=1)
    gxx = gxx.flatten()

    gy = cv2.Sobel(I_32F, cv2.CV_32F, 0, 1, ksize=1)
    gy = cv2.GaussianBlur(gy, (0, 0), 5.0)
    #gy = smoothGradient(gy)
    gyy = cv2.Sobel(gy, cv2.CV_32F, 0, 1, ksize=1)
    #gyy = cv2.bilateralFilter(gyy,15,20,10)
    gyy = gyy.flatten()

    h, w = I_32F.shape[:2]
    num_verts = h * w
    A = scipy.sparse.diags([-1, -1, -1, -1, 4],
                       [1, w, -1, -w, 0],
                       shape=(num_verts, num_verts))

    #AtA = A.T * A

    b = - 100.0 * (gxx + gyy)
    #Atb = A.T * b
    return w_cons * A, w_cons * b


def depthFromGradient(I_32F, A_8U):
    if A_8U is not None:
        I_32F = preProcess(I_32F, A_8U)

    h, w = I_32F.shape[:2]

    A_g, b_g = gradientConstraints(I_32F, w_cons=1.0)
    A_rg = l2Regularization(h*w, w_rg=0.000001)
    A_L = laplacianMatrix((h, w))

    A = A_g + A_rg
    b = b_g

    D_flat = amg_solver.solve(A, b)
    D_32F = D_flat.reshape(h, w)

    return D_32F


def smoothGradient(gx):
    h, w = gx.shape[:2]
    A_L = laplacianMatrix((h, w))

    w_g = 1.0
    gx_flat = gx.flatten()
    cons_ids = np.where(gx_flat > 0.01 * np.max(0.0))
    num_verts = h * w
    diags = np.zeros(num_verts)
    diags[cons_ids] = w_g

    A = scipy.sparse.diags(diags, 0) + A_L

    b = np.zeros(num_verts, dtype=np.float32)
    b[cons_ids] = w_g * gx_flat[cons_ids]

    gx_flat = amg_solver.solve(A, b)
    gx = gx_flat.reshape(h, w)
    print gx.shape
    return np.float32(gx)

def preProcess(I0_32F, A_8U):
    foreground = A_8U > 0.5 * np.max(A_8U)
    background = A_8U == 0

    I_32F = np.array(I0_32F)
    I_32F[background] = np.min(I_32F)

    I_min, I_max = np.min(I_32F), np.max(I_32F)
    I_32F = (I_32F - I_min) / (I_max - I_min)

    I_32F = cv2.bilateralFilter(I_32F,15,20,10)

    sigma = 10.0
    for i in xrange(10):
        I_32F = cv2.GaussianBlur(I_32F, (0, 0), sigma)
        I_32F[foreground] = I0_32F[foreground]

    return I_32F