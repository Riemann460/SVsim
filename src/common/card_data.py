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
    def __contains__(self, key):
        if super().__contains__(key):
            return True
        for card_data_obj in self.values():
            if card_data_obj.name == key:
                return True
        return False

    def __getitem__(self, key):
        if super().__contains__(key):
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
    if "type" not in attrs:
        attrs["type"] = None
    if "value" not in attrs:
        attrs["value"] = None
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
        if e_dict.get("process") == "ADD_EFFECT" and ("value" not in e_dict or e_dict.get("value") is None or e_dict.get("value") == ""):
            continue
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
        EffectType.COMBO: EventType.CARD_PLAYED,
        EffectType.SKYBOUND_ART: EventType.CARD_PLAYED,
        EffectType.SUPER_SKYBOUND_ART: EventType.CARD_PLAYED,
        EffectType.OVERFLOW: EventType.CARD_PLAYED,
        EffectType.RALLY: EventType.CARD_PLAYED,
        EffectType.SPELLBOOST: EventType.CARD_PLAYED,
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
        EffectType.ON_LEAVE_FIELD: EventType.LEAVE_FIELD,
        EffectType.ON_DISCARD: EventType.CARD_DISCARDED,
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
        raw_effects_text=card_dict.get("raw_effects_text", ""),
        required_listeners=list(listeners),
        fuse_condition=fuse_condition,
        name_ko=KOR_NAME_MAP.get(card_dict["name"], card_dict["name"])
    )
    return card_data_obj

def _is_safe_runtime_directive(val: str) -> bool:
    """런타임에 해석해야 하는 안전한 지시어인지 검사합니다."""
    directives = [
        "instead", "copy", "copies", "it", "them", "this", "each", "remove", 
        "give the exact copy", "destroy this card", "your opponent",
        "leftmost", "random", "cost of", "returned", "banished", "allied",
        "to your hand", "add a", "set its cost"
    ]
    val_lower = val.lower()
    return any(d in val_lower for d in directives) or "+" in val or "-" in val

def _is_missing_token_card(name: str) -> bool:
    """데이터베이스에 누락되었으나 실재하는 토큰 카드명인지 검사합니다."""
    missing_tokens = {
        "Mimi", "White Psalm", "New Revelation", "Black Psalm", "Vier", "Heart Slayer", 
        "Vorlalai", "Eld Blades", "Ominous Artifact", "Steelclad Knight", "Steelclad Knight and give them Rush",
        "Fairy", "Doll Slayer", "Regal Falcon", "Skeleton", "Lazing Flame", "Lilanthim", "Anathema of Edacity",
        "Ersatz Elimination", "Imari's Little Buddies", "Striker Artifact", "Fortifier Artifact",
        "Masterwork Artifact Ω", "Rulenye & Valnareik", "Mireille & Risette", "Mordred", "Illusory Lion",
        "Arthur", "Staunch Dragon", "Zeta & Bea", "Beheading Eld Blades", "Crystalspawn", "Apocalypse Deck",
    }
    if name in missing_tokens:
        return True
    words = name.strip().split()
    if len(words) <= 4 and all(w[0].isupper() if w else False for w in words if w.lower() not in ["&", "of", "and", "the"]):
        if name == "Apocalypse Deck":
            return False
        return True
    return False

def _create_dummy_card(name: str, global_card_db: Dict[str, CardData]) -> CardData:
    """누락된 토큰 카드에 대해 임시 더미 카드 데이터를 생성합니다."""
    if name in global_card_db:
        return global_card_db[name]
    card_type = CardType.FOLLOWER
    if "Artifact" in name or name in ["Mimi", "Vier", "Heart Slayer", "Steelclad Knight", "Knight", "Fairy", "Mireille & Risette", "Mordred", "Illusory Lion", "Arthur", "Staunch Dragon", "Zeta & Bea", "Crystalspawn", "Vorlalai", "Regal Falcon", "Skeleton"]:
        card_type = CardType.FOLLOWER
    elif "Psalm" in name or "Revelation" in name or "Elimination" in name or "Blades" in name:
        card_type = CardType.SPELL
    dummy_id = f"dummy_{abs(hash(name)) % 10000000}"
    dummy = CardData(
        card_id=dummy_id,
        name=name,
        cost=1,
        card_type=card_type,
        class_type=ClassType.NEUTRAL,
        name_ko=name
    )
    global_card_db[name] = dummy
    global_card_db[dummy_id] = dummy
    return dummy

def _resolve_single_value(val: str, effect: Effect, card_id: str, global_card_db: Dict[str, CardData]) -> Any:
    """단일 문자열 값에 대한 카드 참조를 파싱하고 해결합니다."""
    for connector in [" and give them ", " and give it "]:
        if connector in val:
            parts = val.split(connector, 1)
            card_name = parts[0].strip()
            extra_effect = parts[1].strip()
            if card_name in global_card_db:
                effect.extra_effect = extra_effect
                effect.attributes["extra_effect"] = extra_effect
                return global_card_db[card_name]
            elif _is_missing_token_card(card_name):
                dummy_card = _create_dummy_card(card_name, global_card_db)
                effect.extra_effect = extra_effect
                effect.attributes["extra_effect"] = extra_effect
                return dummy_card
    if val in global_card_db:
        return global_card_db[val]
    if _is_missing_token_card(val):
        return _create_dummy_card(val, global_card_db)
    if _is_safe_runtime_directive(val):
        return val
    print(f"[WARNING] 카드 {card_id}의 프로세스 {effect.process.name}에서 카드 데이터 '{val}'을(를) 찾을 수 없습니다.")
    return val

