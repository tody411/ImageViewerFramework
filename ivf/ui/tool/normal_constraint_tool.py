# -*- coding: utf-8 -*-
## @package ivf.ui.tool.normal_constraint_tool
#
#  ivf.ui.tool.normal_constraint_tool utility package.
#  @author      tody
#  @date        2016/02/08


import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.ui.tool.base_tool import BaseTool
from ivf.scene.normal_constraint import NormalConstraintSet, NormalConstraint
from ivf.np.norm import normVectors
from ivf.core.sfs.constraints import normalConstraints, laplacianMatrix, silhouetteConstraints
from ivf.core.solver import amg_solver
from ivf.cv.normal import normalizeImage, normalToColor
from ivf.cv.image import alpha, to8U


class NormalConstraintTool(BaseTool):
    ## Constructor
    def __init__(self):
        super(NormalConstraintTool, self).__init__()
        self._normal_constraints = NormalConstraintSet()
        self._p_old = None
        self._selected_constraint = None
        self._normal_radius = 40.0
        self._image = None

    def setNormalConstraints(self, normal_constraints):
        self._normal_constraints = normal_constraints
        self._view.update()

    def normalConstraints(self):
        return self._normal_constraints

    def setImage(self, image):
        self._image = image
        self._view.render(image)

    def mousePressEvent(self, e):
        p = self._mousePosition(e)

        if self._selectConstraint(p):
            return

        else:
            self.addConstraint(p)

    def mouseReleaseEvent(self, e):
        print "p: ", self._selected_constraint.position()
        print "n: ", self._selected_constraint.normal()
        self._selected_constraint = None

    def mouseMoveEvent(self, e):
        p = self._mousePosition(e)
        self._p_old = p

        if e.buttons() & Qt.LeftButton:
            if self._selected_constraint is None:
                return
            p_c = self._selected_constraint.position()
            dP = p - p_c

            Nx = dP[0] / self._normal_radius
            Ny = -dP[1] / self._normal_radius
            r = np.linalg.norm(np.array([Nx, Ny]))
            Nz = np.sqrt(max(0.001, 1.0 - r * r))
            N = np.array([Nx, Ny, Nz])
            N /= np.linalg.norm(N)
            self._selected_constraint.setNormal(N)

        self._view.update()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_0:
            self._view.render(self._image)

        if e.key() == Qt.Key_1:
            self._interpolateNormal()

        if e.key() == Qt.Key_Delete:
            self._normal_constraints.clear()
            self._view.update()

    def keyReleaseEvent(self, e):
        pass

    def addConstraint(self, p):
        self._selected_constraint = NormalConstraint(point=p)
        self._normal_constraints.addConstraint(self._selected_constraint)

        self._view.update()

    def _addingConstraint(self, e):
        p = self._mousePosition(e)
        if self._stroke_sets.selectedStrokeSet().lastStroke().empty() == 0:
            return True

        p_old = self._stroke_sets.selectedStrokeSet().lastStroke().points()[-1]

        if np.linalg.norm(p - p_old) > 3:
            return True

        return False

    def _interpolateNormal(self):
        if self._normal_constraints.empty():
            return

        ps = np.int32(self._normal_constraints.positions())
        ns = self._normal_constraints.normals()

        h, w = self._image.shape[:2]
        N0_32F = np.zeros((h, w, 3))
        N0_32F[ps[:, 1], ps[:, 0]] = ns
        W_32F = np.zeros((h, w))
        W_32F[ps[:, 1], ps[:, 0]] = 100.0
        A_c, b_c = normalConstraints(W_32F, N0_32F)
        A_8U = None
        if self._image.shape[2] == 4:
            A_8U = to8U(alpha(self._image))
        A_sil, b_sil = silhouetteConstraints(A_8U)

        A_L = laplacianMatrix((h, w))
        A = A_c + A_L + A_sil
        b = b_c + b_sil

        N_32F = amg_solver.solve(A, b).reshape(h, w, 3)
        N_32F = normalizeImage(N_32F)


        self._view.render(normalToColor(N_32F, A_8U))

    def _overlayFunc(self, painter):
        pen = QPen(QColor.fromRgbF(0.0, 1.0, 0.0, 0.5))
        pen.setWidth(5)
        painter.setPen(pen)

        p = self._p_old

        if p is not None:
            painter.drawPoint(QPoint(p[0], p[1]))

        for constraint in self._normal_constraints.constraints():
            pen = QPen(QColor.fromRgbF(1.0, 0.0, 0.0, 0.7))
            pen.setWidth(5)

            painter.setPen(pen)

            p = constraint.position()
            painter.drawPoint(QPoint(p[0], p[1]))

            n = np.array(constraint.normal())
            n[1] = -n[1]
            p_n = p + self._normal_radius * n[:2]

            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(QPoint(p[0], p[1]), QPoint(p_n[0], p_n[1]))

    def _selectConstraint(self, p):
        if self._normal_constraints.empty():
            return False

        ps = self._normal_constraints.positions()

        dP = normVectors(ps - p)

        p_min = np.argmin(dP)

        if dP[p_min] < 5:
            self._selected_constraint = self._normal_constraints.constraint(p_min)
            return True

        return False
