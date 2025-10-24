import os
import argparse

parser = argparse.ArgumentParser(description="Verifica a integridade dos arquivos de um dataset de imagens e anotações.")
parser.add_argument("-d", "--dir", help="Diretório do dataset.", required=True)

img_dir = parser.parse_args().dir + "/images"
ann_dir = parser.parse_args().dir + "/annotations"

# Verifica se os diretórios existem
if not os.path.isdir(img_dir):
    print(f"Diretório de imagens não encontrado: {img_dir}")
    exit(1)

if not os.path.isdir(ann_dir):
    print(f"Diretório de anotações não encontrado: {ann_dir}")
    exit(1)

# Conjunto de treinamento
for set in ["/val", "/test", "/train"]:
    if not os.path.isdir(img_dir + set) or not os.path.isdir(ann_dir + set):
        print(f"Conjunto não encontrado: {set}")
        continue
    for xml_file in os.listdir(ann_dir + set):
        if not xml_file.endswith(".xml"):
            print(f"Ignorando arquivo não XML: {xml_file}")
            continue
        img_file = xml_file.replace(".xml", ".jpg")
        if not os.path.isfile(os.path.join(img_dir + set, img_file)):
            print(f"Arquivo de imagem faltando para a anotação: {xml_file} em {set}")

    for img_file in os.listdir(img_dir + set):
        if not img_file.endswith(".jpg"):
            print(f"Ignorando arquivo não jpg: {img_file}")
            continue
        xml_file = img_file.replace(".jpg", ".xml")
        if not os.path.isfile(os.path.join(ann_dir + set, xml_file)):
            print(f"Arquivo de anotação faltando para a imagem: {img_file} em {set}")
    
