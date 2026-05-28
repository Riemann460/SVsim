# 역할 정의. 플레이어의 묘지로 이동한 카드 목록과 그림자(Shadow) 자원을 관리하는 클래스입니다.

from typing import List
from src.models.card import Card # 상대 경로 임포트입니다.

class Graveyard:
    """플레이어의 묘지를 관리합니다."""
    def __init__(self):
        """Graveyard 클래스의 생성자입니다."""
        self._cards: List[Card] = []
        self.shadows_count = 0  # 묘지에 누적된 그림자 수를 기록하는 필드입니다.

    def add_card(self, card: Card) -> bool:
        """묘지에 카드를 추가하고 성공 여부를 반환합니다."""
        self._cards.append(card)
        self.shadows_count += 1
        print(f"[LOG] 묘지에 카드 {card.get_display_name()} (ID: {card.card_id}) 추가됨. 현재 묘지 사이즈: {len(self._cards)}")
        return True

    def remove_card(self, card_id: str) -> bool:
        """묘지에서 특정 ID를 가진 카드를 제거합니다."""
        for card in self._cards:
            if card.card_id == card_id:
                self._cards.remove(card)
                print(f"[LOG] 묘지에서 카드 {card.get_display_name()} (ID {card_id}) 제거됨. 남은 묘지 사이즈 {len(self._cards)}.")
                return True
        print(f"[LOG] 묘지에서 카드 ID {card_id}를 찾을 수 없어 제거 실패.")
        return False

    def get_cards(self) -> List[Card]:
        """묘지에 있는 모든 카드의 리스트를 반환합니다."""
        return list(self._cards)

    def size(self) -> int:
        """묘지에 있는 카드의 수를 반환합니다."""
        return len(self._cards)
