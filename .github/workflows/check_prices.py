import os
import requests
import csv
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 商品情報
products = [
    {"name": "16 Pro 128GB", "id": "NewPrice_33821", "retail_price": 159800},
    {"name": "16 Pro 256GB", "id": "NewPrice_33831", "retail_price": 174800},
    {"name": "16 Pro 512GB", "id": "NewPrice_33841", "retail_price": 204800},
    {"name": "16 Pro 1TB", "id": "NewPrice_33851", "retail_price": 234800},
    {"name": "16 Pro Max 256GB", "id": "NewPrice_33781", "retail_price": 189800},
    {"name": "16 Pro Max 512GB", "id": "NewPrice_33791", "retail_price": 219800},
    {"name": "16 Pro Max 1TB", "id": "NewPrice_33801", "retail_price": 249800}
]

# モバイルミックスの商品情報
mobile_mix_products = [
    {"name": "16 Pro 128GB", "id": "model444", "retail_price": 159800},
    {"name": "16 Pro 256GB", "id": "model445", "retail_price": 174800},
    {"name": "16 Pro 512GB", "id": "model446", "retail_price": 204800},
    {"name": "16 Pro 1TB", "id": "model447", "retail_price": 234800},
    {"name": "16 Pro Max 256GB", "id": "model441", "retail_price": 189800},
    {"name": "16 Pro Max 512GB", "id": "model442", "retail_price": 219800},
    {"name": "16 Pro Max 1TB", "id": "model443", "retail_price": 249800}
]

# 買取Wikiの商品情報
wiki_products = [
    {"name": "16 Pro 128GB", "url": "https://iphonekaitori.tokyo/purchase/iPhone-16-Pro-128GB-desert", "id": "rank_n", "retail_price": 159800},
    {"name": "16 Pro 256GB", "url": "https://iphonekaitori.tokyo/purchase/iPhone-16-Pro-256GB-dessert", "id": "rank_n", "retail_price": 174800},
    {"name": "16 Pro 512GB", "url": "https://iphonekaitori.tokyo/purchase/iPhone-16-Pro-512GB-desert", "id": "rank_n", "retail_price": 204800},
    {"name": "16 Pro 1TB", "url": "https://iphonekaitori.tokyo/purchase/iPhone-16-Pro-1TB-desert", "id": "rank_n", "retail_price": 234800},
    {"name": "16 Pro Max 256GB", "url": "https://iphonekaitori.tokyo/purchase/iPhone-16-Pro-Max-256GB-desert", "id": "rank_n", "retail_price": 189800},
    {"name": "16 Pro Max 512GB", "url": "https://iphonekaitori.tokyo/purchase/iPhone-16-Pro-Max-512GB-desert", "id": "rank_n", "retail_price": 219800},
    {"name": "16 Pro Max 1TB", "url": "https://iphonekaitori.tokyo/purchase/iPhone-16-Pro-Max-1TB-desert", "id": "rank_n", "retail_price": 249800}
]

# 買取ルデヤ-iPhoneの商品情報
rudeya_iphone_products = [
    {"name": "16 Pro 128GB", "url": "https://kaitori-rudeya.com/product/item/4877", "class": "price", "retail_price": 159800},
    {"name": "16 Pro 256GB", "url": "https://kaitori-rudeya.com/product/item/4883", "class": "price", "retail_price": 174800},
    {"name": "16 Pro 512GB", "url": "https://kaitori-rudeya.com/product/item/4888", "class": "price", "retail_price": 204800},
    {"name": "16 Pro 1TB", "url": "https://kaitori-rudeya.com/product/item/4894", "class": "price", "retail_price": 234800},
    {"name": "16 Pro Max 256GB", "url": "https://kaitori-rudeya.com/product/item/4862", "class": "price", "retail_price": 189800},
    {"name": "16 Pro Max 512GB", "url": "https://kaitori-rudeya.com/product/item/4867", "class": "price", "retail_price": 219800},
    {"name": "16 Pro Max 1TB", "url": "https://kaitori-rudeya.com/product/item/4873", "class": "price", "retail_price": 249800}
]

