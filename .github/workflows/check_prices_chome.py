import os
import requests
import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pytz

# GASのウェブアプリのURL
gas_url = "https://script.google.com/macros/s/AKfycbxTBmByMUDxXD8I6bWnpbC74pCX8aZrR2_mh1YJOgjgbLwewK8t6BjfYCm9NinhH06MRA/exec"

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 日本時間（JST）を設定
JST = pytz.timezone('Asia/Tokyo')

# 商品情報
products = [
    {"name": "16 Pro 128GB", "id": "NewPrice_33821", "retail_price": 159800, 'xpath': '//*[@id="smartphone-view-table"]/div[1]/div/div/div[2]/label[3]/small'},
    {"name": "16 Pro 256GB", "id": "NewPrice_33831", "retail_price": 174800, 'xpath': '//*[@id="smartphone-view-table"]/div[3]/div/div/div[2]/label[3]/small'},
    {"name": "16 Pro 512GB", "id": "NewPrice_33841", "retail_price": 204800, 'xpath': '//*[@id="smartphone-view-table"]/div[5]/div/div/div[2]/label[3]/small'},
    {"name": "16 Pro 1TB", "id": "NewPrice_33851", "retail_price": 234800, 'xpath': '//*[@id="smartphone-view-table"]/div[7]/div/div/div[2]/label[3]/small'},
    {"name": "16 Pro Max 256GB", "id": "NewPrice_33781", "retail_price": 189800, 'xpath': '//*[@id="smartphone-view-table"]/div[9]/div/div/div[2]/label[3]/small'},
    {"name": "16 Pro Max 512GB", "id": "NewPrice_33791", "retail_price": 219800, 'xpath': '//*[@id="smartphone-view-table"]/div[11]/div/div/div[2]/label[3]/small'},
    {"name": "16 Pro Max 1TB", "id": "NewPrice_33801", "retail_price": 249800, 'xpath': '//*[@id="smartphone-view-table"]/div[13]/div/div/div[2]/label[3]/small'}
]

