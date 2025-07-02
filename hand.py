from typing import List
from card import Card # 상대 경로 임포트
from graveyard import Graveyard # 상대 경로 임포트 (순환 참조 주의, 인스턴스 전달)

class Hand:
    """플레이어의 패를 관리합니다."""
    MAX_HAND_SIZE = 9  # [사용자 질의]

    def __init__(self):
        self._cards: List[Card] = []

    def add_card(self, card: Card):
        if self.size() >= self.MAX_HAND_SIZE:
            return False
        else:
            self._cards.append(card)
            return True

    def remove_card(self, card_id: str) -> bool:
        for card in self._cards:
            if card.card_id == card_id:
                self._cards.remove(card)
                return True
        return False

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)