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

    def draw_card(self) -> Optional[Card]:
        if self._cards:
            return self._cards.pop(0)
        return None

    def add_card_to_bottom(self, card: Card):
        self._cards.append(card)

    def size(self) -> int:
        return len(self._cards)