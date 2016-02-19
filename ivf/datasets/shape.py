# -*- coding: utf-8 -*-
## @package ivf.datasets.threed_model
#
#  ivf.datasets.threed_model utility package.
#  @author      tody
#  @date        2016/02/18

import os
from ivf.datasets.datasets import datasetRootDir, subDirectory, datasetFiles


def shapeDatasetDir():
    return os.path.join(datasetRootDir(), "3dmodel")


def shapeFiles():
    return datasetFiles(shapeDatasetDir(), file_filter=".png")


def shapeFile(shape_name):
    return os.path.join(shapeDatasetDir(), shape_name + ".png")


def shapeResultsDir():
    return subDirectory(shapeDatasetDir(), "results")