import json
from collections import Counter


def analyze_effect_texts(file_path):
    set_ids = ["100", "101", "102", "900"]

    raw_effect_starters = Counter()
    raw_action_starters = Counter()
    raw_target_starters = Counter()

    for set_id in set_ids:
        try:
            with open(set_id+file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find the file at {file_path}")
            return
        for card_name, card_details in data.items():
            if 'effects' in card_details and isinstance(card_details['effects'], list):
                for effect in card_details['effects']:
                    if isinstance(effect, dict):
                        if 'raw_effect_text' in effect:
                            text = effect['raw_effect_text']
                            # Split by sentences and get the start of the first one
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
        print(f'"{starter}": {count}')

    print("\n--- Most Common raw_action_text Starters ---")
    for starter, count in raw_action_starters.most_common(10):
        print(f'"{starter}": {count}')

    print("\n--- Most Common raw_target_text Starters ---")
    for starter, count in raw_target_starters.most_common(10):
        print(f'"{starter}": {count}')


if __name__ == "__main__":
    analyze_effect_texts("_card_database_parsed.json")