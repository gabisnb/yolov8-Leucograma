import os
import xml.etree.ElementTree as ET
from PIL import Image
from add_bbox_tag import calculate_bounding_box
import unicodedata
import argparse
import random


class_names = ["neutrofilo", "linfocito", "monocito", "bastonete", "metamielocito", "eosinofilo", "metarrubricito"]
class_dict = {name: index for index, name in enumerate(class_names)}

parser = argparse.ArgumentParser(description="Um script que converte arquivos XML de anotações de linfócitos para o formato YOLO.")
parser.add_argument("-d", "--dir", help="Diretório do dataset.", required=True)
parser.add_argument("-s", "--segmentation", action="store_true", help="Converter para a versão de segmentação.")
parser.add_argument("-c", "--count", action="store_true", help="Contar o número de indivíduos por classe.")
parser.add_argument("-b", "--balanced", action="store_true", help="Gerar dataset balanceado.")

source_dir = parser.parse_args().dir
source_dir = source_dir.rstrip("/")
count = parser.parse_args().count
count_dict = count and {name: 0 for name in class_names} or {}

balance = parser.parse_args().balanced

def extract_bounding_box(obj):
    bbox = obj.find("bbox")
    if bbox is None:
        # add bbox tag
        points = []
        i = 1

        while obj.find("x"+str(i)) is not None:
            x_ = float(obj.find("x"+str(i)).text)
            y_ = float(obj.find("y"+str(i)).text)
            points.append([x_, y_])
            i += 1
        bbox = calculate_bounding_box(points)
        return bbox
    return bbox
    

def extract_points(obj):
    points_temp = obj.find("points")

    if points_temp is None:
        if obj.find("bbox") is not None:
            print("No points found")
            exit(1)
        points_temp = obj

    points = []
    i = 1
    # for point in points_temp:
    while points_temp.find("x"+str(i)) is not None:
        x = float(points_temp.find("x"+str(i)).text)
        y = float(points_temp.find("y"+str(i)).text)
        points.append([x, y])
        i += 1
    print(i)
    return points

def xml_to_txt(xml_file, output_dir, image_size):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    txt_file = os.path.join(output_dir, os.path.basename(xml_file).replace(".xml", ".txt"))
    class_count = {name: 0 for name in class_names}
    is_unbalanced = balance

    with open(txt_file, "w") as f:
        for obj in root.findall(".//objects/*"):
            class_name = unicodedata.normalize("NFKD", obj.tag).encode("ascii", "ignore").decode("ascii")
            # print("Class name: ", class_name)

            if class_name not in class_dict:
                print(f"Unknown class in {xml_file}: {class_name}")
                continue
            
            if balance and class_name != "neutrofilo":
                is_unbalanced = False

            if count:
                class_count[class_name] += 1

            # Extract bounding box details
            bbox = obj.find("bbox")
            x, y, width, height = None, None, None, None
            if bbox is None:
                bbox = extract_bounding_box(obj)
                x, y, width, height = bbox
                # print("bbox not on xml")
            else:
                x = float(bbox.find("x").text)
                y = float(bbox.find("y").text)
                width = float(bbox.find("width").text)
                height = float(bbox.find("height").text)
                # print("bbox on xml")

            # print("X: ", x, "Y: ", y, "Width: ", width, "Height: ", height)
            class_id = class_dict[class_name]

            # Calculate YOLO format: normalized center x, center y, width, height
            dw = 1.0 / image_size[1]
            dh = 1.0 / image_size[0]
            x_center = (x + width / 2.0) * dw
            y_center = (y + height / 2.0) * dh
            normalized_width = width * dw
            normalized_height = height * dh

            # Write the annotation in YOLO format: class_id x_center y_center width height
            f.write(f"{class_id} {x_center} {y_center} {normalized_width} {normalized_height}\n")

    # Antigo
    # if class_count["neutrofilo"] > 2 * max([class_count[name] for name in class_names if name != "neutrofilo"]):
    #     is_unbalanced = True

    # if class_count["linfocito"] > 3 * max([class_count[name] for name in class_names if name != "linfocito"]):
    #     is_unbalanced = True

    # if class_count["eosinofilo"] > 3 * max([class_count[name] for name in class_names if name != "eosinofilo"]):
    #     is_unbalanced = True
    
    # Novo
    if balance and not is_unbalanced:
        if class_count["metarrubricito"] > 0 or class_count["metamielocito"] > 0:
            is_unbalanced = False

        elif class_count["monocito"] > 1 or class_count["bastonete"] > 1 or class_count["eosinofilo"] > 1:
            is_unbalanced = False

        else:
            if class_count["neutrofilo"] > max([class_count[name] for name in class_names if name != "neutrofilo"]):
                is_unbalanced = True

            if class_count["linfocito"] > 2 * max([class_count[name] for name in class_names if name != "linfocito"]):
                is_unbalanced = True

            if class_count["eosinofilo"] > 3 * max([class_count[name] for name in class_names if name != "eosinofilo"]):
                is_unbalanced = True

    if count and not is_unbalanced:
        for class_name, cnt in class_count.items():
            count_dict[class_name] += cnt

    return is_unbalanced

