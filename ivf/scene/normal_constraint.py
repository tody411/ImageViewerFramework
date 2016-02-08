# -*- coding: utf-8 -*-
## @package ivf.scene.normal_constraint
#
#  ivf.scene.normal_constraint utility package.
#  @author      tody
#  @date        2016/02/08


import numpy as np

from ivf.scene.data import Data


class NormalConstraint(Data):
    ## Constructor
    def __init__(self, point=np.array((0.0, 0.0)),
                 normal=np.array((0.0, 0.0, 1.0))):
        super(NormalConstraint, self).__init__()
        self._position = point
        self._normal = normal

    def setPosition(self, p):
        self._position = np.array(p)

    def position(self):
        return self._position

    def setNormal(self, n):
        self._normal = np.array(n)

    def normal(self):
        return self._normal

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {"position": np.array(self._position).tolist(), "normal": np.array(self._normal).tolist()}
        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._position = data["position"]


class NormalConstraintSet(Data):
    ## Constructor
    def __init__(self, constraints=[]):
        self._constraints = constraints

    def empty(self):
        return len(self._constraints) == 0

    def addConstraint(self, constraint):
        self._constraints.append(constraint)

    def constraints(self):
        return self._constraints

    def constraint(self, index):
        return self._constraints[index]

    def positions(self):
        ps = []

        for constraint in self._constraints:
            ps.append(constraint.position())
        return np.array(ps)

    def normals(self):
        ns = []

        for constraint in self._constraints:
            ns.append(constraint.normal())
        return np.array(ns)

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {}
        data["constraints"] = [constraint._dataDict() for constraint in self._constraints]
        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._constraints = []
        constraints_data = data["constraints"]
        for constraint_data in constraints_data:
            constraint = NormalConstraint()
            constraint._setDataDict(constraint_data)
            self.addConstraint(constraint)
