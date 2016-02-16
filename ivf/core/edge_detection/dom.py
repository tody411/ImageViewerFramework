# -*- coding: utf-8 -*-
## @package ivf.core.edge_detection.dom
#
#  ivf.core.edge_detection.dom utility package.
#  @author      tody
#  @date        2016/02/15

import cv2
from ivf.cv.image import to8U, to32F


## DoM filter.
#  @param  img  input gray image.
#  @param  sigma  sigma for small Gaussian filter.
#  @param  k_sigma  large/small sigma (Gaussian filter).
def DoM(img, sigma):
    ksize = 2 * int(sigma / 2) + 1
    img_8U = to8U(img)
    M = cv2.medianBlur(img_8U, ksize=ksize)
    D = to32F(img_8U) - to32F(M)

    return D
