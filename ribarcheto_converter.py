import csv
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Зареждаме променливите от .env файл
load_dotenv()

# Проверка дали сме в GitHub Actions и определяне на базовата папка
if os.getenv('GITHUB_ACTIONS') == 'true':  # Check if running in GitHub Actions
    base_path = os.getcwd()  # GitHub Actions uses the current working directory (root of repo)
else:
    base_path = '/Users/vladimir/Desktop/Python/Наличности/Рибачето'  # Local path for local execution


def csv_to_xml(csv_file, xml_file):
    if not os.path.exists(csv_file):
        print(f"Файлът {csv_file} не е намерен!")
        return

    root = ET.Element('products')

    with open(csv_file, encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        for row in reader:
            if not row:
                continue
            sku, availability = row[0], row[1]
            item = ET.SubElement(root, 'item')
            ET.SubElement(item, 'sku').text = sku
            ET.SubElement(item, 'availability').text = availability

    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
    print(f"✅ XML файлът е успешно създаден: {xml_file}")

if __name__ == "__main__":
    csv_file = os.path.join(base_path, "results.csv")
    xml_file = os.path.join(base_path, "products_sync.xml")
    csv_to_xml(csv_file, xml_file)
