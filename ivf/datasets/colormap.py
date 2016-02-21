# -*- coding: utf-8 -*-
## @package ivf.datasets.colormap
#
#  ivf.datasets.colormap utility package.
#  @author      tody
#  @date        2016/02/18
import cv2
import os
from ivf.datasets.datasets import datasetRootDir, datasetFiles, subDirectory
from ivf.io_util.image import loadRGB
from ivf.cv.image import to32F


def colorMapDatasetDir():
    return os.path.join(datasetRootDir(), "colormap")


def colorMapFiles():
    return datasetFiles(colorMapDatasetDir(), file_filter=".png")


def colorMapFile(cmap_id):
    return os.path.join(colorMapDatasetDir(), "ColorMap%02d.png" %cmap_id)


def loadColorMap(file_path):
    M_32F = to32F(loadRGB(file_path))
    h, w = M_32F.shape[:2]
    #M_32F = cv2.resize(M_32F, (4 * w, h))
    #M_32F = cv2.bilateralFilter(M_32F, 0, 0.1, 3)
    return M_32F[0, :, :]


def colorMapResultsDir():
    return subDirectory(colorMapDatasetDir(), "results")