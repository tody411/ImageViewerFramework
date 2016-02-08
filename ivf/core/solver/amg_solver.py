# -*- coding: utf-8 -*-
## @package ivf.core.solver.amg_solver
#
#  ivf.core.solver.amg_solver utility package.
#  @author      tody
#  @date        2016/02/05

import numpy as np
import pyamg
from pyamg.relaxation import gauss_seidel, sor
from ivf.util.timer import timing_func


@timing_func
def solve(A, b, tol=1e-8):
    ml = pyamg.smoothed_aggregation_solver(A)

    if len(b.shape) == 1:
        x = ml.solve(b, tol=tol)
        return x

    x = np.zeros(b.shape)
    for bi in xrange(b.shape[1]):
        x[:, bi] = ml.solve(b[:, bi], tol=tol)
    return x


def gauss_seidel_iter(A, x, b, iterations=1):
    gauss_seidel(A, x, b, iterations=iterations)


def sor_iter(A, x, b, omega, iterations=1):
    sor(A, x, b, omega, iterations=iterations)
