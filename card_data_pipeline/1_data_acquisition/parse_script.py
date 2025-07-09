import json
import re
from enum import Enum
from typing import Dict

from enums import EffectType, ProcessType, TargetType, CardType
from card_data import CardData
from effect import Effect


def parse_effect_text(description: str):
    if not description:
        return []

    lines = [line.strip() for line in description.strip().split('\n') if line.strip()]
    parsed_effects = []

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

    # Summon 패턴 처리
    if text.startswith("Summon "):
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

    # ... (rest of the original parse_action function) ...

    action['raw_action_text'] = text
    return action