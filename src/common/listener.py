# 역할 정의. 특정 이벤트가 발생했을 때 호출될 콜백 함수와 조건을 가지는 이벤트 리스너를 정의합니다.

from dataclasses import dataclass, field
from typing import Callable, Optional
from src.common.enums import EventType
from src.common.event import Event

@dataclass
class Listener:
    """이벤트 리스너를 나타내는 클래스입니다."""
    id: str
    event_type: EventType
    callback: Callable[[Event], None]
    condition: Callable[[Event], bool] = field(default=lambda event: True)
    card_id: str = None
    player_id: str = None
