import os
import re
import requests
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium_stealth import stealth
from openpyxl import Workbook
from openpyxl.drawing.image import Image


options = uc.ChromeOptions()
options.add_argument('--disable-popup-blocking')

# 파일 이름에서 특수 문자 및 길이 제한을 제거하는 함수
def clean_filename(filename):
    return re.sub(r'[\/:*?"<>|]', '', filename)[:100]  # 최대 길이 100자로 제한


# 이미지 다운로드 함수 정의
def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    else:
        with open(save_path, 'wb') as file:
            file.write(response.content)

# 이미지를 저장할 디렉토리 생성
if not os.path.exists('images'):
    os.makedirs('images', exist_ok=True)

# WebDriver 객체 생성
driver = uc.Chrome( options = options,enable_cdp_events=True,incognito=True)

today_date = datetime.now().strftime("%Y%m%d")

stealth(driver,
        vendor="Google Inc. ",
        platform="Win32",
        webgl_vendor="intel Inc. ",
        renderer= "Intel Iris OpenGL Engine",
        fix_hairline=True,
        )


options.add_argument('--remote-debugging-port=9222')

# 드라이버 생성
driver = webdriver.Chrome(options=options)


# 결과를 저장할 리스트 초기화
all_product_data = []

# 시작 페이지 번호
page_number = 1

keyword = input("검색어를 입력하세요.")
# while True:
for i in range(1,3) :
    # Coupang 검색 결과 페이지로 이동
    url = f"https://www.coupang.com/np/search?component=&q={keyword}&channel=user&page={page_number}"
    driver.get(url)
    driver.implicitly_wait(5)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")

    # 페이지 소스 가져오기
    html = driver.page_source

    # BeautifulSoup을 사용하여 파싱
    soup = BeautifulSoup(html, "html.parser")

    # 상품 정보를 담을 리스트 초기화
    product_data = []

    # 상품 정보 요소 찾기
    product_elements = soup.find_all("li", class_="search-product")

    # 각 상품 정보를 리스트에 추가
    for element in product_elements:
        product_name = element.find("div", class_="name").text.strip()
        price = element.find("strong", class_="price-value").text.strip()
        product_detail_link = element.find("a", class_="search-product-link")["href"]
        base_price_element = element.find("del", class_="base-price")
        base_price = base_price_element.text.strip() if base_price_element else ""
        discount_rate_element = element.find("span", class_="instant-discount-rate")
        discount_rate = discount_rate_element.text.strip() if discount_rate_element else ""
        rating_element = element.find("em", class_="rating")
        rating = rating_element.text.strip() if rating_element else ""
        rating_total_count_element = element.find("span", class_="rating-total-count")
        rating_total_count = rating_total_count_element.text.strip() if rating_total_count_element else ""

        # 상품 이미지
        product_image_url = element.find("img", class_="search-product-wrap-img")["src"]
        product_image = f'images/{clean_filename(product_name)}.jpg'  # 이미지 파일명 생성
        print(product_image_url)
        download_image(f"https:{product_image_url}", product_image)  # 이미지 다운로드


        product_data.append({
            "상품이름": product_name,
            "할인가격": price,
            "상품 상세 페이지": f"https://www.coupang.com{product_detail_link}",
            "원가": base_price,
            "할인율": discount_rate,
            "상품 이미지": product_image,
            "후기 점수": rating,
            "후기 수": rating_total_count
        })

    # 현재 페이지의 데이터를 전체 데이터 리스트에 추가
    all_product_data.extend(product_data)

    # 다음 페이지로 이동하기 위해 페이지 번호 증가
    page_number += 1

    # 다음 페이지로 이동할 element 찾기 (새로운 URL 생성 방식으로 변경)
    next_page_link = f"https://www.coupang.com/np/search?component=&q=%EC%98%81%EC%96%91%EC%A0%9C&channel=user&page={page_number}"

    # 현재 URL과 다음 페이지 URL이 동일하면 반복 종료
    if url == next_page_link:
        break

# 데이터를 DataFrame으로 변환
df = pd.DataFrame(all_product_data)

# DataFrame을 엑셀 파일로 저장
with pd.ExcelWriter(f"coupang_products_{keyword}_{today_date}.xlsx", engine='openpyxl', mode='w') as writer:
    df.to_excel(writer, index=False)

# 웹 드라이버 종료
driver.quit()
