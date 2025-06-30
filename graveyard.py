from typing import List
from card import Card # 상대 경로 임포트
from event import Event # 상대 경로 임포트
from event_manager import EventManager # 상대 경로 임포트

class Graveyard:
    """플레이어의 묘지를 관리합니다."""
    def __init__(self, event_manager: EventManager):
        self._cards: List[Card] = []
        self.event_manager = event_manager

    def add_card(self, card: Card):
        self._cards.append(card)
        self.event_manager.queue_event(Event("CardSentToGraveyard", {'card': card}))
        print(f"{card.data.name}이(가) 묘지로 이동했습니다.")

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def size(self) -> int:
        return len(self._cards)