# 買取ルデヤ-カメラの商品情報
rudeya_camera_products = [
    {"name": "SX740 HS [ブラック]", "url": "https://kaitori-rudeya.com/product/item/3512", "class": "price", "retail_price": 66000},
    {"name": "SX740 HS [シルバー]", "url": "https://kaitori-rudeya.com/product/item/3513", "class": "price", "retail_price": 66000},
    {"name": "IXY650 [ブラック]", "url": "https://kaitori-rudeya.com/product/item/3624", "class": "price", "retail_price": 42900},
    {"name": "IXY650 [シルバー]", "url": "https://kaitori-rudeya.com/product/item/3623", "class": "price", "retail_price": 42900}
]

# 買取ルデヤ-チェキの商品情報
rudeya_instax_products = [
    {"name": "写ルンです", "url": "https://kaitori-rudeya.com/product/item/4531", "class": "price", "retail_price": 1980},
    {"name": "instax mini JP1", "url": "https://kaitori-rudeya.com/product/item/3598", "class": "price", "retail_price": 814},
    {"name": "instax mini JP2", "url": "https://kaitori-rudeya.com/product/item/3597", "class": "price", "retail_price": 1510}
]

#TOMIYA富屋-チェキの商品情報
tomiya_instax_products = [
    {"name": "写ルンです", "url": "https://www.jptomiya.com/web/#/", "xpath": "/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-scroll-view/div/div/div/uni-view/uni-view[1]/uni-view[3]/uni-view[2]/uni-view[2]/uni-view[1]/uni-view[1]/uni-view[3]/uni-view[2]/uni-view[2]/uni-view[1]/span/span/uni-view/uni-view/uni-view[2]/uni-text[2]/span", "retail_price": 1980},
    {"name": "instax mini JP1", "url": "https://www.jptomiya.com/web/#/", "xpath": "/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-scroll-view/div/div/div/uni-view/uni-view[1]/uni-view[3]/uni-view[2]/uni-view[2]/uni-view[1]/uni-view[1]/uni-view[2]/uni-view[2]/uni-view[2]/uni-view[1]/span/span/uni-view/uni-view/uni-view[2]/uni-text[2]/span", "retail_price": 814},
    {"name": "instax mini JP2", "url": "https://www.jptomiya.com/web/#/", "xpath": "/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-scroll-view/div/div/div/uni-view/uni-view[1]/uni-view[3]/uni-view[2]/uni-view[2]/uni-view[1]/uni-view[1]/uni-view[1]/uni-view[2]/uni-view[2]/uni-view[1]/span/span/uni-view/uni-view/uni-view[2]/uni-text[2]/span", "retail_price": 1510}
]

# 森森買取の商品情報
morimori_products = [
    {"name": "16 Pro 128GB", "url": "https://www.morimori-kaitori.jp/product/268465", "id": "price-target", "retail_price": 159800},
    {"name": "16 Pro 256GB", "url": "https://www.morimori-kaitori.jp/product/270422", "id": "price-target", "retail_price": 174800},
    {"name": "16 Pro 512GB", "url": "https://www.morimori-kaitori.jp/product/270426", "id": "price-target", "retail_price": 204800},
    {"name": "16 Pro 1TB", "url": "https://www.morimori-kaitori.jp/product/270431", "id": "price-target", "retail_price": 234800},
    {"name": "16 Pro Max 256GB", "url": "https://www.morimori-kaitori.jp/product/268453", "id": "price-target", "retail_price": 189800},
    {"name": "16 Pro Max 512GB", "url": "https://www.morimori-kaitori.jp/product/268457", "id": "price-target", "retail_price": 219800},
    {"name": "16 Pro Max 1TB", "url": "https://www.morimori-kaitori.jp/product/268461", "id": "price-target", "retail_price": 249800}
]


# URL
URL_KAITORI_ICHOME = "https://www.1-chome.com/keitai"
URL_MOBILE_MIX = "https://mobile-mix.jp/?category=7"

# DiscordのウェブフックURLを設定
# 冒険者ギルド：iphone
#DISCORD_WEBHOOK_URL1 = 'https://discord.com/api/webhooks/1325079173399842889/hHIUsQ0WuOmboet6aq9-4q9gyTPxzKzKcH6V1F6qmKJad1-wIZJDwgVwFuAhy4jxSqNu'
DISCORD_WEBHOOK_URL1 = 'https://discord.com/api/webhooks/1163480358612901999/nFGZynR9-97R_XncfZw54VDrcZbA-S1YgrSc6mAYX-MgKEaQ9YZ_IeVTeALbu4ihmnyR'

