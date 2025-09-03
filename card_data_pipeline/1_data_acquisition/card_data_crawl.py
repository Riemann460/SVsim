import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- 설정 값 ---
BASE_URL = "https://shadowverse.gg/cards"
# 분석할 카드팩 ID
TARGET_EXPANSION = '103'


def _get_stat(stats_section, label_text):
    """stats_section에서 라벨에 해당하는 값을 찾아 반환하는 헬퍼 함수"""
    label_div = stats_section.find('div', string=label_text)
    if label_div:
        value_div = label_div.find_next_sibling('div')
        if value_div:
            return value_div.text.strip()
    return None


def parse_card_from_html(html: str):
    """HTML에서 카드 정보를 파싱합니다."""
    soup = BeautifulSoup(html, 'html.parser')
    card_info = {}
    container = soup.find('div', id='rootOfProContentshadowverse')
    if not container:
        return None

    name_tag = container.find('h2')
    if name_tag:
        card_info['카드 이름'] = name_tag.text.split(' - ')[0].strip()

    description_label = container.find('div', string='Description')
    if description_label and description_label.find_next_sibling('div'):
        card_info['카드 능력 서술문구'] = description_label.find_next_sibling('div').text.strip()

    stats_section = container.find('section')
    if stats_section:
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
        for label, key in labels_to_find.items():
            value = _get_stat(stats_section, label)
            if value:
                card_info[key] = value

    return card_info


def generate_card_prefixes(expansion_id: str):
    """ID의 앞 6자리(카드 카테고리) 조합을 생성합니다."""
    expansions = [expansion_id]
    classes = ['0', '1', '2', '3', '4', '5', '6', '7']
    rarities = ['1', '2', '3', '4']
    card_types = ['1', '2', '3']

    prefixes = []
    for exp in expansions:
        for cls in classes:
            for rar in rarities:
                # 특정 카드팩의 규칙 (예: Basic 팩은 레전드/골드 없음)
                if exp == '100' and rar in ['3', '4']:
                    continue
                for typ in card_types:
                    prefixes.append(f"{exp}{cls}{rar}{typ}")
    return prefixes


def main():
    """ID 생성 및 순차적 크롤링을 실행합니다."""
    print(f"Generating card prefixes for expansion {TARGET_EXPANSION}...")
    card_prefixes = generate_card_prefixes(TARGET_EXPANSION)
    total_categories = len(card_prefixes)
    print(f"Generated {total_categories} categories to check.")

    card_database = {}

    # --- Selenium WebDriver 옵션 최적화 ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    # 페이지 로딩에 30초 이상 걸리면 타임아웃 발생
    driver.set_page_load_timeout(30)

    # --- 파일명 설정 ---
    temp_filename = f"{TARGET_EXPANSION}_card_database_generated_temp.json"
    final_filename = f"{TARGET_EXPANSION}_card_database_raw.json"

    try:
        for i, prefix in enumerate(card_prefixes):
            print(f"\n--- Checking Category {i + 1}/{total_categories} (Prefix: {prefix}) ---")

            for u_id_multiplier in range(1, 10):
                # 카드 ID 생성 로직 (고유 ID 부분은 추측에 기반)
                unique_id = str(u_id_multiplier * 10)
                card_id = f"{prefix}{unique_id}"
                url = f"{BASE_URL}/{card_id}"

                print(f"Checking URL: {url}")

                html_source = None
                card_found = False
                try:
                    driver.get(url)
                    # 페이지 로딩이 성공하면, 내용이 나타날 때까지 최대 5초 대기
                    wait = WebDriverWait(driver, 5)
                    wait.until(
                        EC.presence_of_element_located((By.ID, "rootOfProContentshadowverse"))
                    )
                    html_source = driver.page_source
                    card_found = True
                
                except TimeoutException:
                    print(f"  -> Page load timed out or element not found for {url}. Skipping.")
                    continue # 다음 카드로 넘어감

                except Exception as e:
                    print(f"  -> An unexpected error occurred: {e}")
                    break

                if card_found and html_source:
                    result = parse_card_from_html(html_source)
                    if result and result.get('카드 이름'):
                        card_database[card_id] = result
                        print("  [SUCCESS] Card Info:")
                        print(f"      - 이름: {result.get('카드 이름', 'N/A')}")
                        print(
                            f"      - 코스트: {result.get('카드 코스트', 'N/A')}, "
                            f"공격력: {result.get('카드 공격력', 'N/A')}, "
                            f"방어력: {result.get('카드 방어력', 'N/A')}")
                        print(f"      - 능력: {result.get('카드 능력 서술문구', 'N/A')[:50]}...")
                    else:
                        print("  [FAIL] Found container, but failed to parse card info. Skipping rest of this category.")
                        break

                time.sleep(0.5)  # 서버 부하를 줄이기 위한 지연

            # 10개 카테고리마다 중간 저장
            if i % 10 == 9:
                print(f"\n--- Saving progress ({len(card_database)} cards collected) ---")
                with open(temp_filename, "w", encoding="utf-8") as f:
                    json.dump(card_database, f, ensure_ascii=False, indent=4)

    finally:
        driver.quit()

    with open(final_filename, "w", encoding="utf-8") as f:
        json.dump(card_database, f, ensure_ascii=False, indent=4)

    print("\nScraping complete!")
    print(f"Total {len(card_database)} cards saved to {final_filename}")


if __name__ == "__main__":
    main()