"""I/O of the TRI file format according to the Nebula specification (https://nebula-simulator.github.io/nebula-format-tri/)"""

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

import os
import struct

import bpy
import mathutils
import bpy_extras

colors = {-122:(0.0343389, 0.313989, 0.708376, 1),-123:(0.327776, 0.0998987, 0.467784, 1),-124:(0.879618, 0.552012, 0.0047771, 1)
,-125:(0.791294, 0.208637, 0.0159964, 1),-126:(0.0273201, 0.603828, 0.165132, 1),-127:(0.799099, 0.0722718, 0.0451863, 1),-128:(0.0343395, 0.066626, 0.111932, 1)}

def SidedMaterial(material,indexMaterial,name):
    side = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    colorMix = material.node_tree.nodes.new('ShaderNodeMix')
    colorMix.location = (-240,0)
    colorMix.data_type = 'RGBA'
    colorMix.blend_type = 'MULTIPLY'
    material.node_tree.links.new(side.inputs[0], colorMix.outputs["Result"])

    extracolors = material.node_tree.nodes.new('ShaderNodeValToRGB')
    extracolors.color_ramp.elements[0].color = (1,1,1,1)
    extracolors.color_ramp.elements[1].color = (0,0,0,1)

    material.node_tree.links.new(colorMix.inputs["A"], extracolors.outputs["Color"])

    defaultcolors = material.node_tree.nodes.new('ShaderNodeValToRGB')
    defaultcolors.color_ramp.interpolation = 'CONSTANT'
    defaultcolors.color_ramp.elements.remove(defaultcolors.color_ramp.elements[0])
    indexes = list(colors.keys())[::-1]
    for i,index in enumerate(indexes):
        defaultcolors.color_ramp.elements.new(i/(len(indexes)+1))
        defaultcolors.color_ramp.elements[i].color = colors[index]

    material.node_tree.links.new(colorMix.inputs["B"], defaultcolors.outputs["Color"])

    mapPositive = material.node_tree.nodes.new('ShaderNodeMapRange')
    mapPositive.inputs[1].default_value = 0
    mapPositive.inputs[2].default_value = 4

    material.node_tree.links.new(extracolors.inputs[0], mapPositive.outputs[0])

    mapNegative = material.node_tree.nodes.new('ShaderNodeMapRange')
    mapNegative.inputs[1].default_value = -128
    mapNegative.inputs[2].default_value = -121

    material.node_tree.links.new(defaultcolors.inputs[0], mapNegative.outputs[0])

    lessThan = material.node_tree.nodes.new('ShaderNodeMath')
    lessThan.operation = 'LESS_THAN'
    lessThan.inputs[1].default_value = 0

    material.node_tree.links.new(colorMix.inputs[0], lessThan.outputs[0])

    insideIndex = material.node_tree.nodes.new('ShaderNodeValue')
    insideIndex.name = name
    insideIndex.outputs[0].default_value = indexMaterial

    material.node_tree.links.new(mapPositive.inputs[0], insideIndex.outputs[0])
    material.node_tree.links.new(mapNegative.inputs[0], insideIndex.outputs[0])
    material.node_tree.links.new(lessThan.inputs[0], insideIndex.outputs[0])
    return side

def TwoSideMaterial(insideI,outsideI):
    material = bpy.data.materials.new(name=f"{insideI}_{outsideI}")
    material.use_nodes = True

    # Remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
    material_output = material.node_tree.nodes.get('Material Output')
    mix = material.node_tree.nodes.new('ShaderNodeMixShader')
    geometry = material.node_tree.nodes.new('ShaderNodeNewGeometry')
    geometry.location = (-240,250)

    # link emission shader to material
    material.node_tree.links.new(material_output.inputs[0], mix.outputs[0])
    material.node_tree.links.new(mix.inputs[0], geometry.outputs["Backfacing"])
    outside = SidedMaterial(material,float(outsideI),"OutsideValue")
    material.node_tree.links.new(mix.inputs[1], outside.outputs[0])
    inside = SidedMaterial(material,float(insideI),"InsideValue")
    material.node_tree.links.new(mix.inputs[2], inside.outputs[0])
    return material

