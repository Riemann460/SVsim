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


def _parse_single_effect(text: str):
    simple_keywords = {
        "Ward": EffectType.WARD, "Storm": EffectType.STORM, "Rush": EffectType.RUSH,
        "Bane": EffectType.BANE, "Drain": EffectType.DRAIN, "Barrier": EffectType.BARRIER,
        "Ambush": EffectType.AMBUSH, "Intimidate": EffectType.INTIMIDATE, "Aura": EffectType.AURA
    }
    if text in simple_keywords:
        return Effect(type=simple_keywords[text])

    enhance_match = re.match(r"Enhance \((\d+)\): (.*)", text)
    if enhance_match:
        cost, sub_text = enhance_match.groups()
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.ENHANCE, enhance_cost=int(cost))
        return effect

    evolve_match = re.match(r"Evolve: (.*)", text)
    if evolve_match:
        sub_text = evolve_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.ON_EVOLVE)
        return effect

    super_evolve_match = re.match(r"Super-Evolve: (.*)", text)
    if super_evolve_match:
        sub_text = super_evolve_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.ON_SUPER_EVOLVE)
        return effect

    fanfare_match = re.match(r"Fanfare: (.*)", text)
    if fanfare_match:
        sub_text = fanfare_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.FANFARE)
        return effect

    engage_without_cost_match = re.match(r"Engage: (.*)", text)
    if engage_without_cost_match:
        sub_text = engage_without_cost_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.ACTIVATE)
        return effect

    engage_with_cost_match = re.match(r"Engage \((\d+)\): (.*)", text)
    if engage_with_cost_match:
        cost, sub_text = engage_with_cost_match.groups()
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.ACTIVATE, cost=int(cost))
        return effect

    last_words_match = re.match(r"Last Words: (.*)", text)
    if last_words_match:
        sub_text = last_words_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.LAST_WORDS)
        return effect

    at_end_of_turn_match = re.search(r"At the end of your turn, (.*)", text)
    if at_end_of_turn_match:
        sub_text = at_end_of_turn_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.ON_MY_TURN_END)
        return effect

    at_end_of_opponent_turn_match = re.search(r"At the end of your opponent's turn, (.*)", text)
    if at_end_of_opponent_turn_match:
        sub_text = at_end_of_opponent_turn_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.ON_OPPONENTS_TURN_END)
        return effect

    evovled_match = re.search(r"When this follower evolves, (.*)", text)
    if evovled_match:
        sub_text = evovled_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.EVOLVED)
        return effect

    spellboost_match = re.search(r"On Spellboost: (.*)", text)
    if spellboost_match:
        sub_text = spellboost_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.SPELLBOOST)
        return effect

    countdown_match = re.search(r"Countdown \((\d+)\)", text)
    if countdown_match:
        turns = countdown_match.group(1)
        effect = Effect(type=EffectType.COUNTDOWN, value=turns)
        return effect

    return Effect(raw_effect_text=text)


def parse_target(text: str) -> Dict:
    target = {}
    self_match = re.search("this follower", text)
    if self_match:
        target['target'] = TargetType.SELF
        return target

    own_leader_match = re.search("your leader", text)
    if own_leader_match:
        target['target'] = TargetType.OWN_LEADER
        return target

    opponent_leader_match = re.search("the enemy leader", text)
    if opponent_leader_match:
        target['target'] = TargetType.OPPONENT_LEADER
        return target

    all_opponent_follower_match = re.search("all enemy followers", text)
    if all_opponent_follower_match:
        target['target'] = TargetType.ALL_OPPONENT_FOLLOWERS
        return target

    random_opponent_follower_match = re.search("a random enemy follower", text)
    if random_opponent_follower_match:
        target['target'] = TargetType.OPPONENT_FOLLOWER_RANDOM
        return target

    opponent_follower_choice_match = re.search("Select an enemy follower on the field", text)
    if opponent_follower_choice_match:
        target['target'] = TargetType.OPPONENT_FOLLOWER_CHOICE
        return target

    another_ally_follower_choice = re.search("Select another allied follower on the field", text)
    if another_ally_follower_choice:
        target['target'] = TargetType.ANOTHER_ALLY_FOLLOWER_CHOICE
        return target

    ally_follower_choice = re.search("Select an allied follower on the field", text)
    if ally_follower_choice:
        target['target'] = TargetType.ALLY_FOLLOWER_CHOICE
        return target

    all_other_ally_follower_match = re.search("all other allied followers on the field", text)
    if all_other_ally_follower_match:
        target['target'] = TargetType.ALL_OTHER_ALLY_FOLLOWERS
        return target

    target['raw_target_text'] = text
    return target


