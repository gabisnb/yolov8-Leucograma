import os
from tqdm.auto import tqdm
import xml.etree.ElementTree as ET
import numpy as np

#read the objects in the annotation xml file
def parse_annotation(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for obj in root.find("objects"):
        if(obj.find("bbox") != None):
            return
        
        xCoords = []
        yCoords = []
        for coord in obj:
            print(coord)
            if coord.tag.find("x") != -1:
                xCoords.append(float(coord.text))
                i = coord.tag.replace('x', 'y')
                print(i)
                y = obj.find(i)
                yCoords.append(float(y.text))
                obj.remove(y)
            # elif (coord.tag.find("y") != -1):
            #     yCoords.append(float(coord.text))

            obj.remove(coord)
        
        if len(xCoords) != len(yCoords):
            print("Erro: numero de coordenadas incompatível")
            return
        xmin, ymin, width, height = calculate_bounding_box_normalized(xCoords, yCoords)

        # adds points tag
        points = ET.Element("points")
        for i in range(len(xCoords)):
            newX = ET.Element("x" + str(i+1))
            newX.text = str(xCoords[i])
            points.append(newX)
            
            newY = ET.Element("y" + str(i+1))
            newY.text = str(yCoords[i])
            points.append(newY)

        # adds bbox tag
        bbox = ET.Element("bbox")
        x = ET.Element("x")
        x.text = str(xmin)
        bbox.append(x)

        y = ET.Element("y")
        y.text = str(ymin)
        bbox.append(y)

        w = ET.Element("width")
        w.text = str(width)
        bbox.append(w)

        h = ET.Element("height")
        h.text = str(height)
        bbox.append(h)

        obj.append(bbox)
        obj.append(points)
        tree.write(xml_file)

#calculate bounding boxes with points provided
def calculate_bounding_box_normalized(xCoords, yCoords):
    coords = [xCoords, yCoords]
    points = np.column_stack(coords)

    min_x = float(np.min(points[0, :]))
    min_y = float(np.min(points[1, :]))

    max_x = float(np.max(points[0, :]))
    max_y = float(np.max(points[1, :]))

    width =  max_x - min_x
    height = max_y - min_y

    return (min_x, min_y, width, height)

parse_annotation("/home/gabriela/projetos/yolov8keras/Bach1/annotations/459P-0000.xml")