import requests
from bs4 import BeautifulSoup
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pprint

BASE_URL = "https://shadowverse.gg/cards"


def parse_card_from_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    card_info = {}
    container = soup.find('div', id='rootOfProContentshadowverse')
    if not container:
        return None
    name_tag = container.find('h2')
    if name_tag:
        card_info['카드 이름'] = name_tag.text.split(' - ')[0].strip()
    description_label = container.find('div', string='Description')
    if description_label:
        value_div = description_label.find_next_sibling('div')
        if value_div:
            card_info['카드 능력 서술문구'] = value_div.text.strip()
    stats_section = container.find('section')
    if stats_section:
        # 찾고 싶은 정보의 라벨 리스트를 미리 정의합니다.
        labels_to_find = {
            'Set': '카드팩',
            'Type': '카드 타입',
            'Cost': '카드 코스트',
            'Attack': '카드 공격력',
            'Life': '카드 방어력',
            'Class': '카드 클래스',
            'Rarity': '카드 희귀도',
            'Tribes': '카드 종족 타입'
        }

        for label_text, info_key in labels_to_find.items():
            # 라벨 텍스트를 가진 div를 직접 찾습니다.
            label_div = stats_section.find('div', string=label_text)

            if label_div:
                # 라벨 div 바로 다음에 오는 형제(sibling) div에서 값을 가져옵니다.
                value_div = label_div.find_next_sibling('div')
                if value_div:
                    card_info[info_key] = value_div.text.strip()
    return card_info


def generate_card_prefixes():
    """ID의 앞 6자리(카드 카테고리) 조합을 생성합니다."""
    expansions = ['102']
    classes = ['0', '1', '2', '3', '4', '5', '6', '7']
    rarities = ['1', '2', '3', '4']
    card_types = ['1', '2', '3']

    prefixes = []
    for exp in expansions:
        for cls in classes:
            for rar in rarities:
                if exp == '100' and rar in ['3', '4']:
                    continue
                for typ in card_types:
                    prefixes.append(f"{exp}{cls}{rar}{typ}")
    return prefixes


def main():
    """ID 생성 및 순차적 크롤링을 실행합니다. (속도 개선 적용)"""
    print("Generating card prefixes based on rules...")
    card_prefixes = generate_card_prefixes()
    total_categories = len(card_prefixes)
    print(f"Generated {total_categories} categories to check.")

    card_database = {}

    # --- 1. Selenium WebDriver 옵션 최적화 ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 이미지 로딩 비활성화
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    try:
        for i, prefix in enumerate(card_prefixes):
            print(f"\n--- Checking Category {i + 1}/{total_categories} (Prefix: {prefix}) ---")

            for u_id_multiplier in range(1, 10):
                unique_id = str(u_id_multiplier * 10)
                card_id = f"{prefix}{unique_id}"
                url = f"{BASE_URL}/{card_id}"

                print(f"Checking URL: {url}")

                html_source = None
                card_found = False
                try:
                    driver.get(url)
                    wait = WebDriverWait(driver, 5)
                    wait.until(
                        EC.presence_of_element_located((By.ID, "rootOfProContentshadowverse"))
                    )
                    html_source = driver.page_source
                    card_found = True

                except Exception as e:
                    print(f"  -> An unexpected error occurred: {e}")
                    break

                if card_found and html_source:
                    result = parse_card_from_html(html_source)
                    if result and result.get('카드 이름'):
                        card_name = result['카드 이름']
                        card_database[card_name] = result

                        print("  [SUCCESS] Card Info:") # 유니코드 문자 제거
                        print(f"      - 이름: {result.get('카드 이름', 'N/A')}")
                        print(
                            f"      - 코스트: {result.get('카드 코스트', 'N/A')}, 공격력: {result.get('카드 공격력', 'N/A')}, 방어력: {result.get('카드 방어력', 'N/A')}")
                        print(f"      - 능력: {result.get('카드 능력 서술문구', 'N/A')[:50]}...")
                    else:
                        print("  [FAIL] Found container, but failed to parse card info. Skipping rest of this category.") # 유니코드 문자 제거
                        break

                time.sleep(0.5)

            # 중간 저장 로직 (선택적)
            if i > 0 and i % 10 == 0:
                print(f"\n--- Saving progress ({len(card_database)} cards collected) ---")
                with open("102_card_database_generated_temp.json", "w", encoding="utf-8") as f:
                    json.dump(card_database, f, ensure_ascii=False, indent=4)

    finally:
        driver.quit()

    with open("102_card_database_raw.json", "w", encoding="utf-8") as f: # 인코딩 명시
        json.dump(card_database, f, ensure_ascii=False, indent=4)

    print("\nScraping complete!")
    print(f"Total {len(card_database)} cards saved to card_database_raw.json") # 파일명 수정


if __name__ == "__main__":
    main()
