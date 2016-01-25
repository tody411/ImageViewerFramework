
# -*- coding: utf-8 -*-
## @package ivf.io_util.image
#
#  Image io functions.
#  @author      tody
#  @date        2015/07/29


import cv2

from ivf.cv.image import *
from ivf.cv.normal import colorToNormal, normalToColor


def loadGray(file_path):
    bgr = cv2.imread(file_path)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return gray


def loadRGB(file_path):
    bgr = cv2.imread(file_path)
    if bgr is None:
        return None
    return bgr2rgb(bgr)


def loadRGBA(file_path):
    bgra = cv2.imread(file_path, -1)
    if bgra is None:
        return None

    if bgra.shape[2] == 3:
        return bgr2rgb(bgra)
    return bgra2rgba(bgra)


def loadAlpha(file_path):
    bgra = cv2.imread(file_path, -1)
    return alpha(bgra)


def saveRGBA(file_path, img):
    bgra = rgba2bgra(to8U(img))
    cv2.imwrite(file_path, bgra)


def saveRGB(file_path, img):
    bgr = rgb2bgr(to8U(img))
    cv2.imwrite(file_path, bgr)


def saveGray(file_path, img):
    rgbImg = rgb(img)
    cv2.imwrite(file_path, rgbImg)


def saveImage(file_path, img):
    img_8U = to8U(img)

    if len(img_8U.shape) == 2:
        saveGray(file_path, img_8U)
        return

    if img_8U.shape[2] == 3:
        saveRGB(file_path, img_8U)
        return

    if img_8U.shape[2] == 4:
        saveRGBA(file_path, img_8U)
        return


def loadNormal(file_path):
    C_8U = loadRGBA(file_path)
    if C_8U is None:
        return None

    A_8U = alpha(C_8U)
    rgb_8U = rgb(C_8U)
    rgb_8U = cv2.bilateralFilter(rgb_8U, 5, 0.1, 5)
    C_8U[:, :, :3] = rgb_8U
    C_8U[:, :, 3] = A_8U
    N_32F = colorToNormal(C_8U)
    return N_32F, A_8U


def saveNormal(file_path, N_32F, A_8U=None):
    C_8U = normalToColor(N_32F, A_8U)
    saveImage(file_path, C_8U)