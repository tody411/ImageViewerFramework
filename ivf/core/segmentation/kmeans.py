# -*- coding: utf-8 -*-
## @package ivf.core.segmentation.kmeans
#
#  ivf.core.segmentation.kmeans utility package.
#  @author      tody
#  @date        2016/02/15

import numpy as np
import cv2

from sklearn.utils import shuffle
import sklearn.cluster

from ivf.cv.image import to32F, alpha, Lab2rgb, setAlpha
from ivf.core.image_features.image_features import positionFeatures, LabFeatures, foreGroundFeatures


class KMeans(object):

    def __init__(self, image, num_colors=20):
        super(KMeans, self).__init__()
        self._image = image
        self._num_colors = num_colors
        self._compute()

    def centers(self):
        return self._centers

    def labels(self):
        return self._labels

    def centerImage(self):
        Labxy = np.float32(self._centers[self._labels])
        Lab = Labxy[:, :, :3]

        print Lab.shape
        print Lab.dtype

        C_32F = Lab2rgb(Lab)

        C_32F = setAlpha(C_32F, self._A_32F)
        return C_32F

    def histogram(self):
        label_min, label_max = np.min(self._labels), np.max(self._labels)
        hist = np.zeros((label_max - label_min + 1), dtype=np.float32)
        for label in xrange(label_min, label_max):
            hist[label] = np.count_nonzero(self._labels[self._A_32F > 0.5] == label)
        return hist

    def histImage(self):
        hist = self.histogram()
        num_hist = len(hist)

        h, w = num_hist, num_hist
        hist_image = np.zeros((h, w, 3), dtype=np.float32)

        hist_max = np.max(hist)

        ys = np.arange(h)

        for label in xrange(num_hist):
            hist_i = hist[label] / hist_max

            for y in xrange(h):
                if y > (h - 1) * hist_i:
                    continue
                hist_image[h- 1 - y, label, :] = self._centers[label, :3]

        hist_image = Lab2rgb(hist_image)
        hist_image = cv2.resize(hist_image, (512, 512), interpolation = cv2.INTER_NEAREST)
        return hist_image

    def _compute(self):
        image = self._image

        img_32F = to32F(self._image)
        self._A_32F = alpha(img_32F)

        sigma_xy = 100.0
        xy = positionFeatures(img_32F) / sigma_xy
        Lab = LabFeatures(img_32F)

        sigma_L = 1.0
        Lab[:, 0] /= sigma_L

        foreground = foreGroundFeatures(img_32F)

        Labxy = np.concatenate((Lab, xy), axis=1)

        Labxy_samples = shuffle(Labxy[foreground, :], random_state=0)[:1000]

        kmeans = sklearn.cluster.KMeans(n_clusters=self._num_colors, random_state=0).fit(Labxy_samples)

        self._centers = kmeans.cluster_centers_
        self._centers[:, 0] *= sigma_L

        labels = kmeans.predict(Labxy)
        self._labels = labels.reshape(image.shape[:2])

