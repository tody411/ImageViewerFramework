# -*- coding: utf-8 -*-
## @package ivf.core.sparse_interpolation.bilateral_smoothing
#
#  ivf.core.sparse_interpolation.bilateral_smoothing utility package.
#  @author      tody
#  @date        2016/02/03


import numpy as np

from sklearn.utils import shuffle

from ivf.core.image_features.image_features import positionFeatures, LabFeatures, foreGroundFeatures
from scipy.interpolate.rbf import Rbf
from ivf.cv.image import Lab2rgb, to8U, setAlpha, alpha


def bilateralSmoothing(image):
    sigma_xy = 0.1
    xy = positionFeatures(image) / sigma_xy
    Lab = LabFeatures(image)
    foreground = foreGroundFeatures(image)

    Labxy = np.concatenate((Lab, xy), axis=1)[foreground, :]
    sigma_L = 1.0
    Labxy[:, 0] = Labxy[:, 0] / sigma_L
    Labxy_sparse = shuffle(Labxy, random_state=0)[:1000]

    Lab_smooth = np.array(Lab)

    smooth = 0.0

    L_rbf = Rbf(Labxy_sparse[:, 0], Labxy_sparse[:, 1], Labxy_sparse[:, 2],
                Labxy_sparse[:, 3], Labxy_sparse[:, 4], sigma_L * Labxy_sparse[:, 0], function='linear', smooth=smooth)

    a_rbf = Rbf(Labxy_sparse[:, 0], Labxy_sparse[:, 1], Labxy_sparse[:, 2],
                Labxy_sparse[:, 3], Labxy_sparse[:, 4], Labxy_sparse[:, 1], function='linear', smooth=smooth)
    b_rbf = Rbf(Labxy_sparse[:, 0], Labxy_sparse[:, 1], Labxy_sparse[:, 2],
                Labxy_sparse[:, 3], Labxy_sparse[:, 4], Labxy_sparse[:, 2], function='linear', smooth=smooth)

    #Lab_smooth[:, 0] = L_rbf(Labxy[:, 0], Labxy[:, 1], Labxy[:, 2], Labxy[:, 3], Labxy[:, 4])
    Lab_smooth[foreground, 0] = L_rbf(*(Labxy.T))
    Lab_smooth[foreground, 1] = a_rbf(*(Labxy.T))
    Lab_smooth[foreground, 2] = b_rbf(*(Labxy.T))

    h, w = image.shape[:2]
    Lab_smooth = Lab_smooth.reshape((h, w, 3))

    rgb_smooth = Lab2rgb(np.float32(Lab_smooth))
    rgb_smooth_8U = to8U(rgb_smooth)
    rgb_smooth_8U = setAlpha(rgb_smooth_8U, alpha(image))
    return rgb_smooth_8U