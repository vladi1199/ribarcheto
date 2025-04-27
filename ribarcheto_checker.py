import csv
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Зареждаме променливите от .env файл
load_dotenv()

base_path = os.getenv('BASE_PATH') if os.getenv('GITHUB_ACTIONS') != 'true' else os.getcwd()

# Функция за четене на SKU кодове от CSV файл
def read_sku_codes_from_csv(file_path):
    sku_codes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Пропускане на заглавния ред
            for row in reader:
                sku_codes.append(row[0])
    except FileNotFoundError:
        print(f"Файлът {file_path} не е намерен!")
    return sku_codes

# Функция за извличане на линк към продукта
def search_and_get_product_link(sku_code):
    search_url = f"https://www.ribarcheto.bg/index.php?route=product/search&search={sku_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_div = soup.find('div', class_='product-thumb')
    if product_div:
        return product_div.find('a')['href']
    return None

# Функция за проверка на наличността
def check_product_availability(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    availability_span = soup.find('span', class_='tb_stock_status_in_stock')
    if availability_span:
        return "Наличен"
    else:
        return "Изчерпан"

# Функция за записване на резултатите в CSV файл
def save_results_to_csv(results, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['SKU', 'Наличност'])
        for result in results:
            writer.writerow(result)

# Основна функция
def main():
    sku_list_file = os.path.join(base_path, "sku_list.csv")
    results_file_path = os.path.join(base_path, "results.csv")
    
    sku_codes = read_sku_codes_from_csv(sku_list_file)
    
    results = []
    for sku in sku_codes:
        print(f"Започва търсене за модел: {sku}")
        product_link = search_and_get_product_link(sku)
        
        if product_link:
            print(f"Намерен линк: {product_link}")
            availability = check_product_availability(product_link)
            results.append([sku, availability])
        else:
            results.append([sku, "Изчерпан"])
    
    save_results_to_csv(results, results_file_path)
    print(f"Резултатите са записани в: {results_file_path}")

if __name__ == "__main__":
    main()
