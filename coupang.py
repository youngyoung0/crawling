from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import undetected_chromedriver as uc
from selenium_stealth import stealth

options = uc.ChromeOptions()
options.add_argument('--disable-popup-blocking')

# WebDriver 객체 생성
driver = uc.Chrome( options = options,enable_cdp_events=True,incognito=True)

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

for i in range(1,3):
    # Coupang 검색 결과 페이지로 이동
    url = f"https://www.coupang.com/np/search?component=&q=%EC%98%81%EC%96%91%EC%A0%9C&channel=user&page={page_number}"
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
        product_image = element.find("img", class_="search-product-wrap-img").text.strip()
        product_detail_link = element.find("a", class_="search-product-link")
        rating_element = element.find("em", class_="rating")
        rating = rating_element.text.strip() if rating_element else ""
        rating_total_count_element = element.find("span", class_="rating-total-count")
        rating_total_count = rating_total_count_element.text.strip() if rating_total_count_element else ""

        product_data.append({
            "product_name": product_name,
            "price": price,
            "product_image": product_image,
            "product_detail_link": product_detail_link,
            "rating": rating,
            "rating-total-count": rating_total_count
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
df.to_excel("coupang_products.xlsx", index=False)

# 웹 드라이버 종료
driver.quit()
