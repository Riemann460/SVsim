# 역할 정의. 카드 효과 텍스트를 파싱하여 개별 효과 및 대상을 규칙 패턴에 기반해 분석하는 핵심 파서 클래스입니다.

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
    EffectType.ENGAGE.name: EventType.CARD_ENGAGED,
    EffectType.ON_FOLLOWER_ENTER_FIELD.name: EventType.FOLLOWER_ENTER_FIELD,
    EffectType.ON_SUPER_EVOLVE.name: EventType.FOLLOWER_SUPER_EVOLVED,
    EffectType.SUPER_EVOLVED.name: EventType.FOLLOWER_SUPER_EVOLVED,
    EffectType.COUNTDOWN.name: EventType.TURN_START,
    EffectType.ON_MY_TURN_END.name: EventType.TURN_END,
    EffectType.ON_OPPONENTS_TURN_END.name: EventType.TURN_END,
    EffectType.DRAIN.name: EventType.DAMAGE_DEALT_BY_COMBAT,
    EffectType.ON_LEAVE_FIELD.name: EventType.LEAVE_FIELD,
}

def parse_effect_text(description: str, card_type_enum):
    """카드 텍스트의 줄바꿈과 HTML 요소를 정돈하고 구조화된 리스트로 변환합니다."""
    if not description:
        return []

    # 1. 원래 줄바꿈이나 태그 기준으로 문단을 분리합니다.
    # <hr>, <ev>, </ev>, \n 등을 기준으로 분리하되, 숫자(1., 2.)로 시작하는 줄은 이전 문단에 포함시킵니다.
    description_clean = description.replace("<hr>", "\n").replace("<ev>", "\n").replace("</ev>", "\n")
    raw_lines = [p.strip() for p in description_clean.split('\n') if p.strip()]
    
    paragraphs = []
    for line in raw_lines:
        if paragraphs and re.match(r"^\d\.", line):
            paragraphs[-1] = paragraphs[-1] + "\n" + line
        else:
            paragraphs.append(line)

    parsed_effects = []

    for paragraph in paragraphs:
        # 2. 모든 HTML 태그를 제거합니다.
        p_clean = re.sub(r"<[^>]*>", "", paragraph)
        
        # 3. 특수 공백 및 깨진 문자를 필터링합니다.
        p_clean = p_clean.replace("&nbsp;", " ")
        p_clean = p_clean.replace("①", "1").replace("②", "2").replace("③", "3").replace("④", "4")
        p_clean = p_clean.replace("\ufffd", "")
        p_clean = re.sub(r"Ominous Artifact\s+[^a-zA-Z0-9\s]+", "Ominous Artifact", p_clean)
        
        # 4. 마침표 뒤 대문자로 시작하는 다중 문장들을 분할합니다 (앞에 숫자가 붙은 모드 선택 형태 '1.' 등은 예외 처리합니다).
        p_clean = re.sub(r"(?<!\b\d)\.\s*([A-Z])", r".\n\1", p_clean)

        lines = [line.strip() for line in p_clean.strip().split('\n') if line.strip()]
        
        paragraph_effects = []
        inherited_type = None
        inherited_enhance_cost = None
        inherited_cost = None

        i = 0
        while i < len(lines):
            line = lines[i]

            # "Select a Mode" 또는 "Select X Modes" 또는 "abilities from the following" 구문이 포함된 라인을 찾습니다.
            if ("Select" in line and "Mode" in line) or "abilities from the following" in line:
                trigger_effect = _parse_single_effect(line)
                if isinstance(trigger_effect, list):
                    if trigger_effect:
                        inherited_type = trigger_effect[0].get('type')
                        inherited_enhance_cost = trigger_effect[0].get('enhance_cost')
                        inherited_cost = trigger_effect[0].get('cost')
                        trigger_effect = trigger_effect[0]
                    else:
                        trigger_effect = Effect()
                else:
                    inherited_type = trigger_effect.get('type')
                    inherited_enhance_cost = trigger_effect.get('enhance_cost')
                    inherited_cost = trigger_effect.get('cost')
                
                trigger_effect.update(process=ProcessType.CHOOSE, choices=[])

                i += 1
                # 다음 줄부터 숫자(1., 2.)로 시작하는 선택지들을 파싱합니다.
                while i < len(lines) and re.match(r"^\d\.", lines[i]):
                    choice_text = re.sub(r"^\d\.\s*", "", lines[i])
                    action_attrs = parse_action(choice_text)
                    action_attrs['type'] = EffectType.SPELL
                    trigger_effect.choices.append(Effect(**action_attrs))
                    i += 1

                paragraph_effects.append(trigger_effect)
            else:
                result = _parse_single_effect(line)
                if isinstance(result, list):
                    if result:
                        inherited_type = result[0].get('type')
                        inherited_enhance_cost = result[0].get('enhance_cost')
                        inherited_cost = result[0].get('cost')
                    for r in result:
                        paragraph_effects.append(r)
                else:
                    # 명시적인 이펙트 패턴이 존재하는지 확인합니다.
                    has_explicit_pattern = False
                    if line.lower().strip() in SIMPLE_KEYWORD_EFFECTS:
                        has_explicit_pattern = True
                    else:
                        for pattern in EFFECT_PATTERNS:
                            if re.match(pattern['regex'], line, re.IGNORECASE):
                                has_explicit_pattern = True
                                break
                    
                    if not has_explicit_pattern and inherited_type is not None:
                        result.update(type=inherited_type)
                        if inherited_enhance_cost is not None:
                            result.update(enhance_cost=inherited_enhance_cost)
                        if inherited_cost is not None:
                            result.update(cost=inherited_cost)
                    else:
                        inherited_type = result.get('type')
                        inherited_enhance_cost = result.get('enhance_cost')
                        inherited_cost = result.get('cost')
                    
                    paragraph_effects.append(result)
                i += 1

        parsed_effects.extend(paragraph_effects)

    if card_type_enum == "SPELL":
        for effect in parsed_effects:
            if effect.get('type') != EffectType.CHOOSE:
                effect.update(type=EffectType.SPELL)
            if effect.get('choices'):
                for choice in effect.choices:
                    choice.update(type=EffectType.SPELL)

    return parsed_effects


