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
        print(f"[LOG] 덱이 셔플되었습니다. 현재 덱 사이즈: {len(self._cards)}")

    def remove_card(self, card_id: str) -> bool:
        for card in self._cards:
            if card.card_id == card_id:
                self._cards.remove(card)
                print(f"[LOG] 덱에서 카드 {card.get_display_name()} (ID: {card_id}) 제거됨. 남은 덱 사이즈: {len(self._cards)}")
                return True
        print(f"[LOG] 덱에서 카드 ID {card_id}를 찾을 수 없어 제거 실패.")
        return False

    def add_card(self, card: Card):
        self._cards.append(card)
        print(f"[LOG] 덱에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 덱 사이즈: {len(self._cards)}")

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)