def xml_to_txt_segmentation(xml_file, output_dir, image_size):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    txt_file = os.path.join(output_dir, os.path.basename(xml_file).replace(".xml", ".txt"))
    class_count = {name: 0 for name in class_names}
    is_unbalanced = balance

    with open(txt_file, "w") as f:
        for obj in root.findall(".//objects/*"):
            class_name = unicodedata.normalize("NFKD", obj.tag).encode("ascii", "ignore").decode("ascii")
            # print("Class name: ", class_name)

            if class_name not in class_dict:
                print(f"Unknown class in {xml_file}: {class_name}")
                continue

            if balance and class_name != "neutrofilo":
                is_unbalanced = False

            if count:
                count_dict[class_name] += 1
            
            # Extract bounding box details
            points = extract_points(obj)
            class_id = class_dict[class_name]

            # Calculate YOLO format: normalized points
            dw = 1.0 / image_size[1]
            dh = 1.0 / image_size[0]
            for point in points:
                point[0] = point[0] * dw
                point[1] = point[1] * dh

            # Write the annotation in YOLO format: class_id x_center y_center width height
            file = f"{class_id}"
            for point in points:
                file = file + " " + str(point[0]) + " " + str(point[1])
            file = file + "\n"
            f.write(file)

    if balance and not is_unbalanced:
        if class_count["metarrubricito"] > 0 or class_count["metamielocito"] > 0:
            is_unbalanced = False

        elif class_count["monocito"] > 1 or class_count["bastonete"] > 1 or class_count["eosinofilo"] > 1:
            is_unbalanced = False

        else:
            if class_count["neutrofilo"] > max([class_count[name] for name in class_names if name != "neutrofilo"]):
                is_unbalanced = True

            if class_count["linfocito"] > 2 * max([class_count[name] for name in class_names if name != "linfocito"]):
                is_unbalanced = True

            if class_count["eosinofilo"] > 3 * max([class_count[name] for name in class_names if name != "eosinofilo"]):
                is_unbalanced = True

    if count and not is_unbalanced:
        for class_name, cnt in class_count.items():
            count_dict[class_name] += cnt
    return is_unbalanced
                

def process_dataset(image_dir, xml_dir, output_dir):
    num_img = 0
    for xml_file in os.listdir(xml_dir):
        if xml_file.endswith(".xml"):
            # print(f"Processing {xml_file}")
            xml_path = os.path.join(xml_dir, xml_file)

            # Extract the corresponding image path and get image size
            image_path = os.path.join(image_dir, xml_file.replace(".xml", ".jpg"))
            img = Image.open(image_path)
            image_size = img.size

            # Convert XML to YOLO format
            is_unbalanced = xml_to_txt(xml_path, output_dir, image_size)
            if balance and is_unbalanced:
                os.remove(image_path)
                os.remove(xml_path)
                os.remove(os.path.join(output_dir, xml_file.replace(".xml", ".txt")))
            else:
                num_img+=1

    return num_img

def process_dataset_segmentation(image_dir, xml_dir, output_dir):
    num_img = 0
    for xml_file in os.listdir(xml_dir):
        if xml_file.endswith(".xml"):
            print(f"Processing {xml_file}")
            xml_path = os.path.join(xml_dir, xml_file)

            # Extract the corresponding image path and get image size
            image_path = os.path.join(image_dir, xml_file.replace(".xml", ".jpg"))
            img = Image.open(image_path)
            image_size = img.size

            # Convert XML to YOLO format
            is_unbalanced = xml_to_txt_segmentation(xml_path, output_dir, image_size)
            if balance and is_unbalanced:
                os.remove(image_path)
                os.remove(xml_path)
                os.remove(os.path.join(output_dir, xml_file.replace(".xml", ".txt")))
            else:
                num_img+=1

    return num_img


# *********************************************MAIN*********************************************

def __main__():

    if parser.parse_args().balanced:
        str = input("Gerar dataset balanceado em "+ source_dir +" (y/n)? Imagens poderão ser excluídas durante o processo. ")
        if str.lower() == "n":
            print("Operação cancelada.")
            return
        elif str.lower() != "y":
            print("Entrada inválida. Operação cancelada.")
            return
        
    os.makedirs(source_dir+"/labels/train", exist_ok=True)
    os.makedirs(source_dir+"/labels/val", exist_ok=True)
    os.makedirs(source_dir+"/labels/test", exist_ok=True)

    num_img = None

    if parser.parse_args().segmentation:          
        num_img = process_dataset_segmentation(source_dir+"/images/train", source_dir+"/annotations/train", source_dir+"/labels/train")
        num_img += process_dataset_segmentation(source_dir+"/images/val", source_dir+"/annotations/val", source_dir+"/labels/val")
        num_img += process_dataset_segmentation(source_dir+"/images/test", source_dir+"/annotations/test", source_dir+"/labels/test")
    else:
        num_img = process_dataset(source_dir+"/images/train", source_dir+"/annotations/train", source_dir+"/labels/train")
        num_img += process_dataset(source_dir+"/images/val", source_dir+"/annotations/val", source_dir+"/labels/val")
        num_img += process_dataset(source_dir+"/images/test", source_dir+"/annotations/test", source_dir+"/labels/test")

    if num_img == None:
        print("\nErro na contagem de imagens!")
    else:
        print(f"\nNúmero total de imagens: {num_img}")

    if count:
        print("\nContagem de indivíduos por classe:")
        for class_name, cnt in count_dict.items():
            print(f"{class_name}: {cnt}")



if(__name__ == "__main__"):
    __main__()
