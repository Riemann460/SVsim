import json
import os
import glob
from typing import List, Any, Dict
from src.common.enums import CardType, EffectType, TargetType, ProcessType, ClassType, TribeType, EventType
from src.common.effect import Effect

KOR_NAME_MAP = {}

def load_kor_names(kor_db_dir: str = 'card_database/2_kor_database'):
    """한글 카드명 매핑 데이터를 불러옵니다."""
    global KOR_NAME_MAP
    if not os.path.exists(kor_db_dir):
        kor_db_dir = os.path.join('..', kor_db_dir)
        if not os.path.exists(kor_db_dir):
            return
    for file_path in glob.glob(os.path.join(kor_db_dir, '*.json')):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.values():
                    en_name = item.get('카드 이름')
                    ko_name = item.get('카드 이름 (한글)')
                    if en_name and ko_name:
                        KOR_NAME_MAP[en_name] = ko_name
        except Exception as e:
            print(f"[WARNING] Failed to load kor names from {file_path} {e}")

class CardDatabase(dict):
    """card_id와 name 모두로 검색이 가능한 데이터베이스 클래스입니다."""
    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        for card_data_obj in self.values():
            if card_data_obj.name == key:
                return card_data_obj
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

# 전역 변수
BASIC_CARD_DATABASE = CardDatabase()
LEGENDS_RISE_CARD_DATABASE = CardDatabase()
TOKEN_CARD_DATABASE = CardDatabase()

class CardData:
    """카드의 정적 데이터를 정의합니다."""
    def __init__(self, card_id: str, name: str, cost: int,
                 card_type: CardType, class_type: ClassType,
                 attack: int = 0, defense: int = 0,
                 tribes: List = None, effects: List[Effect] = None,
                 raw_effects_text: str = "", required_listeners: List[EventType] = None,
                 fuse_condition: str = None, name_ko: str = None):
        self.card_id = card_id
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.class_type = class_type
        self.attack = attack
        self.defense = defense
        self.tribes = tribes if tribes is not None else []
        self.effects = effects if effects is not None else []
        self.raw_effects_text = raw_effects_text
        self.required_listeners = required_listeners if required_listeners is not None else []
        self.fuse_condition = fuse_condition
        self.name_ko = name_ko

    def get(self, key: str, default: Any = None) -> Any:
        """객체의 속성 값을 가져옵니다."""
        return getattr(self, key, default)

    def __repr__(self):
        effects_repr = repr(self.effects)
        tribe = self.tribes[0] if self.tribes and len(self.tribes) > 0 else None
        tribe_str = str(tribe) if tribe else ""
        return (f'CardData("{self.card_id}", "{self.name}", {self.cost}, '
                f'CardType.{self.card_type.name}, '
                f'ClassType.{self.class_type.name}, {self.attack}, {self.defense}, '
                f'tribes=[{tribe_str}], effects={effects_repr}), '
                f'raw_effects_text={self.raw_effects_text}')

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"CardData에 '{key}' 속성이 없습니다.")

