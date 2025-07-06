import re

# 기존 파일에서 데이터와 Enum을 가져옵니다.
from enums import EffectType, ProcessType, TargetType
from formatted_database import BASIC_CARD_DATABASE, LEGENDS_RISE_CARD_DATABASE, TOKEN_CARD_DATABASE
from enum import Enum


class Effect:
    """카드의 개별 효과를 나타내는 데이터 클래스."""
    def __init__(self, **kwargs):
        self.attributes = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        """
        Effect 객체를 출력하거나 파일에 쓸 때 호출되는 메소드.
        가독성 좋은 한 줄 문자열로 변환합니다. (수정됨)
        """
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


def parse_effect_text(description: str):
    """
    하나의 카드 능력 서술 문장을 받아 구조화된 effect 리스트로 변환합니다.
    """
    if not description:
        return []

    # 여러 줄로 된 효과는 각 줄을 개별 효과로 처리
    lines = description.strip().split('\n')
    parsed_effects = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. 단순 키워드 처리 (예: "Ward", "Storm")
        simple_keywords = {
            "Ward": EffectType.WARD, "Storm": EffectType.STORM, "Rush": EffectType.RUSH,
            "Bane": EffectType.BANE, "Drain": EffectType.DRAIN, "Barrier": EffectType.BARRIER,
            "Ambush": EffectType.AMBUSH, "Intimidate": EffectType.INTIMIDATE
        }
        if line in simple_keywords:
            parsed_effects.append(Effect(type=simple_keywords[line]))
            continue

        # 2. 복합 효과 처리 (정규표현식 사용)
        # Enhance 패턴: "Enhance (비용): 효과"
        enhance_match = re.match(r"Enhance \((\d+)\): (.*)", line)
        if enhance_match:
            cost, text = enhance_match.groups()
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.ENHANCE, enhance_cost=int(cost))
            parsed_effects.append(effect)
            continue

        # Activate 패턴: "Engage (비용): 효과"
        engage_with_cost_match = re.match(r"Engage \((\d+)\): (.*)", line)
        if engage_with_cost_match:
            cost, text = engage_with_cost_match.groups()
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.ACTIVATE, cost=int(cost))
            parsed_effects.append(effect)
            continue

        # Activate 패턴: "Engage: 효과"
        engage_match = re.match(r"Engage: (.*)", line)
        if engage_match:
            text = engage_match.group(1)
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.ACTIVATE)
            parsed_effects.append(effect)
            continue

        # Last Words 패턴
        last_words_match = re.match(r"Last Words: (.*)", line)
        if last_words_match:
            text = last_words_match.group(1)
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.LAST_WORDS)
            parsed_effects.append(effect)
            continue

        # Fanfare 패턴
        fanfare_match = re.match(r"Fanfare: (.*)", line)
        if fanfare_match:
            text = fanfare_match.group(1)
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.FANFARE)
            parsed_effects.append(effect)
            continue

        # Evolve 패턴
        evolve_match = re.match(r"Evolve: (.*)", line)
        if evolve_match:
            text = evolve_match.group(1)
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.ON_EVOLVE)
            parsed_effects.append(effect)
            continue

        # Super-Evolve 패턴
        super_evolve_match = re.match(r"Super-Evolve: (.*)", line)
        if super_evolve_match:
            text = super_evolve_match.group(1)
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.ON_SUPER_EVOLVE)
            parsed_effects.append(effect)
            continue

        # Strike 패턴
        strike_match = re.match(r"Strike: (.*)", line)
        if strike_match:
            text = strike_match.group(1)
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.STRIKE)
            parsed_effects.append(effect)
            continue

        # Countdown 패턴: "Countdown (턴): 효과"
        engage_with_cost_match = re.match(r"Countdown \((\d+)\): (.*)", line)
        if engage_with_cost_match:
            turns, text = engage_with_cost_match.groups()
            effect = Effect(**parse_action(text))
            effect.update(type=EffectType.ACTIVATE, value=int(turns))
            parsed_effects.append(effect)
            continue

        # 그 외의 경우는 아직 파싱 규칙이 없는 것으로 간주, 원본 텍스트 저장
        parsed_effects.append({'raw_effect_text': line})

    return parsed_effects


def parse_action(text: str):
    """
    효과 텍스트의 '액션' 부분을 분석하여 process, target, value 등을 추출합니다.
    ❗ 게임의 모든 효과를 처리하려면 이 부분의 규칙을 계속 확장해야 합니다.
    """
    action = {}

    # 예시 규칙 1: "Draw X card(s)."
    draw_match = re.search(r"Draw (\d+|a) card", text)
    if draw_match:
        count = draw_match.group(1)
        action['process'] = ProcessType.DRAW
        action['target'] = TargetType.OWN_LEADER
        action['value'] = 1 if count == 'a' else int(count)
        return action

    # 예시 규칙 2: "Give this follower +X/+Y."
    stat_buff_match = re.search(r"Give this follower \+(\d+)\/\+(\d+)", text)
    if stat_buff_match:
        attack, defense = stat_buff_match.groups()
        action['process'] = ProcessType.STAT_BUFF
        action['target'] = TargetType.SELF
        action['value'] = (int(attack), int(defense))
        return action

    # 예시 규칙 3: "Restore X defense to your leader."
    heal_match = re.search(r"Restore (\d+) defense to your leader", text)
    if heal_match:
        amount = heal_match.group(1)
        action['process'] = ProcessType.HEAL
        action['target'] = TargetType.OWN_LEADER
        action['value'] = int(amount)
        return action

    # 예: "Deal X damage...", "Summon a ...", "Destroy..." 등

    # 규칙에 맞지 않는 경우, 원본 텍스트를 저장하여 수동으로 처리하도록 함
    action['raw_action_text'] = text
    return action


def main():
    all_databases = {
        "BASIC_CARD_DATABASE": BASIC_CARD_DATABASE,
        "LEGENDS_RISE_CARD_DATABASE": LEGENDS_RISE_CARD_DATABASE,
        "TOKEN_CARD_DATABASE": TOKEN_CARD_DATABASE
    }

    print("Parsing card effects...")
    # 모든 데이터베이스의 모든 카드를 순회하며 효과 변환
    for db_name, db in all_databases.items():
        for card_name, card_data in db.items():
            # effects 리스트의 첫 번째 항목에 description이 있다고 가정
            if card_data.effects:
                # 파싱 함수 호출
                parsed_effects = parse_effect_text(card_data.effects[0])
                print(parsed_effects)

                # 기존 effects를 파싱된 결과로 교체
                card_data.effects = parsed_effects

    # 파싱된 결과를 새로운 .py 파일로 저장
    output_filename = "final_database.py"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")  # 인코딩 명시
        f.write("from enums import CardType, ClassType, EffectType, ProcessType, TargetType, TribeType\n")
        f.write("from card_data import CardData\n\n")

        for db_name, db_content in all_databases.items():
            f.write(f"{db_name} = {{\n")
            for card_name, card_obj in db_content.items():
                f.write(f'    "{card_name}": {repr(card_obj)},\n')
            f.write("}\n\n")

    print(f"\nParsing complete!")
    print(f"Data saved to {output_filename}")


if __name__ == "__main__":
    main()