def export_tri(op, mesh):
    if mesh.matrix_world != mathutils.Matrix.Identity(4):
        op.report({'WARNING'}, "Object's world-space transform is not exported")
    
    #Gather data and validate export settings
    basis = bpy_extras.io_utils.axis_conversion(
        from_forward='-Y', 
        from_up='Z', 
        to_forward=op.axis_forward, 
        to_up=op.axis_up).to_4x4()
    
    V = len(mesh.data.vertices)
    
    tris = []
    for f in mesh.data.polygons:
        if len(f.vertices) == 3:
            tris.append(f)
        else:
            raise RuntimeError("Only tris and quads are supported")
    
    T = len(tris)

    #Start export
    with open(op.filepath, "w") as file:
        for f in tris:
            #fallback material
            inside = 128
            outside = 128
            material = mesh.data.materials[f.material_index]
            if material.node_tree.nodes["InsideValue"]:
                inside = round(material.node_tree.nodes["InsideValue"].outputs[0].default_value)
            else:
                raise RuntimeWarning(f"Couldn't find inside index node for material {matName}.(index will be set to 128)")
            if material.node_tree.nodes["OutsideValue"]:
                outside = round(material.node_tree.nodes["OutsideValue"].outputs[0].default_value)
            else:
                raise RuntimeWarning(f"Couldn't find outside index node for material {matName}.(index will be set to 128)")
            file.write(f"{inside} {outside}")
            for j in range(3):
                file.write(" " + " ".join([str(round(float(i))) for i in map(str,basis @ (op.length_scale * mesh.data.vertices[f.vertices[j]].co))]))
            file.write("\n")
        
        op.report({'INFO'}, op.filepath + " exported successfully")

def import_tri(op, context):
    with open(op.filepath, "r") as file:
        #Create and activate new mesh
        name = os.path.splitext(os.path.basename(op.filepath))[0]
        mesh_data = context.blend_data.meshes.new(name)
        mesh = context.blend_data.objects.new(name, mesh_data)
        
        bpy.ops.object.select_all(action='DESELECT')
        
        context.collection.objects.link(mesh)
        mesh.select_set(True)
        context.view_layer.objects.active = mesh
        
        #Start import
        lines = list(line for line in (l.strip() for l in file) if line)

        vertices = []
        faces = []
        mat_index = []
        material_dict = {}

        # Parse each line
        for i,line in enumerate(lines):
            parts = line.strip().split(' ')
            parts = [part for part in parts if part != '']
            if len(parts) >= 5:
                # Extract material names
                mat_name = f"{parts[0]}_{parts[1]}"
                mat_index.append(mat_name)
        
                # Check if the material already exists
                if mat_name not in material_dict:
                    # Create a new material
                    material = TwoSideMaterial(parts[0],parts[1])
                    material_dict[mat_name] = material
                else:
                    material = material_dict[mat_name]
                
                # Extract vertex coordinates
                for j in range(3):
                    x, y, z = map(float, parts[2 + j*3:5 + j*3])
                    vertices.append([x, y, z])
                faces.append([i*3,1 + i*3,2 + i*3])
        
        #transfer to the mesh
        mesh.data.from_pydata(vertices, [], faces)
        
        # Assign materials to the mesh
        mesh.data.materials.clear()
        for mat in material_dict.values():
            mesh.data.materials.append(mat)

        # Assign material to each face
        for i, poly in enumerate(mesh.data.polygons):
            mat_name = mat_index[i]
            poly.material_index = list(material_dict.keys()).index(mat_name)

        #in case of corrupt data, delete the mesh and cancel import
        if mesh.data.validate():
            if IS_2_79:
                context.scene.objects.unlink(mesh)
            else:
                context.collection.objects.unlink(mesh)
            context.blend_data.objects.remove(mesh)
            context.blend_data.meshes.remove(mesh_data)
            raise RuntimeError("Invalid mesh data; file is corrupt or in an unknown format")
        
        #Apply user transforms
        mesh.matrix_world = bpy_extras.io_utils.axis_conversion(
            from_forward=op.axis_forward, 
            from_up=op.axis_up, 
            to_forward='-Y', 
            to_up='Z').to_4x4()
        
        mesh.scale = (1 / op.length_scale, 1 / op.length_scale, 1 / op.length_scale)
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        
        op.report({'INFO'}, op.filepath + " imported successfully")


