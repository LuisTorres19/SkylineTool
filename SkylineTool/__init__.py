# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "SkylineTool",
    "author" : "LTorres",
    "description" : "",
    "blender" : (2, 93, 9),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import numpy as np
import os
from bpy.types import Panel, Operator
from bpy_extras.io_utils import ImportHelper

matrix = []

class MyProperties(bpy.types.PropertyGroup):
    escala : bpy.props.FloatProperty(
        name= 'Escala',
        soft_min= 0
    )
    matriz : bpy.props.StringProperty(
        name= 'Ruta de matriz',
        subtype= 'FILE_PATH'
    )


class ST_PT_Panel(Panel):
    bl_idname = "ST_PT_Panel"
    bl_label = "Skyline Tool"
    bl_category = "Skyline Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        

        row = layout.row()
        row.prop(context.scene.propiedades, 'escala')

        row = layout.row()
        row.prop(context.scene.propiedades, 'matriz')

        row = layout.row()
        row.operator("text.load_matrix_operator")

        row = layout.row()
        row.operator("text.clean_scene_operator")

        row = layout.row()
        row.operator("text.create_skyline_operator")

class ST_OP_LoadMatrix(Operator, ImportHelper):
    bl_idname = "text.load_matrix_operator"
    bl_label = "Cargar Matriz"

    def execute(self, context):
        self.report({'INFO'}, 'Input File Path: ' + str(self.filepath))
        context.scene.propiedades.matriz = self.filepath
        return {'FINISHED'}


class ST_OP_CleanScene(Operator):
    bl_idname = "text.clean_scene_operator"
    bl_label = "Limpiar Escena"

    def execute(self, context):
        for obj in context.scene.objects:
            obj.select_set(False)
            if obj.type == 'MESH':
                obj.select_set(True)                                
        bpy.ops.object.delete()
        return{'FINISHED'}


class ST_OP_CreateSkyline(Operator):
    bl_idname = "text.create_skyline_operator"
    bl_label = "Crear Escena"

    def execute(self, context):
        escala = context.scene.propiedades.escala
        if(context.scene.propiedades.matriz):
            matrix = np.loadtxt(context.scene.propiedades.matriz)
            matrix = np.array(matrix)
        if(matrix.any() and escala):
            (columnas, filas) = matrix.shape
            x0 = columnas * escala / 2
            y0 = filas * escala / 2
            bpy.ops.mesh.primitive_plane_add()
            bpy.context.active_object.scale = (columnas * escala / 2, filas * escala / 2, 1)
            for i in range(columnas):
                for j in range(filas):
                    if(matrix[i][j]):
                        bpy.ops.mesh.primitive_cube_add(
                            scale=(escala/2,escala/2,escala/2),
                            location=((escala/2 + escala*i - x0),(escala/2 + escala*j - y0),escala/2)
                            )

        return {'FINISHED'}


classes = [MyProperties, ST_PT_Panel, ST_OP_LoadMatrix, ST_OP_CleanScene, ST_OP_CreateSkyline]

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.propiedades =  bpy.props.PointerProperty(type=MyProperties)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.propiedades


if __name__ == "__main__":
    register()

