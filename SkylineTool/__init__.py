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

import bpy, bmesh
import numpy as np
from bpy.types import Panel, Operator
import cv2

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
    imagen : bpy.props.StringProperty(
        name='Ruta de la imagen',
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
        row.operator("text.clean_scene_operator")

        row = layout.row()
        row.operator("text.create_skyline_operator")


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

class ST_OP_CreateSkylineFromMatrix(Operator):
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
class ST_OP_Create_CreateSkylineFromImage(Operator):
    def execute(self, context):
        #Import image from path
        img = cv2.imread(context.scene.propiedades.imagen)
        #Calculate area of image in pixels
        dimensions = img.shape
        area = dimensions[0] * dimensions[1]
        #Process image in Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV)
        #Compute Contours in image
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        
        for i in contours:
            if cv2.contourArea(i) > 0.01 * area:
                #aprox each contour as a Poly
                epsilon = 0.01 * cv2.arcLength(i, True)
                aprox = cv2.approxPolyDP(i,epsilon, True)
                #Proportional reduction from pixels to units
                verts = aprox * -0.3
                #Create a new mesh
                bm = bmesh.new()
                for v in verts:
                    bm.verts.new((v[0][0], v[0][1], 0))
                bm.faces.new(bm.verts)
                bm.faces.ensure_lookup_table()
                bm.normal_update()
                
                bm.faces[0].select = True
                me = bpy.data.meshes.new("")
                bm.to_mesh(me)
                #Create a new object from mesh
                ob = bpy.data.objects.new("", me)
                bpy.context.collection.objects.link(ob)


        return {'FINISHED'}


classes = [MyProperties, ST_PT_Panel, ST_OP_CleanScene, ST_OP_CreateSkylineFromMatrix]

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

