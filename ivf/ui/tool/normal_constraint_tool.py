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
from ivf.np.norm import normVectors, normalizeVector
from ivf.core.sfs.amg_constraints import normalConstraints, laplacianMatrix, silhouetteConstraints
from ivf.core.solver import amg_solver, image_solver
from ivf.cv.normal import normalizeImage, normalToColor
from ivf.cv.image import alpha, to8U, rgb, to32F, luminance
from ivf.core.sfs import image_constraints
from ivf.core.sfs.image_constraints import postNormalize
from ivf.core.sfs.pr_sfs import Wu08SFS


class NormalConstraintTool(BaseTool):
    ## Constructor
    def __init__(self):
        super(NormalConstraintTool, self).__init__()
        self._normal_constraints = NormalConstraintSet()
        self._p_old = None
        self._n_old = None
        self._selected_constraint = None
        self._normal_radius = 40.0
        self._image = None
        self._N_32F = None

    def setNormalConstraints(self, normal_constraints):
        self._normal_constraints = normal_constraints
        self._view.update()

    def normalConstraints(self):
        return self._normal_constraints

    def setImage(self, image):
        self._image = image
        self._interpolateNormal()
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
        self._interpolateNormal()

    def mouseMoveEvent(self, e):
        p = self._mousePosition(e)
        self._p_old = p

        if e.buttons() & Qt.LeftButton:
            if self._selected_constraint is None:
                return
            p_c = self._selected_constraint.position()
            N_c = self._n_old
            dP = p - p_c

            Nx, Ny = N_c[0], N_c[1]
            Nx += dP[0] / self._normal_radius
            Ny += -dP[1] / self._normal_radius
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
            if self._N_32F is None:
                self._interpolateNormal()
            A_8U = None
            if self._image.shape[2] == 4:
                A_8U = to8U(alpha(self._image))
            self._view.render(normalToColor(self._N_32F, A_8U))

        if e.key() == Qt.Key_2:
            self._interpolateNormal()
            if self._N_32F is None:
                self._interpolateNormal()
            A_8U = None
            if self._image.shape[2] == 4:
                A_8U = to8U(alpha(self._image))
            self._view.render(normalToColor(self._N_32F, A_8U))

        if e.key() == Qt.Key_Delete:
            self._normal_constraints.clear()
            self._view.update()

    def keyReleaseEvent(self, e):
        pass

    def addConstraint(self, p):
        n = np.array([0.0, 0.0, 1.0])
        if self._N_32F is not None:
            n = self._N_32F[p[1], p[0], :]
        self._selected_constraint = NormalConstraint(point=p, normal=n)
        self._normal_constraints.addConstraint(self._selected_constraint)
        self._n_old = self._selected_constraint.normal()
        self._view.update()

    def _interpolateNormal(self):
        if self._normal_constraints.empty():
            return

        if self._image is None:
            return

        ps = np.int32(self._normal_constraints.positions())
        ns = self._normal_constraints.normals()

        h, w = self._image.shape[:2]
        N0_32F = np.zeros((h, w, 3))
        N0_32F[ps[:, 1], ps[:, 0]] = ns
        W_32F = np.zeros((h, w))
        W_32F[ps[:, 1], ps[:, 0]] = 1.0

        A_8U = None
        if self._image.shape[2] == 4:
            A_8U = to8U(alpha(self._image))

        self._N_32F = self._interpolateNormalImage(N0_32F, W_32F, A_8U)
        self._projectConstraints()

    def _interpolateNormalImage(self, N0_32F, W_32F, A_8U):
        constraints = []
        constraints.append(image_constraints.laplacianConstraints(w_c=0.1))
        constraints.append(image_constraints.normalConstraints(W_32F, N0_32F, w_c=3.0))
        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))
        I_32F = luminance(to32F(rgb(self._image)))
        I_min, I_max = np.min(I_32F), np.max(I_32F)

        I_32F = (I_32F - I_min) / (I_max - I_min)

        # constraints.append(image_constraints.brightnessConstraints(L, I_32F, w_c=0.5))
        constraints.append(image_constraints.silhouetteConstraints(A_8U, w_c=0.8))

        solver_iter = image_solver.solveIterator(constraints,
                                                 [postNormalize(th=0.0)])

        N_32F = np.array(N0_32F)
        N_32F = image_solver.solveMG(N_32F, solver_iter, iterations=10)
        N_32F = image_constraints.NxyToNz(N_32F)

        return N_32F

    def _interpolateNormalAMG(self, N0_32F, W_32F, A_8U):
        h, w = N0_32F.shape[:2]
        A_c, b_c = normalConstraints(W_32F, N0_32F)
        A_8U = None
        if self._image.shape[2] == 4:
            A_8U = to8U(alpha(self._image))
        A_sil, b_sil = silhouetteConstraints(A_8U)

        A_L = laplacianMatrix((h, w))
        A = 10.0 * A_c + A_L + A_sil
        b = 10.0 * b_c + b_sil

        N_32F = amg_solver.solve(A, b).reshape(h, w, 3)
        N_32F = normalizeImage(N_32F)

        return N_32F

    def _projectConstraints(self):
        for constraint in self._normal_constraints.constraints():
            p = constraint.position()
            N = self._N_32F[p[1], p[0]]
            constraint.setNormal(N)
        self._view.update()

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
            self._n_old = self._selected_constraint.normal()
            return True

        return False