# ちんおちんちん：iphone
#DISCORD_WEBHOOK_URL2 = 'https://discord.com/api/webhooks/1297388299912085606/RcfnqtqUjXbC46Lb_5uY-IPuqIVfkuJ44bzm09wgTQOUAI0Yg5C0cU5BsjeCb22o4m9p'
DISCORD_WEBHOOK_URL2 = 'https://discord.com/api/webhooks/1163480358612901999/nFGZynR9-97R_XncfZw54VDrcZbA-S1YgrSc6mAYX-MgKEaQ9YZ_IeVTeALbu4ihmnyR'

# 冒険者ギルド：カメラ
#DISCORD_WEBHOOK_URL3 = 'https://discord.com/api/webhooks/1325079403243503616/a4F7IqxqHcw_ZfnFLLyiz4N49Lky-gWxsbG7tmjIze1_UfoY7ssm2jShSlwakFylutK2'
DISCORD_WEBHOOK_URL3 = 'https://discord.com/api/webhooks/1325092803109458051/KbF85tUoBTPtYyZC8ARg0W7JHTQsnHBWyVofGF24GStd_5fYJQQcYaAtb4Kz7p-3uqN6'

# 冒険者ギルド：iphoneのDiscordに通知を送信する関数
def send_discord_notify1(message):
    url = DISCORD_WEBHOOK_URL1
    headers = {"Content-Type": "application/json"}
    payload = {"content": message}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logging.info('通知が送信されました')
    else:
        logging.error('通知の送信に失敗しました')

# ちんおちんちん：iphoneのDiscordに通知を送信する関数
def send_discord_notify2(message):
    url = DISCORD_WEBHOOK_URL2
    headers = {"Content-Type": "application/json"}
    payload = {"content": message}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logging.info('通知が送信されました')
    else:
        logging.error('通知の送信に失敗しました')

# 冒険者ギルド：カメラのDiscordに通知を送信する関数
def send_discord_notify3(message):
    url = DISCORD_WEBHOOK_URL3
    headers = {"Content-Type": "application/json"}
    payload = {"content": message}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logging.info('通知が送信されました')
    else:
        logging.error('通知の送信に失敗しました')

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1920x1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36")

# WebDriverのパスを指定
service = Service('C:/webdriver/chromedriver.exe')  # Replace with your path to chromedriver

csv_file_path = 'buyback_prices.csv'

# CSVファイルが存在しない場合、作成してヘッダーを設定
if not os.path.exists(csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(["time", "product", "site", "price", "change", "profit"])

def check_price(driver, url, products, site_name, csv_file_path):
    logging.info(f"Checking prices from URL: {url}")

    try:
        driver.get(url)
        time.sleep(5)  # ページが完全にロードされるのを待つ

        prices = []
        profits = []
        changes = False

        for product in products:
            product_name = product["name"]
            product_id = product["id"]
            retail_price = product["retail_price"]

            try:
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, product_id)))  # タイムアウト時間を40秒に延長
                price_element = driver.find_element(By.ID, product_id)

                if site_name == "買取一丁目":
                    current_price = int(price_element.get_attribute("data-price").replace(',', ''))  # カンマを削除して数値に変換
                elif site_name == "モバイルミックス":
                    current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
                    current_price = int(current_price_text)

                logging.info(f"Current Price for {product_name} on {site_name}: {current_price}")

                # 現在の買取価格をCSVファイルから読み込む
                last_price = None
                with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    rows = list(reader)
                    for row in rows:
                        if row[1] == product_name and row[2] == site_name:
                            last_price = int(row[3])

                # 変化率と利益を計算
                change = current_price - last_price if last_price else 0
                profit = current_price - retail_price
                profit1 = int((retail_price / 100) + profit)
                profit2 = int((retail_price / 50) + profit)

                logging.info(f"Price Change for {product_name} on {site_name}: {change}, Profit: {profit}")

                # 価格に変動があったかチェック
                if last_price is None or current_price != last_price:
                    changes = True

                # リストに保存
                change_str = f'+{change}円' if change > 0 else f'-{abs(change)}円' if change < 0 else '±0'
                prices.append(f'{product_name}: {current_price}円 ({change_str}){"🔥" if change > 0 else "💧" if change < 0 else ""}')
                profit_str = f'+{profit}円' if profit > 0 else f'-{abs(profit)}円' if profit < 0 else '0円'
                profit1_str = f'1%: +{profit1}円' if profit1 > 0 else f'1%: -{abs(profit1)}円' if profit1 < 0 else '1%: 0円'
                profits.append(f'{product_name}: {profit_str} ({profit1_str})')

                # CSVファイルに新しい買取価格を保存
                with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), product_name, site_name, current_price, change, profit])

            except Exception as e:
                logging.error(f"エラーが発生しました（{product_name} on {site_name}）: {e}")

        # 価格変動があった場合のみ通知を送信
        if changes:
            kaitoriya_icon = f'1️⃣' if site_name == '買取一丁目' else '📱'
            URL_NOFICE = f'{URL_KAITORI_ICHOME}' if site_name == '買取一丁目' else URL_MOBILE_MIX
            message = (
                f'{kaitoriya_icon} [{site_name}](<{URL_NOFICE}>)\n' +
                '\n'.join(prices) + '\n\n' +
                '～定価との差額～\n' +
                '\n'.join(profits) + '\n\n' +
                '￣￣￣￣￣'
            )
            send_discord_notify1(message)
            send_discord_notify2(message)

    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")

