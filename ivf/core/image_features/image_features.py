
# -*- coding: utf-8 -*-
## @package ivf.core.sparse_interpolation.image_features
#
#  ivf.core.sparse_interpolation.image_features utility package.
#  @author      tody
#  @date        2016/02/03


import numpy as np

from ivf.cv.image import to32F, alpha, rgb2Lab, rgb2hsv


def alphaFeatures(image):
    h, w = image.shape[:2]
    if alpha(image) == None:
        return 255 * np.ones((h * w))
    features = alpha(image).reshape(h * w)
    return features


def foreGroundFeatures(image):
    a_features = alphaFeatures(image)

    return a_features > 0.7 * np.max(a_features)


def positionFeatures(image):
    h, w = image.shape[:2]

    x = np.arange(w)
    y = np.arange(h)

    xs, ys = np.meshgrid(x, y)
    xs = xs.flatten()
    ys = ys.flatten()

    features = np.array([xs, ys]).T
    return features


def rgbFeatures(image):
    img_32F = to32F(image)
    features = img_32F[:, :, :3].reshape(-1, 3)
    return features


def LabFeatures(image, w_L=1.0, w_a=1.0, w_b=1.0):
    img_32F = to32F(image)
    rgb_32F = img_32F[:, :, :3]
    Lab_32F = rgb2Lab(rgb_32F)

    h, w, cs = image.shape
    features = Lab_32F.reshape(h * w, -1)

    features[:, 0] *= w_L
    features[:, 1] *= w_a
    features[:, 2] *= w_b

    return features


def HSVFeatures(image, w_H=1.0, w_S=1.0, w_V=1.0):
    img_32F = to32F(image)
    rgb_32F = img_32F[:, :, :3]
    hsv_32F = rgb2hsv(rgb_32F)

    h, w, cs = image.shape
    features = hsv_32F.reshape(h * w, -1)

    features[:, 0] *= w_H
    features[:, 1] *= w_S
    features[:, 2] *= w_V

    return features
