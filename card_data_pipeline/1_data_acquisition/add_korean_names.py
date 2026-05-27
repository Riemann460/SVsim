# 이 파일은 공식 덱포탈 API를 호출하여 전체 한글 카드 명칭을 획득하고 로컬 DB에 추가합니다.

import json
import os
import urllib.request
import time

# 설정값들입니다.
API_URL_TEMPLATE = "https://shadowverse-wb.com/web/CardList/cardList?offset={offset}"
TARGET_EXPANSIONS = ["104", "105", "106", "107", "900"]
WORKING_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def fetch_all_korean_names() -> dict:
    """공식 API를 20개 단위의 offset 루프로 호출하여 전체 한글 카드명 매핑 테이블을 생성합니다."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "lang": "ko",
        "Referer": "https://shadowverse-wb.com/ko/deck/cardslist/"
    }
    
    korean_names = {}
    offset = 0
    total_count = 999  # 초기값으로 큰 수를 세팅하고 첫 응답에서 업데이트합니다.
    
    print("[INFO] 공식 API로부터 한글 카드명 수집을 시작합니다.")
    
    while offset < total_count:
        url = API_URL_TEMPLATE.format(offset=offset)
        print(f"  -> Offset {offset} 데이터 수집 중...")
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=10.0) as response:
                res_data = json.loads(response.read().decode("utf-8"))
            
            data = res_data.get("data", {})
            total_count = data.get("count", 999)
            details = data.get("card_details", {})
            
            if not details:
                print("  -> 더 이상 디테일 정보가 없어 루프를 탈출합니다.")
                break
                
            for card_id_str, val in details.items():
                common = val.get("common", {})
                name_ko = common.get("name")
                if name_ko:
                    korean_names[card_id_str] = name_ko
                    
            offset += 20
            time.sleep(0.05)
            
        except Exception as e:
            print(f"  [ERROR] Offset {offset} 수집 중 에러 발생 {e}")
            break
            
    print(f"[INFO] 수집 완료. 총 {len(korean_names)}개의 한글 카드명을 확보했습니다.")
    return korean_names


def process_expansion(korean_names: dict, expansion_id: str):
    """지정한 카드팩에 대해 한글 카드명을 로컬 DB에 추가하고 새 경로에 저장합니다."""
    input_dir = os.path.normpath(os.path.join(WORKING_DIRECTORY, "../../card_database/1_raw_database"))
    output_dir = os.path.normpath(os.path.join(WORKING_DIRECTORY, "../../card_database/2_kor_database"))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    input_filename = os.path.join(input_dir, f"{expansion_id}_card_database_raw.json")
    output_filename = os.path.join(output_dir, f"{expansion_id}_card_database_kor_added.json")

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            card_database = json.load(f)
    except FileNotFoundError:
        print(f"오류. 입력 파일 '{input_filename}'이 존재하지 않아 건너뜁니다.")
        return

    updated_card_database = {}
    matched_count = 0

    for card_id, card_data in card_database.items():
        name_ko = korean_names.get(card_id)
        if name_ko:
            card_data['카드 이름 (한글)'] = name_ko
            matched_count += 1
        else:
            card_data['카드 이름 (한글)'] = None

        updated_card_database[card_id] = card_data

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(updated_card_database, f, ensure_ascii=False, indent=4)
    print(f"[COMPLETE] {expansion_id} 한글 카드명 저장 완료. 매칭된 카드 {matched_count}개 중 {len(card_database)}개.")


def main():
    """전체 한국어 카드명 사전을 로드하고 익스팬션별 처리를 대리 실행합니다."""
    korean_names = fetch_all_korean_names()
    if not korean_names:
        print("[ERROR] 한글 카드명을 가져오지 못해 처리를 종료합니다.")
        return
        
    for exp_id in TARGET_EXPANSIONS:
        process_expansion(korean_names, exp_id)


if __name__ == "__main__":
    main()
