
# -*- coding: utf-8 -*-
## @package ivf.ui.qimage_util
#
#  ivf.ui.qimage_util utility package.
#  @author      tody
#  @date        2016/01/29

import numpy as np

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.cv.image import to8U, gray2rgb


def ndarrayToQImage(img):
    C_8U = to8U(img)

    if len(C_8U.shape) == 2:
        C_8U = gray2rgb(C_8U)

    if C_8U.shape[2] == 2:
        C_8U = rg_to_rgb(C_8U)

    if C_8U.shape[2] == 3:
        return rgb_to_Qrgb(C_8U)

    if C_8U.shape[2] == 4:
        return rgba_to_Qargb(C_8U)

    return QImage()


def ndarrayToQPixmap(img):
    qimg = ndarrayToQImage(img)
    return  QPixmap.fromImage(qimg)


def rg_to_rgb(C_8U):
    h,w,cs = C_8U.shape
    rgb_8U = np.zeros((h,w,3))

    for ci in range(3):
        rgb_8U[:,:,ci] = C_8U[:,:,ci]
    return rgb_8U


def rgb_to_Qrgb(C_8U):
    return QImage(C_8U.data,C_8U.shape[1], C_8U.shape[0], QImage.Format_RGB888)


def rgba_to_Qargb(C_8U):
    return QImage(C_8U.data,C_8U.shape[1], C_8U.shape[0], QImage.Format_ARGB32).rgbSwapped()