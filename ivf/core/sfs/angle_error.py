# -*- coding: utf-8 -*-
## @package ivf.core.sfs.angle_error
#
#  ivf.core.sfs.angle_error utility package.
#  @author      tody
#  @date        2016/02/01

import numpy as np


def angleError(N1, N2):
    cos_error = np.dot(N1, N2)
    cos_error = np.clip(cos_error, -1.0, 1.0)
    angle_error = np.arccos(cos_error)
    return np.degrees(angle_error)


def angleErros(Ns1, Ns2):
    cos_errors = [np.dot(N1, N2) for N1, N2 in zip(Ns1, Ns2)]
    cos_errors = np.clip(cos_errors, -1.0, 1.0)
    angle_errors = np.arccos(cos_errors)
    return np.degrees(angle_errors)
