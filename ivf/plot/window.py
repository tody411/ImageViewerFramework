# -*- coding: utf-8 -*-
## @package ivf.plot.window
#
#  Matplot window functions.
#  @author      tody
#  @date        2015/07/29

from matplotlib import pyplot as plt
from ivf.cv.image import trim, alpha


class SubplotGrid:
    def __init__(self, num_rows, num_cols):
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._plot_id = 1

    def showImage(self, image, title, alpha_clip=True):
        plt.subplot(self._num_rows, self._num_cols, self._plot_id)
        plt.title(title)
        if len(image.shape) == 2:
            plt.gray()

        show_image = image
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                show_image = trim(image, alpha(image))

        plt.imshow(show_image)
        plt.axis('off')
        self._plot_id += 1

    def showColorMap(self, image, title, v_min=None, v_max=None, cmap=plt.cm.jet):
        plt.subplot(self._num_rows, self._num_cols, self._plot_id)
        plt.title(title)
        plt.imshow(image, cmap=cmap, vmin=v_min, vmax=v_max)
        plt.axis('off')
        plt.colorbar()
        self._plot_id += 1


def createFigure(title, font_size=15):
    fig, axes = plt.subplots(figsize=(11, 5))
    fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.05, wspace=0.05)
    fig.suptitle(title, fontsize=font_size)


## Maximize the matplot window.
def showMaximize():
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()