def check_rudeya_iphone_prices(driver, products, csv_file_path):
    prices = []
    profits = []
    changes = False

    for product in products:
        product_name = product["name"]
        product_url = product["url"]
        product_class = product["class"]
        retail_price = product["retail_price"]

        logging.info(f"Checking price from URL: {product_url}")

        try:
            driver.get(product_url)
            time.sleep(5)  # ページが完全にロードされるのを待つ

            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, product_class)))  # タイムアウト時間を40秒に延長
            price_element = driver.find_element(By.CLASS_NAME, product_class)
            current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
            current_price = int(current_price_text)

            logging.info(f"Current Price for {product_name} on 買取ルデヤ: {current_price}")

            # 現在の買取価格をCSVファイルから読み込む
            last_price = None
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = list(reader)
                for row in rows:
                    if row[1] == product_name and row[2] == "買取ルデヤ":
                        last_price = int(row[3])

            # 変化率と利益を計算
            change = current_price - last_price if last_price else 0
            profit = current_price - retail_price
            profit1 = int((retail_price / 100) + profit)
            profit2 = int((retail_price / 50) + profit)

            logging.info(f"Price Change for {product_name} on 買取ルデヤ: {change}, Profit: {profit}")

            # 価格に変動があったかチェック
            if last_price is None or current_price != last_price:
                changes = True

            # リストに保存
            change_str = f'+{change}円' if change > 0 else f'-{abs(change)}円' if change < 0 else '±0'
            prices.append(f'{product_name}: {current_price}円 ({change_str}){"🔥" if change > 0 else "💧" if change < 0 else ""}')
            profit_str = f'+{profit}円' if profit > 0 else f'-{abs(profit)}円' if profit < 0 else '0円'
            profit1_str = f'1%: +{profit1}円' if profit1 > 0 else f'1%: -{abs(profit1)}円' if profit1 < 0 else '1%: 0円'
            profits.append(f'{product_name}: {profit_str} ({profit1_str})')

            # CSVファイルに新しい買取価格を保存
            with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), product_name, "買取ルデヤ", current_price, change, profit])

        except Exception as e:
            logging.error(f"エラーが発生しました（{product_name} on 買取ルデヤ）: {e}")

    # 価格変動があった場合のみ通知を送信
    if changes:
        message = (
            '🥸 [買取ルデヤ](<https://kaitori-rudeya.com/search/index/iPhone%2016/-/-/->)\n' +
            '\n'.join(prices) + '\n\n' +
            '～定価との差額～\n' +
            '\n'.join(profits) + '\n\n' +
            '￣￣￣￣￣'
        )
        send_discord_notify1(message)
        send_discord_notify2(message)

