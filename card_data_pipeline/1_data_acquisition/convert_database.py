import json
import os
import sys

# 현재 파일이 위치한 디렉토리와 프로젝트 루트 디렉토리를 sys.path에 추가합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.normpath(os.path.join(current_dir, "../..")))
# Add path to src/common for enums and other modules
src_common_path = os.path.normpath(os.path.join(current_dir, "../../src/common"))
if src_common_path not in sys.path:
    sys.path.append(src_common_path)

from enums import CardType, ClassType, TribeType, EffectType, ProcessType, TargetType
from parse_script import parse_effect_text, get_required_listeners
from effect import Effect


def convert_json_to_class_script(json_file_path: str, output_json_path: str) -> None:
    """Convert a Korean‑augmented card JSON file into a structured JSON representation.

    Parameters
    ----------
    json_file_path: str
        Path to the source JSON file containing raw card data (Korean names included).
    output_json_path: str
        Destination path for the parsed JSON file.
    """
    # Enum reverse maps for conversion
    class_map = {e.value: e for e in ClassType}
    type_map = {"Follower": CardType.FOLLOWER, "Spell": CardType.AMULET, "4": CardType.SPELL}
    tribe_map = {e.value: e for e in TribeType}

    # Default fallbacks
    class_map["Unknown"] = ClassType.NEUTRAL
    tribe_map["Earth Sigil"] = TribeType.EARTH_SIGIL

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"오류: '{json_file_path}' 파일을 찾을 수 없습니다.")
        return

    database = {}
    for card_en_name, details in raw_data.items():
        try:
            # 기본 정보 추출
            card_name_kr = details.get("카드 이름 (한글)", details.get("카드 이름", card_en_name))
            cost = int(details.get("카드 코스트", 0))
            attack = int(details.get("카드 공격력", 0))
            defense = int(details.get("카드 방어력", 0))
            card_type_str = details.get("카드 타입", "Follower")
            class_type_str = details.get("카드 클래스", "Neutral")

            # Enum 변환
            card_type_enum = type_map.get(card_type_str, CardType.FOLLOWER).name
            class_type_enum = class_map.get(class_type_str, ClassType.NEUTRAL).name

            # 종족 파싱
            tribes = []
            tribe = details.get("카드 종족 타입")
            if tribe:
                resolved_tribe = tribe_map.get(tribe)
                if resolved_tribe:
                    tribes.append(resolved_tribe.name)

            # 효과 파싱
            raw_effects_text = ""
            parsed_effects = []
            if details.get("카드 능력 서술문구"):
                raw_effects_text = details["카드 능력 서술문구"]
                parsed_effects_list = parse_effect_text(raw_effects_text, card_type_enum)
                for effect_obj in parsed_effects_list:
                    parsed_effects.append(effect_obj.to_dict())

            # Spell 타입이면 효과에 명시적으로 Spell 타입을 부여
            if card_type_enum == CardType.SPELL.name:
                for eff in parsed_effects:
                    eff.update(type=EffectType.SPELL.name)

            required_listeners = get_required_listeners(parsed_effects)

            # 영어 이름(기존 키)와 한글 이름을 모두 보관
            card_name_en = details.get("카드 이름", card_en_name)
            card_data_dict = {
                "card_id": card_en_name,
                "name": card_name_en,
                "name_kr": card_name_kr,
                "cost": cost,
                "card_type": card_type_enum,
                "class_type": class_type_enum,
                "attack": attack,
                "defense": defense,
                "tribes": tribes,
                "effects": parsed_effects,
                "raw_effects_text": raw_effects_text,
                "required_listeners": required_listeners,
            }

            # 현재 set 에 따라 적절한 DB에 저장 (일단 개별 파일에만 저장)
            database[card_en_name] = card_data_dict
        except (ValueError, KeyError) as e:
            print(f"카드 '{card_en_name}' 처리 중 에러 발생: {e}, {card_data_dict}")
            continue

    # Write per‑set parsed JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
    print(f"데이터 변환 완료! 결과가 '{output_json_path}' 파일에 저장되었습니다.")
    print(f"- {len(database)}개 카드")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    set_ids = ["100", "101", "102", "103", "104", "105", "106", "107", "900"]

    # 1️⃣ 개별 set 을 파싱하여 3_parsed_database 에 저장
    for set_id in set_ids:
        convert_json_to_class_script(
            json_file_path=os.path.normpath(
                os.path.join(script_dir, f"../../card_database/2_kor_database/{set_id}_card_database_kor_added.json")
            ),
            output_json_path=os.path.normpath(
                os.path.join(script_dir, f"../../card_database/3_parsed_database/{set_id}_card_database_parsed.json")
            ),
        )

    # 2️⃣ 모든 파싱된 파일을 하나의 merged_database 로 병합
    merged_database = {
        "BASIC_CARD_DATABASE": {},
        "LEGENDS_RISE_CARD_DATABASE": {},
        "TOKEN_CARD_DATABASE": {},
    }
    for set_id in set_ids:
        parsed_path = os.path.normpath(
            os.path.join(script_dir, f"../../card_database/3_parsed_database/{set_id}_card_database_parsed.json")
        )
        if not os.path.exists(parsed_path):
            continue
        with open(parsed_path, "r", encoding="utf-8") as f:
            set_data = json.load(f)
        if set_id == "100":
            merged_database["BASIC_CARD_DATABASE"].update(set_data)
        elif set_id == "900":
            merged_database["TOKEN_CARD_DATABASE"].update(set_data)
        else:
            merged_database["LEGENDS_RISE_CARD_DATABASE"].update(set_data)

    # 3️⃣ name → id 매핑 (영문 & 한글 모두 매핑)
    name_to_id: dict[str, str] = {}
    for db_key in ["BASIC_CARD_DATABASE", "LEGENDS_RISE_CARD_DATABASE", "TOKEN_CARD_DATABASE"]:
        for cid, info in merged_database[db_key].items():
            en_name = info.get("name")
            if en_name:
                name_to_id[en_name] = cid
            kr_name = info.get("name_kr")
            if kr_name:
                name_to_id[kr_name] = cid

    # 4️⃣ 효과값에 카드 이름이 있으면 ID 로 교체
    def replace_effect_values(section: dict) -> None:
        for card in section.values():
            for effect in card.get("effects", []):
                val = effect.get("value")
                if isinstance(val, str):
                    key = val.strip()
                    if key in name_to_id:
                        effect["value"] = name_to_id[key]
                elif isinstance(val, list):
                    new_list = []
                    for item in val:
                        if isinstance(item, str) and item.strip() in name_to_id:
                            new_list.append(name_to_id[item.strip()])
                        else:
                            new_list.append(item)
                    effect["value"] = new_list

    for sect in merged_database.values():
        replace_effect_values(sect)

    # 5️⃣ 최종 merged 파일 기록
    final_output_path = os.path.normpath(os.path.join(script_dir, "../../card_database/3_parsed_database/card_database_parsed.json"))
    with open(final_output_path, "w", encoding="utf-8") as f:
        json.dump(merged_database, f, ensure_ascii=False, indent=4)
    print(f"통합 데이터베이스 빌드 완료! 결과가 '{final_output_path}' 파일에 저장되었습니다.")
