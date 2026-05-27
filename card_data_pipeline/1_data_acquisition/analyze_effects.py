# 역할 정의. 카드 데이터베이스에서 추출된 효과 텍스트들의 시작 단어 패턴을 분석하는 스크립트입니다.

import json
import os
from collections import Counter


def analyze_effect_texts(file_path):
    """카드 데이터베이스 파일들에서 효과 텍스트의 다빈도 시작 단어를 분석합니다."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    set_ids = ["100", "101", "102", "103", "900"]

    raw_effect_starters = Counter()
    raw_action_starters = Counter()
    raw_target_starters = Counter()

    for set_id in set_ids:
        try:
            full_path = os.path.normpath(os.path.join(script_dir, f"../../card_database/3_parsed_database/{set_id}{file_path}"))
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error - Could not find the file at {full_path}")
            return
        for card_name, card_details in data.items():
            if 'effects' in card_details and isinstance(card_details['effects'], list):
                for effect in card_details['effects']:
                    if isinstance(effect, dict):
                        if 'raw_effect_text' in effect:
                            text = effect['raw_effect_text']
                            # 문장별로 분리하고 첫 번째 문장의 시작 단어들을 가져옵니다.
                            starter = " ".join(text.split()[:4])
                            raw_effect_starters[starter] += 1
                        if 'raw_action_text' in effect:
                            text = effect['raw_action_text']
                            starter = " ".join(text.split()[:4])
                            raw_action_starters[starter] += 1
                        if 'raw_target_text' in effect:
                            text = effect['raw_target_text']
                            starter = " ".join(text.split()[:4])
                            raw_target_starters[starter] += 1

    print("--- Most Common raw_effect_text Starters ---")
    for starter, count in raw_effect_starters.most_common(10):
        print(f'"{starter}" - {count}')

    print("\n--- Most Common raw_action_text Starters ---")
    for starter, count in raw_action_starters.most_common(10):
        print(f'"{starter}" - {count}')

    print("\n--- Most Common raw_target_text Starters ---")
    for starter, count in raw_target_starters.most_common(10):
        print(f'"{starter}" - {count}')


if __name__ == "__main__":
    analyze_effect_texts("_card_database_parsed.json")
