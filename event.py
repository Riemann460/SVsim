from typing import Any, Dict

class Event:
    """모든 게임 이벤트의 기본 클래스입니다."""
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data if data is not None else {}