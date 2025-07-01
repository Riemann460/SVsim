import random
from typing import List, Optional
from card import Card # 상대 경로 임포트

class Deck:
    """플레이어의 덱을 관리합니다."""
    def __init__(self, cards: List[Card]):
        self._cards = cards
        self.shuffle()

    def shuffle(self):
        random.shuffle(self._cards)

    def remove_card(self, card: Card) -> bool:
        if card in self._cards:
            self._cards.remove(card)
            return True
        return False

    def add_card(self, card: Card):
        self._cards.append(card)

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)