import json
from collections import Counter
import re

def analyze_effect_texts(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the file at {file_path}")
        return

    raw_effect_starters = Counter()
    raw_action_starters = Counter()

    for db_name, db_content in data.items():
        if isinstance(db_content, dict):
            for card_name, card_details in db_content.items():
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

    print("--- Most Common raw_effect_text Starters ---")
    for starter, count in raw_effect_starters.most_common(10):
        print(f'"{starter}": {count}')

    print("\n--- Most Common raw_action_text Starters ---")
    for starter, count in raw_action_starters.most_common(10):
        print(f'"{starter}": {count}')

if __name__ == "__main__":
    analyze_effect_texts("C:/Users/SYS/PycharmProjects/pythonProject/shadowverse/process_card_db/card_database_parsed.json")