# 패턴과 해당 효과를 매핑하는 데이터 구조입니다.
EFFECT_PATTERNS = [
    # 키워드 - 설명 (정규식 그룹).
    {'regex': r"Enhance \((\d+)\): (.*)", 'type': EffectType.ENHANCE, 'groups': ['enhance_cost', 'action_text']},
    {'regex': r"Evolve: (.*)", 'type': EffectType.ON_EVOLVE, 'groups': ['action_text']},
    {'regex': r"Super-Evolve: (.*)", 'type': EffectType.ON_SUPER_EVOLVE, 'groups': ['action_text']},
    {'regex': r"Fanfare: (.*)", 'type': EffectType.FANFARE, 'groups': ['action_text']},
    {'regex': r"Engage: (.*)", 'type': EffectType.ENGAGE, 'groups': ['action_text']},
    {'regex': r"Engage \((\d+)\): (.*)", 'type': EffectType.ENGAGE, 'groups': ['cost', 'action_text']},
    {'regex': r"Last Words: (.*)", 'type': EffectType.LAST_WORDS, 'groups': ['action_text']},
    {'regex': r"At the end of your turn, (.*)", 'type': EffectType.ON_MY_TURN_END, 'groups': ['action_text']},
    {'regex': r"At the end of your opponent's turn, (.*)", 'type': EffectType.ON_OPPONENTS_TURN_END, 'groups': ['action_text']},
    {'regex': r"When this card leaves the field, (.*)", 'type': EffectType.ON_LEAVE_FIELD, 'groups': ['action_text']},
    {'regex': r"When this follower evolves, (.*)", 'type': EffectType.EVOLVED, 'groups': ['action_text']},
    {'regex': r"On Spellboost: (.*)", 'type': EffectType.SPELLBOOST, 'groups': ['action_text']},
    {'regex': r"Countdown \((\d+)\)", 'type': EffectType.COUNTDOWN, 'groups': ['value']},
    {'regex': r"Whenever (.*) enters the field, (.*)", 'type': EffectType.ON_FOLLOWER_ENTER_FIELD, 'groups': ['condition_text', 'action_text']},
    {'regex': r"Combo \((\d+)\) - (.*)", 'type': EffectType.COMBO, 'groups': ['value', 'action_text']},
    {'regex': r"Combo \((\d+)\): (.*)", 'type': EffectType.COMBO, 'groups': ['value', 'action_text']},
    {'regex': r"Earth Rite \((\d+)\) - (.*)", 'type': EffectType.EARTH_RITE, 'groups': ['value', 'action_text']},
    {'regex': r"Earth Rite \((\d+)\): (.*)", 'type': EffectType.EARTH_RITE, 'groups': ['value', 'action_text']},
    {'regex': r"Earth Rite: (.*)", 'type': EffectType.EARTH_RITE, 'groups': ['action_text']},
    {'regex': r"Strike: (.*)", 'type': EffectType.STRIKE, 'groups': ['action_text']},
    {'regex': r"Clash: (.*)", 'type': EffectType.CLASH, 'groups': ['action_text']},
    {'regex': r"Invoke: (.*)", 'type': EffectType.INVOKE, 'groups': ['action_text']},
    {'regex': r"Super Skybound Art: (.*)", 'type': EffectType.SUPER_SKYBOUND_ART, 'groups': ['action_text']},
    {'regex': r"Super Skybound Art\s*-\s*(.*)", 'type': EffectType.SUPER_SKYBOUND_ART, 'groups': ['action_text']},
    {'regex': r"Skybound Art: (.*)", 'type': EffectType.SKYBOUND_ART, 'groups': ['action_text']},
    {'regex': r"Select a Mode to activate", 'type': EffectType.CHOOSE, 'groups': []},
    {'regex': r"Select (\d+)", 'type': EffectType.CHOOSE, 'process': ProcessType.CHOOSE, 'groups': ['value']},
    {'regex': r".*Activates in hand.*", 'type': EffectType.SPELL, 'groups': []},
    {'regex': r"Activates in deck", 'type': EffectType.SPELL, 'groups': []},
    {'regex': r"Fuse: (.*)", 'type': EffectType.SPELL, 'process': ProcessType.FUSE, 'groups': ['value']},
    {'regex': r"X starts at (\d+)", 'type': EffectType.SPELL, 'process': ProcessType.DEFINE_VARIABLE, 'groups': ['value']},
    {'regex': r"X is (.*)", 'type': EffectType.SPELL, 'process': ProcessType.DEFINE_VARIABLE, 'groups': ['value']},
    {'regex': r"(\d+|X) or more:\s*(.*)", 'type': EffectType.SPELL, 'groups': ['value', 'action_text']},
    {'regex': r"(\d+|X):\s*(.*)", 'type': EffectType.SPELL, 'groups': ['value', 'action_text']},
    {'regex': r"Can't be played", 'type': EffectType.SPELL, 'process': ProcessType.IMMUNITY, 'groups': []},
    {'regex': r"It costs (\d+) until the end of the turn", 'type': EffectType.SPELL, 'process': ProcessType.SET_COST, 'groups': ['value']},
]

