# -*- coding: utf-8 -*-
## @package ivf.batch.batch
#
#  ivf.batch.batch utility package.
#  @author      tody
#  @date        2016/02/05

import os

from ivf.util.timer import Timer
from ivf.io_util.dict_data import saveDict
from ivf.datasets.datasets import datasetDir, datasetFiles, subDirectory


class BaseBatch(object):
    def __init__(self, name=""):
        super(BaseBatch, self).__init__()
        self._name = name
        self._input_info = ""
        self._output_info = ""

    def name(self):
        return self._name

    def run(self):
        timer = Timer(self._name)
        self._runImp()
        timer.stop()
        message = self._name + "(" + self._input_info + ")"
        if self._output_info is not "":
            message += "=> " + self._output_info
        message += ": " + str(timer.secs())
        print message

    def _runImp(self):
        pass


class DirectoryBatch(BaseBatch):
    def __init__(self, name="", target_dir=""):
        super(DirectoryBatch, self).__init__(name)
        self._target_dir = target_dir

    def targetDir(self):
        return self._target_dir


class DatasetBatch(DirectoryBatch):
    def __init__(self, name="", dataset_name=""):
        target_dir = datasetDir(dataset_name)
        super(DatasetBatch, self).__init__(name, target_dir)
        self._dataset_name = dataset_name
        self._data_name = ""
        self._data_file_name = ""
        self._data_file = ""

    def run(self):
        dataset_files = datasetFiles(self._target_dir)
        self._result_root = subDirectory(self._target_dir, "results/" + self._name)

        for data_file in dataset_files:
            self._data_file_name = os.path.basename(data_file)
            self._data_name = os.path.splitext(self._data_file_name)[0]
            self._data_file = data_file
            timer = Timer(self._name)
            self._runImp()
            timer.stop()

            message = self._data_name + ":  " + str(timer.secs()) + "sec \n"
            message += "  " + self._input_info + "\n"
            if self._output_info is not "":
                message += "=> " + self._output_info
            print message

    def resultFile(self, file_name):
        return os.path.join(self._result_root, file_name)

    def _runImp(self):
        pass
