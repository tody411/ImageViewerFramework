# -*- coding: utf-8 -*-
## @package ivf.cmds.sparse_interpolation.bilateral_normal_smoothing
#
#  ivf.cmds.sparse_interpolation.bilateral_normal_smoothing utility package.
#  @author      tody
#  @date        2016/02/03

import numpy as np

from sklearn.utils import shuffle

from ivf.core.image_features.image_features import positionFeatures, LabFeatures, foreGroundFeatures
from scipy.interpolate.rbf import Rbf
from ivf.cv.image import Lab2rgb, to8U, setAlpha, alpha
from ivf.cv.normal import normalizeImage


def bilateralNormalSmoothing(image, normal):
    sigma_xy = 1.0
    xy = positionFeatures(image) / sigma_xy
    Lab = LabFeatures(image)
    foreground = foreGroundFeatures(image)

    N = normal[:, :, :3].reshape(-1, 3)

    LabxyN = np.concatenate((Lab, xy, N), axis=1)[foreground, :]
    sigma_L = 1.0
    LabxyN[:, 0] = LabxyN[:, 0] / sigma_L
    LabxyN_sparse = shuffle(LabxyN, random_state=0)[:100]

    N_smooth = np.array(N)

    smooth = 10.0

    f_x = np.vstack((LabxyN_sparse[:, :5].T, LabxyN_sparse[:, 5]))
    f_y = np.vstack((LabxyN_sparse[:, :5].T, LabxyN_sparse[:, 6]))
    f_z = np.vstack((LabxyN_sparse[:, :5].T, LabxyN_sparse[:, 7]))

    Nx_rbf = Rbf(*(f_x), function='linear', smooth=smooth)
    Ny_rbf = Rbf(*(f_y), function='linear', smooth=smooth)
    Nz_rbf = Rbf(*(f_z), function='linear', smooth=smooth)

    Labxy = LabxyN[:, :5]

    #Lab_smooth[:, 0] = L_rbf(Labxy[:, 0], Labxy[:, 1], Labxy[:, 2], Labxy[:, 3], Labxy[:, 4])
    N_smooth[foreground, 0] = Nx_rbf(*(Labxy.T))
    N_smooth[foreground, 1] = Ny_rbf(*(Labxy.T))
    N_smooth[foreground, 2] = Nz_rbf(*(Labxy.T))

    h, w = image.shape[:2]
    N_smooth = N_smooth.reshape((h, w, 3))

    N_smooth = normalizeImage(N_smooth)
    return N_smooth