
# -*- coding: utf-8 -*-
## @package ivf.datasets.datasets
#
#  ivf.datasets.datasets utility package.
#  @author      tody
#  @date        2016/02/05


import os

from ivf.io_util.dict_data import saveDict, loadDict

_root = __file__


## Dataset root directories.
def datasetRootDirs():
    setting_file = os.path.abspath(os.path.join(_root, "../setting.json"))
    setting_data = loadDict(setting_file)
    dataset_root_dirs = setting_data["dataset_roots"]
    return dataset_root_dirs


## Dataset root directory.
def datasetRootDir():
    dataset_root_dirs = datasetRootDirs()

    for dataset_root_dir in dataset_root_dirs:
        if os.path.exists(dataset_root_dir):
            return dataset_root_dir


## Dataset direcotry.
def datasetDir(dataset_name):
    return os.path.join(datasetRootDir(), dataset_name)


## Dataset file names.
def datasetFileNames(dataset_dir, file_filter=".png"):
    file_names = os.listdir(dataset_dir)
    if file_filter is not None:
        file_names = [file_name for file_name in file_names if file_filter in file_name]
    return os.listdir(dataset_dir)


## Dataset files.
def datasetFiles(dataset_dir, file_filter=".png"):
    file_names = datasetFileNames(dataset_dir, file_filter=file_filter)
    files = [os.path.join(dataset_dir, file_name) for file_name in file_names]
    return files


## Sub directory.
def subDirectory(target_dir, dir_name, make_dir=True):
    sub_dir = os.path.join(target_dir, dir_name)
    if make_dir and not os.path.exists(sub_dir):
        os.makedirs(sub_dir)
    return sub_dir
