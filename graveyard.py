from typing import List
from card import Card # 상대 경로 임포트

class Graveyard:
    """플레이어의 묘지를 관리합니다."""
    def __init__(self):
        self._cards: List[Card] = []

    def add_card(self, card: Card):
        self._cards.append(card)
        print(f"[LOG] 묘지에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 묘지 사이즈: {len(self._cards)}")

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)