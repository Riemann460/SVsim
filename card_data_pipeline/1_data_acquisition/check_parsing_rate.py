import os
import json

# 경로 정의
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARSED_DB_DIR = os.path.join(BASE_DIR, "card_database", "3_parsed_database")

def check_parsing_rate():
    """파싱 성공률을 측정하고 미구현된 키워드와 액션 통계를 출력합니다."""
    total_cards = 0
    parsed_fully_cards = 0
    failed_cards = []
    
    unparsed_reasons = {}

    if not os.path.exists(PARSED_DB_DIR):
        print(f"Error: {PARSED_DB_DIR} does not exist.")
        return

    for filename in os.listdir(PARSED_DB_DIR):
        if not filename.endswith(".json") or filename == "card_database_parsed.json":
            continue
        
        filepath = os.path.join(PARSED_DB_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                db = json.load(f)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue
            
            for card_id, card in db.items():
                total_cards += 1
                is_failed = False
                unparsed_parts = []
                
                effects = card.get("effects", [])
                for effect in effects:
                    # raw_effect_text 또는 raw_action_text가 존재하는지 체크
                    if "raw_effect_text" in effect or "raw_action_text" in effect or "raw_target_text" in effect:
                        is_failed = True
                        if "raw_effect_text" in effect:
                            unparsed_parts.append(f"Effect: {effect['raw_effect_text']}")
                            unparsed_reasons[effect['raw_effect_text']] = unparsed_reasons.get(effect['raw_effect_text'], 0) + 1
                        if "raw_action_text" in effect:
                            unparsed_parts.append(f"Action: {effect['raw_action_text']}")
                            unparsed_reasons[effect['raw_action_text']] = unparsed_reasons.get(effect['raw_action_text'], 0) + 1
                        if "raw_target_text" in effect:
                            unparsed_parts.append(f"Target: {effect['raw_target_text']}")
                            unparsed_reasons[effect['raw_target_text']] = unparsed_reasons.get(effect['raw_target_text'], 0) + 1

                if is_failed:
                    failed_cards.append((card.get("name", "N/A"), card_id, unparsed_parts, card.get("raw_effects_text", "")))
                else:
                    parsed_fully_cards += 1

    success_rate = (parsed_fully_cards / total_cards * 100) if total_cards > 0 else 0
    print(f"Total Cards: {total_cards}")
    print(f"Fully Parsed Cards: {parsed_fully_cards}")
    print(f"Failed Cards: {len(failed_cards)}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Manual Work Ratio: {100 - success_rate:.2f}%")
    
    print("\n--- Top Unparsed Reason Texts (Frequency) ---")
    sorted_reasons = sorted(unparsed_reasons.items(), key=lambda x: x[1], reverse=True)
    for reason, count in sorted_reasons[:25]:
        print(f"- [{count} times]: {reason}")
        
    # Failed card list sample
    print("\n--- Failed Card Samples (Top 10) ---")
    for name, cid, parts, raw_text in failed_cards[:15]:
        print(f"- {name} ({cid}):")
        print(f"  Raw: {raw_text}")
        for part in parts:
            print(f"  * {part}")

if __name__ == "__main__":
    check_parsing_rate()
