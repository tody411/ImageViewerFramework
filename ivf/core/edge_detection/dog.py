# -*- coding: utf-8 -*-
## @package ivf.core.edge_detection.dog
#
#  ivf.core.edge_detection.dog utility package.
#  @author      tody
#  @date        2016/02/15

import cv2


## DoG filter.
#  @param  img  input gray image.
#  @param  sigma  sigma for small Gaussian filter.
#  @param  k_sigma  large/small sigma (Gaussian filter).
def DoG(img, sigma, k_sigma=1.6):
    sigma_large = sigma * k_sigma
    G_small = cv2.GaussianBlur(img, (0, 0), sigma)
    G_large = cv2.GaussianBlur(img, (0, 0), sigma_large)

    D = G_small - G_large
    return D
