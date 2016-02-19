# -*- coding: utf-8 -*-
## @package ivf.batch.initial_normal
#
#  ivf.batch.initial_normal utility package.
#  @author      tody
#  @date        2016/02/19

import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch
from ivf.io_util.image import loadNormal, saveNormal
from ivf.core.sfs import amg_constraints
from ivf.core.solver import amg_solver
from ivf.core.sfs.lumo import computeNz
from ivf.cv.normal import normalizeImage
from ivf.np.norm import normalizeVectors


class InitialNormalBatch(DatasetBatch):
    def __init__(self, name="InitialNormal", dataset_name="3dmodel"):
        super(InitialNormalBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data

        h, w = A_8U.shape[:2]
        A_c, b_c = amg_constraints.silhouetteConstraints(A_8U, is_flat=True)

        A_L = amg_constraints.laplacianMatrix((h, w), num_elements=3)
        A = A_c + A_L
        b = b_c

        N = amg_solver.solve(A, b).reshape(-1, 3)
        N = computeNz(N)
        N = normalizeVectors(N)
        N_32F = N.reshape(h, w, 3)

        file_path = self.resultFile(self._data_file_name)
        saveNormal(file_path, N_32F, A_8U)

if __name__ == '__main__':
    InitialNormalBatch().run()