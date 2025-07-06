import json
from enums import CardType, ClassType, TribeType

class CardData:
    def __init__(self, card_id, name, cost, card_type, class_type, attack=0, defense=0, tribes=None, effects=None):
        self.card_id = card_id
        self.name = name  # 한글 이름 (번역 필요)
        self.cost = cost
        self.card_type = card_type
        self.class_type = class_type
        self.attack = attack
        self.defense = defense
        self.tribes = tribes if tribes is not None else []
        self.effects = effects if effects is not None else []

    def __repr__(self):
        # 객체를 출력할 때 보기 좋은 형태로 만들기 위함
        return (f'CardData("{self.card_id}", "{self.name}", {self.cost}, {self.card_type}, '
                f'{self.class_type}, {self.attack}, {self.defense}, tribes=[{self.tribes}], effects={self.effects})')


def convert_json_to_class_script(json_file_path, output_py_path):
    """
    JSON 데이터를 읽어 CardData 클래스 인스턴스를 사용하는 .py 파일을 생성합니다.
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
        # CardData 인스턴스 생성을 위한 데이터 파싱
        try:
            card_pack_str = details.get('카드팩')

            # 일부 데이터에 '카드 이름'이 없는 경우, 최상위 키(영문명)를 사용
            card_name_kr = details.get('카드 이름', card_en_name)  # 한글 이름은 없으므로 영문명으로 대체

            cost = int(details.get('카드 코스트', 0))
            attack = int(details.get('카드 공격력', 0))
            defense = int(details.get('카드 방어력', 0))

            card_type_str = details.get('카드 타입', 'Follower')
            class_type_str = details.get('카드 클래스', 'Neutral')

            # 요청대로 효과는 원본 문자열을 그대로 저장
            effects_list = []
            if details.get('카드 능력 서술문구'):
                effects_list.append(details['카드 능력 서술문구'])

            # Enum으로 변환
            card_type_enum = type_map.get(card_type_str, CardType.FOLLOWER)
            class_type_enum = class_map.get(class_type_str, ClassType.NEUTRAL)
            tribe = details.get('카드 종족 타입', None)
            if tribe:
                tribes = str(tribe_map.get(tribe))
            else:
                tribes = ""

            # CardData 인스턴스 생성
            card_instance = CardData(
                card_id=card_en_name,
                name=card_name_kr,
                cost=cost,
                card_type=card_type_enum,
                class_type=class_type_enum,
                attack=attack,
                defense=defense,
                tribes=tribes,
                effects=effects_list
            )

            # 카드팩에 따라 적절한 데이터베이스에 저장
            if card_pack_str == '[10000] Basic':
                databases["BASIC_CARD_DATABASE"][card_en_name] = card_instance
            elif card_pack_str == '[10001] Legends Rise':
                databases["LEGENDS_RISE_CARD_DATABASE"][card_en_name] = card_instance
            elif card_pack_str == '[90000] Basic A':  # 토큰 카드
                databases["TOKEN_CARD_DATABASE"][card_en_name] = card_instance

        except (ValueError, KeyError) as e:
            print(f"카드 '{card_en_name}' 처리 중 에러 발생: {e}")
            continue

    # --- .py 파일 생성 ---
    with open(output_py_path, 'w', encoding='utf-8') as f:
        # 파일 상단에 필요한 import 구문 작성
        f.write("from enums import CardType, ClassType, EffectType, ProcessType, TargetType, TribeType\n")
        f.write("from card_data import CardData  # CardData 클래스가 정의된 파일을 import해야 합니다.\n\n")

        # 각 데이터베이스를 파일에 작성
        for db_name, db_content in databases.items():
            f.write(f"{db_name} = {{\n")
            for card_name, card_obj in db_content.items():
                f.write(f'    "{card_name}": {repr(card_obj)},\n')
            f.write("}\n\n")

    print(f"데이터 변환 완료! 결과가 '{output_py_path}' 파일에 저장되었습니다.")
    for db_name, db_content in databases.items():
        print(f"- {db_name}: {len(db_content)}개 카드")


if __name__ == "__main__":
    convert_json_to_class_script(
        json_file_path="card_database.json",
        output_py_path="formatted_database.py"
    )