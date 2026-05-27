# 역할 정의. 플레이어가 획득하여 쥐고 있는 손패 카드 목록을 관리하는 클래스입니다.

from typing import List
from src.models.card import Card # 상대 경로 임포트입니다.
from src.models.graveyard import Graveyard # 상대 경로 임포트이며 순환 참조 방지를 위해 인스턴스로 전달받습니다.

class Hand:
    """플레이어의 패를 관리합니다."""
    MAX_HAND_SIZE = 9  # 사용자 질의에 의해 결정된 최대 손패 매수입니다.

    def __init__(self):
        """Hand 클래스의 생성자입니다."""
        self._cards: List[Card] = []

    def add_card(self, card: Card):
        """패에 카드를 추가합니다."""
        if self.size() >= self.MAX_HAND_SIZE:
            print(f"[LOG] 손패에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가 실패: 손패 제한 ({self.MAX_HAND_SIZE}) 초과.")
            return False
        else:
            self._cards.append(card)
            print(f"[LOG] 손패에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 손패 사이즈: {len(self._cards)}")
            return True

    def remove_card(self, card_id: str) -> bool:
        """패에서 특정 ID를 가진 카드를 제거합니다."""
        for card in self._cards:
            if card.card_id == card_id:
                self._cards.remove(card)
                print(f"[LOG] 손패에서 카드 {card.get_display_name()} (ID: {card_id}) 제거됨. 남은 손패 사이즈: {len(self._cards)}")
                return True
        print(f"[LOG] 손패에서 카드 ID {card_id}를 찾을 수 없어 제거 실패.")
        return False

    def get_cards(self) -> List[Card]:
        """패에 있는 모든 카드의 리스트를 반환합니다."""
        return list(self._cards)

    def size(self) -> int:
        """패에 있는 카드의 수를 반환합니다."""
        return len(self._cards)
