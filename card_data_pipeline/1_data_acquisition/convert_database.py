import json
from enum import Enum

from enums import CardType, ClassType, TribeType, EffectType, ProcessType, TargetType
from parse_script import parse_effect_text, get_required_listeners  # Import Effect class for type checking
from effect import Effect


def convert_json_to_class_script(json_file_path, output_json_path):
    """
    JSON 데이터를 읽어 구조화된 카드 데이터를 JSON 파일로 생성합니다.
    """
    # Enum 변환을 위한 역방향 맵 생성
    class_map = {e.value: e for e in ClassType}
    type_map = {"Follower": CardType.FOLLOWER, "Spell": CardType.AMULET, "4": CardType.SPELL}
    tribe_map = {e.value: e for e in TribeType}

    # 기본값 설정
    class_map['Unknown'] = ClassType.NEUTRAL
    tribe_map['Earth Sigil'] = TribeType.EARTH_SIGIL

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"오류: '{json_file_path}' 파일을 찾을 수 없습니다.")
        return

    # 카드팩별로 데이터를 저장할 딕셔너리 초기화
    database = {}

    for card_en_name, details in raw_data.items():
        try:
            card_pack_str = details.get('카드팩')
            card_name_kr = details.get('카드 이름', card_en_name)
            cost = int(details.get('카드 코스트', 0))
            attack = int(details.get('카드 공격력', 0))
            defense = int(details.get('카드 방어력', 0))
            card_type_str = details.get('카드 타입', 'Follower')
            class_type_str = details.get('카드 클래스', 'Neutral')

            # Enum으로 변환 및 문자열화
            card_type_enum = type_map.get(card_type_str, CardType.FOLLOWER).name
            class_type_enum = class_map.get(class_type_str, ClassType.NEUTRAL).name
            tribes = []
            tribe = details.get('카드 종족 타입', None)
            if tribe:
                resolved_tribe = tribe_map.get(tribe)
                if resolved_tribe:  # None이 아닌 경우에만 추가
                    tribes.append(resolved_tribe.name)

            # 효과 파싱 및 딕셔너리 변환
            raw_effects_text = ""
            parsed_effects = []
            if details.get('카드 능력 서술문구'):
                raw_effects_text = details['카드 능력 서술문구']
                parsed_effects_list = parse_effect_text(raw_effects_text, card_type_enum)
                for effect_obj in parsed_effects_list:
                    effect_dict = effect_obj.to_dict()
                    parsed_effects.append(effect_dict)
            if card_type_enum == CardType.SPELL.name:
                for effect in parsed_effects:
                    effect.update(type=EffectType.SPELL.name)

            required_listeners = get_required_listeners(parsed_effects)

            # CardData 딕셔너리 생성
            card_data_dict = {
                "card_id": card_en_name,
                "name": card_name_kr,
                "cost": cost,
                "card_type": card_type_enum,
                "class_type": class_type_enum,
                "attack": attack,
                "defense": defense,
                "tribes": tribes,
                "effects": parsed_effects,
                "raw_effects_text": raw_effects_text,
                "required_listeners": required_listeners
            }

            # 카드팩에 따라 적절한 데이터베이스에 저장
            database[card_en_name] = card_data_dict

        except (ValueError, KeyError) as e:
            print(f"카드 '{card_en_name}' 처리 중 에러 발생: {e}, {card_data_dict}")
            continue

    # --- JSON 파일 생성 ---
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=4)

    print(f"데이터 변환 완료! 결과가 '{output_json_path}' 파일에 저장되었습니다.")
    print(f"- {len(database)}개 카드")


if __name__ == "__main__":
    set_ids = ["100", "101", "102", "900"]
    for set_id in set_ids:
        convert_json_to_class_script(
            json_file_path=f"../../card_database/raw_database/{set_id}_card_database_raw.json",
            output_json_path=f"../../card_database/parsed_database/{set_id}_card_database_parsed.json"
        )