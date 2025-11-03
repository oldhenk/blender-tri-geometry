# TRI Tools
A Blender addon for working with Nebula tri geometry format.

## About
This addon adds two functions to Blender: import and export Geometry TRI files. Its purpose is to quickly generate/edit Geometry TRI files.

## Import-export
The import-export functionality follows the Nebula Geometry format specification (https://nebula-simulator.github.io/nebula-format-tri/). There exist other file formats that use the .tri extension, but those will not be readable. 

The data that is processed includes vertices, faces (tris only). Some data is discarded, since it cannot be represented in a simple way in Blender. This includes labels for vertices and surface points.

Due to blender default material not having inside or outside material the information is stored in the material name.

Import-export supports coordinate system transforms. Default settings make sense for nanometer models: scaled by a factor 100 and facing the opposite direction (positive Y). To import or export the model exactly as it is, set Scale to 1, Forward to -Y and Up to Z.

TRI Tools never changes the vertex order of any model. If you are making a new mesh from scratch, you need too triangulate before making a TRI for it.