def _load_effect_from_dict(effect_dict: Dict[str, Any]) -> Effect:
    """딕셔너리에서 Effect 객체를 로드합니다."""
    attrs = effect_dict
    if "type" in effect_dict and effect_dict["type"] is not None:
        try:
            attrs["type"] = EffectType[effect_dict["type"]]
        except KeyError:
            print(f"[WARNING] EffectType '{effect_dict['type']}' not recognized. Keeping as string.")
            attrs["type"] = effect_dict["type"]
    if "target" in effect_dict and effect_dict["target"] is not None:
        try:
            attrs["target"] = TargetType[effect_dict["target"]]
        except KeyError:
            print(f"[WARNING] TargetType '{effect_dict['target']}' not recognized. Keeping as string.")
            attrs["target"] = effect_dict["target"]
    if "process" in effect_dict and effect_dict["process"] is not None:
        try:
            attrs["process"] = ProcessType[effect_dict["process"]]
        except KeyError:
            print(f"[WARNING] ProcessType '{effect_dict['process']}' not recognized. Keeping as string.")
            attrs["process"] = effect_dict["process"]

    if isinstance(attrs.get("type"), str):
        original = attrs["type"]
        attrs["type"] = EffectType.FANFARE
        attrs["raw_type"] = original
    if isinstance(attrs.get("target"), str):
        original = attrs["target"]
        attrs["target"] = TargetType.SELF
        attrs["raw_target"] = original
    if isinstance(attrs.get("process"), str):
        original = attrs["process"]
        attrs["process"] = ProcessType.ADD_CARD_TO_HAND
        attrs["raw_process"] = original
    if attrs.get("target") is None:
        effect_type = attrs.get("type")
        process_type = attrs.get("process")
        if effect_type in [EffectType.ON_EVOLVE, EffectType.ON_SUPER_EVOLVE] or process_type == ProcessType.TRIGGER_EFFECT:
            attrs["target"] = TargetType.SELF
        elif process_type == ProcessType.RETURN_TO_DECK:
            attrs["target"] = TargetType.OWN_HAND_CHOICE
    for key, value in effect_dict.items():
        if isinstance(value, dict):
            attrs[key] = _load_effect_from_dict(value)
        elif isinstance(value, list) and key == "choices":
            attrs[key] = [_load_effect_from_dict(item) for item in value if isinstance(item, dict)]
    if "process" in effect_dict and (attrs["process"] in [ProcessType.REMOVE_KEYWORD, ProcessType.TRIGGER_EFFECT]) and "value" in effect_dict and isinstance(effect_dict["value"], str):
        try:
            attrs["value"] = EffectType[effect_dict["value"].upper()]
        except KeyError:
            print(f"[WARNING] EffectType '{effect_dict['value']}' not found for {attrs['process'].name} effect.")
    condition = effect_dict.get("condition")
    if condition:
        attrs["condition"] = condition
    return Effect(**attrs)

def _load_card_data_from_dict(card_dict: Dict[str, Any]) -> CardData:
    """딕셔너리에서 카드 데이터를 읽어들입니다."""
    effects = []
    for e_dict in card_dict.get("effects", []):
        if "raw_effect_text" in e_dict:
            effects.append(e_dict)
        else:
            effects.append(_load_effect_from_dict(e_dict))
    fuse_condition = card_dict.get("fuse_condition", None)
    if not fuse_condition:
        for e_dict in card_dict.get("effects", []):
            for k in ["raw_effect_text", "raw_action_text"]:
                text = e_dict.get(k, "")
                if text.startswith("Fuse:"):
                    fuse_condition = text.replace("Fuse:", "").strip()
                    break
            if fuse_condition:
                break
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
        EffectType.ENGAGE: EventType.CARD_ENGAGED,
        EffectType.ON_FOLLOWER_ENTER_FIELD: EventType.FOLLOWER_ENTER_FIELD,
        EffectType.ON_SUPER_EVOLVE: EventType.FOLLOWER_SUPER_EVOLVED,
        EffectType.SUPER_EVOLVED: EventType.FOLLOWER_SUPER_EVOLVED,
        EffectType.COUNTDOWN: EventType.TURN_START,
        EffectType.ON_MY_TURN_END: EventType.TURN_END,
        EffectType.ON_OPPONENTS_TURN_END: EventType.TURN_END,
        EffectType.DRAIN: EventType.DAMAGE_DEALT_BY_COMBAT,
    }
    listeners = []
    for effect in effects:
        if isinstance(effect, Effect):
            if effect.type in effect_to_event_map:
                event_type = effect_to_event_map[effect.type]
                if event_type.name in required_listeners_from_json:
                    if (event_type, effect) not in listeners:
                        listeners.append((event_type, effect))
            if effect.type in [EffectType.ON_EVOLVE, EffectType.EVOLVED, EffectType.ON_SUPER_EVOLVE, EffectType.SUPER_EVOLVED]:
                if EventType.FOLLOWER_SUPER_EVOLVED.name in required_listeners_from_json:
                    if (EventType.FOLLOWER_SUPER_EVOLVED, effect) not in listeners:
                        listeners.append((EventType.FOLLOWER_SUPER_EVOLVED, effect))
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
        required_listeners=list(listeners),
        fuse_condition=fuse_condition,
        name_ko=KOR_NAME_MAP.get(card_dict["name"], card_dict["name"])
    )
    return card_data_obj

