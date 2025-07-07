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
            print(f"[LOG] 손패에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가 실패: 손패 제한 ({self.MAX_HAND_SIZE}) 초과.")
            return False
        else:
            self._cards.append(card)
            print(f"[LOG] 손패에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 손패 사이즈: {len(self._cards)}")
            return True

    def remove_card(self, card_id: str) -> bool:
        for card in self._cards:
            if card.card_id == card_id:
                self._cards.remove(card)
                print(f"[LOG] 손패에서 카드 {card.get_display_name()} (ID: {card_id}) 제거됨. 남은 손패 사이즈: {len(self._cards)}")
                return True
        print(f"[LOG] 손패에서 카드 ID {card_id}를 찾을 수 없어 제거 실패.")
        return False

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)