def _resolve_effect_references_recursive(effect: Effect, card_id: str, global_card_db: Dict[str, CardData]):
    """개별 효과 및 내포된 후속 조치의 카드 참조를 재귀적으로 해결합니다."""
    if not isinstance(effect, Effect):
        return
    if "process" in effect.attributes.keys() and effect.process in [ProcessType.ADD_CARD_TO_HAND, ProcessType.SUMMON, ProcessType.REPLACE_DECK]:
        effect_value = getattr(effect, "value", None)
        if isinstance(effect_value, str):
            resolved_val = _resolve_single_value(effect_value, effect, card_id, global_card_db)
            effect.value = resolved_val
            effect.attributes["value"] = resolved_val
        elif isinstance(effect_value, list):
            resolved_list = []
            for item in effect_value:
                if isinstance(item, str):
                    resolved_list.append(_resolve_single_value(item, effect, card_id, global_card_db))
                else:
                    resolved_list.append(item)
            effect.value = resolved_list
            effect.attributes["value"] = resolved_list
    elif "value" in effect.attributes.keys():
        process_type = getattr(effect, 'process', None)
        process_name = process_type.name if process_type else 'None'
        if process_type == ProcessType.ADD_EFFECT:
            if isinstance(effect.value, str):
                try:
                    keyword_enum = EffectType[effect.value.upper()]
                    effect.value = Effect(type=keyword_enum, value=None)
                    effect.attributes["value"] = effect.value
                except KeyError:
                    print(f"[WARNING] 카드 {card_id}의 프로세스 {process_name}에 예기치 않은 스트링 입력 {effect.value}.")
            elif isinstance(effect.value, list):
                resolved_list = []
                for v in effect.value:
                    if isinstance(v, str):
                        try:
                            keyword_enum = EffectType[v.upper()]
                            resolved_list.append(Effect(type=keyword_enum, value=None))
                        except KeyError:
                            print(f"[WARNING] 카드 {card_id}의 프로세스 {process_name}에 예기치 않은 스트링 입력 {v}.")
                    else:
                        resolved_list.append(v)
                effect.value = resolved_list
                effect.attributes["value"] = resolved_list
        elif isinstance(effect.value, str):
            if effect.value in TargetType.__members__:
                effect.value = TargetType[effect.value]
                effect.attributes["value"] = effect.value
            elif "random card in your opponent's deck" in effect.value or "random cards in your opponent's deck" in effect.value:
                effect.value = TargetType.OPPONENT_DECK_RANDOM
                effect.attributes["value"] = effect.value
            elif "random followers in your deck" in effect.value:
                effect.value = TargetType.OWN_DECK_RANDOM_FOLLOWER
                effect.attributes["value"] = effect.value
            else:
                safe_string_processes = {
                    ProcessType.DEAL_DAMAGE,
                    ProcessType.DEFINE_VARIABLE,
                    ProcessType.GAIN_CREST,
                    ProcessType.TRANSFORM,
                    ProcessType.REDUCE_COST,
                    ProcessType.FUSE,
                    ProcessType.DESTROY_CREST,
                    ProcessType.RECOVER_PP,
                    ProcessType.DRAW,
                    ProcessType.DESTROY,
                    ProcessType.BANISH,
                    ProcessType.HEAL,
                    ProcessType.IMMUNITY,
                    ProcessType.DISCARD,
                    ProcessType.ADVANCE_COUNTDOWN,
                    ProcessType.REANIMATE,
                    ProcessType.SET_COST,
                    ProcessType.SET_ATTACK,
                    ProcessType.SET_DEFENSE,
                    ProcessType.SUMMON_COPY,
                }
                if process_type not in safe_string_processes:
                    print(f"[WARNING] 카드 {card_id}의 프로세스 {process_name}에 예기치 않은 스트링 입력 {effect.value}.")

    post_action = getattr(effect, "post_action", None)
    if post_action:
        _resolve_effect_references_recursive(post_action, card_id, global_card_db)

def resolve_card_references(card_db: Dict[str, CardData], global_card_db: Dict[str, CardData]):
    """카드 데이터베이스 내의 카드 참조를 해결합니다."""
    for card_id, card_data_obj in card_db.items():
        for effect in card_data_obj.effects:
            _resolve_effect_references_recursive(effect, card_id, global_card_db)

def load_card_databases(path: str = 'card_database/4_manual_database/card_database_manual.json'):
    """단일 통합 수동 JSON 파일에서 카드 데이터베이스를 불러옵니다.
    JSON은 각 데이터베이스에 대한 최상위 키를 포함합니다.
    모든 카드는 대응하는 전역 데이터베이스로 로드됩니다."""
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
    """로드된 모든 카드 데이터베이스에 대해 상호 카드 참조를 해결합니다.
    이것은 모든 카드의 결합된 뷰를 구축하고 각 최상위 데이터베이스에 대해 resolve_card_references를 호출합니다."""
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

    elif condition_str.startswith("COST_IS_"):
        try:
            cost_val = int(condition_str.replace("COST_IS_", ""))
            return card.current_cost == cost_val
        except ValueError:
            return False
        
    return True

def get_card_data_by_id(card_id: str) -> Any:
    """ID를 기반으로 정적 카드 데이터를 조회합니다."""
    for db in [BASIC_CARD_DATABASE, LEGENDS_RISE_CARD_DATABASE, TOKEN_CARD_DATABASE]:
        if card_id in db:
            return db[card_id]
    return None
