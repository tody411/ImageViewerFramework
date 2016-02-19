# -*- coding: utf-8 -*-
## @package ivf.batch.shape_estimation_figure
#
#  ivf.batch.shape_estimation_figure utility package.
#  @author      tody
#  @date        2016/02/19
import numpy as np
import matplotlib.pyplot as plt

from ivf.datasets.colormap import colorMapFile, loadColorMap
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.np.norm import normalizeVector
from ivf.core.shader.light_sphere import lightSphere
from ivf.core.sfs.colormap_sphere import colorMapSphere
from ivf.datasets.shape import shapeFile, shapeResultFile, shapeNames
from ivf.io_util.image import loadNormal
from ivf.core.sfs.pr_sfs import Wu08SFS
from ivf.core.shader.toon import ColorMapShader
from ivf.cv.normal import normalToColor
from ivf.core.shader.lambert import LambertShader
from ivf.cv.image import to32F, setAlpha
from ivf.core.sfs.toon_sfs import ToonSFS


def fullLuminanceConstraintFigure():
    target_colormaps = [23, 0, 6, 22, 4, 12]
    colormap_files = [colorMapFile(cmap_id) for cmap_id in target_colormaps]

    # target_shapes = ["Raptor", "Man", "Blob1", "OctaFlower", "Pulley", "Cone"][:4]
    #shape_names = target_shapes
    shape_names = shapeNames()[3:7]

    num_rows = len(shape_names) + 1
    num_cols = 5

    w = 10
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, hspace=0.05, wspace=0.05)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    L = normalizeVector(np.array([-0.2, 0.3, 0.6]))
    L_img = lightSphere(L)

    plot_grid.showImage(L_img, "")
    plot_grid.showImage(L_img, "")
    plot_grid.showImage(L_img, "")
    plot_grid.showImage(L_img, "")
    plot_grid.showImage(L_img, "")

    M_32F = loadColorMap(colormap_files[-3])

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        plot_grid.showImage(normalToColor(Ng_32F, A_8U), "")

        # C0_32F = LambertShader().diffuseShading(L, Ng_32F)
        C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        sfs_method = ToonSFS(L, C0_32F, A_8U)
        sfs_method.setInitialNormal(N0_32F)
        sfs_method.run()
        N_32F = sfs_method.normal()
        C_32F = sfs_method.shading()
        C_error = sfs_method.shadingError()
        C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0

        plot_grid.showImage(normalToColor(N_32F, A_8U), "")
        plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), "")
        plot_grid.showImage(setAlpha(C_32F, to32F(A_8U)), "")
        plot_grid.showColorMap(C_error, "", v_min=0, v_max=0.1)

    showMaximize()
    #file_path = shapeResultFile("LightEstimation", "LightEstimationError")
    #fig.savefig(file_path, transparent=True)

if __name__ == '__main__':
    fullLuminanceConstraintFigure()