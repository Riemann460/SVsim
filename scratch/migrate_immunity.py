import json
import glob
import os

manual_db_dir = "card_database/4_manual_database"

def migrate_effect(effect):
    if effect.get("process") == "IMMUNITY":
        val = effect.get("value")
        # 공격 불가 면역
        if val is None or isinstance(val, str):
            effect["type"] = "DISABLE"
            # process key를 삭제
            if "process" in effect:
                del effect["process"]
            if "value" in effect:
                del effect["value"]
        # 데미지 상한 면역
        elif isinstance(val, int):
            effect["process"] = "ADD_EFFECT"
    return effect

# 1. 개별 manual json 수정
for file_path in glob.glob(os.path.join(manual_db_dir, "*_manual.json")):
    with open(file_path, "r", encoding="utf-8") as f:
        db = json.load(f)
    for card_id, card in db.items():
        if "effects" in card:
            card["effects"] = [migrate_effect(eff) for eff in card["effects"]]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

# 2. 통합 card_database_manual.json 수정
unified_path = os.path.join(manual_db_dir, "card_database_manual.json")
if os.path.exists(unified_path):
    with open(unified_path, "r", encoding="utf-8") as f:
        db = json.load(f)
    for db_section, cards in db.items():
        for card_id, card in cards.items():
            if "effects" in card:
                card["effects"] = [migrate_effect(eff) for eff in card["effects"]]
    with open(unified_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

print("Migration completed successfully.")
