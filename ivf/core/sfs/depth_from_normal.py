
# -*- coding: utf-8 -*-
## @package npr_sfs.core.sfs.depth_from_normal
#
#  npr_sfs.core.sfs.depth_from_normal utility package.
#  @author      tody
#  @date        2015/12/09

import numpy as np
import scipy.sparse
from scipy import ndimage
import cv2

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import pyamg
from pyamg.gallery import laplacian
from ivf.util.timer import timing_func
from ivf.cv.normal import normalizeImage


def initialDepth(N_32F, A_8U):
    D0_32F = np.zeros(A_8U.shape)
    foreground = A_8U > 200
    D0_32F[foreground] = N_32F[foreground, 2]
    return D0_32F


def dxy(image_size):
    h, w = image_size
    max_size = float(max(h, w))

    dx = 0.5 / max_size
    dy = 0.5 / max_size

    return dx, dy


def xyCoordinates(image_size):
    h, w = image_size
    max_size = float(max(h, w))

    w_scaled = w / max_size
    h_scaled = h / max_size

    ys = np.linspace(-h_scaled, h_scaled, h)
    xs = np.linspace(-w_scaled, w_scaled, w)
    return xs, ys


@timing_func
def initialDepthConstraint(N_32F, A_8U, w0=0.1):
    D0_32F = initialDepth(N_32F, A_8U)

    h, w = A_8U.shape[:2]
    num_verts = h * w

    diags = np.ones(num_verts)

    A = w0 * scipy.sparse.diags(diags, 0)
    b = w0 * D0_32F.flatten()
    return A, b


@timing_func
def laplacianConstraints(image_size, num_elements=1, w_L=1.0):
    h, w = image_size
    num_verts = h * w * num_elements

    L_csr = w_L * scipy.sparse.diags([-1, -1, -1, -1, 4],
                       [-num_elements, num_elements, - w * num_elements,  w * num_elements, 0],
                       shape=(num_verts, num_verts))
    return L_csr


def normalIntegralConstraints(A_8U, N_32F, w_cons=20.0):

    epsilon = 0.1
    N_flat = N_32F.reshape(-1, 3)
    Nx = N_flat[:, 0]
    Ny = N_flat[:, 1]
    Nz = np.clip(N_flat[:, 2], epsilon, 1.0)

    h, w = A_8U.shape
    num_verts = h * w

    A = w_cons * scipy.sparse.diags([-1, -1, 2],
                       [1, w, 0],
                       shape=(num_verts, num_verts))

    b = (Nx - Ny) / Nz
    b = w_cons * b
    return A, b


def normalHeightConstraints(A_8U, N_32F, w_cons=0.05):
    Nx = cv2.Sobel(N_32F, cv2.CV_64F, 1, 0, ksize=1)
    Ny = cv2.Sobel(N_32F, cv2.CV_64F, 0, 1, ksize=1)

    Nx_flat = Nx.reshape(-1, 3)
    Ny_flat = Ny.reshape(-1, 3)

    epsilon = 0.01
    Hx = - Nx_flat[:, 2] / (epsilon + np.abs(Nx_flat[:, 0]))
    Hy = - Ny_flat[:, 2] / (epsilon + np.abs(Ny_flat[:, 1]))
    #Nxy = epsilon + np.abs(Nx_flat[:, 0]) + np.abs(Ny_flat[:, 1])
    h, w = A_8U.shape
    num_verts = h * w

    A = w_cons * scipy.sparse.diags([-1, -1, 2],
                       [1, w, 0],
                       shape=(num_verts, num_verts))

    b = (-Hx + Hy)
    b = w_cons * b
    return A, b


