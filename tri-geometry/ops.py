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
import bpy_extras

from . import io as io

AXES = [
    ("X", "X", "X axis"), 
    ("Y", "Y", "Y axis"), 
    ("Z", "Z", "Z axis"),
    ("-X", "-X", "Negative X axis"), 
    ("-Y", "-Y", "Negative Y axis"), 
    ("-Z", "-Z", "Negative Z axis"),
]

class TRIOperator(bpy.types.Operator):
    def execute(self, context):
        try:
            self.execute_impl(context)
        
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        
        return {'FINISHED'}


@bpy_extras.io_utils.orientation_helper(axis_forward='Y', axis_up='Z')
class TRIExport(TRIOperator, bpy_extras.io_utils.ExportHelper):
    bl_label = 'Export TRI'
    bl_idname = 'export_mesh.geometry_tri'
    bl_description = "Export Geometry TRI file"
    
    filename_ext = ".tri"
    
    filter_glob: bpy.props.StringProperty(
        default="*.tri",
        options={'HIDDEN'})
        
    length_scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale of exported model",
        default=100.0)
    
    def invoke(self, context, event):
        obj = context.active_object
        
        if obj == None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh")
            return {'CANCELLED'}
        
        self.filepath = obj.name
        return bpy_extras.io_utils.ExportHelper.invoke(self, context, event)
    
    def execute_impl(self, context):
        io.export_tri(self, context.active_object)


@bpy_extras.io_utils.orientation_helper(axis_forward='Y', axis_up='Z')
class TRIImport(TRIOperator, bpy_extras.io_utils.ImportHelper):
    bl_label = 'Import TRI'
    bl_idname = 'import_mesh.geometry_tri'
    bl_description = "Import Geometry TRI file"
    bl_options = {'UNDO'}
    
    filename_ext = ".tri"
    
    filter_glob: bpy.props.StringProperty(
        default="*.tri",
        options={'HIDDEN'})
    
    length_scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale of imported model",
        default=100.0)
    
    def execute_impl(self, context):
        io.import_tri(self, context)

def exportop(self, context):
    self.layout.operator(TRIExport.bl_idname, text="Geometry TRI (.tri)")
    
def importop(self, context):
    self.layout.operator(TRIImport.bl_idname, text="Geometry TRI (.tri)")

def register():
    bpy.utils.register_class(TRIExport)
    bpy.utils.register_class(TRIImport)
    
    bpy.types.TOPBAR_MT_file_import.append(importop)
    bpy.types.TOPBAR_MT_file_export.append(exportop)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(exportop)
    bpy.types.TOPBAR_MT_file_import.remove(importop)
    
    bpy.utils.unregister_class(TRIExport)
    bpy.utils.unregister_class(TRIImport)