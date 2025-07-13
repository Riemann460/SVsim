import random
from typing import List, Optional
from card import Card # 상대 경로 임포트

class Deck:
    """플레이어의 덱을 관리합니다."""
    def __init__(self, cards: List[Card]):
        """Deck 클래스의 생성자입니다."""
        self._cards = cards
        self.shuffle()

    def shuffle(self):
        """덱의 카드 순서를 무작위로 섞습니다."""
        random.shuffle(self._cards)
        print(f"[LOG] 덱이 셔플되었습니다. 현재 덱 사이즈: {len(self._cards)}")

    def remove_card(self, card_id: str) -> bool:
        """덱에서 특정 ID를 가진 카드를 제거합니다."""
        for card in self._cards:
            if card.card_id == card_id:
                self._cards.remove(card)
                print(f"[LOG] 덱에서 카드 {card.get_display_name()} (ID: {card_id}) 제거됨. 남은 덱 사이즈: {len(self._cards)}")
                return True
        print(f"[LOG] 덱에서 카드 ID {card_id}를 찾을 수 없어 제거 실패.")
        return False

    def add_card(self, card: Card):
        """덱에 카드를 추가합니다."""
        self._cards.append(card)
        print(f"[LOG] 덱에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 덱 사이즈: {len(self._cards)}")

    def get_cards(self) -> List[Card]:
        """덱에 있는 모든 카드의 리스트를 반환합니다."""
        return list(self._cards)

    def size(self) -> int:
        """덱에 있는 카드의 수를 반환합니다."""
        return len(self._cards)