def normalLaplacianConstraints(A_8U, N_32F, w_cons=1.0):
    epsilon = 0.0001
    weights = np.array([[0, -1, 0],[-1, 4, -1],[0, -1, 0]]) / 4.0
    N_L = np.zeros(N_32F.shape)
    N_L[1:-1, 1:-1, :] = N_32F[1:-1, 1:-1, :] - (N_32F[0:-2, 1:-1, :]
                                                 + N_32F[2:, 1:-1, :]
                                                 + N_32F[1:-1, 0:-2, :]
                                                 + + N_32F[1:-1, 2:, :]) / 4.0

    N_flat = N_32F.reshape(-1, 3)
    Z_flat = 1.0 - N_flat[:, 2]
    N_L_flat = N_L.reshape(-1, 3)

    h, w = A_8U.shape
    num_verts = h * w
    A = w_cons * scipy.sparse.diags([-1, -1, -1, -1, 4],
                       [1, w, -1, -w, 0],
                       shape=(num_verts, num_verts))

    b = 4.0 *  Z_flat
    b = w_cons * b
    return A, b


def backgroundConstraint(A_8U, w_bg=0.005):
    h, w = A_8U.shape
    num_verts = h * w

    foreground = A_8U.flatten() > 0.5 * np.max(A_8U)

    diags = np.ones(num_verts)
    #diags[foreground] = 0.0

    A = w_bg * scipy.sparse.diags(diags, 0)
    return A


@timing_func
def solveMG(A, b, with_normalize=False):
    ml = pyamg.smoothed_aggregation_solver(A)
    x = ml.solve(b, tol=1e-4)
    return x


def depthToNormal(D_32F):
    h, w = D_32F.shape
    gx = cv2.Sobel(D_32F, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(D_32F, cv2.CV_64F, 0, 1, ksize=3)

    T_32F = np.zeros((h, w, 3), dtype=np.float32)
    T_32F[:, :, 0] = 1.0
    T_32F[:, :, 2] = gx

    B_32F = np.zeros((h, w, 3), dtype=np.float32)
    B_32F[:, :, 1] = 1.0
    B_32F[:, :, 2] = - gy

    T_flat = T_32F.reshape(-1, 3)
    B_flat = B_32F.reshape(-1, 3)

    N_flat = np.cross(T_flat, B_flat)
    N_32F = N_flat.reshape(h, w, 3)

    N_32F = normalizeImage(N_32F)
    return N_32F


def depthFromNormal(N_32F, A_8U):
    if A_8U is not None:
        N_32F = preProcess(N_32F, A_8U)

    h, w = N_32F.shape[:2]
    #A0, b0 = initialDepthConstraint(N_32F, A_8U)
    A_L = laplacianConstraints((h, w), num_elements=1)
    A_i, b_i = normalIntegralConstraints(A_8U, N_32F, w_cons=1.0)
    A_bg = backgroundConstraint(A_8U)

    A = A_i + A_bg
    b = b_i

    D_flat = solveMG(A, b)
    D_32F = D_flat.reshape(h, w)
    #D_32F = postProcess(D_32F, A_8U)
    # N_32F = depthToNormal(D_32F)

    return D_32F


def preProcess(N0_32F, A_8U):
    foreground = A_8U > 0.5 * np.max(A_8U)
    background = A_8U == 0

    N_32F = np.array(N0_32F)
    N_32F[background, :] = np.array([0.0, 0.0, 1.0])
    sigma = 5.0
    for i in xrange(5):
        N_32F = cv2.GaussianBlur(N_32F, (0, 0), sigma)
        N_32F[foreground, :] = N0_32F[foreground, :]
        #N_32F[background, :] = np.array([0.0, 0.0, 1.0])
    #N_32F[background, :] = np.array([0.0, 0.0, 1.0])
    N_32F = normalizeImage(N_32F)
    return N_32F


def postProcess(D_32F, A_8U):
    foreground = A_8U > 200
    D_min = np.min(D_32F[foreground])

    background = True - foreground

    D_32F[background] = D_min
    # D_32F[D_32F < 0.0] = 0.0
    return D_32F


def plotDepth(D_32F):
    h, w = D_32F.shape

    xs, ys = xyCoordinates((h, w))

    Y, X = np.meshgrid(ys, xs)

    Z = D_32F

    colors = np.ones((h, w, 3))