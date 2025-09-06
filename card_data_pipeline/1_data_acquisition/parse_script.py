import json
import re
from enum import Enum
from typing import Dict, List

from enums import EffectType, ProcessType, TargetType, CardType, EventType, ClassType
from card_data import CardData
from effect import Effect

EFFECT_TO_EVENT_MAP = {
    EffectType.FANFARE.name: EventType.CARD_PLAYED,
    EffectType.SPELL.name: EventType.CARD_PLAYED,
    EffectType.ENHANCE.name: EventType.CARD_PLAYED,
    EffectType.LAST_WORDS.name: EventType.DESTROYED_ON_FIELD,
    EffectType.STRIKE.name: EventType.ATTACK_DECLARED,
    EffectType.CLASH.name: EventType.COMBAT_INITIATED,
    EffectType.ON_EVOLVE.name: EventType.FOLLOWER_EVOLVED,
    EffectType.EVOLVED.name: EventType.FOLLOWER_EVOLVED,
    EffectType.ACTIVATE.name: EventType.AMULET_ACTIVATED,
    EffectType.ON_FOLLOWER_ENTER_FIELD.name: EventType.FOLLOWER_ENTER_FIELD,
    EffectType.ON_SUPER_EVOLVE.name: EventType.FOLLOWER_SUPER_EVOLVED,
    EffectType.SUPER_EVOLVED.name: EventType.FOLLOWER_SUPER_EVOLVED,
    EffectType.COUNTDOWN.name: EventType.TURN_START,
    EffectType.ON_MY_TURN_END.name: EventType.TURN_END,
    EffectType.ON_OPPONENTS_TURN_END.name: EventType.TURN_END,
    EffectType.DRAIN.name: EventType.DAMAGE_DEALT_BY_COMBAT,
}

def parse_effect_text(description: str, card_type_enum):
    if not description:
        return []

    lines = [line.strip() for line in description.strip().split('\n') if line.strip()]
    parsed_effects = []
    if card_type_enum == "SPELL":
        for line in lines:
            effect_attrs = parse_action(line)
            effect = Effect(**effect_attrs)
            effect.update(type=EffectType.SPELL)
            parsed_effects.append(effect)
        return parsed_effects

    for line in lines:
        parsed_effects.append(_parse_single_effect(line))
    return parsed_effects


# 패턴과 해당 효과를 매핑하는 데이터 구조
EFFECT_PATTERNS = [
    {'regex': r"Enhance \((\d+)\): (.*)", 'type': EffectType.ENHANCE, 'groups': ['enhance_cost', 'action_text']},
    {'regex': r"Evolve: (.*)", 'type': EffectType.ON_EVOLVE, 'groups': ['action_text']},
    {'regex': r"Super-Evolve: (.*)", 'type': EffectType.ON_SUPER_EVOLVE, 'groups': ['action_text']},
    {'regex': r"Fanfare: (.*)", 'type': EffectType.FANFARE, 'groups': ['action_text']},
    {'regex': r"Engage: (.*)", 'type': EffectType.ACTIVATE, 'groups': ['action_text']},
    {'regex': r"Engage \((\d+)\): (.*)", 'type': EffectType.ACTIVATE, 'groups': ['cost', 'action_text']},
    {'regex': r"Last Words: (.*)", 'type': EffectType.LAST_WORDS, 'groups': ['action_text']},
    {'regex': r"At the end of your turn, (.*)", 'type': EffectType.ON_MY_TURN_END, 'groups': ['action_text']},
    {'regex': r"At the end of your opponent's turn, (.*)", 'type': EffectType.ON_OPPONENTS_TURN_END, 'groups': ['action_text']},
    {'regex': r"When this follower evolves, (.*)", 'type': EffectType.EVOLVED, 'groups': ['action_text']},
    {'regex': r"On Spellboost: (.*)", 'type': EffectType.SPELLBOOST, 'groups': ['action_text']},
    {'regex': r"Countdown \((\d+)\)", 'type': EffectType.COUNTDOWN, 'groups': ['value']},
]

SIMPLE_KEYWORD_EFFECTS = {
    "Ward": EffectType.WARD, "Storm": EffectType.STORM, "Rush": EffectType.RUSH,
    "Bane": EffectType.BANE, "Drain": EffectType.DRAIN, "Barrier": EffectType.BARRIER,
    "Ambush": EffectType.AMBUSH, "Intimidate": EffectType.INTIMIDATE, "Aura": EffectType.AURA
}


