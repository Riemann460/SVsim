from typing import TYPE_CHECKING

from enums import CardType, EffectType, EventType
from event import Event # 상대 경로 임포트
from event_manager import EventManager # 상대 경로 임포트
from deck import Deck # 상대 경로 임포트
from hand import Hand # 상대 경로 임포트
from field import Field # 상대 경로 임포트
from graveyard import Graveyard # 상대 경로 임포트

class Player:
    """개별 플레이어의 상태와 자원을 관리합니다."""
    STARTING_LEADER_HP = 20 # [7, 6]
    MAX_PP = 10 # [7, 6]

    def __init__(self, player_id: str, event_manager: EventManager):
        self.player_id = player_id
        self.leader_hp = self.STARTING_LEADER_HP
        self.current_pp = 0
        self.max_pp = 0
        self.current_ep = 0
        self.max_ep = 2
        self.extra_pp_uses = {'1-5': 1, '6+': 1} # 후공 플레이어 전용 [사용자 질의]
        self.event_manager = event_manager

        # 영역 초기화
        self.graveyard = Graveyard(event_manager)
        self.hand = Hand(event_manager, self.graveyard)
        self.field = Field(event_manager)
        self.deck: Deck = None # 덱은 게임 시작 시 할당됨

    def take_damage(self, amount: int):
        self.leader_hp -= amount
        self.event_manager.publish(EventType.DAMAGE_DEALT, {'player_id': self.player_id, 'amount': amount, 'current_hp': self.leader_hp})
        print(f"{self.player_id} 리더가 {amount} 피해를 입었습니다. 현재 체력: {self.leader_hp}")

    def heal_damage(self, amount: int):
        self.leader_hp += amount
        # self.event_manager.publish(EventType.HEALED, {'player_id': self.player_id, 'amount': amount, 'current_hp': self.leader_hp})
        print(f"{self.player_id} 리더가 {amount} 체력을 회복했습니다. 현재 체력: {self.leader_hp}")

    def gain_pp(self, amount: int):
        self.current_pp = min(self.current_pp + amount, self.max_pp)
        # self.event_manager.publish(EventType.PP_GAINED, {'player_id': self.player_id, 'amount': amount, 'current_pp': self.current_pp})
        print(f"{self.player_id} PP가 {amount} 증가했습니다. 현재 PP: {self.current_pp}")

    def spend_pp(self, amount: int) -> bool:
        if self.current_pp >= amount:
            self.current_pp -= amount
            # self.event_manager.publish(EventType.PP_SPENT, {'player_id': self.player_id, 'amount': amount, 'current_pp': self.current_pp})
            print(f"{self.player_id} PP {amount} 소모. 남은 PP: {self.current_pp}")
            return True
        return False

    def refresh_pp(self):
        amount = self.max_pp-self.current_pp
        self.current_pp = self.max_pp
        # self.event_manager.publish(EventType.PP_GAINED, {'player_id': self.player_id, 'amount': amount, 'current_pp': self.current_pp})
        print(f"{self.player_id} PP가 {amount} 증가했습니다. 현재 PP: {self.current_pp}")

    def use_extra_pp(self, current_turn: int) -> bool:
        if self.player_id == "Player2": # 후공 플레이어만 사용 가능
            if 1 <= current_turn <= 5 and self.extra_pp_uses['1-5'] > 0:
                self.current_pp += 1
                self.extra_pp_uses['1-5'] -= 1
                # self.event_manager.publish(Event("ExtraPPUsed", {'player_id': self.player_id, 'turn_range': '1-5', 'current_pp': self.current_pp}))
                print(f"{self.player_id} 엑스트라 PP 사용! 현재 PP: {self.current_pp}")
                return True
            elif current_turn >= 6 and self.extra_pp_uses['6+'] > 0:
                self.current_pp += 1
                self.extra_pp_uses['6+'] -= 1
                # self.event_manager.publish(Event("ExtraPPUsed", {'player_id': self.player_id, 'turn_range': '6+', 'current_pp': self.current_pp}))
                print(f"{self.player_id} 엑스트라 PP 사용! 현재 PP: {self.current_pp}")
                return True
        print(f"{self.player_id} 엑스트라 PP를 사용할 수 없습니다.")
        return False

    def gain_ep(self, amount: int):
        self.current_ep = min(self.current_ep+amount, self.max_ep)
        # self.event_manager.publish(Event("EvolutionPointGained", {'player_id': self.player_id, 'amount': amount, 'current_ep': self.current_ep}))
        print(f"{self.player_id} 진화 포인트 {amount} 획득. 현재 EP: {self.current_ep}")

    def get_type(self):
        return CardType.LEADER

    def has_keyword(self, effect_type:EffectType):
        '''크레스트 구현용(미구현)'''
        return False