# モバイルミックスの商品情報
mobile_mix_products = [
    {"name": "16 Pro 128GB", "id": "model444", "retail_price": 159800, "xpath": "/html/body/table/tbody/tr[8]/td[2]"},
    {"name": "16 Pro 256GB", "id": "model445", "retail_price": 174800, "xpath": "/html/body/table/tbody/tr[10]/td[2]"},
    {"name": "16 Pro 512GB", "id": "model446", "retail_price": 204800, "xpath": "/html/body/table/tbody/tr[12]/td[2]"},
    {"name": "16 Pro 1TB", "id": "model447", "retail_price": 234800, "xpath": "/html/body/table/tbody/tr[14]/td[2]"},
    {"name": "16 Pro Max 256GB", "id": "model441", "retail_price": 189800, "xpath": "/html/body/table/tbody/tr[2]/td[2]"},
    {"name": "16 Pro Max 512GB", "id": "model442", "retail_price": 219800, "xpath": "/html/body/table/tbody/tr[4]/td[2]"},
    {"name": "16 Pro Max 1TB", "id": "model443", "retail_price": 249800, "xpath": "/html/body/table/tbody/tr[6]/td[2]"}
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
URL_KAITORI_RUDEYA_IPHONE = "https://kaitori-rudeya.com/search/index/iPhone%2016/-/-/-"
URL_KAITORI_RUDEYA_CAMERA = "https://kaitori-rudeya.com/search/index/canon/-/-/11"
URL_KAITORI_RUDEYA_INSTAX = "https://kaitori-rudeya.com/search/index/FUJIFILM%E3%80%80%E6%9E%9A/-/-/-"
URL_MORIMORI_KAITORI = "https://www.morimori-kaitori.jp/search/iphone%2016%20pro?sk=iphone+16+pro"
URL_KAITORI_WIKI = "https://iphonekaitori.tokyo/search?type=&q=iPhone+16+pro#searchtop"
URL_TOMIYA = "https://www.jptomiya.com/web/#/"



# DiscordのウェブフックURLを設定
test_mode = "on"
if test_mode == "on":
    # 冒険者ギルド：iphone
    DISCORD_WEBHOOK_URL1 = 'https://discord.com/api/webhooks/1163480358612901999/nFGZynR9-97R_XncfZw54VDrcZbA-S1YgrSc6mAYX-MgKEaQ9YZ_IeVTeALbu4ihmnyR'
    # ちんおちんちん：iphone
    DISCORD_WEBHOOK_URL2 = 'https://discord.com/api/webhooks/1163480358612901999/nFGZynR9-97R_XncfZw54VDrcZbA-S1YgrSc6mAYX-MgKEaQ9YZ_IeVTeALbu4ihmnyR'
    # 冒険者ギルド：カメラ
    DISCORD_WEBHOOK_URL3 = 'https://discord.com/api/webhooks/1325092803109458051/KbF85tUoBTPtYyZC8ARg0W7JHTQsnHBWyVofGF24GStd_5fYJQQcYaAtb4Kz7p-3uqN6'
elif test_mode == "off":
    # 冒険者ギルド：iphone
    DISCORD_WEBHOOK_URL1 = 'https://discord.com/api/webhooks/1325079173399842889/hHIUsQ0WuOmboet6aq9-4q9gyTPxzKzKcH6V1F6qmKJad1-wIZJDwgVwFuAhy4jxSqNu'
    # ちんおちんちん：iphone
    DISCORD_WEBHOOK_URL2 = 'https://discord.com/api/webhooks/1297388299912085606/RcfnqtqUjXbC46Lb_5uY-IPuqIVfkuJ44bzm09wgTQOUAI0Yg5C0cU5BsjeCb22o4m9p'
    # 冒険者ギルド：カメラ
    DISCORD_WEBHOOK_URL3 = 'https://discord.com/api/webhooks/1325079403243503616/a4F7IqxqHcw_ZfnFLLyiz4N49Lky-gWxsbG7tmjIze1_UfoY7ssm2jShSlwakFylutK2'

# Discordの通知を送信する関数
def send_discord_notify(message, webhook_url):
    headers = {"Content-Type": "application/json"}
    payload = {"content": message}
    response = requests.post(webhook_url, headers=headers, json=payload)
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
service = Service(ChromeDriverManager().install())

# GAS経由でデータを取得
def get_data(site_name):
    try:
        response = requests.get(gas_url, params={'siteName': site_name})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("HTTPリクエストエラー:", e)
    except ValueError:
        logging.error("JSON解析エラー: レスポンスがJSON形式ではありません。レスポンス内容:", response.text)
    return []

# GAS経由でデータを書き込む
def send_data(data):
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(gas_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        logging.info("書き込みのレスポンス内容: " + response.text)  # 修正箇所
    except requests.exceptions.RequestException as e:
        logging.error("HTTPリクエストエラー:", e)


def check_price_group1(driver, url, products, site_name, item_category):
    logging.info(f"Checking prices from URL: {url}")
    data = get_data(site_name)
    latest_data = filter_data(data, site_name, products)

    try:
        driver.get(url)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "body"))) # ページのボディ要素が表示されるまで待機

        # 買取一丁目の場合、ボタンをクリックする
        if site_name == "買取一丁目":
            try:
                all_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "all-button"))
                )
                all_button.click()
                logging.info("All button clicked")
                time.sleep(5)  # ボタンのクリック後、ページが更新されるのを待つ
            except Exception as e:
                logging.error(f"Failed to click the all button: {e}")

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
                
                #色差別情報抽出
                additional_info_element = driver.find_element(By.XPATH, product["xpath"])
                additional_info = additional_info_element.text.strip() # 追加情報を取得

                logging.info(f"Current Price for {product_name} on {site_name}: {current_price}")
                logging.info(f"Additional Info for {product_name} on {site_name}: {additional_info}")

                # 現在の買取価格と色差別情報をGAS経由で取得したデータから読み込む
                last_price = None
                for row in latest_data:
                    if row[1] == product_name and row[2] == site_name:
                        last_price = int(row[3])

                # 変化率と利益を計算
                change = current_price - last_price if last_price else 0
                profit = current_price - retail_price
                profit1 = int((retail_price / 100 * 1) + profit)
                profit1a = int((retail_price / 100 * 1.5) + profit)
                profit2 = int((retail_price / 100 * 2) + profit)

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

                # データをGAS経由でスプレッドシートに保存
                data_to_send = {
                "time": datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S'),
                "product": product_name,
                "site": site_name,
                "price": current_price,
                "change": change,
                "profit": profit,
                "additional_info": additional_info,
                "profit1": profit1,
                "profit1a": profit1a,
                "profit2": profit2,
                "item_category": item_category
                }
                send_data(data_to_send)

            except Exception as e:
                logging.error(f"エラーが発生しました（{product_name} on {site_name}）: {e}")

        # 価格変動があった場合のみ通知を送信
        if changes:
            kaitoriya_icon = f'1️⃣' if site_name == '買取一丁目' else '📱'
            URL_NOFICE = f'{URL_KAITORI_ICHOME}' if site_name == '買取一丁目' else URL_MOBILE_MIX
            message = (
                f'{kaitoriya_icon} [{site_name}](<{URL_NOFICE}>)（[一覧表](<https://docs.google.com/spreadsheets/d/1TlN5EvH2-dd9EqxZdDMW4zuvuxbktOd_In_HcYA3RM0/edit?usp=sharing>)）\n' +
                '\n'.join(prices) + '\n\n' +
                '～定価との差額～\n' +
                '\n'.join(profits) + '\n\n' +
                '￣￣￣￣￣'
            )
            send_discord_notify(message, DISCORD_WEBHOOK_URL1)
            send_discord_notify(message, DISCORD_WEBHOOK_URL2)

    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")


