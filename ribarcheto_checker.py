import csv
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import urllib.parse  # Importing urllib to properly encode URLs

# Зареждаме променливите от .env файл
load_dotenv()

# Dynamically set base path based on the environment
if os.getenv('GITHUB_ACTIONS') == 'true':  # Check if running in GitHub Actions
    base_path = os.getcwd()  # GitHub Actions uses the current working directory (root of repo)
else:
    base_path = '/Users/vladimir/Desktop/Python/Наличности/Рибачето'  # Local path for local execution

# Function to read SKU codes from CSV file
def read_sku_codes_from_csv(file_path):
    sku_codes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                sku_codes.append(row[0])
    except FileNotFoundError:
        print(f"File {file_path} not found!")
    return sku_codes

# Function to extract product link
def search_and_get_product_link(sku_code):
    search_url = f"https://www.ribarcheto.bg/index.php?route=product/search&search={sku_code}"
    search_url_encoded = urllib.parse.quote(search_url, safe=':/?=&')
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url_encoded, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_div = soup.find('div', class_='product-thumb')
    if product_div:
        return product_div.find('a')['href']
    return None

# Function to check product availability
def check_product_availability(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    availability_span = soup.find('span', class_='tb_stock_status_in_stock')
    if availability_span:
        return "Available"
    else:
        return "Out of stock"

# Function to save results to CSV file
def save_results_to_csv(results, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['SKU', 'Availability'])
        for result in results:
            writer.writerow(result)

# Function to save "not found" products to a separate CSV file
def save_not_found_skus_to_csv(not_found_skus, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['SKU'])
        for sku in not_found_skus:
            writer.writerow([sku])

# Main function
def main():
    sku_list_file = os.path.join(base_path, "sku_list.csv")
    results_file_path = os.path.join(base_path, "results.csv")
    not_found_file_path = os.path.join(base_path, "not_found_skus.csv")
    
    sku_codes = read_sku_codes_from_csv(sku_list_file)
    
    results = []
    not_found_skus = []  # List to store SKUs not found
    
    for sku in sku_codes:
        print(f"Searching for model: {sku}")
        product_link = search_and_get_product_link(sku)
        
        if product_link:
            print(f"Found link: {product_link}")
            availability = check_product_availability(product_link)
            results.append([sku, availability])
        else:
            not_found_skus.append(sku)  # Add SKU to not found list
    
    save_results_to_csv(results, results_file_path)
    save_not_found_skus_to_csv(not_found_skus, not_found_file_path)  # Save not found SKUs
    print(f"Results saved to: {results_file_path}")
    print(f"Not found SKUs saved to: {not_found_file_path}")

if __name__ == "__main__":
    main()
