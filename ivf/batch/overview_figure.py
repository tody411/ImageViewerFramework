# -*- coding: utf-8 -*-
## @package ivf.batch.overview_figure
#
#  ivf.batch.overview_figure utility package.
#  @author      tody
#  @date        2016/02/21
import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.datasets.shape import shapeFile, shapeResultFile
from ivf.io_util.image import loadNormal, saveRGBA, saveNormal, saveRGB
from ivf.datasets.colormap import colorMapFile, loadColorMap
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.np.norm import normalizeVector
from ivf.core.shader.toon import ColorMapShader, ToonShader
from ivf.cv.image import setAlpha, to32F, gray2rgb, to8U
from ivf.core.sfs.toon_sfs import ToonSFS
from ivf.cv.normal import normalToColor, normalizeImage
from ivf.core.shader.light_sphere import lightSphere
from ivf.core.sfs.silhouette_normal import silhouetteNormal
from ivf.core.shader.shader import LdotN


def overviewFigure():
    cmap_id = 10
    colormap_file = colorMapFile(cmap_id)

    num_rows = 1
    num_cols = 5

    w = 10
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.02, hspace=0.05, wspace=0.05)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    L = normalizeVector(np.array([-0.4, 0.6, 0.6]))
    L_img = lightSphere(L)

    shape_name = "ThreeBox"

    Ng_data = shapeFile(shape_name)
    Ng_data = loadNormal(Ng_data)
    Ng_32F, A_8U = Ng_data

    N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
    N0_data = loadNormal(N0_file)
    N0_32F, A_8U = N0_data

    M_32F = loadColorMap(colormap_file)
    Cg_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

    borders=[0.6, 0.8, 0.92]
    colors = [np.array([0.2, 0.2, 0.4]),
              np.array([0.3, 0.3, 0.6]),
              np.array([0.4, 0.4, 0.8]),
              np.array([0.5, 0.5, 1.0])]
    #Cg_32F = ToonShader(borders, colors).diffuseShading(L, Ng_32F)
    #Cg_32F = cv2.GaussianBlur(Cg_32F, (0,0), 2.0)

    sfs_method = ToonSFS(L, Cg_32F, A_8U)
    sfs_method.setInitialNormal(N0_32F)
    sfs_method.setNumIterations(iterations=40)
    sfs_method.setWeights(w_lap=10.0)
    sfs_method.run()

    N_32F = sfs_method.normal()
    I_32F = np.float32(np.clip(LdotN(L, N_32F), 0.0, 1.0))
    I0_32F = np.float32(np.clip(LdotN(L, N0_32F), 0.0, 1.0))
    C_32F = sfs_method.shading()
    C0_32F = sfs_method.initialShading()

    M_32F = sfs_method.colorMap().mapImage()

    L1 = normalizeVector(np.array([0.0, 0.6, 0.6]))
    L1_img = lightSphere(L1)
    C1_32F = sfs_method.relighting(L1)

    L2 = normalizeVector(np.array([0.5, 0.8, 0.6]))
    L2_img = lightSphere(L2)
    C2_32F = sfs_method.relighting(L2)

    N_sil = silhouetteNormal(A_8U, sigma=7.0)
    N_sil[:, :, 2]  = N_sil[:, :, 2] ** 10.0
    N_sil = normalizeImage(N_sil)
    A_sil = 1.0 - N_sil[:, :, 2]
    A_sil = to8U(A_sil)
    N_xy = N_sil[:, :, 0] ** 2 + N_sil[:, :, 1] ** 2
    A_sil[N_xy < 0.1] = 0

    title = ""
    plot_grid.showImage(setAlpha(Cg_32F, to32F(A_8U)), title)
    plot_grid.showImage(normalToColor(N0_32F, A_8U), title)
    plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), title)
    plot_grid.showImage(normalToColor(N_32F, A_8U), title)

    plot_grid.showImage(setAlpha(C_32F, to32F(A_8U)), title)
    # plot_grid.showImage(normalToColor(Ng_32F, A_8U), title)

    #showMaximize()
    file_path = shapeResultFile("Overview", "Overview")
    fig.savefig(file_path, transparent=True)

    file_path = shapeResultFile("Overview", "Cg")
    saveRGBA(file_path, setAlpha(Cg_32F, to32F(A_8U)))

    file_path = shapeResultFile("Overview", "L")
    saveRGB(file_path, gray2rgb(to8U(L_img)))

    file_path = shapeResultFile("Overview", "L1")
    saveRGB(file_path, gray2rgb(to8U(L1_img)))

    file_path = shapeResultFile("Overview", "L2")
    saveRGB(file_path, gray2rgb(to8U(L2_img)))

    file_path = shapeResultFile("Overview", "N0")
    saveNormal(file_path, N0_32F, A_8U)

    file_path = shapeResultFile("Overview", "N_sil")
    saveNormal(file_path, N_sil, A_sil)

    file_path = shapeResultFile("Overview", "N")
    saveNormal(file_path, N_32F, A_8U)

    file_path = shapeResultFile("Overview", "C0")
    saveRGBA(file_path, setAlpha(C0_32F, to32F(A_8U)))

    file_path = shapeResultFile("Overview", "C")
    saveRGBA(file_path, setAlpha(C_32F, to32F(A_8U)))

    file_path = shapeResultFile("Overview", "C1")
    saveRGBA(file_path, setAlpha(C1_32F, to32F(A_8U)))

    file_path = shapeResultFile("Overview", "C2")
    saveRGBA(file_path, setAlpha(C2_32F, to32F(A_8U)))

    file_path = shapeResultFile("Overview", "I")
    saveRGBA(file_path, setAlpha(gray2rgb(I_32F), to32F(A_8U)))

    file_path = shapeResultFile("Overview", "I0")
    saveRGBA(file_path, setAlpha(gray2rgb(I0_32F), to32F(A_8U)))

    file_path = shapeResultFile("Overview", "M")
    saveRGB(file_path, M_32F)

if __name__ == '__main__':
    overviewFigure()