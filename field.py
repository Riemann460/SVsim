from typing import List
from card import Card  # 상대 경로 임포트


class Field:
    """플레이어의 전장을 관리합니다."""
    MAX_FIELD_SIZE = 5  # [6]

    def __init__(self):
        self._cards: List[Card] = []

    def add_card(self, card: Card) -> bool:
        if len(self._cards) >= self.MAX_FIELD_SIZE:
            print("전장 공간이 부족합니다.")
            return False
        self._cards.append(card)
        print(f"{card.card_data.name}이(가) 전장에 소환되었습니다.")
        return True

    def remove_card(self, card: Card) -> bool:
        if card in self._cards:
            self._cards.remove(card)
            return True
        return False

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)
