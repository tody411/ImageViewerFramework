# -*- coding: utf-8 -*-
## @package ivf.core.sfs.matcap_estimation
#
#  ivf.core.sfs.matcap_estimation utility package.
#  @author      tody
#  @date        2016/03/29


class MapCapEstimation:
    def __init__(self, Cs, Ns, num_samples=2000):
        self._Cs = Cs
        self._Ns = Ns
        self._num_samples = num_samples
        self._map_size = 256

    def _compute(self):
        pass
