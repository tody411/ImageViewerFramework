
# -*- coding: utf-8 -*-
## @package ivf.cmds.slic
#
#  ivf.cmds.slic utility package.
#  @author      tody
#  @date        2016/02/01


from ivf.cmds.base_cmds import BaseCommand
from ivf.core.super_pixel.slic import slicSegmentation


class SlicCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(SlicCommand, self).__init__(scene, "SLIC", parent)

    def _runImp(self):
        image = self._scene.image()
        slicSegmentation(image, num_segments=1000, sigma=5)