def resolve_card_references(card_db: Dict[str, CardData], global_card_db: Dict[str, CardData]):
    """카드 데이터베이스 내의 카드 참조를 해결합니다."""
    for card_id, card_data_obj in card_db.items():
        for effect in card_data_obj.effects:
            if isinstance(effect, Effect):
                if "process" in effect.attributes.keys() and effect.process in [ProcessType.ADD_CARD_TO_HAND, ProcessType.SUMMON, ProcessType.REPLACE_DECK]:
                    effect_value = getattr(effect, "value", None)
                    if isinstance(effect_value, str):
                        if effect_value in global_card_db:
                            effect.value = global_card_db[effect_value]
                        else:
                            print(f"[WARNING] 카드 {card_id}의 프로세스 {effect.process.name}에서 카드 데이터 '{effect_value}'을(를) 찾을 수 없습니다.")
                    elif isinstance(effect_value, list):
                        resolved_list = []
                        for item in effect_value:
                            if isinstance(item, str) and item in global_card_db:
                                resolved_list.append(global_card_db[item])
                            else:
                                print(f"[WARNING] 카드 {card_id}의 프로세스 {effect.process.name}에서 아이템 '{item}'을(를) 찾을 수 없습니다.")
                                resolved_list.append(item)
                        effect.value = resolved_list
                elif "value" in effect.attributes.keys() and isinstance(effect.value, str):
                    process_name = effect.process.name if getattr(effect, 'process', None) else 'None'
                    print(f"[WARNING] 카드 {card_id}의 프로세스 {process_name})에 예기치 않은 스트링 입력 '{effect.value}'.")

def load_card_databases(path: str = 'card_database/4_manual_database/card_database_manual.json'):
    """Loads card databases from a single merged manual JSON file.
    The JSON contains top‑level keys for each database (e.g. \"BASIC_CARD_DATABASE\",
    \"LEGENDS_RISE_CARD_DATABASE\", \"TOKEN_CARD_DATABASE\").
    All cards are loaded into the corresponding global databases."""
    global BASIC_CARD_DATABASE, LEGENDS_RISE_CARD_DATABASE, TOKEN_CARD_DATABASE
    load_kor_names()
    import os, json
    if not os.path.isfile(path):
        print(f"[WARNING] {path} not found. No card data loaded.")
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    section_map = {
        'BASIC_CARD_DATABASE': BASIC_CARD_DATABASE,
        'LEGENDS_RISE_CARD_DATABASE': LEGENDS_RISE_CARD_DATABASE,
        'TOKEN_CARD_DATABASE': TOKEN_CARD_DATABASE,
    }
    for section_name, card_dict in data.items():
        target_db = section_map.get(section_name)
        if target_db is None:
            print(f"[WARNING] Unknown section '{section_name}' in {path}. Skipping.")
            continue
        for card_id, card_info in card_dict.items():
            target_db[card_id] = _load_card_data_from_dict(card_info)
    resolve_all_card_references()

def resolve_all_card_references():
    """Resolve cross‑card references for all loaded card databases.
    This builds a combined view of all cards and invokes `resolve_card_references`
    for each top‑level database."""
    all_cards = {**BASIC_CARD_DATABASE, **LEGENDS_RISE_CARD_DATABASE, **TOKEN_CARD_DATABASE}
    resolve_card_references(BASIC_CARD_DATABASE, all_cards)
    resolve_card_references(LEGENDS_RISE_CARD_DATABASE, all_cards)
    resolve_card_references(TOKEN_CARD_DATABASE, all_cards)

def evaluate_condition(card: Any, condition_str: str) -> bool:
    """카드가 주어진 condition_str 조건을 만족하는지 검사합니다."""
    if not condition_str:
        return True
    
    if condition_str.startswith("CARD_TYPE_"):
        card_type_str = condition_str.replace("CARD_TYPE_", "")
        try:
            target_type = CardType[card_type_str]
            return card.get_type() == target_type
        except KeyError:
            return False
            
    elif condition_str.startswith("CLASS_TYPE_"):
        class_type_str = condition_str.replace("CLASS_TYPE_", "")
        try:
            target_class = ClassType[class_type_str]
            return card.card_data.class_type == target_class
        except KeyError:
            return False
            
    elif condition_str.startswith("NAME_"):
        name_str = condition_str.replace("NAME_", "")
        return card.card_data.name == name_str
        
    return True
