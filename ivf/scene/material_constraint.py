
# -*- coding: utf-8 -*-
## @package ivf.scene.material_constraint
#
#  ivf.scene.material_constraint utility package.
#  @author      tody
#  @date        2016/01/26


import numpy as np

from ivf.scene.data import Data


class MaterialConstraint(Data):
    diffuse_type = 0
    specular_type = 1
    ## Constructor
    def __init__(self, position=(0, 0), shading_type=0):
        super(MaterialConstraint, self).__init__()
        self._position = position

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {"position": np.array(self._position).tolist()}
        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._position = data["position"]


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
    def __init__(self, position):
        super(MaterialConstraintSets, self).__init__()
        self._constraint_sets = []

    def constraintSets(self):
        return self._constraint_sets