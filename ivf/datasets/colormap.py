# -*- coding: utf-8 -*-
## @package ivf.datasets.colormap
#
#  ivf.datasets.colormap utility package.
#  @author      tody
#  @date        2016/02/18
import os
from ivf.datasets.datasets import datasetRootDir, datasetFiles, subDirectory
from ivf.io_util.image import loadRGB


def colorMapDatasetDir():
    return os.path.join(datasetRootDir(), "colormap")


def colorMapFiles():
    return datasetFiles(colorMapDatasetDir(), file_filter=".png")


def colorMapFile(cmap_id):
    return os.path.join(colorMapDatasetDir(), "ColorMap%02d.png" %cmap_id)


def loadColorMap(file_path):
    M_32F = loadRGB(file_path)
    return M_32F[0, :, :]


def colorMapResultsDir():
    return subDirectory(colorMapDatasetDir(), "results")