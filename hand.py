from typing import List
from card import Card # 상대 경로 임포트
from event import Event # 상대 경로 임포트
from event_manager import EventManager # 상대 경로 임포트
from graveyard import Graveyard # 상대 경로 임포트 (순환 참조 주의, 인스턴스 전달)

class Hand:
    """플레이어의 패를 관리합니다."""
    MAX_HAND_SIZE = 9 # [사용자 질의]

    def __init__(self, event_manager: EventManager, graveyard: Graveyard):
        self._cards: List[Card] = []
        self.event_manager = event_manager
        self.graveyard = graveyard

    def add_card(self, card: Card):
        if len(self._cards) >= self.MAX_HAND_SIZE:
            # 패 제한 초과 시 묘지로 보냄 [사용자 질의]
            self.graveyard.add_card(card)
            self.event_manager.queue_event(Event("CardDiscardedFromHandLimit", {'card': card}))
            print(f"패 제한 초과: {card.data.name}이(가) 묘지로 이동했습니다.")
        else:
            self._cards.append(card)
            self.event_manager.queue_event(Event("CardAddedToHand", {'card': card}))
            print(f"{card.data.name}이(가) 패에 추가되었습니다.")

    def remove_card(self, card: Card) -> bool:
        if card in self._cards:
            self._cards.remove(card)
            self.event_manager.queue_event(Event("CardRemovedFromHand", {'card': card}))
            return True
        return False

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)