def _parse_single_effect(text: str):
    """
    효과 텍스트 한 줄을 파싱하여 Effect 객체로 변환합니다.
    - 단순 키워드 효과를 먼저 확인합니다.
    - 정규식 패턴 목록을 순회하며 복잡한 효과를 파싱합니다.
    """
    # 1. 단순 키워드 효과 처리
    if text in SIMPLE_KEYWORD_EFFECTS:
        return Effect(type=SIMPLE_KEYWORD_EFFECTS[text])

    # 2. 데이터 기반으로 복잡한 효과 패턴 처리
    for pattern in EFFECT_PATTERNS:
        match = re.match(pattern['regex'], text)
        if match:
            # 정규식 그룹과 그룹 이름을 매핑하여 딕셔너리 생성
            extracted_data = dict(zip(pattern['groups'], match.groups()))

            # 숫자 값은 정수형으로 변환 시도
            for key, value in extracted_data.items():
                if key != 'action_text':
                    try:
                        extracted_data[key] = int(value)
                    except ValueError:
                        pass  # 변환 실패 시 문자열 유지

            # 파싱할 액션 텍스트가 있으면 parse_action 호출
            if 'action_text' in extracted_data:
                action_attrs = parse_action(extracted_data.pop('action_text'))
                extracted_data.update(action_attrs)

            # 최종 Effect 객체 생성
            effect = Effect(**extracted_data)
            effect.update(type=pattern['type'])
            return effect

    # 3. 어떤 패턴에도 해당하지 않으면 원본 텍스트를 그대로 반환
    return Effect(raw_effect_text=text)


# 대상 파싱을 위한 패턴 목록
TARGET_PATTERNS = [
    {'regex': r"this follower", 'target': TargetType.SELF},
    {'regex': r"your leader", 'target': TargetType.OWN_LEADER},
    {'regex': r"the enemy leader", 'target': TargetType.OPPONENT_LEADER},
    {'regex': r"all enemy followers", 'target': TargetType.ALL_OPPONENT_FOLLOWERS},
    {'regex': r"a random enemy follower", 'target': TargetType.OPPONENT_FOLLOWER_RANDOM},
    {'regex': r"Select an enemy follower on the field", 'target': TargetType.OPPONENT_FOLLOWER_CHOICE},
    {'regex': r"Select another allied follower on the field", 'target': TargetType.ANOTHER_ALLY_FOLLOWER_CHOICE},
    {'regex': r"Select an allied follower on the field", 'target': TargetType.ALLY_FOLLOWER_CHOICE},
    {'regex': r"all other allied followers on the field", 'target': TargetType.ALL_OTHER_ALLY_FOLLOWERS},
]

