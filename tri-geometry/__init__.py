#Copyright 2024 Jordan Ingram
#
#This file is part of TRI Geometry, a Blender addon for working with 
#Nebula geometry format
#
#TRI Geometry is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#TRI Geometry is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with TRI Geometry. If not, see <https://www.gnu.org/licenses/>.
import bpy

from . import ops as ops

bl_info = {
    'name': "TRI Geometry",
    'author': "Jordan Ingram",
    'version': (1, 2, 0),
    'blender': (3, 2, 0),
    'location': "File > Import-Export and View3D > Tools",
    'description': "Import and export Geometry TRI files, and transfer shape keys by proximity between meshes",
    'doc_url': "",
    'category': "Mesh"}

class MaterialControl(bpy.types.Panel):
    """Creates a Panel in the Material properties window"""
    bl_label = "Index Nodes"
    bl_idname = "MATERIAL_PT_showIndex"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        nt = context.material.node_tree
        for n in nt.nodes:
            if n.bl_idname == 'ShaderNodeValue':
                r = layout.row()
                r.label(text=n.name)
                r.prop(n.outputs[0], "default_value", text="")

def register():
    ops.register()
    bpy.utils.register_class(MaterialControl)

def unregister():
    ops.unregister()
    bpy.utils.unregister_class(MaterialControl)
