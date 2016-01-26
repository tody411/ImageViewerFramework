
# -*- coding: utf-8 -*-
## @package ivf.scene.material_constraint
#
#  ivf.scene.material_constraint utility package.
#  @author      tody
#  @date        2016/01/26


import numpy as np

from ivf.scene.data import Data


class MaterialConstraint(Data):
    ## Constructor
    def __init__(self, point):
        super(MaterialConstraint, self).__init__()
        self._point = (0, 0)


    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {"points": np.array(self._points).tolist(), "brush_sizes": self._brush_sizes}
        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._points = data["points"]
        self._brush_sizes = data["brush_sizes"]


class MaterialConstraintSet(Data):
    ## Constructor
    def __init__(self, name=""):
        super(MaterialConstraintSet, self).__init__()
        self._constraints = []
        self._name = name

    def constraints(self):
        return self._constraints


class MaterialConstraintSets(Data):
    ## Constructor
    def __init__(self, point):
        super(MaterialConstraintSets, self).__init__()
        self._constraint_sets = []

    def constraintSets(self):
        return self._constraint_sets