def parse_action(text: str):
    action = {}

    summon_match = re.search(r"Summon (.*)", text)
    if summon_match:
        summon_copies_match = re.search(r"Summon (\d+) copies of (.*)", text)
        if summon_copies_match:
            count = int(summon_copies_match.group(1))
            card_name = summon_copies_match.group(2).strip().replace('.', '')
            action['process'] = ProcessType.SUMMON
            action['target'] = TargetType.OWN_LEADER
            action['value'] = [card_name] * count
            return action

        card_list_str = text.replace("Summon ", "")
        cards = re.split(r'\s+and\s+|\s*,\s*an?\s*|\s*,\s*', card_list_str)
        card_names = [re.sub(r'^an?\s+', '', card).strip().replace('.', '') for card in cards if card.strip()]

        if card_names:
            action['process'] = ProcessType.SUMMON
            action['target'] = TargetType.OWN_LEADER
            # 카드가 하나면 문자열, 여러 개면 리스트로 저장
            action['value'] = card_names[0] if len(card_names) == 1 else card_names
            return action

    add_match = re.search(r"Add (.*) to your hand", text)
    if add_match:
        add_copies_match = re.search(r"Add (\d+) copies of (.*) to your hand", text)
        if add_copies_match:
            count = int(add_copies_match.group(1))
            card_name = add_copies_match.group(2).strip().replace('.', '')
            action['process'] = ProcessType.ADD_CARD_TO_HAND
            action['target'] = TargetType.OWN_LEADER
            action['value'] = [card_name] * count
            return action

        card_list_str = text.replace("Add ", "").replace(" to your hand.", "")
        cards = re.split(r'\s+and\s+|\s*,\s*an?\s*|\s*,\s*', card_list_str)
        card_names = [re.sub(r'^an?\s+', '', card).strip().replace('.', '') for card in cards if card.strip()]

        if card_names:
            action['process'] = ProcessType.ADD_CARD_TO_HAND
            action['target'] = TargetType.OWN_LEADER
            # 카드가 하나면 문자열, 여러 개면 리스트로 저장
            action['value'] = card_names[0] if len(card_names) == 1 else card_names
            return action

    buff_match = re.search(r"Give (.*) \+(\d+)\/\+(\d+)", text)
    if buff_match:
        action = parse_target(buff_match.group(1))
        action['process'] = ProcessType.STAT_BUFF
        action['value'] = (int(buff_match.group(2)), int(buff_match.group(3)))
        return action

    buff_match_2 = re.search(r"(.*) and give it \+(\d+)\/\+(\d+)", text)
    if buff_match_2:
        action = parse_target(buff_match_2.group(1))
        action['process'] = ProcessType.STAT_BUFF
        action['value'] = (int(buff_match_2.group(2)), int(buff_match_2.group(3)))
        return action

    deal_damage_match = re.search(r"(.*) and deal it (\d+) damage", text)
    if deal_damage_match:
        action = parse_target(deal_damage_match.group(1))
        action['process'] = ProcessType.DEAL_DAMAGE
        action['value'] = int(deal_damage_match.group(2))
        return action

    deal_damage_match_2 = re.search(r"Deal (\d+) damage to (.*)", text)
    if deal_damage_match_2:
        action = parse_target(deal_damage_match_2.group(2))
        action['process'] = ProcessType.DEAL_DAMAGE
        action['value'] = int(deal_damage_match_2.group(1))
        return action

    destroy_match = re.search(r"(.*) and destroy it", text)
    if destroy_match:
        action = parse_target(destroy_match.group(1))
        action['process'] = ProcessType.DESTROY
        return action

    replicate_fanfare_match = re.search(r"Replicate the effects of this card's Fanfare ability", text)
    if replicate_fanfare_match:
        action['process'] = ProcessType.TRIGGER_EFFECT
        action['value'] = EffectType.FANFARE
        return action

    draw_single_match = re.search(r"Draw a card", text)
    if draw_single_match:
        action['process'] = ProcessType.DRAW
        action['target'] = TargetType.OWN_LEADER
        action['value'] = 1
        return action

    draw_multiple_match = re.search(r"Draw (\d+) cards", text)
    if draw_multiple_match:
        action['process'] = ProcessType.DRAW
        action['target'] = TargetType.OWN_LEADER
        action['value'] = int(draw_multiple_match.group(1))
        return action

    heal_match = re.search(r"Restore (\d+) defense (.*)", text)
    if heal_match:
        action = parse_target(heal_match.group(2))
        action['process'] = ProcessType.HEAL
        action['value'] = int(heal_match.group(1))
        return action

    action['raw_action_text'] = text
    return action

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
