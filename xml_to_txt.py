import os
import xml.etree.ElementTree as ET
from PIL import Image
from add_bbox_tag import calculate_bounding_box
import unicodedata


class_names = ["neutrofilo", "linfocito", "monocito", "bastonete", "metamielocito", "eosinofilo"]
class_dict = {name: index for index, name in enumerate(class_names)}

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

    with open(txt_file, "w") as f:
        for obj in root.findall(".//objects/*"):
            class_name = unicodedata.normalize("NFKD", obj.tag).encode("ascii", "ignore").decode("ascii")
            print("Class name: ", class_name)

            if class_name not in class_dict:
                print(f"Unknown class: {class_name}")
                continue

            # Extract bounding box details
            bbox = obj.find("bbox")
            x, y, width, height = None, None, None, None
            if bbox is None:
                bbox = extract_bounding_box(obj)
                x, y, width, height = bbox
                print("bbox not on xml")
            else:
                x = float(bbox.find("x").text)
                y = float(bbox.find("y").text)
                width = float(bbox.find("width").text)
                height = float(bbox.find("height").text)
                print("bbox on xml")

            print("X: ", x, "Y: ", y, "Width: ", width, "Height: ", height)
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

def xml_to_txt_segmentation(xml_file, output_dir, image_size):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    txt_file = os.path.join(output_dir, os.path.basename(xml_file).replace(".xml", ".txt"))

    with open(txt_file, "w") as f:
        for obj in root.findall(".//objects/*"):
            class_name = unicodedata.normalize("NFKD", obj.tag).encode("ascii", "ignore").decode("ascii")
            print("Class name: ", class_name)

            if class_name not in class_dict:
                print(f"Unknown class: {class_name}")
                continue

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
                

def process_dataset(image_dir, xml_dir, output_dir):
    for xml_file in os.listdir(xml_dir):
        if xml_file.endswith(".xml"):
            print(f"Processing {xml_file}")
            xml_path = os.path.join(xml_dir, xml_file)

            # Extract the corresponding image path and get image size
            image_path = os.path.join(image_dir, xml_file.replace(".xml", ".jpg"))
            img = Image.open(image_path)
            image_size = img.size

            # Convert XML to YOLO format
            xml_to_txt(xml_path, output_dir, image_size)

def process_dataset_segmentation(image_dir, xml_dir, output_dir):
    for xml_file in os.listdir(xml_dir):
        if xml_file.endswith(".xml"):
            print(f"Processing {xml_file}")
            xml_path = os.path.join(xml_dir, xml_file)

            # Extract the corresponding image path and get image size
            image_path = os.path.join(image_dir, xml_file.replace(".xml", ".jpg"))
            img = Image.open(image_path)
            image_size = img.size

            # Convert XML to YOLO format
            # xml_to_txt(xml_path, output_dir, image_size)
            xml_to_txt_segmentation(xml_path, output_dir, image_size)


# *********************************************MAIN*********************************************
def __main__():
    # if not os.path.exists("../datasets/leucograma/labels"):
    #     os.makedirs("../datasets/leucograma/labels")
    # if not os.path.exists("../datasets/leucograma/labels/train"):
    #     os.makedirs("../datasets/leucograma/labels/train")
    # if not os.path.exists("../datasets/leucograma/labels/valid"):
    #     os.makedirs("../datasets/leucograma/labels/valid")

    process_dataset_segmentation("datasets/vet_v8/images/train", "datasets/vet_v8/annotations/train", "datasets/vet_v8/labels/train")
    process_dataset_segmentation("datasets/vet_v8/images/test", "datasets/vet_v8/annotations/test", "datasets/vet_v8/labels/test")
    
    # process_dataset("datasets/vet_v8/images/train", "datasets/vet_v8/annotations/train", "datasets/vet_v8/labels/train")
    # process_dataset("datasets/vet_v8/images/test", "datasets/vet_v8/annotations/test", "datasets/vet_v8/labels/test")


if(__name__ == "__main__"):
    __main__()