def check_rudeya_camera_prices(driver, products, csv_file_path):
    prices = []
    profits = []
    changes = False

    for product in products:
        product_name = product["name"]
        product_url = product["url"]
        product_class = product["class"]
        retail_price = product["retail_price"]

        logging.info(f"Checking price from URL: {product_url}")

        try:
            driver.get(product_url)
            time.sleep(5)  # ページが完全にロードされるのを待つ

            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, product_class)))  # タイムアウト時間を40秒に延長
            price_element = driver.find_element(By.CLASS_NAME, product_class)
            current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
            current_price = int(current_price_text)

            logging.info(f"Current Price for {product_name} on 買取ルデヤ: {current_price}")

            # 現在の買取価格をCSVファイルから読み込む
            last_price = None
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = list(reader)
                for row in rows:
                    if row[1] == product_name and row[2] == "買取ルデヤ":
                        last_price = int(row[3])

            # 変化率と利益を計算
            change = current_price - last_price if last_price else 0
            profit = current_price - retail_price
            profit1 = int((retail_price / 100) + profit)
            profit2 = int((retail_price / 50) + profit)

            logging.info(f"Price Change for {product_name} on 買取ルデヤ: {change}, Profit: {profit}")

            # 価格に変動があったかチェック
            if last_price is None or current_price != last_price:
                changes = True

            # リストに保存
            change_str = f'+{change}円' if change > 0 else f'-{abs(change)}円' if change < 0 else '±0'
            prices.append(f'{product_name}: {current_price}円 ({change_str}){"🔥" if change > 0 else "💧" if change < 0 else ""}')
            profit_str = f'+{profit}円' if profit > 0 else f'-{abs(profit)}円' if profit < 0 else '0円'
            profit1_str = f'1%: +{profit1}円' if profit1 > 0 else f'1%: -{abs(profit1)}円' if profit1 < 0 else '1%: 0円'
            profits.append(f'{product_name}: {profit_str} ({profit1_str})')

            # CSVファイルに新しい買取価格を保存
            with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), product_name, "買取ルデヤ", current_price, change, profit])

        except Exception as e:
            logging.error(f"エラーが発生しました（{product_name} on 買取ルデヤ）: {e}")

    # 価格変動があった場合のみ通知を送信
    if changes:
        message = (
            '🥸 [買取ルデヤ](<https://kaitori-rudeya.com/search/index/canon/-/-/11>)\n' +
            '\n'.join(prices) + '\n\n' +
            '～定価との差額～\n' +
            '\n'.join(profits) + '\n\n' +
            '￣￣￣￣￣'
        )
        send_discord_notify3(message)

def check_rudeya_instax_prices(driver, products, csv_file_path):
    prices = []
    profits = []
    changes = False

    for product in products:
        product_name = product["name"]
        product_url = product["url"]
        product_class = product["class"]
        retail_price = product["retail_price"]

        logging.info(f"Checking price from URL: {product_url}")

        try:
            driver.get(product_url)
            time.sleep(5)  # ページが完全にロードされるのを待つ

            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, product_class)))  # タイムアウト時間を40秒に延長
            price_element = driver.find_element(By.CLASS_NAME, product_class)
            current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
            current_price = int(current_price_text)

            logging.info(f"Current Price for {product_name} on 買取ルデヤ: {current_price}")

            # 現在の買取価格をCSVファイルから読み込む
            last_price = None
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = list(reader)
                for row in rows:
                    if row[1] == product_name and row[2] == "買取ルデヤ":
                        last_price = int(row[3])

            # 変化率と利益を計算
            change = current_price - last_price if last_price else 0
            profit = current_price - retail_price
            profit1 = int((retail_price / 100) + profit)
            profit2 = int((retail_price / 50) + profit)

            logging.info(f"Price Change for {product_name} on 買取ルデヤ: {change}, Profit: {profit}")

            # 価格に変動があったかチェック
            if last_price is None or current_price != last_price:
                changes = True

            # リストに保存
            change_str = f'+{change}円' if change > 0 else f'-{abs(change)}円' if change < 0 else '±0'
            prices.append(f'{product_name}: {current_price}円 ({change_str}){"🔥" if change > 0 else "💧" if change < 0 else ""}')
            profit_str = f'+{profit}円' if profit > 0 else f'-{abs(profit)}円' if profit < 0 else '0円'
            profit1_str = f'1%: +{profit1}円' if profit1 > 0 else f'1%: -{abs(profit1)}円' if profit1 < 0 else '1%: 0円'
            profits.append(f'{product_name}: {profit_str} ({profit1_str})')

            # CSVファイルに新しい買取価格を保存
            with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), product_name, "買取ルデヤ", current_price, change, profit])

        except Exception as e:
            logging.error(f"エラーが発生しました（{product_name} on 買取ルデヤ）: {e}")

    # 価格変動があった場合のみ通知を送信
    if changes:
        message = (
            '🥸 [買取ルデヤ](<https://kaitori-rudeya.com/search/index/FUJIFILM%E3%80%80%E6%9E%9A/-/-/->)\n' +
            '\n'.join(prices) + '\n\n' +
            '～定価との差額～\n' +
            '\n'.join(profits) + '\n\n' +
            '￣￣￣￣￣'
        )
        send_discord_notify3(message)



