# -*- coding: utf-8 -*-
## @package ivf.batch.light_estimation_figure
#
#  ivf.batch.light_estimation_figure utility package.
#  @author      tody
#  @date        2016/02/19

import numpy as np
import cv2
import matplotlib.pyplot as plt
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.datasets.colormap import colorMapFiles, loadColorMap, colorMapFile
from ivf.datasets.shape import shapeFiles, shapeNames, shapeFile, shapeResultFile
from ivf.core.sfs.colormap_sphere import colorMapSphere
from ivf.np.norm import normalizeVector
from ivf.core.shader.light_sphere import lightSphere, lightSphereWithBG, lightSphereColorMap
from ivf.io_util.image import loadNormal
from ivf.core.shader.toon import ColorMapShader
from ivf.cv.image import luminance
from ivf.core.sfs.light_estimation import lightEstimation
from ivf.cv.normal import normalToColor
from ivf.core.sfs.angle_error import angleError
from ivf.util.timer import timing_func


@timing_func
def computeErrorTables(Lg=normalizeVector(np.array([-0.2, 0.3, 0.6]))):
    colormap_files = colorMapFiles()
    shape_names = shapeNames()

    num_materials = len(colormap_files)
    num_shapes = len(shape_names)

    L_errors = np.zeros((num_shapes, num_materials))

    Ms = []
    for colormap_file in colormap_files:
        M_32F = loadColorMap(colormap_file)
        Ms.append(M_32F)

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        for mi, M_32F in enumerate(Ms):
            C0_32F = ColorMapShader(M_32F).diffuseShading(Lg, Ng_32F)
            I_32F = luminance(C0_32F)

            L = lightEstimation(I_32F, N0_32F, A_8U)

            L_errors[si, mi] = angleError(Lg, L)

    file_path = shapeResultFile("LightEstimation", "LightEstimationError", file_ext=".npy")
    np.save(file_path, L_errors)


def errorInfo():
    colormap_files = colorMapFiles()
    shape_names = shapeNames()

    num_materials = len(colormap_files)
    num_shapes = len(shape_names)

    file_path = shapeResultFile("LightEstimation", "LightEstimationError", file_ext=".npy")
    L_errors = np.load(file_path)

    shape_errors = np.zeros(num_shapes)
    for si, shape_name in enumerate(shape_names):
        shape_errors[si] = np.average(L_errors[si, :])

    shape_error_orders = np.argsort(shape_errors)
    print shape_error_orders
    print shape_error_orders[:3]
    print shape_error_orders[-3:]

    for shape_error_order in shape_error_orders[:3]:
        print shape_names[shape_error_order]

    for shape_error_order in shape_error_orders[-3:]:
        print shape_names[shape_error_order]

    material_errors = np.zeros(num_materials)
    for mi in xrange(num_materials):
        material_errors[mi] = np.average(L_errors[:, mi])

    material_error_orders = np.argsort(material_errors)

    print material_error_orders[:3]
    print material_error_orders[-3:]


def lightEstimationFigure():
    target_colormaps = [23, 0, 6, 22, 4, 12]
    target_shapes = ["Raptor", "Man", "Blob1", "OctaFlower", "Pulley", "Cone"]
    colormap_files = [colorMapFile(cmap_id) for cmap_id in target_colormaps]
    shape_names = target_shapes

    num_rows = len(shape_names) + 1
    num_cols = len(colormap_files) + 1

    w = 10
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, hspace=0.05, wspace=0.05)
    fig.suptitle("", fontsize=font_size)


    plot_grid = SubplotGrid(num_rows, num_cols)

    Lg = normalizeVector(np.array([-0.2, 0.3, 0.6]))
    Lg_img = lightSphere(Lg)

    plot_grid.showImage(Lg_img, "")

    Ms = []

    for colormap_file in colormap_files:
        M_32F = loadColorMap(colormap_file)
        Cs_32F = colorMapSphere(Lg, M_32F)

        plot_grid.showImage(Cs_32F, "")

        Ms.append(M_32F)

    L_errors = np.zeros((num_rows, num_cols))

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        plot_grid.showImage(normalToColor(Ng_32F, A_8U), "")

        for mi, M_32F in enumerate(Ms):
            C0_32F = ColorMapShader(M_32F).diffuseShading(Lg, Ng_32F)
            I_32F = luminance(C0_32F)

            L = lightEstimation(I_32F, N0_32F, A_8U)
            L_errors[si, mi] = angleError(Lg, L)

            L_img = lightSphereColorMap(L, v=L_errors[si, mi], v_min=0, v_max=40)

            plot_grid.showImage(L_img, "")


    L_error_min, L_error_max = np.min(L_errors), np.max(L_errors)

    file_path = shapeResultFile("LightEstimation", "LightEstimationError")
    fig.savefig(file_path, transparent=True)


if __name__ == '__main__':
    lightEstimationFigure()
