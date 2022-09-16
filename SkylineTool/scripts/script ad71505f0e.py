import cv2
import numpy as np
import bpy, bmesh


img = cv2.imread("C:/Users/G513/Documents/prueba.png")

dimensions = img.shape
area = dimensions[0] * dimensions[1]

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

for i in contours:
    if cv2.contourArea(i) > 0.01 * area:
        epsilon = 0.01 * cv2.arcLength(i, True)
        aprox = cv2.approxPolyDP(i,epsilon, True)
        verts = aprox * -0.3
        #cv2.drawContours(img, [aprox], 0, (0,255,0), 2)
        #cv2.imshow("contorno", img)
        #cv2.waitKey(0)
        bm = bmesh.new()
        for v in verts:
            bm.verts.new((v[0][0], v[0][1], 0))
        bm.faces.new(bm.verts)
        bm.faces.ensure_lookup_table()

        bm.normal_update()
        bm.faces[0].select = True
        me = bpy.data.meshes.new("")
        bm.to_mesh(me)

        ob = bpy.data.objects.new("", me)
        bpy.context.collection.objects.link(ob)
        #bpy.ops.object.select_all(action='DESELECT')
        #print(bpy.context.active_object)
        #bpy.context.view_layer.objects.active = ob
        #ob.select_set(True)
        #bpy.context.view_layer.update()
        #print(bpy.context.active_object)
        #bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.extrude_faces_move(TRANSFORM_OT_shrink_fatten={"value":-100})
        #bpy.ops.object.mode_set(mode='OBJECT')
        
#bpy.ops.object.editmode_toggle()
bpy.context.view_layer.objects.active = bpy.context.collection.objects['Object']
bpy.ops.object.select_all(action='DESELECT')

for obj in bpy.context.collection.objects:
     if obj.type == 'MESH':
        obj.select_set(True)

context = bpy.context.copy()
context.update(active_object = bpy.context.collection.objects['Object'])

bpy.ops.object.mode_set(context, mode='EDIT')
bpy.ops.mesh.extrude_context_move(TRANSFORM_OT_translate=({"value":(0,0,100)}))
bpy.ops.object.mode_set(context, mode='OBJECT')

 

