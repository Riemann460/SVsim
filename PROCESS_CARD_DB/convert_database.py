import json
from enum import Enum

from enums import CardType, ClassType, TribeType, EffectType, ProcessType, TargetType
from parse_script import parse_effect_text, Effect # Import Effect class for type checking

def effect_to_dict(effect_obj):
    if isinstance(effect_obj, Effect):
        effect_dict = {}
        for key, value in effect_obj.attributes.items():
            if isinstance(value, Enum):
                effect_dict[key] = value.name
            elif isinstance(value, Effect):
                effect_dict[key] = effect_to_dict(value)
            elif isinstance(value, list) and all(isinstance(item, Effect) for item in value):
                effect_dict[key] = [effect_to_dict(item) for item in value]
            else:
                effect_dict[key] = value
        return effect_dict
    elif isinstance(effect_obj, dict) and 'raw_effect_text' in effect_obj:
        return effect_obj # Return raw effect dict as is
    return str(effect_obj) # Fallback for unexpected types

def convert_json_to_class_script(json_file_path, output_json_path):
    """
    JSON 데이터를 읽어 구조화된 카드 데이터를 JSON 파일로 생성합니다.
    """
    # Enum 변환을 위한 역방향 맵 생성
    class_map = {e.value: e for e in ClassType}
    type_map = {e.value: e for e in CardType}
    tribe_map = {e.value: e for e in TribeType}

    # 기본값 설정
    class_map['Unknown'] = ClassType.NEUTRAL
    type_map['4'] = CardType.SPELL  # 일부 주문 카드가 '4'로 되어 있어 변환
    tribe_map['Earth Sigil'] = TribeType.EARTH_SIGIL

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"오류: '{json_file_path}' 파일을 찾을 수 없습니다.")
        return

    # 카드팩별로 데이터를 저장할 딕셔너리 초기화
    databases = {
        "BASIC_CARD_DATABASE": {},
        "LEGENDS_RISE_CARD_DATABASE": {},
        "TOKEN_CARD_DATABASE": {}
    }

    for card_en_name, details in raw_data.items():
        try:
            card_pack_str = details.get('카드팩')

            card_name_kr = details.get('카드 이름', card_en_name)

            cost = int(details.get('카드 코스트', 0))
            attack = int(details.get('카드 공격력', 0))
            defense = int(details.get('카드 방어력', 0))

            card_type_str = details.get('카드 타입', 'Follower')
            class_type_str = details.get('카드 클래스', 'Neutral')

            # 효과 파싱 및 딕셔너리 변환
            parsed_effects = []
            if details.get('카드 능력 서술문구'):
                raw_effect_text = details['카드 능력 서술문구']
                parsed_effects_raw = parse_effect_text(raw_effect_text)
                for effect_obj in parsed_effects_raw:
                    parsed_effects.append(effect_to_dict(effect_obj))

            # Enum으로 변환 및 문자열화
            card_type_enum = type_map.get(card_type_str, CardType.FOLLOWER).name
            class_type_enum = class_map.get(class_type_str, ClassType.NEUTRAL).name
            tribes = []
            tribe = details.get('카드 종족 타입', None)
            if tribe:
                resolved_tribe = tribe_map.get(tribe)
                if resolved_tribe: # None이 아닌 경우에만 추가
                    tribes.append(resolved_tribe.name)

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
                "effects": parsed_effects
            }

            # 카드팩에 따라 적절한 데이터베이스에 저장
            if card_pack_str == '[10000] Basic':
                databases["BASIC_CARD_DATABASE"][card_en_name] = card_data_dict
            elif card_pack_str == '[10001] Legends Rise':
                databases["LEGENDS_RISE_CARD_DATABASE"][card_en_name] = card_data_dict
            elif card_pack_str == '[90000] Basic A':  # 토큰 카드
                databases["TOKEN_CARD_DATABASE"][card_en_name] = card_data_dict

        except (ValueError, KeyError) as e:
            print(f"카드 '{card_en_name}' 처리 중 에러 발생: {e}")
            continue

    # --- JSON 파일 생성 ---
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(databases, f, ensure_ascii=False, indent=4)

    print(f"데이터 변환 완료! 결과가 '{output_json_path}' 파일에 저장되었습니다.")
    for db_name, db_content in databases.items():
        print(f"- {db_name}: {len(db_content)}개 카드")


if __name__ == "__main__":
    convert_json_to_class_script(
        json_file_path="card_database_raw.json",  # 변경된 부분
        output_json_path="card_database_parsed.json"
    )