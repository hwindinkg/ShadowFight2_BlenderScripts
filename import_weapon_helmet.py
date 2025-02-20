import xml.etree.ElementTree as ET
import bpy
import mathutils

def create_node(name, x, y, z):
    bpy.ops.object.empty_add(location=(x, y, z))
    obj = bpy.context.object
    obj.name = name
    return obj

def create_edge(node1, node2, radius=0.01):
    length = (node1.location - node2.location).length
    midpoint = (node1.location + node2.location) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=midpoint)
    obj = bpy.context.object
    direction = node2.location - node1.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()
    return obj

def create_triangle(node1, node2, node3):
    mesh = bpy.data.meshes.new(name="Triangle")
    obj = bpy.data.objects.new(name="Triangle", object_data=mesh)
    bpy.context.collection.objects.link(obj)
    mesh.from_pydata([node1.location, node2.location, node3.location], [], [(0, 1, 2)])
    mesh.update()
    return obj

def import_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    nodes = {}
    edges = []
    triangles = []

    for node in root.find('Nodes'):
        name = node.tag
        x = float(node.attrib['X'])
        y = float(node.attrib['Y'])
        z = float(node.attrib['Z'])
        nodes[name] = create_node(name, x, y, z)

    for edge in root.find('Edges'):
        end1 = edge.attrib['End1']
        end2 = edge.attrib['End2']
        radius = float(edge.attrib.get('Radius', 0.01)) # default radius is 0.01 if not specified
        edges.append((nodes[end1], nodes[end2], radius))

    for figure in root.find('Figures'):
        if figure.attrib['Type'] == 'Triangle':
            node1 = figure.attrib['Node1']
            node2 = figure.attrib['Node2']
            node3 = figure.attrib['Node3']
            triangles.append((nodes[node1], nodes[node2], nodes[node3]))

    for edge in edges:
        create_edge(*edge)

    for triangle in triangles:
        create_triangle(*triangle)

xml_filepath  = "path/to/file.xml"

import_xml(xml_filepath)
