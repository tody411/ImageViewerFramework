# -*- coding: utf-8 -*-
## @package ivf.batch.relighting_figure
#
#  ivf.batch.relighting_figure utility package.
#  @author      tody
#  @date        2016/02/22

import numpy as np
import matplotlib.pyplot as plt
import cv2

from ivf.np.norm import normalizeVector
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.datasets.shape import shapeFile, shapeResultFile
from ivf.io_util.image import loadNormal
from ivf.datasets.colormap import colorMapFile, loadColorMap
from ivf.core.shader.toon import ColorMapShader
from ivf.core.sfs.toon_sfs import ToonSFS
from ivf.batch.shape_estimation_figure import lumoSFS, wuSFS, estimatedReflectance
from ivf.core.shader.shader import LdotN
from ivf.cv.image import setAlpha, to32F
from ivf.core.shader.light_sphere import lightSphere
from ivf.plot.fig2np import figure2numpy
from ivf.io_util.video import saveVideo


def relightingVideo(shape_name="Ogre", cmap_id=3):
    num_methods = 3
    num_rows = 1
    num_cols = num_methods + 2

    num_lights = 120

    w = 10
    h = 5

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.04, hspace=0.15, wspace=0.1)
    fig.suptitle("Shading Analysis", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    Lg = normalizeVector(np.array([-0.2, 0.3, 0.5]))
    Lg_img = lightSphere(Lg)

    L1 = normalizeVector(np.array([0.5, 0.5, 0.6]))

    Ls = [normalizeVector(Lg * (1.0 - t) + t * L1) for t in np.linspace(0.0, 1.0, num_lights) ]
    # Ls = [normalizeVector(Lg + 1.0 * np.cos(t) * np.array([1, 0, 0]) + 1.0 * np.sin(t) * np.array([0, 1, 0])) for t in np.linspace(0.0, 1.0, num_lights) ]

    Ng_data = shapeFile(shape_name)
    Ng_data = loadNormal(Ng_data)
    Ng_32F, A_8U = Ng_data

    N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
    N0_data = loadNormal(N0_file)
    N0_32F, A_8U = N0_data
    A_8U = cv2.bilateralFilter(A_8U, 0, 5, 2)

    colormap_file = colorMapFile(cmap_id)
    M_32F = loadColorMap(colormap_file)
    C0_32F = ColorMapShader(M_32F).diffuseShading(Lg, Ng_32F)

    toon_sfs = ToonSFS(Lg, C0_32F, A_8U)
    toon_sfs.setInitialNormal(N0_32F)
    toon_sfs.setNumIterations(iterations=50)
    toon_sfs.setWeights(w_lap=1.0)
    toon_sfs.run()

    N_toon = toon_sfs.normal()
    C_toon = toon_sfs.shading()

    C_lumo, N_lumo = lumoSFS(C0_32F, Lg, N0_32F, A_8U)
    C_wu, N_wu = wuSFS(C0_32F, Lg, N0_32F, A_8U)

    M_lumo = estimatedReflectance(C0_32F, Lg, N_lumo, A_8U)
    M_wu = estimatedReflectance(C0_32F, Lg, N_wu, A_8U)

    plot_grid.showImage(Lg_img, "Light direction")
    plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), "Ground-truth")

    title = ""
    plot_grid.showImage(setAlpha(C_lumo, to32F(A_8U)), "Lumo")
    #plot_grid.showColorMap(C_error_lumo, title, v_min=0, v_max=0.1, with_colorbar=True)
    plot_grid.showImage(setAlpha(C_wu, to32F(A_8U)), "Lambert assumption")
    #plot_grid.showColorMap(C_error_wu, title, v_min=0, v_max=0.1, with_colorbar=True)
    plot_grid.showImage(setAlpha(C_toon, to32F(A_8U)), "Our result")
    #plot_grid.showColorMap(C_error_toon, title, v_min=0, v_max=0.1, with_colorbar=True)

    images = []

    for i in xrange(48):
        images.append(figure2numpy(fig))

    for li, L in enumerate(Ls):
        print li
        fig.clear()
        fig.suptitle("Relighting", fontsize=font_size)
        plot_grid.setPlot(1, 1)

        C1 = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        C1_lumo = M_lumo.shading(LdotN(L, N_lumo).flatten()).reshape(C0_32F.shape)
        C1_wu = M_wu.shading(LdotN(L, N_wu).flatten()).reshape(C0_32F.shape)
        C1_toon = toon_sfs.relighting(L)

        plot_grid.showImage(lightSphere(L), "Light direction")

        plot_grid.showImage(setAlpha(C1, to32F(A_8U)), "Ground-truth")

        title = ""
        plot_grid.showImage(setAlpha(C1_lumo, to32F(A_8U)), "Lumo")
    #plot_grid.showColorMap(C_error_lumo, title, v_min=0, v_max=0.1, with_colorbar=True)
        plot_grid.showImage(setAlpha(C1_wu, to32F(A_8U)), "Lambert assumption")
    #plot_grid.showColorMap(C_error_wu, title, v_min=0, v_max=0.1, with_colorbar=True)
        plot_grid.showImage(setAlpha(C1_toon, to32F(A_8U)), "Our result")

        images.append(figure2numpy(fig))

    file_path = shapeResultFile("Relighting", "Relighting_%s_%s" %(shape_name, cmap_id), file_ext=".wmv")
    saveVideo(file_path, images)