def check_price_group2(driver,URL_NOFICE, products, site_name, item_category, check_pattern):
    data = get_data(site_name)
    latest_data = filter_data(data, site_name, products)
    prices = []
    profits = []
    changes = False

    for product in products:
        product_name = product["name"]
        product_url = product["url"]
        retail_price = product["retail_price"]
        if check_pattern == "class":
            product_class = product["class"]
        elif check_pattern == "id":
            product_id = product["id"]
        elif check_pattern == "xpath":
            product_xpath = product["xpath"]

        logging.info(f"Checking price from URL: {product_url}")

        try:
            driver.get(product_url)
            time.sleep(5)  # ページが完全にロードされるのを待つ
            if check_pattern == "class":
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, product_class)))  # タイムアウト時間を40秒に延長
                price_element = driver.find_element(By.CLASS_NAME, product_class)
            elif check_pattern == "id":
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, product_id)))  # タイムアウト時間を40秒に延長
                price_element = driver.find_element(By.ID, product_id)
            elif check_pattern == "xpath":
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, product_xpath)))  # タイムアウト時間を40秒に延長
                price_element = driver.find_element(By.XPATH, product_xpath)
            current_price_text = price_element.text.replace(',', '').replace('円', '').strip()
            current_price = int(current_price_text)

            logging.info(f"Current Price for {product_name} on {site_name}: {current_price}")

            # 現在の買取価格をGAS経由で取得したデータから読み込む
            last_price = None
            for row in latest_data:
                if row[1] == product_name and row[2] == site_name:
                    last_price = int(row[3])

            # 変化率と利益を計算
            change = current_price - last_price if last_price else 0
            profit = current_price - retail_price
            profit1 = int((retail_price / 100 * 1) + profit)
            profit1a = int((retail_price / 100 * 1.5) + profit)
            profit2 = int((retail_price / 100 * 2) + profit)

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

            # データをGAS経由でスプレッドシートに保存
            data_to_send = {
            "time": datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S'),
            "product": product_name,
            "site": site_name,
            "price": current_price,
            "change": change,
            "profit": profit,
            "additional_info": "",
            "profit1": profit1,
            "profit1a": profit1a,
            "profit2": profit2,
            "item_category": item_category
            }
            send_data(data_to_send)

        except Exception as e:
            logging.error(f"エラーが発生しました（{product_name} on {site_name}）: {e}")

    # 価格変動があった場合のみ通知を送信
    if changes:
        kaitoriya_icon = f'1️⃣' if site_name == '買取一丁目' else '📱' if site_name == 'モバイルミックス'  else '🥸' if site_name == '買取ルデヤ' else '🌳' if site_name == '森森買取' else '📚' if site_name == '買取Wiki' else '🗻'
        message = (
            f'{kaitoriya_icon} [{site_name}](<{URL_NOFICE}>)（[一覧表](<https://docs.google.com/spreadsheets/d/1TlN5EvH2-dd9EqxZdDMW4zuvuxbktOd_In_HcYA3RM0/edit?usp=sharing>)）\n' +
            '\n'.join(prices) + '\n\n' +
            '～定価との差額～\n' +
            '\n'.join(profits) + '\n\n' +
            '￣￣￣￣￣'
        )
        if item_category == "iphone":
            send_discord_notify(message, DISCORD_WEBHOOK_URL1)
            send_discord_notify(message, DISCORD_WEBHOOK_URL2)
        else:
            send_discord_notify(message, DISCORD_WEBHOOK_URL3)


