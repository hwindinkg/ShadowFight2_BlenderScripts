import xml.etree.ElementTree as ET
import bpy
import mathutils
import os

def create_node(name, x, y, z):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, y, z))
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

def create_capsule(node1, node2, radius1, radius2):
    length = (node1.location - node2.location).length
    midpoint = (node1.location + node2.location) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=radius1, depth=length, location=midpoint)
    obj = bpy.context.object
    direction = node2.location - node1.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()
    return obj

def import_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    nodes = {}
    edges = []
    triangles = []
    capsules = []

    # Определяем тип файла по его названию
    filename = os.path.basename(filepath)
    is_armor_or_body = "armor" in filename.lower() or "body" in filename.lower()
    is_weapon_or_helmet = "weapon" in filename.lower() or "helmet" in filename.lower()

    # Обрабатываем узлы
    for node in root.find('Nodes'):
        name = node.tag
        x = float(node.attrib['X'])
        y = float(node.attrib['Y'])
        z = float(node.attrib['Z'])
        nodes[name] = create_node(name, x, y, z)

    # Если это файл типа armor, body, weapon или helmet, добавляем обработку рёбер и треугольников
    if is_armor_or_body or is_weapon_or_helmet:
        # Обрабатываем рёбра
        for edge in root.find('Edges'):
            node1 = edge.attrib['End1']
            node2 = edge.attrib['End2']
            radius = float(edge.attrib.get('Radius', 0.01))  # default radius is 0.01 if not specified
            if node1 in nodes and node2 in nodes:
                edges.append((nodes[node1], nodes[node2], radius))
            else:
                print(f"Warning: One of the nodes for edge {edge.tag} is missing")

        # Обрабатываем треугольники
        for figure in root.find('Figures'):
            if figure.attrib['Type'] == 'Triangle':
                node1 = figure.attrib['Node1']
                node2 = figure.attrib['Node2']
                node3 = figure.attrib['Node3']
                if node1 in nodes and node2 in nodes and node3 in nodes:
                    triangles.append((nodes[node1], nodes[node2], nodes[node3]))
                else:
                    print(f"Warning: One of the nodes for triangle {figure.tag} is missing")
            elif figure.attrib['Type'] == 'Capsule':
                edge = figure.attrib['Edge']
                radius1 = float(figure.attrib['Radius1'])
                radius2 = float(figure.attrib['Radius2'])
                for e in edges:
                    if e[0].name == edge.split('-')[0] and e[1].name == edge.split('-')[1]:
                        capsules.append((e[0], e[1], radius1, radius2))
                        break
                else:
                    print(f"Warning: The edge for capsule {figure.tag} is missing")

        for edge in edges:
            create_edge(*edge)

        for triangle in triangles:
            create_triangle(*triangle)

        for capsule in capsules:
            create_capsule(*capsule)


# Укажите путь к вашему XML файлу
xml_filepath  = "path/to/file.xml"

import_xml(xml_filepath)