# 단순 키워드 효과들을 관리합니다 (정규식이 필요하지 않습니다).
SIMPLE_KEYWORD_EFFECTS = {
    "ward": EffectType.WARD, "storm": EffectType.STORM, "rush": EffectType.RUSH,
    "bane": EffectType.BANE, "drain": EffectType.DRAIN, "barrier": EffectType.BARRIER,
    "ambush": EffectType.AMBUSH, "intimidate": EffectType.INTIMIDATE, "aura": EffectType.AURA,
    "combo": EffectType.COMBO, "earth rite": EffectType.EARTH_RITE, "earth sigil": EffectType.EARTH_SIGIL,
    "necromancy": EffectType.NECROMANCY, "reanimate": EffectType.REANIMATE, "overflow": EffectType.OVERFLOW,
    "rally": EffectType.RALLY, "skybound art": EffectType.SKYBOUND_ART, "super skybound art": EffectType.SUPER_SKYBOUND_ART,
    "invoke": EffectType.INVOKE
}


def _parse_single_effect(text: str) -> Effect | list[Effect]:
    text_clean = text.strip().rstrip('.')
    text_clean = text_clean.replace('"', '')
    low_text = text_clean.lower()
    
    # 1. 단순 키워드 효과를 처리합니다.
    if low_text in SIMPLE_KEYWORD_EFFECTS:
        return Effect(type=SIMPLE_KEYWORD_EFFECTS[low_text])

    # 2. 패턴 기반 효과를 처리합니다.
    for pattern in EFFECT_PATTERNS:
        match = re.match(pattern['regex'], text_clean, re.IGNORECASE)
        if match:
            extracted_data = dict(zip(pattern['groups'], match.groups()))
            # 필요한 경우 숫자 문자열을 정수형으로 변환합니다.
            for key, value in extracted_data.items():
                if 'text' not in key:
                    try:
                        extracted_data[key] = int(value)
                    except (ValueError, TypeError):
                        pass
            # 마침표나 쉼표로 분리된 다중 액션을 가진 FANFARE의 예외 처리를 수행합니다.
            if pattern['type'] == EffectType.FANFARE and 'action_text' in extracted_data:
                actions = [a.strip() for a in re.split(r'[.,]\s*', extracted_data['action_text']) if a.strip()]
                effects: list[Effect] = []
                for act in actions:
                    action_attrs = parse_action(act)
                    ef = Effect(type=EffectType.FANFARE, **action_attrs)
                    effects.append(ef)
                return effects
            # 일반적인 액션 파싱을 수행합니다.
            if 'action_text' in extracted_data:
                action_text = extracted_data.pop('action_text')
                if "Select a Mode" in action_text:
                    extracted_data['process'] = ProcessType.CHOOSE
                    extracted_data['choices'] = []
                else:
                    action_attrs = parse_action(action_text)
                    extracted_data.update(action_attrs)
            effect = Effect(**extracted_data)
            if 'process' not in extracted_data and 'process' in pattern:
                effect.update(process=pattern['process'])
            effect.update(type=pattern['type'])
            return effect

    # 3. 패턴이 없는 독립 액션을 처리합니다.
    action_attrs = parse_action(text_clean)
    if 'raw_action_text' not in action_attrs:
        effect = Effect(**action_attrs)
        effect.update(type=EffectType.SPELL)
        return effect

    # 3.5 대상만을 지정하는 문장을 처리합니다.
    target_attrs = parse_target(text_clean)
    if 'raw_target_text' not in target_attrs:
        effect = Effect(**target_attrs)
        effect.update(type=EffectType.SPELL, process=ProcessType.ADD_EFFECT)
        return effect

    # 4. 파싱에 완전히 실패한 경우의 대체 처리입니다.
    print(f"[WARNING] Could not parse effect text: '{text}'")
    return Effect(raw_effect_text=text)


