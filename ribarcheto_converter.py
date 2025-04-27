import csv
import xml.etree.ElementTree as ET
import os

def csv_to_xml(csv_file, xml_file):
    if not os.path.exists(csv_file):
        print(f"Файлът {csv_file} не е намерен!")
        return

    root = ET.Element('products')

    with open(csv_file, encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Прескачаме заглавния ред
        
        for row in reader:
            if not row:
                continue
            sku = row[0]
            availability = row[1]
            
            item = ET.SubElement(root, 'item')
            
            sku_elem = ET.SubElement(item, 'sku')
            sku_elem.text = sku
            
            avail_elem = ET.SubElement(item, 'availability')
            avail_elem.text = availability

    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
    print(f"✅ XML файлът е успешно създаден: {xml_file}")

if __name__ == "__main__":
    # ВАЖНО: Актуализиран път с "Рибачето"
    base_path = "/Users/vladimir/Desktop/Python/Наличности/Рибачето"
    csv_file = os.path.join(base_path, "results.csv")
    xml_file = os.path.join(base_path, "products_sync.xml")

    csv_to_xml(csv_file, xml_file)
