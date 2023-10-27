from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import pandas as pd

chrome_options = Options()
browser = webdriver.Chrome(options=chrome_options)

base_url = "https://api.openloot.com/v2/market/listings/BT0_Hourglass_Common/items?onSale=true&page={page_num}&pageSize=48&sort=price%3Aasc"
page_num = 1

all_results = []

while True:
    try:
        # 使用 Web Driver 获取网页内容
        browser.get(base_url.format(page_num=page_num))

        # 获取页面的源代码，这是JSON格式的数据
        page_source = browser.page_source

        # 由于返回的页面源代码会包含一些额外的HTML标签，我们只需要页面中的JSON内容
        start_index = page_source.find('{')
        end_index = page_source.rfind('}') + 1
        json_data = page_source[start_index:end_index]

        # 使用json库解析JSON数据
        data = json.loads(json_data)

        # 如果没有items，则跳出循环
        if not data['items']:
            break

        # 提取需要的数据
        for item in data['items']:
            issued_id = item['item']['issuedId']
            price = item['price']
            time_remaining = None
            price_per_time = None
            if item['item']['extra'] and "attributes" in item['item']['extra']:
                time_remaining = next((attr['value'] for attr in item['item']['extra']['attributes'] if attr['name'] == "TimeRemaining"), None)
                if time_remaining:
                    try:
                        time_remaining = float(time_remaining)
                        if time_remaining != 0:  # Avoid division by zero
                            price_per_time = (price / time_remaining) * 60
                    except ValueError:
                        pass
            all_results.append({'issuedId': issued_id, 'price': price, 'TimeRemaining': time_remaining, 'PricePerTime': price_per_time})

        page_num += 1

    except json.JSONDecodeError:
        # 如果出现JSON解码错误，跳出循环
        break

# 将数据按PricePerTime进行排序
sorted_results = sorted(all_results, key=lambda x: x['PricePerTime'] if x['PricePerTime'] is not None else float('inf'))

# 使用pandas将数据保存到Excel文件
df = pd.DataFrame(sorted_results)
df.to_excel('output_data_sorted.xlsx', index=False)

# 关闭浏览器
browser.quit()