# 대상 파싱을 위한 패턴 목록입니다.
TARGET_PATTERNS = [
    # 대상 - 설명.
    {'regex': r"\bthis follower\b", 'target': TargetType.SELF},
    {'regex': r"\byour leader\b", 'target': TargetType.OWN_LEADER},
    {'regex': r"\bthe enemy leader\b", 'target': TargetType.OPPONENT_LEADER},
    {'regex': r"\ball enemy followers\b", 'target': TargetType.ALL_OPPONENT_FOLLOWERS},
    {'regex': r"\ball opposing followers\b", 'target': TargetType.ALL_OPPONENT_FOLLOWERS},
    {'regex': r"\ba random enemy follower\b", 'target': TargetType.OPPONENT_FOLLOWER_RANDOM},
    {'regex': r"\bSelect an enemy follower on the field\b", 'target': TargetType.OPPONENT_FOLLOWER_CHOICE},
    {'regex': r"\bSelect another allied follower on the field\b", 'target': TargetType.ANOTHER_ALLY_FOLLOWER_CHOICE},
    {'regex': r"\bSelect another allied card on the field\b", 'target': TargetType.ANOTHER_ALLY_CARD_CHOICE},
    {'regex': r"\bSelect an allied follower on the field\b", 'target': TargetType.ALLY_FOLLOWER_CHOICE},
    {'regex': r"\bSelect an allied card on the field\b", 'target': TargetType.ALLY_CARD_CHOICE},
    {'regex': r"\ball other allied followers on the field\b", 'target': TargetType.ALL_OTHER_ALLY_FOLLOWERS},
    {'regex': r"\ball followers\b", 'target': TargetType.ALL_FOLLOWERS},
    {'regex': r"\banother random allied follower\b", 'target': TargetType.ANOTHER_ALLY_FOLLOWER_RANDOM},
    {'regex': r"^(it|them)$", 'target': TargetType.SELF},
    {'regex': r"\bthis card\b", 'target': TargetType.SELF},
    {'regex': r"\bthis amulet\b", 'target': TargetType.SELF},
    {'regex': r"\ball enemies\b", 'target': TargetType.ALL_OPPONENTS},
    {'regex': r"\ball unevolved allied followers on the field\b", 'target': TargetType.ALLY_FOLLOWER_CHOICE_UNEVOLVED},
    {'regex': r"\ball other followers\b", 'target': TargetType.ALL_FOLLOWERS},
    {'regex': r"\ball other allied (.*) followers on the field\b", 'target': TargetType.ALL_OTHER_ALLY_FOLLOWERS, 'groups': ['value']},
    {'regex': r"\ball allied followers on the field\b", 'target': TargetType.ALL_ALLY_FOLLOWERS},
    {'regex': r"\ball allied (.*) followers on the field\b", 'target': TargetType.ALL_ALLY_FOLLOWERS, 'groups': ['value']},
    {'regex': r"\b(\d+) random enemy followers\b", 'target': TargetType.OPPONENT_FOLLOWER_RANDOM, 'groups': ['value']},
    {'regex': r"\bthe opposing follower\b", 'target': TargetType.OPPONENT_FOLLOWER_CHOICE},
    {'regex': r"\bto all allies\b", 'target': TargetType.ALL_ALLY_FOLLOWERS},
    {'regex': r"\bSelect another card on the field\b", 'target': TargetType.ANOTHER_ALLY_CARD_CHOICE},
    {'regex': r"^X$", 'target': TargetType.VARIABLE},
    {'regex': r"\ball Forestcraft cards in your hand that cost (\d+) or less\b", 'target': TargetType.OWN_HAND_CHOICE, 'groups': ['value']},
    {'regex': r"\ba random allied follower on the field\b", 'target': TargetType.ANOTHER_ALLY_FOLLOWER_RANDOM},
    {'regex': r"\ball allied copies of (.*) on the field\b", 'target': TargetType.ALL_ALLY_FOLLOWERS, 'groups': ['value']},
    {'regex': r"\bboth leaders\b", 'target': TargetType.ALL_OPPONENTS},
    {'regex': r"\ball (.*) followers in your hand\b", 'target': TargetType.OWN_HAND_CHOICE, 'groups': ['value']},
    {'regex': r"\ball cards in your deck\b", 'target': TargetType.OWN_DECK},
    {'regex': r"\ball leaders with the highest defense\b", 'target': TargetType.ALL_LEADERS_MAX_DEFENSE},
    {'regex': r"\ball followers with the highest defense\b", 'target': TargetType.ALL_FOLLOWERS_MAX_DEFENSE},
    {'regex': r"\ba random unevolved allied follower on the field that didn't attack this turn\b", 'target': TargetType.ANOTHER_ALLY_FOLLOWER_RANDOM_UNEVOLVED_NO_ATTACK},
    {'regex': r"\ba random super-evolved allied follower on the field\b", 'target': TargetType.ALLY_FOLLOWER_RANDOM_SUPER_EVOLVED},
    {'regex': r"\banother allied card\b", 'target': TargetType.ANOTHER_ALLY_CARD_CHOICE},
    {'regex': r"\banother allied follower\b", 'target': TargetType.ANOTHER_ALLY_FOLLOWER_CHOICE},
    {'regex': r"\ban enemy follower\b", 'target': TargetType.OPPONENT_FOLLOWER_CHOICE},
    {'regex': r"\ban allied follower\b", 'target': TargetType.ALLY_FOLLOWER_CHOICE},
    {'regex': r"\ball cards in your hand\b", 'target': TargetType.OWN_HAND_CHOICE},
    {'regex': r"\ball leaders with the lowest defense\b", 'target': TargetType.ALL_LEADERS_MIN_DEFENSE},
    {'regex': r"\ball followers with the lowest defense\b", 'target': TargetType.ALL_FOLLOWERS_MIN_DEFENSE},
    {'regex': r"\ball non-Encroacher followers\b", 'target': TargetType.ALL_NON_ENCROACHER_FOLLOWERS},
    {'regex': r"\ban allied Crystalspawn\b", 'target': TargetType.ALLY_FOLLOWER_CHOICE},
    {'regex': r"\ba random unevolved allied follower on the field with a base cost of (\d+) or more\b", 'target': TargetType.ANOTHER_ALLY_FOLLOWER_RANDOM_UNEVOLVED, 'groups': ['value']},
]

