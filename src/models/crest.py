# -*- coding: utf-8 -*-
# 이 파일은 플레이어가 획득하는 문장 효과를 객체 단위로 정의하고 관리합니다.

from typing import List, Tuple
from src.common.enums import EventType

class Crest:
    """플레이어가 획득하는 문장 효과의 기본 클래스입니다."""
    def __init__(self, name: str, owner_id: str):
        self.name = name
        self.owner_id = owner_id
        self.listeners: List[Tuple[EventType, str]] = []  # 등록된 전역 리스너 정보 목록입니다.
        self.count = 0  # 문장의 카운트를 관리하는 필드입니다.

    def register_listeners(self, game):
        """문장의 지속 효과를 처리하는 리스너들을 등록합니다."""
        pass

    def unregister_listeners(self, game):
        """등록했던 모든 리스너들을 이벤트 매니저에서 해제합니다."""
        for event_type, listener_id in self.listeners:
            game.event_manager.unsubscribe(event_type, listener_id)
        self.listeners.clear()


class MjerrabaineCrest(Crest):
    """제라베인의 문장 효과를 처리하는 클래스입니다."""
    def __init__(self, owner_id: str):
        super().__init__("Mjerrabaine, Great Manifest", owner_id)

    def register_listeners(self, game):
        """턴 종료 이벤트를 구독하여 제라베인의 효과를 실행합니다."""
        listener_id = f"crest_{self.owner_id}_{self.name.replace(' ', '_').replace(',', '')}_turn_end"
        
        def on_turn_end(event):
            # 턴 종료 이벤트를 발생시킨 플레이어가 문장 소유주인 경우에만 발동합니다.
            if event.player_id != self.owner_id:
                return
            
            import random
            from src.common.enums import Zone, CardType
            from src.common.event import DestroyedOnFieldEvent
            
            player = game.game_state_manager.players[self.owner_id]
            opponent_id = game.opponent_id[self.owner_id]
            
            # 아군 전장에 추종자가 단 하나만 존재하는지 확인합니다.
            allied_followers = [c for c in player.field.get_cards() if c.get_type() == CardType.FOLLOWER]
            if len(allied_followers) == 1:
                print(f"[LOG] {self.name} 문장 효과가 발동합니다.")
                opponent = game.game_state_manager.players[opponent_id]
                
                # 상대 리더에게 2 피해를 줍니다.
                opponent.take_damage(2)
                
                # 상대 추종자 중 임의의 하나에게 2 피해를 줍니다.
                opponent_field = game.game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
                opponent_followers = [c for c in opponent_field if c.get_type() == CardType.FOLLOWER]
                if opponent_followers:
                    target_follower = random.choice(opponent_followers)
                    target_follower.take_damage(2)
                    if target_follower.current_defense <= 0:
                        game.game_state_manager.move_card(target_follower.card_id, Zone.FIELD, Zone.GRAVEYARD)
                        game.event_manager.publish(DestroyedOnFieldEvent(target_follower.card_id))
                        game.process_events()

        from src.common.listener import Listener
        game.event_manager.subscribe(Listener(listener_id, EventType.TURN_END, on_turn_end))
        self.listeners.append((EventType.TURN_END, listener_id))


def create_crest(name: str, owner_id: str) -> Crest:
    """문장 이름에 맞추어 해당하는 문장 객체를 생성합니다."""
    if name == "Mjerrabaine, Great Manifest":
        return MjerrabaineCrest(owner_id)
    return Crest(name, owner_id)
