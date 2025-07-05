from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 이전과 동일한 함수들...
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
        info_rows = stats_section.find_all('div', recursive=False)
        for row in info_rows:
            parts = row.find_all('div', recursive=False)
            if len(parts) == 2:
                label = parts[0].text.strip()
                value = parts[1].text.strip()
                if label == 'Set':
                    card_info['카드팩'] = value
                elif label == 'Type':
                    card_info['카드 타입'] = value
                elif label == 'Cost':
                    card_info['카드 코스트'] = value
                elif label == 'Attack':
                    card_info['카드 공격력'] = value
                elif label == 'Life':
                    card_info['카드 방어력'] = value
                elif label == 'Class':
                    card_info['카드 클래스'] = value
                elif label == 'Rarity':
                    card_info['카드 희귀도'] = value
                elif label == 'Tribes':
                    card_info['카드 종족 타입'] = value
    return card_info


# --- [개선 1] URL 대신 ID 앞부분(접두사)을 생성하는 함수로 변경 ---
def generate_card_prefixes():
    """ID의 앞 6자리(카드 카테고리) 조합을 생성합니다."""
    expansions = ['100', '101', '900']
    classes = ['0', '1', '2', '3', '4', '5', '6', '7']
    rarities = ['1', '2', '3', '4']
    card_types = ['1', '2', '3']

    prefixes = []
    for exp in expansions:
        for cls in classes:
            for rar in rarities:
                for typ in card_types:
                    prefixes.append(f"{exp}{cls}{rar}{typ}")
    return prefixes


def main():
    """ID 생성 및 순차적 크롤링을 실행합니다."""
    print("Generating card prefixes based on rules...")
    card_prefixes = generate_card_prefixes()
    total_categories = len(card_prefixes)
    print(f"Generated {total_categories} categories to check.")

    card_database = {}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        # --- [개선 1] 루프 구조 변경 ---
        for i, prefix in enumerate(card_prefixes):
            print(f"\n--- Checking Category {i + 1}/{total_categories} (Prefix: {prefix}) ---")

            # 고유 ID는 10부터 90까지 순차적으로 확인
            for u_id_multiplier in range(1, 10):
                unique_id = str(u_id_multiplier * 10)
                card_id = f"{prefix}{unique_id}"
                url = f"{BASE_URL}/{card_id}"

                print(f"Checking URL: {url}")

                html_source = None
                card_found = False
                try:
                    driver.get(url)
                    # 대기 시간을 3초 정도로 줄여서 실패 시 더 빠르게 넘어갑니다.
                    wait = WebDriverWait(driver, 3)
                    wait.until(
                        EC.presence_of_element_located((By.ID, "rootOfProContentshadowverse"))
                    )
                    html_source = driver.page_source
                    card_found = True

                except TimeoutException:
                    # --- [개선 1] 똑똑한 건너뛰기 로직 ---
                    print(f"  -> Card not found (Timeout). Skipping rest of this category.")
                    break  # 안쪽 for문(고유 ID 루프)을 탈출하고 다음 prefix로 넘어감

                except Exception as e:
                    print(f"  -> An unexpected error occurred: {e}")
                    # 예상치 못한 에러 발생 시에도 다음 카테고리로 넘어감
                    break

                if card_found and html_source:
                    result = parse_card_from_html(html_source)
                    if result and result.get('카드 이름'):
                        card_name = result['카드 이름']
                        card_database[card_name] = result

                        # --- [개선 2] 중간 결과 출력 ---
                        print("  [✓] Success! Card Info:")
                        print(f"      - 이름: {result.get('카드 이름', 'N/A')}")
                        print(
                            f"      - 코스트: {result.get('카드 코스트', 'N/A')}, 공격력: {result.get('카드 공격력', 'N/A')}, 방어력: {result.get('카드 방어력', 'N/A')}")
                        print(f"      - 능력: {result.get('카드 능력 서술문구', 'N/A')[:50]}...")  # 능력 텍스트는 50자만 미리보기
                        with open("card_database_generated.json", "w", encoding="utf-8") as f:
                            json.dump(card_database, f, ensure_ascii=False, indent=4)
                    else:
                        print("  [!] Found container, but failed to parse card info. Skipping rest of this category.")
                        break

                time.sleep(0.5)

    finally:
        driver.quit()

    with open("card_database_generated.json", "w", encoding="utf-8") as f:
        json.dump(card_database, f, ensure_ascii=False, indent=4)

    print("\nScraping complete!")
    print(f"Total {len(card_database)} cards saved to card_database_generated.json")


if __name__ == "__main__":
    main()