# -*- coding: utf-8 -*-
## @package ivf.batch.shape_estimation_figure
#
#  ivf.batch.shape_estimation_figure utility package.
#  @author      tody
#  @date        2016/02/19
import numpy as np
import matplotlib.pyplot as plt
import cv2

from ivf.datasets.colormap import colorMapFile, loadColorMap, colorMapFiles
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
from ivf.cv.image import to32F, setAlpha, trim
from ivf.core.sfs.toon_sfs import ToonSFS
from ivf.core.sfs.angle_error import angleErros


def computeLambertShadingError():
    shape_names = shapeNames()

    L = normalizeVector(np.array([-0.2, 0.3, 0.6]))

    C_errors = np.zeros(len(shape_names))
    N_errors = np.zeros(len(shape_names))

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        C0_32F = LambertShader().diffuseShading(L, Ng_32F)

        sfs_method = ToonSFS(L, C0_32F, A_8U)
        sfs_method.setInitialNormal(N0_32F)
        sfs_method.setNumIterations(iterations=60)
        sfs_method.run()
        N_32F = sfs_method.normal()
        C_32F = sfs_method.shading()
        C_error = sfs_method.shadingError()
        C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0

        C_errors[si] = np.average(C_error[A_8U > 0.5 * np.max(A_8U)])

        h, w = A_8U.shape[:2]
        N_error = angleErros(N_32F.reshape(-1, 3), N0_32F.reshape(-1, 3)).reshape(h, w)
        N_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        N_errors[si] = np.average(N_error[A_8U > 0.5 * np.max(A_8U)])

    file_path = shapeResultFile("ShapeEstimation", "ShadingError", file_ext=".npy")
    np.save(file_path, C_errors)

    file_path = shapeResultFile("ShapeEstimation", "NormalError", file_ext=".npy")
    np.save(file_path, N_errors)


def errorInfo():
    shape_names = shapeNames()
    file_path = shapeResultFile("ShapeEstimation", "ShadingError", file_ext=".npy")
    C_errors = np.load(file_path)
    C_error_orders = np.argsort(C_errors)

    print "Small Shading Error: ", np.min(C_errors)
    for C_error_order in C_error_orders[:5]:
        print "  ", shape_names[C_error_order]

    print "Large Shading Error: ", np.max(C_errors)
    for C_error_order in C_error_orders[-5:]:
        print "  ", shape_names[C_error_order]

    file_path = shapeResultFile("ShapeEstimation", "NormalError", file_ext=".npy")
    N_errors = np.load(file_path)

    N_error_orders = np.argsort(N_errors)

    print "Small Normal Error: ", np.min(N_errors)
    for N_error_order in N_error_orders[:5]:
        print "  ", shape_names[N_error_order]

    print "Large Normal Error: ", np.max(N_errors)
    for N_error_order in N_error_orders[-5:]:
        print "  ", shape_names[N_error_order]


def LambertShadingFigure():
    target_shapes = ["Sphere", "Cone", "Blob1", "Man", "Cone", "OctaFlower", "Pulley", "Grog", "Lucy", "Raptor"]
    target_shapes = ["Blob1", "OctaFlower", "Lucy"]
    shape_names = target_shapes

    num_rows = len(shape_names)
    num_cols = 6

    w = 15
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.02, hspace=0.15, wspace=0.05)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    L = normalizeVector(np.array([-0.2, 0.3, 0.6]))

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        C0_32F = LambertShader().diffuseShading(L, Ng_32F)

        sfs_method = ToonSFS(L, C0_32F, A_8U)
        sfs_method.setInitialNormal(N0_32F)
        sfs_method.setNumIterations(iterations=70)
        sfs_method.run()
        N_32F = sfs_method.normal()
        C_32F = sfs_method.shading()
        C_error = sfs_method.shadingError()
        C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        C_error = trim(C_error, A_8U)

        h, w = A_8U.shape
        N_error = angleErros(N_32F.reshape(-1, 3), N0_32F.reshape(-1, 3)).reshape(h, w)
        N_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        N_error = trim(N_error, A_8U)

        title = ""
        if si == 0:
            title =  "Input"
        plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), title)

        title = ""
        if si == 0:
            title =  "Estimated"
        plot_grid.showImage(setAlpha(C_32F, to32F(A_8U)), title)

        title = ""
        if si == 0:
            title = "Error (Color)"
        plot_grid.showColorMap(C_error, title, v_min=0, v_max=0.1, with_colorbar=True)

        title = ""
        if si == 0:
            title =  "Input"
        plot_grid.showImage(normalToColor(Ng_32F, A_8U), title)

        title = ""
        if si == 0:
            title = "Estimated"
        plot_grid.showImage(normalToColor(N_32F, A_8U), title)

        title = ""
        if si == 0:
            title = "Error (Angle)"

        plot_grid.showColorMap(N_error, title, v_min=0, v_max=30.0, with_colorbar=True)

    file_path = shapeResultFile("ShapeEstimation", "LambertEstimationError")
    fig.savefig(file_path, transparent=True)


def materialShapeVariationFigure():
    target_colormaps = [23, 6, 22, 12]
    target_colormaps = [3, 17]
    colormap_files = [colorMapFile(cmap_id) for cmap_id in target_colormaps]

    target_shapes = ["Blob1", "ThreeBox"]
    shape_names = target_shapes
    #shape_names = shapeNames()[4:5]

    num_shapes = len(shape_names)
    num_colormaps = len(colormap_files)
    num_rows = 2 * num_shapes
    num_cols = 3 * num_colormaps + 1

    w = 10
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.1, hspace=0.05, wspace=0.05)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    L = normalizeVector(np.array([-0.2, 0.3, 0.6]))

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        plot_grid.setPlot(2 * si + 2, 1)

        plot_grid.showImage(normalToColor(Ng_32F, A_8U), "")

        for mi, colormap_file in enumerate(colormap_files):
            M_32F = loadColorMap(colormap_file)
            C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)
            #C0_32F = cv2.bilateralFilter(C0_32F, 0, 0.1, 3)

            sfs_method = ToonSFS(L, C0_32F, A_8U)
            sfs_method.setInitialNormal(N0_32F)
            sfs_method.setNumIterations(iterations=40)
            sfs_method.setWeights(w_lap=5.0)
            sfs_method.run()

            N_32F = sfs_method.normal()
            C_32F = sfs_method.shading()
            #C_32F = cv2.bilateralFilter(C_32F, 0, 0.1, 3)
            C_error = sfs_method.shadingError()

            C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
            C_error = trim(C_error, A_8U)

            h, w = A_8U.shape
            N_error = angleErros(N_32F.reshape(-1, 3), N0_32F.reshape(-1, 3)).reshape(h, w)
            N_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
            N_error = trim(N_error, A_8U)

            plot_grid.setPlot(2 * si + 1, 3 * mi + 2)

            plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), "")
            plot_grid.showImage(setAlpha(C_32F, to32F(A_8U)), "")
            plot_grid.showColorMap(C_error, "", v_min=0, v_max=0.1, with_colorbar=False)

            plot_grid.setPlot(2 * si + 2, 3 * mi + 3)
            plot_grid.showImage(normalToColor(N_32F, A_8U), "")
            plot_grid.showColorMap(N_error, "", v_min=0, v_max=30.0, with_colorbar=False)



    showMaximize()
    file_path = shapeResultFile("ShapeEstimation", "MaterialShapeEvaluation")
    fig.savefig(file_path, transparent=True)

if __name__ == '__main__':
    materialShapeVariationFigure()
