from typing import List
from card import Card # 상대 경로 임포트

class Graveyard:
    """플레이어의 묘지를 관리합니다."""
    def __init__(self):
        """Graveyard 클래스의 생성자입니다."""
        self._cards: List[Card] = []

    def add_card(self, card: Card):
        """묘지에 카드를 추가합니다."""
        self._cards.append(card)
        print(f"[LOG] 묘지에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 묘지 사이즈: {len(self._cards)}")

    def get_cards(self) -> List[Card]:
        """묘지에 있는 모든 카드의 리스트를 반환합니다."""
        return list(self._cards)

    def size(self) -> int:
        """묘지에 있는 카드의 수를 반환합니다."""
        return len(self._cards)
