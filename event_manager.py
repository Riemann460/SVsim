from typing import Callable, Dict, List, Any
from collections import defaultdict
from enums import EventType


class EventManager:
    """이벤트 디스패치 및 구독 관리"""
    def __init__(self):
        from enums import EventType
        self.listeners: Dict[EventType, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)
        self.event_queue: List[Dict[str, Any]] = []

    def subscribe(self, event_type: EventType, listener: Callable[[Dict[str, Any]], None]):
        """이벤트 리스너 등록"""
        self.listeners[event_type].append(listener)
        print(f"[LOG] 리스너 {listener.__name__}가 {event_type.value} 이벤트에 등록됨.")

    def publish(self, event_type: EventType, event_data: Dict[str, Any]):
        """이벤트 게시 (큐에 추가)"""
        event_data['event_type'] = event_type
        self.event_queue.append(event_data)
        print(f"[LOG] 이벤트 {event_type.value}가 큐에 추가됨. 데이터: {event_data}")

    def process_events(self, game_state_manager: 'GameStateManager', effect_processor: 'EffectProcessor'):
        """큐에 있는 모든 이벤트를 처리"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            event_type = event['event_type']
            print(f"[LOG] {event_type.value} 이벤트 처리 시작. 데이터: {event}")
            for listener in self.listeners[event_type]:
                listener(event)