def filter_data(data, site_name, products):
    filtered_data = []
    latest_data = {}

    for row in data:
        time, product, site, price, change, profit, *additional_info = row
        if site == site_name and product in [p['name'] for p in products]:
            time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')  # 修正箇所
            if product not in latest_data or time > latest_data[product]['time']:
                latest_data[product] = {
                    'time': time,
                    'product': product,
                    'site': site,
                    'price': price,
                    'change': change,
                    'profit': profit,
                    'additional_info': additional_info
                }

    for product in [p['name'] for p in products]:
        if product in latest_data:
            filtered_data.append([
                latest_data[product]['time'].strftime('%Y-%m-%d %H:%M:%S'),
                latest_data[product]['product'],
                latest_data[product]['site'],
                latest_data[product]['price'],
                latest_data[product]['change'],
                latest_data[product]['profit'],
                *latest_data[product]['additional_info']
            ])

    return filtered_data



# メイン関数
def main():
    driver = webdriver.Chrome(service=service, options=chrome_options)

    check_price_group1(driver, URL_KAITORI_ICHOME, products, "買取一丁目", "iphone")
    #check_price_group1(driver, URL_MOBILE_MIX, mobile_mix_products, "モバイルミックス", "iphone")
    #check_price_group2(driver, URL_KAITORI_RUDEYA_IPHONE, rudeya_iphone_products, "買取ルデヤ", "iphone", "class")
    #check_price_group2(driver, URL_KAITORI_RUDEYA_CAMERA, rudeya_camera_products, "買取ルデヤ", "camera", "class")
    #check_price_group2(driver, URL_KAITORI_RUDEYA_INSTAX, rudeya_instax_products, "買取ルデヤ", "camera", "class")
    #check_price_group2(driver, URL_MORIMORI_KAITORI, morimori_products, "森森買取", "iphone", "id")
    #check_price_group2(driver, URL_KAITORI_WIKI, wiki_products, "買取Wiki", "iphone", "id")
    #check_price_group2(driver, URL_TOMIYA, tomiya_instax_products, "TOMIYA富屋", "camera", "xpath")

if __name__ == "__main__":
    main()
