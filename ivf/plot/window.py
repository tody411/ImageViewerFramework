# -*- coding: utf-8 -*-
## @package ivf.plot.window
#
#  Matplot window functions.
#  @author      tody
#  @date        2015/07/29

from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ivf.cv.image import trim, alpha


class SubplotGrid:
    def __init__(self, num_rows, num_cols, fig=None):
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._plot_id = 1
        self._fig = fig

    def showImage(self, image, title, alpha_clip=True, font_size=15):
        plt.subplot(self._num_rows, self._num_cols, self._plot_id)
        plt.title(title, fontsize=font_size)
        if len(image.shape) == 2:
            plt.gray()

        show_image = image
        if alpha_clip:
            if len(image.shape) == 3:
                if image.shape[2] == 4:
                    show_image = trim(image, alpha(image))

        plt.imshow(show_image)
        plt.axis('off')
        self._plot_id += 1

    def showColorMap(self, image, title, v_min=None, v_max=None, cmap=plt.cm.jet, with_colorbar=True):
        ax = plt.subplot(self._num_rows, self._num_cols, self._plot_id)
        plt.title(title)
        image_plt = plt.imshow(image, cmap=cmap, vmin=v_min, vmax=v_max)
        plt.axis('off')
        if with_colorbar:
            if self._fig is not None:
                divider = make_axes_locatable(ax)
                ax_cb = divider.new_horizontal(size="8%", pad=0.05)
                self._fig.add_axes(ax_cb)
                plt.colorbar(cax=ax_cb, ticks=[v_min, v_max])
            else:
                plt.colorbar(ticks=[v_min, 0.5 * (v_min + v_max) ,v_max])
        self._plot_id += 1
        return image_plt

    def showColorBar(self, image_plt):
        plt.colorbar(image_plt)
        self._plot_id += 1

    def setPlot(self, row_id, col_id):
        self._plot_id = self._num_cols * (row_id-1) + col_id


def createFigure(title, font_size=15):
    fig, axes = plt.subplots(figsize=(11, 5))
    fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.05, wspace=0.05)
    fig.suptitle(title, fontsize=font_size)


## Maximize the matplot window.
def showMaximize():
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()
