import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

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
async def search_and_get_product_link(session, sku_code):
    search_url = f"https://www.ribarcheto.bg/index.php?route=product/search&search={sku_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with session.get(search_url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        product_div = soup.find('div', class_='product-thumb')
        if product_div:
            return product_div.find('a')['href']
    return None

# Function to check product availability
async def check_product_availability(session, product_url):
    async with session.get(product_url) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
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

# Main function
async def main():
    sku_list_file = os.path.join(base_path, "sku_list.csv")
    results_file_path = os.path.join(base_path, "results.csv")
    
    sku_codes = read_sku_codes_from_csv(sku_list_file)
    
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for sku in sku_codes:
            print(f"Searching for model: {sku}")
            tasks.append(process_sku(session, sku, results))
        
        await asyncio.gather(*tasks)

    save_results_to_csv(results, results_file_path)
    print(f"Results saved to: {results_file_path}")

# Function to process each SKU
async def process_sku(session, sku, results):
    product_link = await search_and_get_product_link(session, sku)
    if product_link:
        print(f"Found link: {product_link}")
        availability = await check_product_availability(session, product_link)
        results.append([sku, availability])
    else:
        results.append([sku, "Out of stock"])

# Run the main function asynchronously
if __name__ == "__main__":
    asyncio.run(main())
