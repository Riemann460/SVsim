from typing import List
from card import Card  # 상대 경로 임포트


class Field:
    """플레이어의 전장을 관리합니다."""
    MAX_FIELD_SIZE = 5  # [6]

    def __init__(self):
        self._cards: List[Card] = []

    def add_card(self, card: Card) -> bool:
        if len(self._cards) >= self.MAX_FIELD_SIZE:
            print(f"[LOG] 필드에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가 실패: 필드 제한 ({self.MAX_FIELD_SIZE}) 초과.")
            return False
        self._cards.append(card)
        print(f"[LOG] 필드에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 필드 사이즈: {len(self._cards)}")
        return True

    def remove_card(self, card_id: str) -> bool:
        for card in self._cards:
            if card.card_id == card_id:
                self._cards.remove(card)
                print(f"[LOG] 필드에서 카드 {card.get_display_name()} (ID: {card_id}) 제거됨. 남은 필드 사이즈: {len(self._cards)}")
                return True
        print(f"[LOG] 필드에서 카드 ID {card_id}를 찾을 수 없어 제거 실패.")
        return False

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)