def check_tomiya_instax_prices(driver, products, csv_file_path):
    prices = []
    profits = []
    changes = False

    for product in products:
        product_name = product["name"]
        product_url = product["url"]
        product_xpath = product["xpath"]
        retail_price = product["retail_price"]

        logging.info(f"Checking price from URL: {product_url}")

        try:
            driver.get(product_url)
            time.sleep(5)  # ページが完全にロードされるのを待つ

            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, product_xpath)))  # タイムアウト時間を40秒に延長
            price_element = driver.find_element(By.XPATH, product_xpath)
            current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
            current_price = int(current_price_text)

            logging.info(f"Current Price for {product_name} on TOMIYA富屋: {current_price}")

            # 現在の買取価格をCSVファイルから読み込む
            last_price = None
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = list(reader)
                for row in rows:
                    if row[1] == product_name and row[2] == "TOMIYA富屋":
                        last_price = int(row[3])

            # 変化率と利益を計算
            change = current_price - last_price if last_price else 0
            profit = current_price - retail_price
            profit1 = int((retail_price / 100) + profit)
            profit2 = int((retail_price / 50) + profit)

            logging.info(f"Price Change for {product_name} on TOMIYA富屋: {change}, Profit: {profit}")

            # 価格に変動があったかチェック
            if last_price is None or current_price != last_price:
                changes = True

            # リストに保存
            change_str = f'+{change}円' if change > 0 else f'-{abs(change)}円' if change < 0 else '±0'
            prices.append(f'**{product_name}**: {current_price}円 ({change_str}){"🔥" if change > 0 else "💧" if change < 0 else ""}')
            profit_str = f'+{profit}円' if profit > 0 else f'-{abs(profit)}円' if profit < 0 else '0円'
            profit1_str = f'1%: +{profit1}円' if profit1 > 0 else f'1%: -{abs(profit1)}円' if profit1 < 0 else '1%: 0円'
            profits.append(f'**{product_name}**: {profit_str} ({profit1_str})')

            # CSVファイルに新しい買取価格を保存
            with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), product_name, "TOMIYA富屋", current_price, change, profit])

        except Exception as e:
            logging.error(f"エラーが発生しました（{product_name} on TOMIYA富屋）: {e}")

    # 価格変動があった場合のみ通知を送信
    if changes:
        message = (
            '🗻 [TOMIYA富屋](<https://www.jptomiya.com/web/#/>)\n' +
            '\n'.join(prices) + '\n\n' +
            '～定価との差額～\n' +
            '\n'.join(profits) + '\n\n' +
            '￣￣￣￣￣'
        )
        send_discord_notify3(message)


def check_morimori_prices(driver, products, csv_file_path):
    prices = []
    profits = []
    changes = False

    for product in products:
        product_name = product["name"]
        product_url = product["url"]
        product_id = product["id"]
        retail_price = product["retail_price"]

        logging.info(f"Checking price from URL: {product_url}")

        try:
            driver.get(product_url)
            time.sleep(5)  # ページが完全にロードされるのを待つ

            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, product_id)))  # タイムアウト時間を40秒に延長
            price_element = driver.find_element(By.ID, product_id)
            current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
            current_price = int(current_price_text)

            logging.info(f"Current Price for {product_name} on 森森買取: {current_price}")

            # 現在の買取価格をCSVファイルから読み込む
            last_price = None
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = list(reader)
                for row in rows:
                    if row[1] == product_name and row[2] == "森森買取":
                        last_price = int(row[3])

            # 変化率と利益を計算
            change = current_price - last_price if last_price else 0
            profit = current_price - retail_price
            profit1 = int((retail_price / 100) + profit)
            profit2 = int((retail_price / 50) + profit)

            logging.info(f"Price Change for {product_name} on 森森買取: {change}, Profit: {profit}")

            # 価格に変動があったかチェック
            if last_price is None or current_price != last_price:
                changes = True

            # リストに保存
            change_str = f'+{change}円' if change > 0 else f'-{abs(change)}円' if change < 0 else '±0'
            prices.append(f'{product_name}: {current_price}円 ({change_str}){"🔥" if change > 0 else "💧" if change < 0 else ""}')
            profit_str = f'+{profit}円' if profit > 0 else f'-{abs(profit)}円' if profit < 0 else '0円'
            profit1_str = f'1%: +{profit1}円' if profit1 > 0 else f'1%: -{abs(profit1)}円' if profit1 < 0 else '1%: 0円'
            profits.append(f'{product_name}: {profit_str} ({profit1_str})')

            # CSVファイルに新しい買取価格を保存
            with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), product_name, "森森買取", current_price, change, profit])

        except Exception as e:
            logging.error(f"エラーが発生しました（{product_name} on 森森買取）: {e}")

    # 価格変動があった場合のみ通知を送信
    if changes:
        message = (
            '🌳 [森森買取](<https://www.morimori-kaitori.jp/search/iphone%2016%20pro?sk=iphone+16+pro>)\n' +
            '\n'.join(prices) + '\n\n' +
            '～定価との差額～\n' +
            '\n'.join(profits) + '\n\n' +
            '￣￣￣￣￣'
        )
        send_discord_notify1(message)
        send_discord_notify2(message)

