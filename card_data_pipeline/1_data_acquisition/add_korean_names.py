import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- 설정 ---
WORKING_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TARGET_EXPANSION = '103'
INPUT_FILENAME = os.path.join(WORKING_DIRECTORY, f'{TARGET_EXPANSION}_card_database_raw.json')
OUTPUT_FILENAME = os.path.join(WORKING_DIRECTORY, f'{TARGET_EXPANSION}_card_database_kor_added.json')
BASE_URL = "https://shadowverse-wb.com/ko/deck/cardslist/card/?card_id="

def get_korean_card_name(driver, card_id):
    """
    주어진 card_id에 대해 selenium을 사용하여 한글 카드 이름을 가져옵니다.
    """
    url = f"{BASE_URL}{card_id}"
    try:
        driver.get(url)
        # 페이지의 한글 이름 태그가 나타날 때까지 최대 10초간 기다립니다.
        wait = WebDriverWait(driver, 10)
        name_element = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "category-title"))
        )
        return name_element.text.strip()
    except TimeoutException:
        print(f"  -> URL 로딩 시간 초과 또는 이름 요소를 찾을 수 없습니다: {url}")
        return None
    except Exception as e:
        print(f"  -> Selenium 처리 중 예기치 않은 오류 발생: {e}")
        return None

def main():
    """
    raw 데이터 파일을 읽어 각 카드에 한글 이름을 추가하고,
    파싱된 데이터 파일로 저장합니다.
    """
    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            card_database = json.load(f)
    except FileNotFoundError:
        print(f"오류: 입력 파일 '{INPUT_FILENAME}'을(를) 찾을 수 없습니다.")
        return
    except json.JSONDecodeError:
        print(f"오류: '{INPUT_FILENAME}' 파일이 올바른 JSON 형식이 아닙니다.")
        return

    print(f"'{INPUT_FILENAME}'에서 {len(card_database)}개의 카드 데이터를 로드했습니다.")

    # --- Selenium WebDriver 설정 ---
    options = Options()
    options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # 이미지 로딩 비활성화로 속도 향상
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    print("한글 카드 이름 추가 작업을 시작합니다...")
    updated_card_database = {}

    try:
        for i, (card_id, card_data) in enumerate(card_database.items()):
            if card_data.get('카드 이름 (한글)') and card_data.get('카드 이름 (한글)') is not None:
                print(f"[{i+1}/{len(card_database)}] 카드 ID: {card_id} (이미 처리됨, 건너뜁니다)")
                updated_card_database[card_id] = card_data
                continue

            print(f"[{i+1}/{len(card_database)}] 카드 ID: {card_id} 처리 중...")
            korean_name = get_korean_card_name(driver, card_id)

            if korean_name:
                card_data['카드 이름 (한글)'] = korean_name
                print(f"  -> 찾은 이름: {korean_name}")
            else:
                card_data['카드 이름 (한글)'] = None
                print("  -> 한글 이름을 찾지 못했습니다.")

            updated_card_database[card_id] = card_data

    finally:
        # 작업이 끝나거나 오류 발생 시 브라우저 종료
        driver.quit()

    # 업데이트된 데이터베이스를 새 파일에 저장
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(updated_card_database, f, ensure_ascii=False, indent=4)
        print(f"\n작업 완료. {len(updated_card_database)}개의 업데이트된 카드 데이터가 '{OUTPUT_FILENAME}'에 저장되었습니다.")
    except IOError as e:
        print(f"\n오류: 파일 '{OUTPUT_FILENAME}' 저장 중 문제가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
