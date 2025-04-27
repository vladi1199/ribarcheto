import csv
import requests
from bs4 import BeautifulSoup
import os

# Функция за четене на SKU кодове от CSV файл
def read_sku_codes_from_csv(file_path):
    sku_codes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Пропускане на заглавния ред
            for row in reader:
                sku_codes.append(row[0])  # Предполага се, че SKU кодът е в първата колона
    except FileNotFoundError:
        print(f"Файлът {file_path} не е намерен!")
    return sku_codes

# Функция за извършване на търсене и извличане на линк към продукта
def search_and_get_product_link(sku_code):
    search_url = f"https://www.ribarcheto.bg/index.php?route=product/search&search={sku_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Извличане на линк към първия намерен продукт
    product_div = soup.find('div', class_='product-thumb')
    if product_div:
        product_link = product_div.find('a')['href']
        return product_link
    return None

# Функция за проверка на наличността на продукта
def check_product_availability(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Извличане на наличността от <dd><span class="tb_stock_status_in_stock">В наличност</span></dd>
    availability_span = soup.find('span', class_='tb_stock_status_in_stock')
    if availability_span:
        # Ако има текст "В наличност", продуктът е наличен
        return "Наличен"
    else:
        # Ако няма текст "В наличност", продуктът е изчерпан
        return "Изчерпан"

# Функция за записване на резултатите в CSV файл
def save_results_to_csv(results, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['SKU', 'Наличност'])  # Записване на заглавията на колоните
        for result in results:
            writer.writerow(result)

# Основна функция за изпълнение на програмата
def main():
    sku_list_file = "/Users/vladimir/Desktop/Python/Наличности/Рибачето/sku_list.csv"  # Път до CSV файла
    results_file_path = "/Users/vladimir/Desktop/Python/Наличности/Рибачето/results.csv"  # Път за записване на резултатите
    
    # Четене на SKU кодовете от CSV файла
    sku_codes = read_sku_codes_from_csv(sku_list_file)
    
    results = []  # Списък за резултатите
    
    # Проверка на наличността на продуктите
    for sku in sku_codes:
        print(f"Започва търсене за модел: {sku}")
        product_link = search_and_get_product_link(sku)
        
        if product_link:
            print(f"Намерени линк към продукта: {product_link}")
            availability = check_product_availability(product_link)
            results.append([sku, availability])  # Добавяне на резултатите в списъка
        else:
            results.append([sku, "Изчерпан"])  # Ако не е намерен продукт
            
    # Записване на резултатите в CSV файл
    save_results_to_csv(results, results_file_path)
    print(f"Резултатите са записани в: {results_file_path}")

if __name__ == "__main__":
    main()
