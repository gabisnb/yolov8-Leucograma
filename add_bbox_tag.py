from bs4 import BeautifulSoup
from os import listdir, path, makedirs
from glob import glob
# from xml_to_new_format import find

import numpy as np
import cv2
import re

# localização do bean leaf dataset
dataset_path = "./data/new_dataset/"

# localização onde serão salvos os xml alterados
output_path = "./data/new_dataset2/"

# plotar e salvar imagens com o poligono e seu bouding box
isPlot = False


bbox_template = """<bbox>
        <x>{0}</x>
        <y>{1}</y>
        <width>{2}</width>
        <height>{3}</height>
      </bbox>
      <normalized-polygon>"""


def calculate_bounding_box(points: [float]) -> (float, float, float):
    points = np.array(points)

    min_x = np.min(points[:, 0])
    min_y = np.min(points[:, 1])

    width = np.max(points[:, 0]) - min_x
    height = np.max(points[:, 1]) - min_y

    return (min_x, min_y, width, height)


def extract_leaf_points(polygon_str: str) -> [float]:
    str_points = polygon_str.split("\n")
    float_points = []

    regex = r'(0\.\d+)'

    for i in range(0, len(str_points), 2):
        x = float(re.search(regex, str_points[i]).group(1))
        y = float(re.search(regex, str_points[i + 1]).group(1))
        float_points.append([x, y])
    return float_points


def process_xml(xml_content: str) -> (str, [float], (float, float, float, float)):
    xml = BeautifulSoup(xml_content, 'xml')

    polygon = find(xml, "leaf.normalized-polygon")
    updated_xml = None

    if polygon:
        leaf_points = extract_leaf_points(polygon)
        bbox = calculate_bounding_box(leaf_points)
        updated_xml = xml_content.replace(
            "<normalized-polygon>", bbox_template.format(*bbox))

    return updated_xml, leaf_points, bbox


def plot(poly: [float], bbox: (float, float, float, float)) -> np.array:
    size = 512
    image = np.zeros((size, size, 3), dtype=np.uint8)

    leaf_points = [[int(x * size), int(y * size)] for x, y in poly]
    scaled_points = np.array(leaf_points, np.int32)

    cv2.fillPoly(image, [scaled_points], color=(255, 0, 0))

    x, y, width, height = bbox
    top_left = (int(x * size), int(y * size))
    bottom_right = (int((x + width) * size),
                    int((y + height) * size))

    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    return image


if __name__ == "__main__":
    for dir in listdir(dataset_path):
        print(dir)

        out_path = path.join(output_path, dir, "annotations")
        makedirs(out_path, exist_ok=True)

        if isPlot:
            plot_out_path = path.join(output_path, dir, "plots")
            makedirs(plot_out_path, exist_ok=True)

        # Lê nome de arquivos xml e garante que estejam em ordem alfabética
        annotations = glob(
            path.join(dataset_path, dir, "annotations", "*.xml"))
        annotations.sort()

        for xml_path in annotations:
            file_name = path.basename(xml_path)

            with open(xml_path) as file:
                xml_content = "".join(file.readlines())
                updated_xml, leaf_points, bbox = process_xml(xml_content)

            if updated_xml is None:
                print("Erro no arquivo:", xml_path)
                print("Tag leaf.normalized-polygon não encontrada")
                continue

            if isPlot:
                image = plot(leaf_points, bbox)
                img_name = file_name.replace(".xml", ".jpg")
                img_path = path.join(plot_out_path, img_name)
                print(img_path)
                cv2.imwrite(img_path, image)

            with open(path.join(out_path, file_name), "w") as out_file:
                out_file.write(updated_xml)
