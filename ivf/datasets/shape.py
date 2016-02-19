# -*- coding: utf-8 -*-
## @package ivf.datasets.threed_model
#
#  ivf.datasets.threed_model utility package.
#  @author      tody
#  @date        2016/02/18

import os
from ivf.datasets.datasets import datasetRootDir, subDirectory, datasetFiles, datasetFileNames


def shapeDatasetDir():
    return os.path.join(datasetRootDir(), "3dmodel")


def shapeNames():
    file_names = datasetFileNames(shapeDatasetDir(), file_filter=".png")
    shape_names = [os.path.splitext(file_name)[0] for file_name in file_names]
    return shape_names

def shapeFiles():
    return datasetFiles(shapeDatasetDir(), file_filter=".png")


def shapeFile(shape_name):
    return os.path.join(shapeDatasetDir(), shape_name + ".png")


def shapeResultsDir():
    return subDirectory(shapeDatasetDir(), "results")


def shapeResultDir(result_name):
    return subDirectory(shapeResultsDir(), result_name)


def shapeResultFiles(result_name):
    result_dir = shapeResultDir(result_name)
    return datasetFiles(result_dir, file_filter=".png")


def shapeResultFile(result_name, data_name):
    result_dir = shapeResultDir(result_name)
    return os.path.join(result_dir, data_name + ".png")