# 액션 파싱을 위한 패턴 목록입니다.
ACTION_PATTERNS = [
    # 패턴 - 설명 (정규식 그룹).
    {'regex': r"Select (?:an|a)? (?:super-evolved|evolved|damaged)? enemy follower on the field and destroy it", 'process': ProcessType.DESTROY, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},
    {'regex': r"Select an enemy follower on the field and banish it", 'process': ProcessType.BANISH, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},
    {'regex': r"Select an enemy card on the field and banish it", 'process': ProcessType.BANISH, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},
    {'regex': r"Select an enemy follower on the field and return it to hand", 'process': ProcessType.RETURN_TO_HAND, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},
    {'regex': r"Select an enemy follower on the field and set its defense to (\d+)", 'process': ProcessType.SET_DEFENSE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': ['value']},
    {'regex': r"Select an enemy follower on the field and give it -0\/-(\d+)", 'process': ProcessType.STAT_BUFF, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': ['value'], 'special_handling': 'neg_def_buff'},

    # 소환 효과를 처리하는 패턴입니다.
    {'regex': r"Summon (\d+) copies of (.*)", 'process': ProcessType.SUMMON, 'groups': ['value', 'card_name'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Summon a (.*)", 'process': ProcessType.SUMMON, 'groups': ['card_names'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Summon (.*)", 'process': ProcessType.SUMMON, 'groups': ['card_names'], 'target': TargetType.OWN_LEADER},

    # 패로 카드를 가져오는 효과를 처리하는 패턴입니다.
    {'regex': r"Add (\d+) copies of (.*) to your hand", 'process': ProcessType.ADD_CARD_TO_HAND, 'groups': ['value', 'card_name'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Add an (.*) to your hand", 'process': ProcessType.ADD_CARD_TO_HAND, 'groups': ['card_names'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Add a (.*) to your hand", 'process': ProcessType.ADD_CARD_TO_HAND, 'groups': ['card_names'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Add (.*) to your hand", 'process': ProcessType.ADD_CARD_TO_HAND, 'groups': ['card_names'], 'target': TargetType.OWN_LEADER},

    # 비용(Cost) 관련 세부 패턴들을 정의합니다 (우선 순위가 높아 상단에 배치합니다).
    {'regex': r"Select a follower in your hand and increase its cost by (\d+)", 'process': ProcessType.INCREASE_COST, 'target': TargetType.OWN_HAND_CHOICE, 'groups': ['value']},
    {'regex': r"increase its cost by (\d+)", 'process': ProcessType.INCREASE_COST, 'target': TargetType.SELF, 'groups': ['value']},

    # 스탯 버프 효과를 정의합니다 (non-greedy 매칭을 적용합니다).
    {'regex': r"Give (.*?) ([+-]?\d+|[+-]?X)\/([+-]?\d+|[+-]?X)", 'process': ProcessType.STAT_BUFF, 'groups': ['target_text', 'value', 'value2']},
    {'regex': r"(.*?) and give it ([+-]?\d+|[+-]?X)\/([+-]?\d+|[+-]?X)", 'process': ProcessType.STAT_BUFF, 'groups': ['target_text', 'value', 'value2']},
    {'regex': r"Select a follower on the field and give it ([+-]?\d+|[+-]?X)\/([+-]?\d+|[+-]?X)", 'process': ProcessType.STAT_BUFF, 'target': TargetType.ALLY_FOLLOWER_CHOICE, 'groups': ['value', 'value2']},
    {'regex': r"give [+-]?([+-]?\d+|[+-]?X)\/[+-]?([+-]?\d+|[+-]?X)", 'process': ProcessType.STAT_BUFF, 'target': TargetType.SELF, 'groups': ['value', 'value2']},

    # 피해(Damage) 효과를 정의합니다 (비어있는 대상 매칭을 방지하기 위해 (.+)를 사용합니다).
    {'regex': r"Deal (\d+|X) damage split between (.+)", 'process': ProcessType.DEAL_DAMAGE, 'groups': ['value', 'target_text'], 'is_split': True},
    {'regex': r"Deal (\d+|X) damage to (.+)", 'process': ProcessType.DEAL_DAMAGE, 'groups': ['value', 'target_text']},
    {'regex': r"(.+) and deal it (\d+|X) damage", 'process': ProcessType.DEAL_DAMAGE, 'groups': ['target_text', 'value']},
    {'regex': r"Deal damage to (.+)", 'process': ProcessType.DEAL_DAMAGE, 'groups': ['target_text'], 'value': 'X'},

    # 파괴 효과를 처리하는 패턴입니다.
    {'regex': r"Destroy a random enemy follower with the highest attack", 'process': ProcessType.DESTROY, 'target': TargetType.OPPONENT_FOLLOWER_MAX_ATTACK_RANDOM, 'groups': []},
    {'regex': r"(.+) and destroy it", 'process': ProcessType.DESTROY, 'groups': ['target_text']},
    {'regex': r"Destroy this card", 'process': ProcessType.DESTROY, 'target': TargetType.SELF, 'groups': []},
    {'regex': r"Banish this card", 'process': ProcessType.BANISH, 'target': TargetType.SELF, 'groups': []},
    {'regex': r"banish it", 'process': ProcessType.BANISH, 'target': TargetType.SELF, 'groups': []},
    {'regex': r"Destroy this amulet", 'process': ProcessType.DESTROY, 'target': TargetType.SELF, 'groups': []},
    {'regex': r"Destroy the opposing follower", 'process': ProcessType.DESTROY, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': []},

    # 드로우 효과를 처리하는 패턴입니다.
    {'regex': r"Draw (\d+|X) cards", 'process': ProcessType.DRAW, 'groups': ['value'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Draw a card", 'process': ProcessType.DRAW, 'groups': [], 'value': 1, 'target': TargetType.OWN_LEADER},
    {'regex': r"Draw a follower", 'process': ProcessType.DRAW, 'groups': [], 'value': 1, 'condition': 'CARD_TYPE_FOLLOWER', 'target': TargetType.OWN_LEADER},
    {'regex': r"Draw a spell", 'process': ProcessType.DRAW, 'groups': [], 'value': 1, 'condition': 'CARD_TYPE_SPELL', 'target': TargetType.OWN_LEADER},
    {'regex': r"Draw (\d+) (.*)", 'process': ProcessType.DRAW, 'groups': ['value', 'card_name'], 'target': TargetType.OWN_LEADER},

    # 회복 효과를 처리하는 패턴입니다.
    {'regex': r"Restore (\d+) defense (.+)", 'process': ProcessType.HEAL, 'groups': ['value', 'target_text']},
    {'regex': r"Restore (\d+) defense", 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'groups': ['value']},

    # 다른 효과 발동을 처리하는 패턴입니다.
    {'regex': r"Replicate the effects of this card's Fanfare ability", 'process': ProcessType.TRIGGER_EFFECT, 'groups': [], 'value': EffectType.FANFARE},

    # 새로 추가된 액션 패턴들을 정의합니다.
    {'regex': r"Increase your Combo by (\d+)", 'process': ProcessType.INCREASE_COMBO, 'groups': ['value']},
    {'regex': r"Gain your Combo by (\d+)", 'process': ProcessType.INCREASE_COMBO, 'groups': ['value']},
    {'regex': r"Gain (\d+) earth sigils", 'process': ProcessType.GAIN_EARTH_SIGIL, 'groups': ['value']},
    {'regex': r"Gain an earth sigil", 'process': ProcessType.GAIN_EARTH_SIGIL, 'groups': []},
    {'regex': r"Reduce the cost of (.*) by (\d+)", 'process': ProcessType.REDUCE_COST, 'groups': ['target_text', 'value']},
    {'regex': r"Advance this amulet's count by (\d+|X)", 'process': ProcessType.ADVANCE_COUNTDOWN, 'groups': ['value']},
    {'regex': r"Evolve this follower", 'process': ProcessType.SUPER_EVOLVE, 'groups': []},
    {'regex': r"Evolve (.*)", 'process': ProcessType.SUPER_EVOLVE, 'groups': ['target_text']},
    {'regex': r"Select an allied follower on the field and give it (.*)", 'process': ProcessType.ADD_EFFECT, 'target': TargetType.ALLY_FOLLOWER_CHOICE, 'groups': ['value']},
    
    # 다중 효과 및 단일 효과를 부여합니다 (non-greedy 매칭을 적용합니다).
    {'regex': r"Give (.*?) (Ward|Storm|Rush|Bane|Drain|Barrier|Ambush|Intimidate|Aura)\s+and\s+(Ward|Storm|Rush|Bane|Drain|Barrier|Ambush|Intimidate|Aura)", 'process': ProcessType.ADD_EFFECT, 'groups': ['target_text', 'value', 'value2']},
    {'regex': r"Give (.*?) (Ward|Storm|Rush|Bane|Drain|Barrier|Ambush|Intimidate|Aura)", 'process': ProcessType.ADD_EFFECT, 'groups': ['target_text', 'value']},
    {'regex': r"Remove (Ward|Storm|Rush|Bane|Drain|Barrier|Ambush|Intimidate|Aura) from (.*)", 'process': ProcessType.REMOVE_KEYWORD, 'groups': ['value', 'target_text']},
    {'regex': r"remove all abilities from (.*)", 'process': ProcessType.REMOVE_KEYWORD, 'groups': ['target_text']},
    {'regex': r"(?:and\s+)?deal it (\d+|X) damage", 'process': ProcessType.DEAL_DAMAGE, 'target': TargetType.SELF, 'groups': ['value']},
    
    {'regex': r"Select a card in your hand and return it to deck", 'process': ProcessType.RETURN_TO_DECK, 'target': TargetType.OWN_HAND_CHOICE, 'groups': []},
    {'regex': r"Select a (?:card|follower|spell|amulet) in your hand and discard it", 'process': ProcessType.DISCARD, 'target': TargetType.OWN_HAND_CHOICE, 'groups': []},
    {'regex': r"Discard a card", 'process': ProcessType.DISCARD, 'target': TargetType.OWN_LEADER, 'groups': []},
    {'regex': r"Discard (\d+) cards", 'process': ProcessType.DISCARD, 'target': TargetType.OWN_LEADER, 'groups': ['value']},
    {'regex': r"Discard your hand", 'process': ProcessType.DISCARD, 'target': TargetType.OWN_LEADER, 'groups': [], 'value': 'all'},
    {'regex': r"Return (\d+) random cards from your hand to deck", 'process': ProcessType.RETURN_TO_DECK, 'target': TargetType.OWN_LEADER, 'groups': ['value']},
    {'regex': r"Add (\d+) shadows? to your cemetery", 'process': ProcessType.GAIN_SHADOW, 'groups': ['value']},
    {'regex': r"Spellboost your hand", 'process': ProcessType.SPELLBOOST_HAND, 'target': TargetType.OWN_LEADER, 'groups': []},
    {'regex': r"Select a Mode to activate", 'process': ProcessType.CHOOSE, 'groups': []},
    {'regex': r"X is (.*)", 'process': ProcessType.DEFINE_VARIABLE, 'groups': ['value']},
    {'regex': r"Increase (.*) by (\d+|X)", 'process': ProcessType.STAT_BUFF, 'groups': ['target_text', 'value']},
    {'regex': r"Recover (\d+|X) play points?", 'process': ProcessType.RECOVER_PP, 'target': TargetType.OWN_LEADER, 'groups': ['value']},
    {'regex': r"Select an enemy follower on the field with (\d+) defense or less and banish it", 'process': ProcessType.BANISH, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': ['value']},
    {'regex': r"Select an enemy follower on the field with (\d+) attack or less and destroy it", 'process': ProcessType.DESTROY, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'groups': ['value']},
    {'regex': r"Select an allied card on the field and return it to hand", 'process': ProcessType.RETURN_TO_HAND, 'target': TargetType.ALLY_CARD_CHOICE, 'groups': []},
    {'regex': r"If (.*), (.*)(?: instead)?", 'process': ProcessType.CONDITIONAL_EFFECT, 'groups': ['condition_text', 'action_text']},
    {'regex': r"Select (\d+) enemy followers on the field and destroy them", 'process': ProcessType.DESTROY, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE2, 'groups': ['value']},
    {'regex': r"Give (.+) \"Can attack (\d+) times per turn\"", 'process': ProcessType.ADD_EFFECT, 'groups': ['target_text', 'value']},
    {'regex': r"Can attack (\d+) times per turn", 'process': ProcessType.MULTI_ATTACK, 'groups': ['value']},
    {'regex': r"Destroy all other allied cards on the field", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_OTHER_ALLY_FOLLOWERS, 'groups': []},
    {'regex': r"Can't be destroyed by (.*)", 'process': ProcessType.IMMUNITY, 'groups': ['value']},
    {'regex': r"Can't take more than (\d+) damage at a time", 'process': ProcessType.IMMUNITY, 'groups': ['value']},
    {'regex': r"Can't attack followers or leaders", 'process': ProcessType.IMMUNITY, 'groups': []},
    {'regex': r"Gain (\d+) max play points?", 'process': ProcessType.GAIN_MAX_PP, 'groups': ['value']},
    {'regex': r"Gain Crest: (.*)", 'process': ProcessType.GAIN_CREST, 'groups': ['value']},
    {'regex': r"Banish all enemy followers with (\d+|X) defense or less", 'process': ProcessType.BANISH, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'groups': ['value']},
    {'regex': r"Replace your deck with the (.*)", 'process': ProcessType.REPLACE_DECK, 'groups': ['value'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Draw an (\d+|X)-cost follower", 'process': ProcessType.DRAW, 'groups': ['value'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Select another allied card on the field and return it to hand", 'process': ProcessType.RETURN_TO_HAND, 'target': TargetType.ANOTHER_ALLY_CARD_CHOICE, 'groups': []},
    {'regex': r"Transform (.*) into (.*)", 'process': ProcessType.TRANSFORM, 'groups': ['target_text', 'value']},
    {'regex': r"Select a card in your hand with On Spellboost and spellboost it", 'process': ProcessType.SPELLBOOST_HAND, 'target': TargetType.OWN_HAND_CHOICE, 'groups': []},
    {'regex': r"Destroy all allied (.*) followers", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_ALLY_FOLLOWERS, 'groups': ['value']},
    {'regex': r"Return your hand to deck", 'process': ProcessType.RETURN_TO_DECK, 'target': TargetType.OWN_LEADER, 'groups': []},
    {'regex': r"Fully recover your play points", 'process': ProcessType.RECOVER_PP, 'target': TargetType.OWN_LEADER, 'value': 'all', 'groups': []},
    {'regex': r"Your opponent draws a card", 'process': ProcessType.DRAW, 'target': TargetType.OPPONENT_LEADER, 'value': 1, 'groups': []},
    {'regex': r"Destroy all allied Shikigami followers", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_ALLY_FOLLOWERS, 'groups': []},
    {'regex': r"activate all of them", 'process': ProcessType.TRIGGER_EFFECT, 'groups': []},
    {'regex': r"Give [+-]?([+-]?\d+|[+-]?X)\/[+-]?([+-]?\d+|[+-]?X)", 'process': ProcessType.STAT_BUFF, 'target': TargetType.SELF, 'groups': ['value', 'value2']},
    {'regex': r"Give it [+-]?([+-]?\d+|[+-]?X)\/[+-]?([+-]?\d+|[+-]?X)", 'process': ProcessType.STAT_BUFF, 'target': TargetType.SELF, 'groups': ['value', 'value2']},
    {'regex': r"Give your opponent Crest: (.*)", 'process': ProcessType.GAIN_CREST, 'target': TargetType.OPPONENT_LEADER, 'groups': ['value']},
    {'regex': r"Reanimate \((\d+)\)", 'process': ProcessType.REANIMATE, 'groups': ['value']},
    {'regex': r"Select an allied and enemy follower on the field and destroy them", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_FOLLOWERS, 'groups': []},
    {'regex': r"Do this (\d+) times:\s*\"(.*)\"", 'process': ProcessType.TRIGGER_EFFECT, 'groups': ['value', 'action_text']},
    {'regex': r"Draw an? amulet", 'process': ProcessType.DRAW, 'value': 'amulet', 'target': TargetType.OWN_LEADER, 'groups': []},
    {'regex': r"Select an amulet in your hand and reduce its cost by (\d+)", 'process': ProcessType.REDUCE_COST, 'target': TargetType.OWN_HAND_CHOICE, 'groups': ['value']},
    {'regex': r"Destroy all allied amulets", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_ALLY_FOLLOWERS, 'groups': []},
    {'regex': r"Draw a (.*) follower that costs (\d+) or less and set its cost to (\d+)", 'process': ProcessType.DRAW, 'groups': ['card_name', 'value'], 'target': TargetType.OWN_LEADER},
    {'regex': r"Select (\d+)", 'process': ProcessType.CHOOSE, 'groups': ['value']},

    # 추가된 신규 액션 패턴들을 정의합니다.
    {'regex': r"Halve the cost of (.*)", 'process': ProcessType.REDUCE_COST, 'value': 'halve', 'groups': ['target_text']},
    {'regex': r"Banish all duplicates from your deck", 'process': ProcessType.BANISH, 'target': TargetType.OWN_DECK, 'groups': []},
    {'regex': r"Banish all (.*) cards from your deck", 'process': ProcessType.BANISH, 'target': TargetType.OWN_DECK, 'groups': ['value']},
    {'regex': r"Banish all enemy copies of it from the field", 'process': ProcessType.BANISH, 'target': TargetType.OPPONENT_FIELD, 'groups': []},
    {'regex': r"Destroy all damaged enemy followers", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_OPPONENT_FOLLOWERS_DAMAGED, 'groups': []},
    {'regex': r"fully restore the defense of this follower and restore the same amount to your leader", 'process': ProcessType.HEAL_LINKED, 'target': TargetType.SELF, 'groups': []},
    {'regex': r"Fully restore the defense of (.*)", 'process': ProcessType.HEAL, 'value': 'full', 'groups': ['target_text']},
    {'regex': r"Increase the number of Modes you can select by (\d+)", 'process': ProcessType.ADD_EFFECT, 'target': TargetType.SELF, 'groups': ['value']},
    {'regex': r"Set the attack of (.*) to (\d+)", 'process': ProcessType.SET_ATTACK, 'groups': ['target_text', 'value']},
    {'regex': r"Destroy (\d+|X) random enemy followers", 'process': ProcessType.DESTROY, 'target': TargetType.OPPONENT_FOLLOWER_RANDOM, 'groups': ['value']},
    {'regex': r"destroy (\d+|X) other random followers", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_FOLLOWERS, 'groups': ['value']},
    {'regex': r"Advance the count of your Crest: (.*?) by (\d+)", 'process': ProcessType.ADVANCE_CREST, 'groups': ['value', 'value2']},
    {'regex': r"Destroy your Crest: (.*)", 'process': ProcessType.DESTROY_CREST, 'groups': ['value']},
    {'regex': r"Recover (\d+) evolution points?", 'process': ProcessType.RECOVER_EP, 'target': TargetType.OWN_LEADER, 'groups': ['value']},
    {'regex': r"Increase the Skybound Art gauges of all cards in your hand by (\d+)", 'process': ProcessType.ADD_EFFECT, 'target': TargetType.OWN_HAND_CHOICE, 'groups': ['value']},
    {'regex': r"Activate (\d+) random abilities from the following", 'process': ProcessType.TRIGGER_EFFECT, 'groups': ['value']},
    {'regex': r"Set the enemy leader's max defense to (\d+)", 'process': ProcessType.SET_MAX_HEALTH, 'target': TargetType.OPPONENT_LEADER, 'groups': ['value']},
    {'regex': r"Delay the counts of all your crests by (\d+)", 'process': ProcessType.ADVANCE_CREST, 'groups': ['value', 'value2'], 'special_handling': 'neg_val'},
    {'regex': r"Add (\d+) copies of (.*) to your deck", 'process': ProcessType.ADD_CARD_TO_HAND, 'target': TargetType.OWN_DECK, 'groups': ['value', 'card_name']},
    {'regex': r"Add (.*) to your deck", 'process': ProcessType.ADD_CARD_TO_HAND, 'target': TargetType.OWN_DECK, 'groups': ['card_names']},
    {'regex': r"Add (\d+)", 'process': ProcessType.ADD_CARD_TO_HAND, 'target': TargetType.OWN_LEADER, 'groups': ['value']},
    {'regex': r"Give (.*?) (\d+) random abilities from the following", 'process': ProcessType.ADD_EFFECT, 'groups': ['target_text', 'value']},
    {'regex': r"Destroy all enemy followers with (\d+) defense", 'process': ProcessType.DESTROY, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'groups': ['value']},

    # 덜 구체적인 매칭 조건으로 하단에 위치시켜야 하는 패턴들입니다.
    {'regex': r"Select (.*?) on the field", 'process': ProcessType.SELECT, 'groups': ['target_text']},
    {'regex': r"Deal (\d+|X) damage", 'process': ProcessType.DEAL_DAMAGE, 'groups': ['value']},
]


def parse_target(text: str) -> Dict:
    """텍스트에서 대상을 분석하여 TargetType enum 매핑 결과를 반환합니다."""
    text_clean = text.strip().rstrip('.')
    for pattern in TARGET_PATTERNS:
        if re.search(pattern['regex'], text_clean, re.IGNORECASE):
            return {'target': pattern['target']}
    return {'raw_target_text': text_clean}


def parse_action(text: str):
    """텍스트에서 수행할 액션을 분석하여 ProcessType enum 및 속성 매핑 결과를 반환합니다."""
    text_clean = text.strip().rstrip('.')
    text_clean = text_clean.replace('"', '')
    for pattern in ACTION_PATTERNS:
        match = re.search(pattern['regex'], text_clean, re.IGNORECASE)
        if match:
            action = {'process': pattern['process']}
            groups = dict(zip(pattern.get('groups', []), match.groups()))

            if 'target_text' in groups:
                action.update(parse_target(groups['target_text']))

            if 'value' in groups:
                try:
                    action['value'] = int(groups['value'])
                except ValueError:
                    action['value'] = groups['value']
            if 'value2' in groups:
                v1 = action.get('value', 0)
                try:
                    v2 = int(groups['value2'])
                except ValueError:
                    v2 = groups['value2']
                action['value'] = (v1, v2)

            if 'value' in pattern:
                action['value'] = pattern['value']
            if 'target' in pattern:
                action['target'] = pattern['target']
            if 'condition' in pattern:
                action['condition'] = pattern['condition']
            if 'is_split' in pattern:
                action['is_split'] = pattern['is_split']

            if pattern.get('special_handling') == 'neg_def_buff':
                try:
                    def_val = -int(groups['value'])
                except ValueError:
                    def_val = f"-{groups['value']}"
                action['value'] = (0, def_val)
            elif pattern.get('special_handling') == 'neg_val':
                try:
                    action['value2'] = -int(groups['value2'])
                except (ValueError, KeyError):
                    action['value2'] = f"-{groups.get('value2', 0)}"

            # 카드 이름과 추가 효과 지시어가 혼합된 텍스트를 전처리합니다.
            def _clean_card_text(text_val, action_dict):
                for connector in [" and give them ", " and give it "]:
                    if connector in text_val.lower():
                        idx = text_val.lower().find(connector)
                        card_part = text_val[:idx].strip()
                        extra_part = text_val[idx + len(connector):].strip()
                        action_dict['extra_effect'] = extra_part
                        return card_part
                return text_val

            if 'card_name' in groups:
                count = int(groups.get('value', 1))
                card_name = groups['card_name'].strip().replace('.', '')
                card_name = _clean_card_text(card_name, action)
                action['value'] = [card_name] * count
            elif 'card_names' in groups:
                card_list_str = groups['card_names']
                card_list_str = _clean_card_text(card_list_str, action)
                cards = re.split(r'\s*,\s*and\s+an?\s*|\s*,\s*and\s*|\s+and\s+|\s*,\s*an?\b\s*|\s*,\s*', card_list_str)
                card_names = [re.sub(r'^an?\s+', '', card).strip().replace('.', '') for card in cards if card.strip()]
                if card_names:
                    action['value'] = card_names[0] if len(card_names) == 1 else card_names

            return action

    return {'raw_action_text': text_clean}


def get_required_listeners(effects: List[Effect]) -> List:
    """효과 리스트를 바탕으로 바인딩이 필요한 이벤트 리스너들의 목록을 반환합니다."""
    listeners = set()
    for effect in effects:
        if 'type' not in effect.keys():
            continue
        if effect['type'] in EFFECT_TO_EVENT_MAP:
            listeners.add(EFFECT_TO_EVENT_MAP[effect['type']].name)
        if effect['type'] in [EffectType.ON_EVOLVE.name, EffectType.EVOLVED.name]:
            listeners.add(EventType.FOLLOWER_SUPER_EVOLVED.name)

    return list(listeners)


def parse_card_data(raw_data: Dict) -> CardData:
    """raw card data 딕셔너리를 가공하여 구조화된 CardData 객체를 반환합니다."""
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

    effects = parse_effect_text(description, card_type_str.upper() if card_type_str else None)

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
