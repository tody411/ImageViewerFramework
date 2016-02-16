# -*- coding: utf-8 -*-
## @package ivf.core.sparse_interpolation.sparse_sampling
#
#  ivf.core.sparse_interpolation.sparse_sampling utility package.
#  @author      tody
#  @date        2016/02/03


import numpy as np

from skimage.segmentation import slic, mark_boundaries

import cv2

from ivf.core.image_features.image_features import positionFeatures, LabFeatures
from ivf.util.timer import timing_func
from ivf.cv.image import to8U, Lab2rgb, setAlpha, alpha, to32F, rgb


@timing_func
def sparseSampling(image):
    return sparseHistogramSampling(image)


def slicSampling(image, num_segments=4000, sigma=5):
    h, w = image.shape[:2]
    C_32F = to32F(rgb(image))
    segments = slic(C_32F, n_segments=num_segments, sigma=sigma)
    print segments.shape
    print np.max(segments)
    num_centers = np.max(segments) + 1
    hist_centers = np.zeros((num_centers), dtype=np.float32)
    centers = np.zeros((num_centers, 3), dtype=np.float32)

    hist_centers[segments[:, :]] += 1.0
    centers[segments[:, :], :] += C_32F[:, :, :3]

    hist_positive = hist_centers > 0.0

    print np.count_nonzero(hist_positive)

    for ci in xrange(3):
        centers[hist_positive, ci] /= hist_centers[hist_positive]

    map_rgb = to8U(centers[segments[:, :], :].reshape(h, w, -1))
    #map_rgb = to8U(mark_boundaries(C_32F, segments))
    map_image = setAlpha(map_rgb, alpha(image))
    return map_image


def sparseHistogramSampling(image, num_color_bin=24, num_xy_bins=64):
    h, w = image.shape[:2]

    Lab = LabFeatures(image)
    xy = positionFeatures(image)

    Labxy = np.concatenate((Lab, xy), axis=1)

    num_bins = [num_color_bin, num_color_bin, num_color_bin, num_xy_bins, num_xy_bins]
    num_color_bins = num_bins[:]
    num_color_bins.append(3)

    hist_bins = np.zeros(num_bins, dtype=np.float32)
    color_bins = np.zeros(num_color_bins, dtype=np.float32)

    f_min = np.min(Labxy, axis=0)
    f_max = np.max(Labxy, axis=0)

    num_bins = np.array(num_bins)
    f_ids = (num_bins - 1) * (Labxy - f_min) / (f_max - f_min)
    f_ids = np.int32(f_ids)

    hist_bins[f_ids[:, 0], f_ids[:, 1], f_ids[:, 2], f_ids[:, 3], f_ids[:, 4]] += 1
    color_bins[f_ids[:, 0], f_ids[:, 1], f_ids[:, 2], f_ids[:, 3], f_ids[:, 4]] += Lab[:, :]

    hist_positive = hist_bins > 0.0

    print np.count_nonzero(hist_positive)

    for ci in xrange(3):
        color_bins[hist_positive, ci] /= hist_bins[hist_positive]

    map_Lab = color_bins[f_ids[:, 0], f_ids[:, 1], f_ids[:, 2], f_ids[:, 3], f_ids[:, 4]].reshape(h, w, -1)
    map_rgb = to8U(Lab2rgb(map_Lab))

    print image.shape
    print map_rgb.shape

    map_image = setAlpha(map_rgb, alpha(image))

    return map_image