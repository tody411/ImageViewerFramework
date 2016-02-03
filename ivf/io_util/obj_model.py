
# -*- coding: utf-8 -*-
## @package ivf.io_util.obj_model
#
#  ivf.io_util.obj_model utility package.
#  @author      tody
#  @date        2016/02/02


# Numpy module
import numpy as np

import os


## Save Wavefront OBJ data.
def saveOBJ(filePath, vertices, index_array, vertex_colors = None):
    f_out = open(filePath, 'w')

    f_out.write("####\n")
    f_out.write("#\n")
    f_out.write("# OBJ File Generated by python code\n")
    f_out.write("#\n")
    f_out.write("# Vertices: %s\n" %(vertices.shape[0]))
    f_out.write("# Faces: %s\n" %(len( index_array)))
    f_out.write("#\n")
    f_out.write("####\n")

    for vi, v in enumerate( vertices ):
        vStr = "v %s %s %s"  %(v[0], v[1], v[2])
        if vertex_colors is not None:
            color = vertex_colors[vi]
            vStr += " %s %s %s" %(color[0], color[1], color[2])
        vStr += "\n"
        f_out.write(vStr)
    f_out.write("# %s vertices\n\n"  %(vertices.shape[0]))

    for fvID in index_array:
        fStr = "f"
        for vID in fvID:
            fStr += " %s" %( vID + 1 )
        fStr += "\n"
        f_out.write(fStr)
    f_out.write("# %s faces\n\n"  %( len( index_array)) )

    f_out.write("# End of File\n")
    f_out.close()
