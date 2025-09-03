from dataclasses import dataclass, field
from typing import Callable, Optional
from enums import EventType
from event import Event

@dataclass
class Listener:
    """이벤트 리스너를 나타내는 클래스"""
    id: str
    event_type: EventType
    callback: Callable[[Event], None]
    condition: Callable[[Event], bool] = field(default=lambda event: True)
    card_id: str = None
    player_id: str = None
