from typing import Dict, List
from collections import defaultdict
from enums import EventType
from event import Event
from listener import Listener


class EventManager:
    """이벤트 디스패치 및 구독 관리"""
    def __init__(self):
        self.listeners: Dict[EventType, List[Listener]] = defaultdict(list)
        self.event_queue: List[Event] = []

    def subscribe(self, listener: Listener):
        """이벤트 리스너 등록"""
        self.listeners[listener.event_type].append(listener)
        print(f"[LOG] 리스너 ID '{listener.id}'가 {listener.event_type.value} 이벤트에 등록됨.")

    def unsubscribe(self, event_type: EventType, listener_id: str):
        """특정 ID를 가진 이벤트 리스너를 제거"""
        initial_len = len(self.listeners[event_type])
        self.listeners[event_type] = [l for l in self.listeners[event_type] if l.id != listener_id]
        if len(self.listeners[event_type]) < initial_len:
            print(f"[LOG] 리스너 ID '{listener_id}'가 {event_type.value} 이벤트에서 제거됨.")

    def publish(self, event: Event):
        """이벤트 게시 (큐에 추가)"""
        self.event_queue.append(event)
        print(f"[LOG] 이벤트 {event.event_type.value}가 큐에 추가됨. 데이터: {event}")

    def process_events(self):
        """큐에 있는 모든 이벤트를 처리"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            print(f"[LOG] {event.event_type.value} 이벤트 처리 시작. 데이터: {event}")
            # 리스너 목록을 복사하여 순회 중에 리스너가 변경되어도 안전하도록 함
            for listener in list(self.listeners[event.event_type]):
                if listener.card_id and event.card_id != listener.card_id:
                    continue
                if listener.player_id and event.player_id != listener.player_id:
                    continue
                if listener.condition(event):
                    listener.callback(event)
