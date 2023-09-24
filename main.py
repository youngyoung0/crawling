from bs4 import BeautifulSoup
from selenium import webdriver
import time

base_url = "https://www.coupang.com/np/search?component=&q="

keyword = input("검색어를 입력하세요 : ")

search_url = base_url + keyword

driver = webdriver.Chrome()

driver.get(search_url)

time.sleep(3)

for i in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

items = soup.select(".search-product-wrap")

for rank_num, item in enumerate(items, 1):
    print(f"<<{rank_num}>>")
    ad = item.select_one(".link_ad")
    if ad:
        print("광고입니다.")
        continue

    product_name = item.select_one(".name ").text
    print(f"{product_name}")

    product_price = item.select_one(".sale ").text
    print(f"{product_price}")

    product_unit_price = item.select_one(".unit-price")
    if product_unit_price:
        print(f"{product_unit_price}")
        continue

    print()

driver.quit()