def relightingFigure():
    num_methods = 3
    num_lights = 2
    num_rows = num_lights + 1
    num_cols = num_methods + 2

    w = 15
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.04, hspace=0.15, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    Lg = normalizeVector(np.array([-0.2, 0.3, 0.5]))
    Lg_img = lightSphere(Lg)


    L1 = normalizeVector(np.array([ 0.3, 0.5, 0.6]))

    # Ls = [normalizeVector(Lg * (1.0 - t) + t * L1) for t in np.linspace(0.0, 1.0, num_lights) ]
    Ls = [normalizeVector(Lg + 0.5 * np.cos(t) * np.array(1, 0, 0) + 0.5 * np.sin(t) * np.array(0, 1, 0)) for t in np.linspace(0.0, 1.0, num_lights) ]

    shape_name = "Vase"

    Ng_data = shapeFile(shape_name)
    Ng_data = loadNormal(Ng_data)
    Ng_32F, A_8U = Ng_data

    N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
    N0_data = loadNormal(N0_file)
    N0_32F, A_8U = N0_data
    A_8U = cv2.bilateralFilter(A_8U, 0, 5, 2)

    cmap_id = 3
    colormap_file = colorMapFile(cmap_id)
    M_32F = loadColorMap(colormap_file)
    C0_32F = ColorMapShader(M_32F).diffuseShading(Lg, Ng_32F)

    toon_sfs = ToonSFS(Lg, C0_32F, A_8U)
    toon_sfs.setInitialNormal(N0_32F)
    toon_sfs.setNumIterations(iterations=20)
    toon_sfs.setWeights(w_lap=5.0)
    toon_sfs.run()

    N_toon = toon_sfs.normal()
    C_toon = toon_sfs.shading()

    C_lumo, N_lumo = lumoSFS(C0_32F, Lg, N0_32F, A_8U)
    C_wu, N_wu = wuSFS(C0_32F, Lg, N0_32F, A_8U)

    M_lumo = estimatedReflectance(C0_32F, Lg, N_lumo, A_8U)
    M_wu = estimatedReflectance(C0_32F, Lg, N_wu, A_8U)

    plot_grid.showImage(Lg_img, "Light direction")
    plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), "Ground-truth")

    title = ""
    plot_grid.showImage(setAlpha(C_lumo, to32F(A_8U)), "Lumo")
    #plot_grid.showColorMap(C_error_lumo, title, v_min=0, v_max=0.1, with_colorbar=True)
    plot_grid.showImage(setAlpha(C_wu, to32F(A_8U)), "Lambert assumption")
    #plot_grid.showColorMap(C_error_wu, title, v_min=0, v_max=0.1, with_colorbar=True)
    plot_grid.showImage(setAlpha(C_toon, to32F(A_8U)), "Our result")
    #plot_grid.showColorMap(C_error_toon, title, v_min=0, v_max=0.1, with_colorbar=True)

    for L in Ls:
        C1 = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        C1_lumo = M_lumo.shading(LdotN(L, N_lumo).flatten()).reshape(C0_32F.shape)
        C1_wu = M_wu.shading(LdotN(L, N_wu).flatten()).reshape(C0_32F.shape)
        C1_toon = toon_sfs.relighting(L)

        plot_grid.showImage(lightSphere(L), "")

        plot_grid.showImage(setAlpha(C1, to32F(A_8U)), "")

        title = ""
        plot_grid.showImage(setAlpha(C1_lumo, to32F(A_8U)), "")
    #plot_grid.showColorMap(C_error_lumo, title, v_min=0, v_max=0.1, with_colorbar=True)
        plot_grid.showImage(setAlpha(C1_wu, to32F(A_8U)), "")
    #plot_grid.showColorMap(C_error_wu, title, v_min=0, v_max=0.1, with_colorbar=True)
        plot_grid.showImage(setAlpha(C1_toon, to32F(A_8U)), "")

    # showMaximize()
    file_path = shapeResultFile("Relighting", "RelightingComparison", file_ext=".png")
    fig.savefig(file_path, transparent=True)

if __name__ == '__main__':
    relightingVideo(shape_name="Fertility", cmap_id=14)