import json
from typing import List, Any, Dict
from enums import CardType, EffectType, TargetType, ProcessType, ClassType, TribeType, EventType
from effect import Effect

# 전역 변수
BASIC_CARD_DATABASE: Dict[str, 'CardData'] = {}
LEGENDS_RISE_CARD_DATABASE: Dict[str, 'CardData'] = {}
TOKEN_CARD_DATABASE: Dict[str, 'CardData'] = {}


class CardData:
    """카드의 정적 데이터를 정의합니다."""
    def __init__(self, card_id: str, name: str, cost: int, card_type: CardType, class_type: ClassType, attack: int = 0, defense: int = 0, tribes: List = None, effects: List[Effect] = None, raw_effects_text: str = "", required_listeners: List[EventType] = None):
        self.card_id = card_id  # 영문명
        self.name = name  # 한글명
        self.cost = cost
        self.card_type = card_type
        self.class_type = class_type
        self.attack = attack  # 추종자 전용
        self.defense = defense  # 추종자 전용
        self.tribes = tribes if tribes is not None else []
        self.effects = effects if effects is not None else []  # Effect 인스턴스 리스트
        self.raw_effects_text = raw_effects_text
        self.required_listeners = required_listeners if required_listeners is not None else []

    def get(self, key: str, default: Any = None) -> Any:
        """객체의 속성 값을 가져옵니다."""
        return getattr(self, key, default)

    def __repr__(self):
        """CardData 객체를 대표하는 문자열을 반환합니다."""
        effects_repr = repr(self.effects)
        tribe = self.tribes[0] if self.tribes and len(self.tribes) > 0 else None
        tribe_str = str(tribe) if tribe else ""

        return (f'CardData("{self.card_id}", "{self.name}", {self.cost}, CardType.{self.card_type.name}, '
                f'ClassType.{self.class_type.name}, {self.attack}, {self.defense}, tribes=[{tribe_str}], effects={effects_repr}), raw_effects_text={self.raw_effects_text}')

    def __getitem__(self, key: str) -> Any:
        """키를 사용하여 객체의 속성에 접근할 수 있게 합니다."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"CardData에 '{key}' 속성이 없습니다.")


def _load_effect_from_dict(effect_dict: Dict[str, Any]) -> Effect:
    """딕셔너리에서 Effect 객체를 로드합니다."""
    attrs = effect_dict
    # Enum 값은 문자열로 저장되어 있으므로 변환
    if "type" in effect_dict and effect_dict["type"] is not None:
        attrs["type"] = EffectType[effect_dict["type"]]
    if "target" in effect_dict and effect_dict["target"] is not None:
        attrs["target"] = TargetType[effect_dict["target"]]
    if "process" in effect_dict and effect_dict["process"] is not None:
        attrs["process"] = ProcessType[effect_dict["process"]]

    # effect 인스턴스 처리
    for key, value in effect_dict.items():
        if isinstance(value, dict):
            attrs[key] = _load_effect_from_dict(value)

    # REMOVE_KEYWORD와 TRIGGER_EFFECT의 EffectType enum value 처리
    if "process" in effect_dict and (attrs["process"] in [ProcessType.REMOVE_KEYWORD, ProcessType.TRIGGER_EFFECT]) and isinstance(effect_dict["value"], str):
        try:
            attrs["value"] = EffectType[effect_dict["value"]]
        except KeyError:
            print(f"[WARNING] EffectType '{value}' not found for {process_type.name} effect.")
            pass # Keep as string if not found, will cause error later if not handled

    # condition 처리
    condition = effect_dict.get("condition")
    if condition and isinstance(condition, str):
        if condition.startswith("CARD_TYPE_"):
            card_type_str = condition.replace("CARD_TYPE_", "")
            try:
                condition = lambda x: x.get_type() == CardType[card_type_str]
            except KeyError:
                print(f"[WARNING] CardType '{card_type_str}' not found for condition.")
                condition = None
        elif condition.startswith("CLASS_TYPE_"):
            class_type_str = condition.replace("CLASS_TYPE_", "")
            try:
                condition = lambda x: x.card_data['class_type'] == ClassType[class_type_str]
            except KeyError:
                print(f"[WARNING] ClassType '{class_type_str}' not found for condition.")
                condition = None
        elif condition.startswith("NAME_"):
            name_str = condition.replace("NAME_", "")
            try:
                condition = lambda x: x.card_data['name'] == name_str
            except KeyError:
                print(f"[WARNING] Name '{name_str}' not found for condition.")
                condition = None
        attrs["condition"] = condition

    return Effect(**attrs)


def _load_card_data_from_dict(card_dict: Dict[str, Any]) -> CardData:
    """딕셔너리에서 CardData 객체를 로드합니다."""
    effects = []
    for e_dict in card_dict.get("effects", []):
        if "raw_effect_text" in e_dict:
            # Raw text effects are stored as dictionaries with 'raw_effect_text' key
            effects.append(e_dict) # Keep as dict for now
        else:
            effects.append(_load_effect_from_dict(e_dict))

    required_listeners_from_json = card_dict.get("required_listeners", [])
    
    effect_to_event_map = {
        EffectType.FANFARE: EventType.CARD_PLAYED,
        EffectType.SPELL: EventType.CARD_PLAYED,
        EffectType.ENHANCE: EventType.CARD_PLAYED,
        EffectType.LAST_WORDS: EventType.DESTROYED_ON_FIELD,
        EffectType.STRIKE: EventType.ATTACK_DECLARED,
        EffectType.CLASH: EventType.COMBAT_INITIATED,
        EffectType.ON_EVOLVE: EventType.FOLLOWER_EVOLVED,
        EffectType.EVOLVED: EventType.FOLLOWER_EVOLVED,
        EffectType.ACTIVATE: EventType.AMULET_ACTIVATED,
        EffectType.ON_FOLLOWER_ENTER_FIELD: EventType.FOLLOWER_ENTER_FIELD,
        EffectType.ON_SUPER_EVOLVE: EventType.FOLLOWER_SUPER_EVOLVED,
        EffectType.SUPER_EVOLVED: EventType.FOLLOWER_SUPER_EVOLVED,
        EffectType.COUNTDOWN: EventType.TURN_START,
        EffectType.ON_MY_TURN_END: EventType.TURN_END,
        EffectType.ON_OPPONENTS_TURN_END: EventType.TURN_END,
        EffectType.DRAIN: EventType.DAMAGE_DEALT_BY_COMBAT,
    }
    
    listeners = set()
    for effect in effects:
        if isinstance(effect, Effect):
            if effect.type in effect_to_event_map:
                event_type = effect_to_event_map[effect.type]
                if event_type.name in required_listeners_from_json:
                    listeners.add((event_type, effect))
            
            if effect.type in [EffectType.ON_EVOLVE, EffectType.EVOLVED, EffectType.ON_SUPER_EVOLVE, EffectType.SUPER_EVOLVED]:
                if EventType.FOLLOWER_SUPER_EVOLVED.name in required_listeners_from_json:
                    listeners.add((EventType.FOLLOWER_SUPER_EVOLVED, effect))

    card_data_obj = CardData(
        card_id=card_dict["card_id"],
        name=card_dict["name"],
        cost=card_dict["cost"],
        card_type=CardType[card_dict["card_type"]],
        class_type=ClassType[card_dict["class_type"]],
        attack=card_dict.get("attack", 0),
        defense=card_dict.get("defense", 0),
        tribes=[TribeType[t] for t in card_dict.get("tribes", [])],
        effects=effects,
        required_listeners=list(listeners)
    )
    
    return card_data_obj


def resolve_card_references(card_db: Dict[str, CardData], global_card_db: Dict[str, CardData]):
    """카드 데이터베이스 내의 카드 참조를 해결합니다."""
    for card_id, card_data_obj in card_db.items():
        for effect in card_data_obj.effects:
            if isinstance(effect, Effect):
                # 카드 인스턴스를 생성하는 이펙트 체크
                if "process" in effect.attributes.keys() and effect.process in [ProcessType.ADD_CARD_TO_HAND, ProcessType.SUMMON, ProcessType.REPLACE_DECK]:
                    # 단일 카드 생성
                    if isinstance(effect.value, str):
                        if effect.value in global_card_db:
                            effect.value = global_card_db[effect.value]
                        else:
                            print(f"[WARNING] 카드 {card_id}의 프로세스 {effect.process.name}에서 카드 데이터 '{effect.value}'을(를) 찾을 수 없습니다.")

                    # 복수 카드 생성
                    elif isinstance(effect.value, list):
                        resolved_list = []
                        for item in effect.value:
                            if isinstance(item, str) and item in global_card_db:
                                resolved_list.append(global_card_db[item])
                            else:
                                print(f"[WARNING] 카드 {card_id}의 프로세스 {effect.process.name}에서 아이템 '{item}'을(를) 찾을 수 없습니다.")
                                resolved_list.append(item)
                        effect.value = resolved_list

                # 나머지 이펙트에 카드 이름이 입력된 경우 체크
                elif "value" in effect.attributes.keys() and isinstance(effect.value, str):
                    print(f"[WARNING] 카드 {card_id}의 프로세스 {effect.process.name})에 예기치 않은 스트링 입력 '{effect.value}'.")


def load_card_databases(json_path: str = 'card_database/parsed_database/card_database_parsed.json'):
    """JSON 파일에서 모든 카드 데이터베이스를 로드합니다."""
    global BASIC_CARD_DATABASE, LEGENDS_RISE_CARD_DATABASE, TOKEN_CARD_DATABASE
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1차 로딩: 모든 CardData 객체 생성 (참조는 아직 해결하지 않음)
    for db_name, db_data in data.items():
        if db_name == "BASIC_CARD_DATABASE":
            for card_id, card_dict in db_data.items():
                BASIC_CARD_DATABASE[card_id] = _load_card_data_from_dict(card_dict)
        elif db_name == "LEGENDS_RISE_CARD_DATABASE":
            for card_id, card_dict in db_data.items():
                LEGENDS_RISE_CARD_DATABASE[card_id] = _load_card_data_from_dict(card_dict)
        elif db_name == "TOKEN_CARD_DATABASE":
            for card_id, card_dict in db_data.items():
                TOKEN_CARD_DATABASE[card_id] = _load_card_data_from_dict(card_dict)

    # 2차 로딩: 카드 참조 해결
    all_cards = {**BASIC_CARD_DATABASE, **LEGENDS_RISE_CARD_DATABASE, **TOKEN_CARD_DATABASE}
    resolve_card_references(BASIC_CARD_DATABASE, all_cards)
    resolve_card_references(LEGENDS_RISE_CARD_DATABASE, all_cards)
    resolve_card_references(TOKEN_CARD_DATABASE, all_cards)


# load_card_databases()
