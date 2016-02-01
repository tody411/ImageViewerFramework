
# -*- coding: utf-8 -*-
## @package ivf.core.super_pixel.slic
#
#  ivf.core.super_pixel.slic utility package.
#  @author      tody
#  @date        2016/02/01


from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float

import matplotlib.pyplot as plt

from ivf.cv.image import rgb, to8U


def slicSegmentation(image, num_segments=200, sigma=5):
    C_8U = rgb(image)
    C_32F = to8U(C_8U)
    segments = slic(C_32F, n_segments=num_segments, sigma=sigma)

    fig = plt.figure("Superpixels -- %d segments" % (num_segments))
    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(mark_boundaries(C_32F, segments))
    plt.axis("off")
    plt.show()