# 액션 파싱을 위한 패턴 목록
ACTION_PATTERNS = [
    # 대상 지정 + 단일 행동 (구체적인 패턴을 먼저 확인)
    {'regex': r"Select an enemy follower on the field and destroy it", 'process': ProcessType.DESTROY, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},
    {'regex': r"Select an enemy follower on the field and banish it", 'process': ProcessType.BANISH, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},
    {'regex': r"Select an enemy follower on the field and return it to hand", 'process': ProcessType.RETURN_TO_HAND, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},
    {'regex': r"Select an enemy follower on the field and set its defense to (\d+)", 'process': ProcessType.SET_DEFENSE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': ['value']},
    {'regex': r"Select an enemy follower on the field and give it -0\/-(\d+)", 'process': ProcessType.STAT_BUFF, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': ['value'], 'special_handling': 'neg_def_buff'},

    # 소환
    {'regex': r"Summon (\d+) copies of (.*)", 'process': ProcessType.SUMMON, 'groups': ['value', 'card_name'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Summon (.*)", 'process': ProcessType.SUMMON, 'groups': ['card_names'], 'target': TargetType.OWN_LEADER},
    # 패로 가져오기
    {'regex': r"Add (\d+) copies of (.*) to your hand", 'process': ProcessType.ADD_CARD_TO_HAND, 'groups': ['value', 'card_name'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Add (.*) to your hand", 'process': ProcessType.ADD_CARD_TO_HAND, 'groups': ['card_names'], 'target': TargetType.OWN_LEADER},
    # 스탯 버프
    {'regex': r"Give (.*) \+(\d+)\/\+(\d+)", 'process': ProcessType.STAT_BUFF, 'groups': ['target_text', 'value', 'value2']},
    {'regex': r"(.*) and give it \+(\d+)\/\+(\d+)", 'process': ProcessType.STAT_BUFF, 'groups': ['target_text', 'value', 'value2']},
    # 데미지
    {'regex': r"Deal (\d+) damage to (.*)", 'process': ProcessType.DEAL_DAMAGE, 'groups': ['value', 'target_text']},
    {'regex': r"(.*) and deal it (\d+) damage", 'process': ProcessType.DEAL_DAMAGE, 'groups': ['target_text', 'value']},
    # 파괴 (일반)
    {'regex': r"(.*) and destroy it", 'process': ProcessType.DESTROY, 'groups': ['target_text']},
    # 드로우
    {'regex': r"Draw (\d+) cards", 'process': ProcessType.DRAW, 'groups': ['value'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Draw a card", 'process': ProcessType.DRAW, 'groups': [], 'value': 1, 'target': TargetType.OWN_LEADER},
    # 회복
    {'regex': r"Restore (\d+) defense (.*)", 'process': ProcessType.HEAL, 'groups': ['value', 'target_text']},
    # 효과 발동
    {'regex': r"Replicate the effects of this card's Fanfare ability", 'process': ProcessType.TRIGGER_EFFECT, 'groups': [], 'value': EffectType.FANFARE},
]


def parse_target(text: str) -> Dict:
    """
    대상 텍스트를 파싱하여 대상 정보를 담은 딕셔너리를 반환합니다.
    """
    for pattern in TARGET_PATTERNS:
        if re.search(pattern['regex'], text):
            return {'target': pattern['target']}
    return {'raw_target_text': text}


def parse_action(text: str):
    """
    액션 텍스트를 파싱하여 액션 정보를 담은 딕셔너리를 반환합니다.
    """
    for pattern in ACTION_PATTERNS:
        match = re.search(pattern['regex'], text)
        if match:
            action = {'process': pattern['process']}
            groups = dict(zip(pattern.get('groups', []), match.groups()))

            # target_text가 있으면 parse_target 호출
            if 'target_text' in groups:
                action.update(parse_target(groups['target_text']))

            # value, value2 처리
            if 'value' in groups:
                try:
                    action['value'] = int(groups['value'])
                except ValueError:
                    action['value'] = groups['value'] # 숫자 변환 실패 시 문자열
            if 'value2' in groups:
                action['value'] = (action.get('value', 0), int(groups['value2']))

            # 고정 value, target 처리
            if 'value' in pattern:
                action['value'] = pattern['value']
            if 'target' in pattern:
                action['target'] = pattern['target']

            # 특수 핸들링 로직
            if pattern.get('special_handling') == 'neg_def_buff':
                action['value'] = (0, -int(groups['value']))

            # 카드 이름 처리 (단일/복수)
            if 'card_name' in groups:
                count = int(groups.get('value', 1))
                card_name = groups['card_name'].strip().replace('.', '')
                action['value'] = [card_name] * count
            elif 'card_names' in groups:
                card_list_str = groups['card_names']
                cards = re.split(r'\s+and\s+|\s*,\s*an?\s*|\s*,\s*', card_list_str)
                card_names = [re.sub(r'^an?\s+', '', card).strip().replace('.', '') for card in cards if card.strip()]
                if card_names:
                    action['value'] = card_names[0] if len(card_names) == 1 else card_names

            return action

    return {'raw_action_text': text}

def get_required_listeners(effects: List[Effect]) -> List:
    """효과 목록을 기반으로 필요한 이벤트 리스너 목록을 결정합니다."""
    listeners = set()
    for effect in effects:
        if 'type' not in effect.keys():
            continue
        if effect['type'] in EFFECT_TO_EVENT_MAP:
            listeners.add(EFFECT_TO_EVENT_MAP[effect['type']].name)
        # super_evolved 리스너는 진화 관련 효과가 있을 때도 등록
        if effect['type'] in [EffectType.ON_EVOLVE.name, EffectType.EVOLVED.name]:
            listeners.add(EventType.FOLLOWER_SUPER_EVOLVED.name)

    return list(listeners)

def parse_card_data(raw_data: Dict) -> CardData:
    card_id = raw_data.get("card_name_id")
    name = raw_data.get("card_name")
    cost = raw_data.get("cost")
    card_type_str = raw_data.get("card_type")
    class_type_str = raw_data.get("class")
    attack = raw_data.get("atk")
    defense = raw_data.get("life")
    tribes = raw_data.get("tribe_name")
    description = raw_data.get("description")

    card_type = CardType[card_type_str.upper()] if card_type_str else None
    class_type = None
    if class_type_str:
        try:
            class_type = getattr(ClassType, class_type_str.upper())
        except AttributeError:
            class_type = ClassType.NEUTRAL

    effects = parse_effect_text(description)

    return CardData(
        card_id=card_id,
        name=name,
        cost=cost,
        card_type=card_type,
        class_type=class_type,
        attack=attack,
        defense=defense,
        tribes=tribes.split('/') if tribes else [],
        effects=effects,
        raw_effects_text=description
    )