def check_wiki_prices(driver, products, csv_file_path):
    prices = []
    profits = []
    changes = False

    for product in products:
        product_name = product["name"]
        product_url = product["url"]
        product_id = product["id"]
        retail_price = product["retail_price"]

        logging.info(f"Checking price from URL: {product_url}")

        try:
            driver.get(product_url)
            time.sleep(5)  # ページが完全にロードされるのを待つ

            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, product_id)))  # タイムアウト時間を40秒に延長
            price_element = driver.find_element(By.ID, product_id)
            current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
            current_price = int(current_price_text)

            logging.info(f"Current Price for {product_name} on 買取Wiki: {current_price}")

            # 現在の買取価格をCSVファイルから読み込む
            last_price = None
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = list(reader)
                for row in rows:
                    if row[1] == product_name and row[2] == "買取Wiki":
                        last_price = int(row[3])

            # 変化率と利益を計算
            change = current_price - last_price if last_price else 0
            profit = current_price - retail_price
            profit1 = int((retail_price / 100) + profit)
            profit2 = int((retail_price / 50) + profit)

            logging.info(f"Price Change for {product_name} on 買取Wiki: {change}, Profit: {profit}")

            # 価格に変動があったかチェック
            if last_price is None or current_price != last_price:
                changes = True

            # リストに保存
            change_str = f'+{change}円' if change > 0 else f'-{abs(change)}円' if change < 0 else '±0'
            prices.append(f'{product_name}: {current_price}円 ({change_str}){"🔥" if change > 0 else "💧" if change < 0 else ""}')
            profit_str = f'+{profit}円' if profit > 0 else f'-{abs(profit)}円' if profit < 0 else '0円'
            profit1_str = f'1%: +{profit1}円' if profit1 > 0 else f'1%: -{abs(profit1)}円' if profit1 < 0 else '1%: 0円'
            profits.append(f'{product_name}: {profit_str} ({profit1_str})')

            # CSVファイルに新しい買取価格を保存
            with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), product_name, "買取Wiki", current_price, change, profit])

        except Exception as e:
            logging.error(f"エラーが発生しました（{product_name} on 買取Wiki）: {e}")

    # 価格変動があった場合のみ通知を送信
    if changes:
        message = (
            '📚 [買取Wiki](<https://iphonekaitori.tokyo/search?type=&q=iPhone+16+pro#searchtop>)\n' +
            '\n'.join(prices) + '\n\n' +
            '～定価との差額～\n' +
            '\n'.join(profits) + '\n\n' +
            '￣￣￣￣￣'
        )
        send_discord_notify1(message)
        send_discord_notify2(message)


# メイン関数
def main():
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 30秒ごとに無限にチェックを繰り返す
    while True:
        check_tomiya_instax_prices(driver, tomiya_instax_products, csv_file_path)
        check_price(driver, URL_KAITORI_ICHOME, products, "買取一丁目", csv_file_path)
        check_price(driver, URL_MOBILE_MIX, mobile_mix_products, "モバイルミックス", csv_file_path)
        check_rudeya_iphone_prices(driver, rudeya_iphone_products, csv_file_path)
        check_rudeya_camera_prices(driver, rudeya_camera_products, csv_file_path)
        check_rudeya_instax_prices(driver, rudeya_instax_products, csv_file_path)
        check_morimori_prices(driver, morimori_products, csv_file_path)
        check_wiki_prices(driver, wiki_products, csv_file_path)
        logging.info("30秒後に再チェックします...")
        time.sleep(30)

if __name__ == "__main__":
    main()









