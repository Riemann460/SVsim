import json
import re
from enum import Enum
from enums import EffectType, ProcessType, TargetType, CardType
from card_data import CardData


class Effect:
    def __init__(self, **kwargs):
        self.attributes = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        parts = []
        sorted_keys = sorted(self.attributes.keys(), key=lambda k: k != 'type')

        for key in sorted_keys:
            value = self.attributes[key]

            if isinstance(value, Enum):
                formatted_value = f"{type(value).__name__}.{value.name}"
            else:
                formatted_value = repr(value)

            parts.append(f"'{key}': {formatted_value}")

        return "{"+f"{', '.join(parts)}"+"}"

    def update(self, **kwargs):
        self.attributes.update(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


def _is_new_major_effect_start(line: str) -> bool:
    simple_keywords = {
        "Ward", "Storm", "Rush", "Bane", "Drain", "Barrier", "Ambush", "Intimidate"
    }
    if line in simple_keywords:
        return True

    patterns = [
        r"Enhance \(\d+\):",
        r"Engage \(\d+\):",
        r"Engage:",
        r"Last Words:",
        r"Fanfare:",
        r"Evolve:",
        r"Super-Evolve:",
        r"Strike:",
        r"Countdown \(\d+\):",
        r"Whenever",
        r"At the end of your turn",
        r"On Spellboost:",
        r"When this follower evolves,",
        r"Follower Strike:",
        r"Can attack \d+ times per turn.",
        r"Activates in hand.",
        r"If you've unlocked super-evolution,",
        r"Once on each of your turns,",
        r"Fuse:",
        r"When you Fuse to this card,",
        r"Your opponent can't select any cards other than this one for abilities.",
        r"At the end of your opponent's turn,",
        r"When this card is discarded,",
        r"When this card leaves the field,",
        r"X starts at \d+.",
        r"Then, if X is at least \d+,"
        r"\d+\. ",
    ]
    for pattern in patterns:
        if re.match(pattern, line):
            return True
    return False


def parse_effect_text(description: str):
    if not description:
        return []

    lines = [line.strip() for line in description.strip().split('\n') if line.strip()]
    parsed_effects = []
    current_effect_lines = []

    for line in lines:
        if _is_new_major_effect_start(line) and current_effect_lines:
            combined_text = " ".join(current_effect_lines)
            parsed_effects.append(_parse_single_effect_block(combined_text))
            current_effect_lines = [line]
        else:
            current_effect_lines.append(line)

    if current_effect_lines:
        combined_text = " ".join(current_effect_lines)
        parsed_effects.append(_parse_single_effect_block(combined_text))

    return parsed_effects


def _parse_single_effect_block(text: str):
    simple_keywords = {
        "Ward": EffectType.WARD, "Storm": EffectType.STORM, "Rush": EffectType.RUSH,
        "Bane": EffectType.BANE, "Drain": EffectType.DRAIN, "Barrier": EffectType.BARRIER,
        "Ambush": EffectType.AMBUSH, "Intimidate": EffectType.INTIMIDATE
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

    # ... (rest of the _parse_single_effect_block function) ...

    return {'raw_effect_text': text}


def parse_action(text: str):
    action = {}

    select_and_deal_damage_match = re.search(r"Select an enemy follower on the field and deal it (\d+) damage", text)
    if select_and_deal_damage_match:
        action['process'] = ProcessType.DEAL_DAMAGE
        action['target'] = TargetType.OPPONENT_FOLLOWER_CHOICE
        action['value'] = int(select_and_deal_damage_match.group(1))
        return action

    select_and_destroy_match = re.search(r"Select an enemy follower on the field and destroy it", text)
    if select_and_destroy_match:
        action['process'] = ProcessType.DESTROY
        action['target'] = TargetType.OPPONENT_FOLLOWER_CHOICE
        return action

    select_and_buff_match = re.search(r"Select another allied follower on the field and give it \+(\d+)\/\+(\d+)", text)
    if select_and_buff_match:
        action['process'] = ProcessType.STAT_BUFF
        action['target'] = TargetType.ALLY_FOLLOWER_CHOICE
        action['value'] = (int(select_and_buff_match.group(1)), int(select_and_buff_match.group(2)))
        return action

    at_end_of_turn_match = re.search(r"At the end of your turn, (.*)", text)
    if at_end_of_turn_match:
        sub_text = at_end_of_turn_match.group(1)
        effect_attrs = parse_action(sub_text)
        effect = Effect(**effect_attrs)
        effect.update(type=EffectType.AURA, trigger='END_OF_TURN')
        return effect.attributes

    replicate_fanfare_match = re.search(r"Replicate the effects of this card's Fanfare ability", text)
    if replicate_fanfare_match:
        action['process'] = ProcessType.REPLICATE_EFFECT
        action['value'] = 'FANFARE'
        return action

    advance_count_match = re.search(r"Advance this amulet's count by (\d+)", text)
    if advance_count_match:
        action['process'] = ProcessType.ADVANCE_COUNTDOWN
        action['target'] = TargetType.SELF
        action['value'] = int(advance_count_match.group(1))
        return action

    # ... (rest of the original parse_action function) ...

    action['raw_action_text'] = text
    return action


def main():
    # Since we are not running from the root, we need to load the data directly
    with open("card_database_parsed.json", 'r', encoding='utf-8') as f:
        all_databases_json = json.load(f)

    all_databases = {}
    for db_name, db_content in all_databases_json.items():
        all_databases[db_name] = {}
        for card_name, card_data in db_content.items():
            # A simplified CardData object for this script's purpose
            all_databases[db_name][card_name] = CardData(
                card_id=card_data.get('card_id'),
                name=card_data.get('name'),
                cost=card_data.get('cost'),
                card_type=CardType[card_data.get('card_type')],
                class_type=None, # Not needed for this script
                attack=card_data.get('attack'),
                defense=card_data.get('defense'),
                tribes=[], # Not needed
                effects=[e.get('raw_effect_text') or e.get('raw_action_text') or '' for e in card_data.get('effects', [])]
            )


    print("Parsing card effects...")
    for db_name, db in all_databases.items():
        for card_name, card_data in db.items():
            if card_data.effects:
                parsed_effects = parse_effect_text(card_data.effects[0])
                card_data.effects = parsed_effects

    output_filename = "final_database.py"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("from enums import CardType, ClassType, EffectType, ProcessType, TargetType, TribeType\n")
        f.write("from card_data import CardData\n\n")

        for db_name, db_content in all_databases.items():
            f.write(f"{db_name} = {{\n")
            for card_name, card_obj in db_content.items():
                f.write(f'    \"{card_name}\": {repr(card_obj)},\n')
            f.write("}\n\n")

    print(f"\nParsing complete!")
    print(f"Data saved to {output_filename}")


if __name__ == "__main__":
    main()
