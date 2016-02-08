# -*- coding: utf-8 -*-
## @package ivf.core.sfs.constraints
#
#  ivf.core.sfs.constraints utility package.
#  @author      tody
#  @date        2016/02/05

import numpy as np
import scipy.sparse

import cv2

from ivf.core.sfs.silhouette_normal import silhouetteNormal
from ivf.util.timer import timing_func


def laplacianMatrix(image_size, num_elements=1):
    h, w = image_size
    num_verts = h * w * num_elements

    L = scipy.sparse.diags([-1, -1, -1, -1, 4],
                       [-num_elements, num_elements, - w * num_elements,  w * num_elements, 0],
                       shape=(num_verts, num_verts))
    return L


@timing_func
def silhouetteConstraints(A_8U, w_cons=1e+10, th_alpha=0.2, is_flat=False):
    h, w = A_8U.shape
    N0_32F = silhouetteNormal(A_8U)
    W_32F = th_alpha - A_8U / np.float32(np.max(A_8U))
    W_32F = W_32F / th_alpha
    W_32F = np.clip(W_32F, 0.0, 1.0)
    if is_flat:
        A, b = normalConstraintsFlat(W_32F, N0_32F)
    else:
        A, b = normalConstraints(W_32F, N0_32F)
    return w_cons * A, w_cons * b


## Normal constraints from the alpha mask and the initial normal.
def normalConstraints(W_32F, N0_32F):
    h, w = W_32F.shape[:2]
    num_verts = h * w
    diags = np.zeros(num_verts)
    W_flat = W_32F.flatten()
    cons_ids = np.where(W_flat > 0.0)
    diags[cons_ids] = W_flat[cons_ids]

    A = scipy.sparse.diags(diags, 0)

    b = np.zeros((num_verts, 3), dtype=np.float32)
    N0_flat = N0_32F.reshape(-1, 3)
    for i in xrange(3):
        b[:, i] = W_flat[:] * N0_flat[:, i]

    return A, b


def normalConstraintsFlat(W_32F, N0_32F):
    num_verts = W_32F.size

    W_flat3 = np.zeros(3 * num_verts)
    W_flat = W_32F.flatten()
    cons_ids = np.where(W_flat > 0.0)
    W_flat3[np.multiply(3, cons_ids)] = W_flat[cons_ids]
    W_flat3[np.multiply(3, cons_ids)+1] = W_flat[cons_ids]
    W_flat3[np.multiply(3, cons_ids)+2] = W_flat[cons_ids]

    A = scipy.sparse.diags(W_flat3, 0)

    b = W_flat3 * N0_32F.flatten()
    return A, b


def gradientConstraints(I_32F, scale=1.0, w_cons=1.0):
    sigma = 3.0
    gx = cv2.Sobel(I_32F, cv2.CV_64F, 1, 0, ksize=1)
    gx = cv2.GaussianBlur(gx, (0, 0), sigma)
    gx = gx.flatten()

    gy = - cv2.Sobel(I_32F, cv2.CV_64F, 0, 1, ksize=1)
    gy = cv2.GaussianBlur(gy, (0, 0), sigma)
    gy = gy.flatten()

    h, w = I_32F.shape[:2]
    num_verts = h * w

    diags = np.ones(num_verts)
    A = scipy.sparse.diags(diags, 0)

    b = np.zeros((num_verts, 3), dtype=np.float32)
    b[:, 0] = - scale * gx
    b[:, 1] = - scale * gy

    return w_cons * A, w_cons * b


@timing_func
def brightnessConstraints(L, I_32F, w_cons=1.0):
    h, w = I_32F.shape

    num_verts = h * w
    print num_verts

    I_flat = I_32F.reshape(h * w)

    #num_samples = 1000
    #sample_ids = np.random.randint(num_verts - 1, size=num_samples)
    sample_ids = np.where(I_flat > 0.2)
    num_samples = len(sample_ids)

    A = scipy.sparse.lil_matrix((num_samples, 3 * num_verts))
    print A.shape

    for i, sample_id in enumerate(sample_ids):
        A[i, 3 * sample_id] = L[0]
        A[i, 3 * sample_id + 1] = L[1]
        A[i, 3 * sample_id + 2] = L[2]

    A = scipy.sparse.csr_matrix(A)

    At = A.T
    AtA = At * A

    b = I_flat[sample_ids]

    print "At.shape", At.shape
    print "b.shape", b.shape

    Atb = At * b
    print "Atb.shape", Atb.shape
    return w_cons * AtA, w_cons * Atb


def laplacianConstraints(I_32F, scale=1.0, w_cons=1.0):
    sigma = 5.0
#     gx = cv2.Sobel(I_32F, cv2.CV_64F, 1, 0, ksize=1)
#     gx = cv2.GaussianBlur(gx, (0, 0), sigma)
#     gxx = cv2.Sobel(gx, cv2.CV_64F, 1, 0, ksize=1)
#     gxx = cv2.GaussianBlur(gxx, (0, 0), sigma)
#     gxx = gxx.flatten()
#
#     gy = - cv2.Sobel(I_32F, cv2.CV_64F, 0, 1, ksize=1)
#     gy = cv2.GaussianBlur(gy, (0, 0), sigma)
#     gyy = - cv2.Sobel(gy, cv2.CV_64F, 0, 1, ksize=1)
#     gyy = cv2.GaussianBlur(gyy, (0, 0), sigma)
#     gyy = gyy.flatten()

    I_L = cv2.Laplacian(I_32F, cv2.CV_32F, 8)
    I_L = I_L.flatten()

    h, w = I_32F.shape[:2]
    num_verts = h * w

    A = scipy.sparse.diags([-1, -1, -1, -1, 4],
                       [-1, 1, - w,  w, 0],
                       shape=(num_verts, num_verts))

    b = np.zeros((num_verts, 3), dtype=np.float32)
    b[:, 0] = - scale * I_L
    b[:, 1] = - scale * I_L

    b = A.T * b
    A = A.T * A

    return w_cons * A, w_cons * b


