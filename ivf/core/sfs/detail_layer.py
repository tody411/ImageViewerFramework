# -*- coding: utf-8 -*-
## @package ivf.core.sfs.detail_layer
#
#  ivf.core.sfs.detail_layer utility package.
#  @author      tody
#  @date        2016/02/10

import cv2
from ivf.cv.image import to8U, to32F


def baseDetailSeparationGaussian(I_32F, sigma=5.0):
    B = cv2.GaussianBlur(I_32F, (0, 0), sigma)
    D = I_32F - B

    return B, D


def baseDetailSeparationBilateral(I_32F, sigma_space=5.0, sigma_range=0.1):
    B = cv2.bilateralFilter(I_32F, 0, sigma_range, sigma_space)
    D = I_32F - B

    return B, D


def baseDetailSeprationDOG(I_32F, sigma=5.0, sigma_scale=1.6):
    B_small = cv2.GaussianBlur(I_32F, (0, 0), sigma)
    B_large = cv2.GaussianBlur(I_32F, (0, 0), sigma * sigma_scale)

    D = B_small - B_large
    B = I_32F - D
    return B, D


def baseDetailSeparationMedian(I_32F, ksize=5):
    ksize = 2 * (ksize / 2) + 1

    B = to32F(cv2.medianBlur(to8U(I_32F), ksize))

    D = I_32F - B

    return B, D