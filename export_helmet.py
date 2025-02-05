import xml.etree.ElementTree as ET
import bpy
from mathutils import Vector 

def compute_lcc(location):
    x, y, z = location.x, location.y, location.z

    lcc1 = 0.0448 * x - 0.0239 * y - 0.0455 * z + 5.6771 + 0.02
    lcc2 = 0.00043 * x + 0.00072 * y + 0.0909 * z - 0.9873
    lcc3 = -0.0460 * x - 0.0223 * y - 0.0451 * z + 5.3259 - 0.002
    lcc4 = 0.00077 * x + 0.0454 * y - 0.00036 * z - 9.0352 + 0.02

    return lcc1, lcc2, lcc3, lcc4

def export_xml(filepath):
    root = ET.Element('Scene')
    nodes_element = ET.SubElement(root, 'Nodes')
    edges_element = ET.SubElement(root, 'Edges')
    figures_element = ET.SubElement(root, 'Figures')

    nodes = {}
    node_id = 1

    def transform_coordinates(location):
        new_x = location.x
        new_y = location.z
        new_z = -location.y
        return new_x, new_y, new_z

    def get_node_id(location):
        nonlocal node_id
        node_name = f'MacroParadox-Node{node_id}'

        # Поворот координат
        new_x, new_y, new_z = transform_coordinates(location)
        
        lcc1, lcc2, lcc3, lcc4 = compute_lcc(Vector((new_x, new_y, new_z)))
        node_element = ET.SubElement(nodes_element, node_name, {
            'Type': 'MacroNode',
            'X': f'{new_x:.6f}',
            'Y': f'{new_y:.6f}',
            'Z': f'{new_z:.6f}',
            'Mass': '0.001',
            'Fixed': '1',
            'Visible': '1',
            'NodesCount': '4',
            'ChildNode1': 'NHeadS_1',
            'ChildNode2': 'NHeadF',
            'ChildNode3': 'NHeadS_2',
            'ChildNode4': 'NTop',
            'LCC1': f'{lcc1:.3f}',
            'LCC2': f'{lcc2:.3f}',
            'LCC3': f'{lcc3:.3f}',
            'LCC4': f'{lcc4:.3f}'
        })
        nodes[node_name] = (node_id, location)
        node_id += 1
        return node_name

    # Экспорт только выделенных объектов
    selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    for obj in selected_objects:
        mesh = obj.data
        for poly in mesh.polygons:
            vertices = [mesh.vertices[vertex].co for vertex in poly.vertices]
            node_ids = [get_node_id(location) for location in vertices]
            ET.SubElement(figures_element, f'MacroParadox-Triangle-{node_id}', {
                'Type': 'Triangle',
                'DoubleSided': '1',
                'Node1': node_ids[0],
                'Node2': node_ids[1],
                'Node3': node_ids[2]
            })

    # Красивое форматирование XML
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                indent(subelem, level + 1)
            if not subelem.tail or not subelem.tail.strip():
                subelem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    indent(root)

    tree = ET.ElementTree(root)
    with open(filepath, "wb") as f:
        tree.write(f, encoding='Windows-1251', xml_declaration=True, method="xml")

# Укажите путь для сохранения XML файла
xml_filepath = "D:/sf/123.xml"
export_xml(xml_filepath)
