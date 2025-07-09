import json
from typing import List, Any, Dict
from enums import CardType, EffectType, TargetType, ProcessType, ClassType, TribeType
from effect import Effect

# 전역 변수로 선언하여 다른 함수에서 접근 가능하도록 함
BASIC_CARD_DATABASE: Dict[str, 'CardData'] = {}
LEGENDS_RISE_CARD_DATABASE: Dict[str, 'CardData'] = {}
TOKEN_CARD_DATABASE: Dict[str, 'CardData'] = {}


class CardData:
    """카드의 정적 데이터를 정의합니다."""
    def __init__(self, card_id: str, name: str, cost: int, card_type: CardType, class_type: ClassType, attack: int = 0, defense: int = 0, tribes: List = None, effects: List[Effect] = None, raw_effects_text: str = ""):
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

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __repr__(self):
        effects_repr = repr(self.effects)
        tribe = self.tribes[0] if self.tribes and len(self.tribes) > 0 else None
        tribe_str = str(tribe) if tribe else ""

        return (f'CardData("{self.card_id}", "{self.name}", {self.cost}, CardType.{self.card_type.name}, '
                f'ClassType.{self.class_type.name}, {self.attack}, {self.defense}, tribes=[{tribe_str}], effects={effects_repr}), raw_effects_text={self.raw_effects_text}')

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"CardData에 '{key}' 속성이 없습니다.")


def _load_effect_from_dict(effect_dict: Dict[str, Any]) -> Effect:
    # Enum 값은 문자열로 저장되어 있으므로 변환
    effect_type = EffectType[effect_dict["type"]]
    target_type = TargetType[effect_dict["target"]] if "target" in effect_dict and effect_dict["target"] is not None else None
    process_type = ProcessType[effect_dict["process"]] if "process" in effect_dict and effect_dict["process"] is not None else None
    value = effect_dict.get("value")
    enhance_cost = effect_dict.get("enhance_cost")
    cost = effect_dict.get("cost")

    # Handle nested Effect for ADD_KEYWORD
    if process_type == ProcessType.ADD_KEYWORD and isinstance(value, dict) and "type" in value:
        value = _load_effect_from_dict(value)
    # Handle EffectType for REMOVE_KEYWORD and TRIGGER_EFFECT
    elif (process_type == ProcessType.REMOVE_KEYWORD or process_type == ProcessType.TRIGGER_EFFECT) and isinstance(value, str):
        try:
            value = EffectType[value]
        except KeyError:
            print(f"[WARNING] EffectType '{value}' not found for {process_type.name} effect.")
            pass # Keep as string if not found, will cause error later if not handled

    # condition handling (assuming condition is a string for now)
    condition = effect_dict.get("condition")
    if condition and isinstance(condition, str) and condition.startswith("CARD_TYPE_"):
        # Example: "CARD_TYPE_FOLLOWER" -> lambda x: x.card_type == CardType.FOLLOWER
        card_type_str = condition.replace("CARD_TYPE_", "")
        try:
            condition = lambda x: x.card_type == CardType[card_type_str]
        except KeyError:
            print(f"[WARNING] CardType '{card_type_str}' not found for condition.")
            condition = None
    elif condition and isinstance(condition, str) and condition.startswith("NECROMANCY_"):
        # Example: "NECROMANCY_4"
        pass # Keep as string, will be handled by rule engine
    elif condition and isinstance(condition, str) and condition == "OVERFLOW":
        pass # Keep as string, will be handled by rule engine

    # trigger handling (assuming trigger is a string for now)
    trigger = effect_dict.get("trigger")
    if trigger and isinstance(trigger, str) and trigger.startswith("ALLY_") and trigger.endswith("_ENTERS_FIELD"):
        pass # Keep as string, will be handled by event manager
    elif trigger and isinstance(trigger, str) and trigger == "ENGAGE_AMULET":
        pass # Keep as string, will be handled by event manager
    elif trigger and isinstance(trigger, str) and trigger == "DISCARDED":
        pass # Keep as string, will be handled by event manager

    return Effect(type=effect_type, target=target_type, process=process_type, value=value, condition=condition, enhance_cost=enhance_cost, cost=cost, trigger=trigger)


def _load_card_data_from_dict(card_dict: Dict[str, Any]) -> CardData:
    effects = []
    for e_dict in card_dict.get("effects", []):
        if "raw_effect_text" in e_dict:
            # Raw text effects are stored as dictionaries with 'raw_effect_text' key
            effects.append(e_dict) # Keep as dict for now
        else:
            effects.append(_load_effect_from_dict(e_dict))

    return CardData(
        card_id=card_dict["card_id"],
        name=card_dict["name"],
        cost=card_dict["cost"],
        card_type=CardType[card_dict["card_type"]],
        class_type=ClassType[card_dict["class_type"]],
        attack=card_dict.get("attack", 0),
        defense=card_dict.get("defense", 0),
        tribes=[TribeType[t] for t in card_dict.get("tribes", [])],
        effects=effects
    )


def resolve_card_references(card_db: Dict[str, CardData], global_card_db: Dict[str, CardData]):
    for card_id, card_data_obj in card_db.items():
        for effect in card_data_obj.effects:
            # Check if it's a structured Effect object or a raw text dict
            if isinstance(effect, Effect):
                # Only resolve card references for specific process types
                if effect.process in [ProcessType.ADD_CARD_TO_HAND, ProcessType.SUMMON, ProcessType.REPLACE_DECK]:
                    if isinstance(effect.value, str): # value is a single card ID string
                        if effect.value == "Apocalypse Deck": # Special case for Apocalypse Deck
                            # This needs to be handled as a list of CardData objects for the Apocalypse Deck
                            # For now, keep as string, will be resolved in game logic if needed
                            pass
                        elif effect.value in global_card_db:
                            effect.value = global_card_db[effect.value]
                        else:
                            print(f"[WARNING] Card reference '{effect.value}' not found for effect in {card_id} (process: {effect.process.name})")
                    elif isinstance(effect.value, list): # value is a list of card ID strings
                        resolved_list = []
                        for item in effect.value:
                            if isinstance(item, str) and item in global_card_db:
                                resolved_list.append(global_card_db[item])
                            else:
                                # If it's not a string or not in DB, keep it as is (might be a literal or an error)
                                print(f"[WARNING] Item '{item}' in list for effect in {card_id} not a valid card reference.")
                                resolved_list.append(item)
                        effect.value = resolved_list
                # For other process types, value should not be a card reference string
                # If it's a string and not an EffectType (already handled in _load_effect_from_dict), it's likely an error in JSON
                elif isinstance(effect.value, str) and not isinstance(effect.value, EffectType):
                    print(f"[WARNING] Unexpected string value '{effect.value}' for effect in {card_id} (process: {effect.process.name}). Expected a literal or EffectType.")


def load_card_databases(json_path: str = 'card_database_parsed.json'):
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
