# -*- coding: utf-8 -*-
## @package ivf.core.segmentation.edge_based_segmentation
#
#  ivf.core.segmentation.edge_based_segmentation utility package.
#  @author      tody
#  @date        2016/02/15
import numpy as np
import cv2

from ivf.cv.image import rgb, to32F, rgb2Lab, luminance
from ivf.core.edge_detection.dog import DoG
from ivf.np.norm import normVectors


class EdgeBasedSegmentaiton:
    def __init__(self, image):
        self._image = image
        self._compute()

    def _compute(self):
        C0_8U = self._image
        C0_32F = to32F(rgb(C0_8U))
        Lab_32F = rgb2Lab(C0_32F)
        I_32F = luminance(C0_32F)

        h, w = I_32F.shape[:2]
        edge_mask = np.zeros((h, w), dtype=np.uint8)

        #E_32F = DoG(Lab_32F, sigma=7.0)

#         E_32F[E_32F > 0.0] = 0.0
#         E_32F = - E_32F
#         E_32F /= np.max(E_32F)
#         th_contour = 0.05
#         for ci in xrange(3):
#             edge_area = E_32F[:, :, ci] > th_contour
#             edge_mask[edge_area] = 255

        E_32F = DoG(I_32F, sigma=3.0)
        h, w = E_32F.shape[:2]
        E_norm = - np.array(E_32F)
        E_norm[E_norm < 0.0] = 0.0

        th_contour = 0.1
        edge_area = E_norm > th_contour * np.max(E_norm)
        edge_mask[edge_area] = 255
        self._edge_mask = edge_mask

        labels = np.array(edge_mask)

        mask = np.ones((h+2, w+2), dtype = np.uint8)
        mask[1:-1, 1:-1] = self._edge_mask

        for label in xrange(1, 3):
            regionSeeds = np.where(self._edge_mask==0)
            if len(regionSeeds[0]) == 0:
                break
            p = (regionSeeds[1][0], regionSeeds[0][0])
            cv2.floodFill(labels, mask, p, label)
            self._edge_mask[labels == label] = label
        self._labels = labels

    def edgeMask(self):
        return self._edge_mask

    def labels(self):
        return self._labels
