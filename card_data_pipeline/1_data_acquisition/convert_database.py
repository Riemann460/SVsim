# 역할 정의. 개별 카드 JSON 데이터를 통합하고 구조화된 클래스 기반의 파싱된 JSON 데이터베이스로 변환하는 스크립트입니다.

import json
import os
import sys

# 현재 파일이 위치한 디렉토리와 프로젝트 루트 디렉토리를 sys.path에 추가합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.normpath(os.path.join(current_dir, "../..")))
# enums 및 기타 모듈을 위해 src/common 경로를 추가합니다.
src_common_path = os.path.normpath(os.path.join(current_dir, "../../src/common"))
if src_common_path not in sys.path:
    sys.path.append(src_common_path)

from enums import CardType, ClassType, TribeType, EffectType, ProcessType, TargetType
from parse_script import parse_effect_text, get_required_listeners
from effect import Effect


def convert_json_to_class_script(json_file_path: str, output_json_path: str) -> None:
    """한글 데이터가 보강된 카드 JSON 파일을 구조화된 JSON 데이터베이스로 변환합니다.

    매개변수
    ----------
    json_file_path (str) - 한글 카드명이 포함된 원본 JSON 파일 경로입니다.
    output_json_path (str) - 구조화되어 파싱된 JSON 결과를 저장할 파일 경로입니다.
    """
    # 변환을 위한 역방향 Enum 맵을 정의합니다.
    class_map = {e.value: e for e in ClassType}
    type_map = {"Follower": CardType.FOLLOWER, "Amulet": CardType.AMULET, "Spell": CardType.AMULET, "4": CardType.SPELL}
    tribe_map = {e.value: e for e in TribeType}

    # 기본 예외 처리 값들을 설정합니다.
    class_map["Unknown"] = ClassType.NEUTRAL
    tribe_map["Earth Sigil"] = TribeType.EARTH_SIGIL

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"오류 - '{json_file_path}' 파일을 찾을 수 없습니다.")
        return

    database = {}
    for card_en_name, details in raw_data.items():
        try:
            # 기본 정보를 추출합니다.
            card_name_kr = details.get("카드 이름 (한글)", details.get("카드 이름", card_en_name))
            cost = int(details.get("카드 코스트", 0))
            attack = int(details.get("카드 공격력", 0))
            defense = int(details.get("카드 방어력", 0))
            card_type_str = details.get("카드 타입", "Follower")
            class_type_str = details.get("카드 클래스", "Neutral")

            # Enum 형식으로 변환합니다.
            card_type_enum = type_map.get(card_type_str, CardType.FOLLOWER).name
            class_type_enum = class_map.get(class_type_str, ClassType.NEUTRAL).name

            # 종족을 파싱합니다.
            tribes = []
            tribe = details.get("카드 종족 타입")
            if tribe:
                resolved_tribe = tribe_map.get(tribe)
                if resolved_tribe:
                    tribes.append(resolved_tribe.name)

            # 효과를 파싱합니다.
            raw_effects_text = ""
            parsed_effects = []
            if details.get("카드 능력 서술문구"):
                raw_effects_text = details["카드 능력 서술문구"]
                parsed_effects_list = parse_effect_text(raw_effects_text, card_type_enum)
                for effect_obj in parsed_effects_list:
                    parsed_effects.append(effect_obj.to_dict())

            if card_type_enum == CardType.SPELL.name:
                for eff in parsed_effects:
                    if eff.get("type") is None:
                        eff.update(type=CardType.SPELL.name)

            required_listeners = get_required_listeners(parsed_effects)

            # 영어 이름(기존 키)과 한글 이름을 모두 보관합니다.
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

            # 현재 세트에 따라 적절한 DB에 저장합니다 (우선 개별 파일로만 기록됩니다).
            database[card_en_name] = card_data_dict
        except (ValueError, KeyError) as e:
            print(f"카드 '{card_en_name}' 처리 중 에러 발생 - {e}, {card_data_dict}")
            continue

    # 세트별로 파싱된 JSON 파일을 기록합니다.
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
    print(f"데이터 변환 완료! 결과가 '{output_json_path}' 파일에 저장되었습니다.")
    print(f"- {len(database)}개 카드")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    set_ids = ["100", "101", "102", "103", "104", "105", "106", "107", "900"]

    # 1️⃣ 개별 세트를 파싱하여 3_parsed_database 에 저장합니다.
    for set_id in set_ids:
        convert_json_to_class_script(
            json_file_path=os.path.normpath(
                os.path.join(script_dir, f"../../card_database/2_kor_database/{set_id}_card_database_kor_added.json")
            ),
            output_json_path=os.path.normpath(
                os.path.join(script_dir, f"../../card_database/3_parsed_database/{set_id}_card_database_parsed.json")
            ),
        )

    # 2️⃣ 모든 파싱된 파일을 하나의 merged_database 로 병합합니다.
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

    # 3️⃣ name 에서 id 로의 매핑을 수행합니다 (영문 및 한글 모두 매핑됩니다).
    name_to_id: dict[str, str] = {}
    for db_key in ["BASIC_CARD_DATABASE", "LEGENDS_RISE_CARD_DATABASE", "TOKEN_CARD_DATABASE"]:
        for cid, info in merged_database[db_key].items():
            en_name = info.get("name")
            if en_name:
                name_to_id[en_name] = cid
            kr_name = info.get("name_kr")
            if kr_name:
                name_to_id[kr_name] = cid

    # 4️⃣ 효과값에 카드 이름이 존재할 경우 ID 로 교체합니다.
    def replace_effect_values(section: dict) -> None:
        for card in section.values():
            for effect in card.get("effects", []):
                # processes 리스트를 순회하며 개별 프로세스의 value를 ID로 치환합니다.
                for process in effect.get("processes", []):
                    val = process.get("value")
                    if isinstance(val, str):
                        key = val.strip()
                        if key in name_to_id:
                            process["value"] = name_to_id[key]
                    elif isinstance(val, list):
                        new_list = []
                        for item in val:
                            if isinstance(item, str) and item.strip() in name_to_id:
                                new_list.append(name_to_id[item.strip()])
                            else:
                                new_list.append(item)
                        process["value"] = new_list

                # 하위 호환성을 위해 Effect 레벨의 value 치환 로직도 유지합니다.
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

    # 5️⃣ 최종 병합 파일을 기록합니다.
    final_output_path = os.path.normpath(os.path.join(script_dir, "../../card_database/3_parsed_database/card_database_parsed.json"))
    with open(final_output_path, "w", encoding="utf-8") as f:
        json.dump(merged_database, f, ensure_ascii=False, indent=4)
    print(f"통합 데이터베이스 빌드 완료! 결과가 '{final_output_path}' 파일에 저장되었습니다.")
