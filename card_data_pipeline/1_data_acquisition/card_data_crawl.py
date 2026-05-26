# -*- coding: utf-8 -*-
# 이 파일은 api.dotgg.gg/cgfw/getcards API를 활용하여 지정 카드팩들의 카드 데이터를 효율적으로 수집 및 로컬 파일로 저장합니다.

import json
import os
import urllib.request

# 설정값들입니다.
API_URL = "https://api.dotgg.gg/cgfw/getcards?game=shadowverse"
TARGET_EXPANSIONS = ["104", "105", "106", "107", "900"]
WORKING_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def map_rarity(rarity_val: str) -> str:
    """API의 희귀도 값을 기존 로컬 DB 형식에 맞추어 문자열로 맵핑합니다.
    1부터 4까지의 숫자를 각각 Bronze, Silver, Gold, Legendary로 맵핑합니다.
    """
    mapping = {
        "1": "Bronze",
        "2": "Silver",
        "3": "Gold",
        "4": "Legendary"
    }
    return mapping.get(str(rarity_val), "Bronze")


def main():
    """API 데이터를 다운로드하여 카드팩별로 가공한 후 JSON 파일로 저장합니다."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    print("[INFO] API로부터 카드 데이터 수집을 시작합니다.")
    req = urllib.request.Request(API_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15.0) as response:
            cards_list = json.loads(response.read().decode("utf-8"))
        print(f"[INFO] API 호출 성공. 총 {len(cards_list)}개의 카드를 로드했습니다.")
    except Exception as e:
        print(f"[ERROR] API 호출 실패. 에러 메시지 {e}")
        return

    raw_db_dir = os.path.normpath(os.path.join(WORKING_DIRECTORY, "../../card_database/1_raw_database"))
    if not os.path.exists(raw_db_dir):
        os.makedirs(raw_db_dir)

    # 팩 ID별로 데이터를 분류하여 딕셔너리에 모읍니다.
    categorized_cards = {exp_id: {} for exp_id in TARGET_EXPANSIONS}

    for card in cards_list:
        card_id = card.get("id")
        if not card_id:
            continue

        # 해당 카드가 수집 대상 팩에 속하는지 접두사로 판정합니다.
        matched_exp = None
        for exp_id in TARGET_EXPANSIONS:
            if card_id.startswith(exp_id):
                matched_exp = exp_id
                break

        if matched_exp:
            # 로컬 DB 포맷으로 카드의 데이터를 변환합니다.
            mapped_card = {}
            mapped_card["카드 이름"] = card.get("name", "")
            mapped_card["카드 능력 서술문구"] = card.get("skill_text", "")
            
            # 카드팩 필드 맵핑 (예: [10004] Skybound Dragons)
            set_id = card.get("setId", "")
            set_name = card.get("set_name", "")
            mapped_card["카드팩"] = f"[{set_id}] {set_name}" if set_id and set_name else "Unknown"
            
            mapped_card["카드 타입"] = card.get("type", "")
            mapped_card["카드 코스트"] = str(card.get("cost", "0"))
            mapped_card["카드 공격력"] = str(card.get("atk", "0"))
            mapped_card["카드 방어력"] = str(card.get("life", "0"))
            mapped_card["카드 클래스"] = card.get("color", "Neutral")
            mapped_card["카드 희귀도"] = map_rarity(card.get("rarity", "1"))
            
            # tribes(종족)가 리스트로 제공될 경우 기존 포맷에 맞추어 문자열로 변환합니다.
            tribes = card.get("tribes", [])
            if tribes:
                mapped_card["카드 종족 타입"] = ", ".join(tribes)

            categorized_cards[matched_exp][card_id] = mapped_card

    # 분류된 카드들을 파일로 내보냅니다.
    for exp_id, card_dict in categorized_cards.items():
        final_filename = os.path.join(raw_db_dir, f"{exp_id}_card_database_raw.json")
        with open(final_filename, "w", encoding="utf-8") as f:
            json.dump(card_dict, f, ensure_ascii=False, indent=4)
        print(f"[COMPLETE] {exp_id} 카드팩 상세 수집 완료. 최종 저장 장수 {len(card_dict)}장.")


if __name__ == "__main__":
    main()