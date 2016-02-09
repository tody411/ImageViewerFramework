import numpy as np

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
import os

from ivf.batch.batch import DatasetBatch
from ivf.io_util.image import loadNormal
from ivf.cv.image import to32F, setAlpha
from ivf.np.norm import normalizeVector
from ivf.core.shader.lambert import LambertShader
from ivf.ui.image_view import ImageView
from ivf.ui.tool.normal_constraint_tool import NormalConstraintTool
from ivf.scene.normal_constraint import NormalConstraintSet


class NormalConstraintBatch(DatasetBatch):
    def __init__(self, view, tool, name="Normal Constraint", dataset_name="3dmodel"):
        super(NormalConstraintBatch, self).__init__(name, dataset_name)
        self._view = view
        self._normal_constraint = NormalConstraintSet()
        self._tool = tool
        self._tool.setNormalConstraints(self._normal_constraint)

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data
        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))

        C0_32F = LambertShader().diffuseShading(L, N0_32F)

        self._normal_constraint.clear()

        if os.path.exists(self.constraintFile()):
            self._normal_constraint.load(self.constraintFile())
        self._view.render(setAlpha(C0_32F, A_32F))

    def constraintFile(self):
        return self.resultFile(self._data_name + "_normal_constraint.json")

    def finish(self):
        constraint_file = self.resultFile(self._data_name + "_normal_constraint.json")
        self._normal_constraint.save(constraint_file)
        self.runNext()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ImageView()
    view.show()
    tool = NormalConstraintTool()
    view.setTool(tool)
    batch = NormalConstraintBatch(view, tool)
    view.setReturnCallback(batch.finish)
    sys.exit(app.exec_())