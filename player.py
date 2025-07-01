from typing import TYPE_CHECKING, List

from card import Card
from enums import CardType, EffectType, EventType, Zone
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
        self.current_defense = self.STARTING_LEADER_HP
        self.max_defense = self.STARTING_LEADER_HP
        self.current_pp = 0
        self.max_pp = 0
        self.current_ep = 0
        self.max_ep = 2
        self.extra_pp_uses = {'1-5': 1, '6+': 1}  # 후공 플레이어 전용
        self.event_manager = event_manager
        self.spent_ep_in_turn = False
        self.effects = []  # 크레스트 효과 인스턴스

        # 영역 초기화
        self.hand = Hand()
        self.graveyard = Graveyard()
        self.field = Field()
        self.deck = Deck([])  # 덱은 게임 시작 시 할당됨
        self.zone_dict = {Zone.HAND: self.hand, Zone.GRAVEYARD: self.graveyard, Zone.FIELD: self.field, Zone.DECK: self.deck}

    def take_damage(self, amount: int):
        """리더가 피해를 입음"""
        self.current_defense -= amount
        self.event_manager.publish(EventType.DAMAGE_DEALT, {'player_id': self.player_id, 'amount': amount, 'current_hp': self.current_defense})
        print(f"{self.player_id} 리더가 {amount} 피해를 입었습니다. 현재 체력: {self.current_defense}")
        if self.current_defense <= 0:
            return True  # 게임 종료
        return False

    def heal_damage(self, amount: int):
        """리더가 회복됨"""
        self.current_defense = min(self.current_defense+amount, self.max_defense)
        print(f"{self.player_id} 리더가 {amount} 체력을 회복했습니다. 현재 체력: {self.current_defense}")

    def gain_pp(self, amount: int):
        """pp가 회복됨"""
        self.current_pp = min(self.current_pp + amount, self.max_pp)
        print(f"{self.player_id} PP가 {amount} 증가했습니다. 현재 PP: {self.current_pp}")

    def spend_pp(self, amount: int) -> bool:
        """pp가 소모됨"""
        if self.current_pp >= amount:
            self.current_pp -= amount
            print(f"{self.player_id} PP {amount} 소모. 남은 PP: {self.current_pp}")
            return True
        return False

    def refresh_pp(self):
        """pp가 전부 회복됨"""
        amount = self.max_pp - self.current_pp
        self.current_pp = self.max_pp
        print(f"{self.player_id} PP가 {amount} 증가했습니다. 현재 PP: {self.current_pp}")

    def use_extra_pp(self, current_turn: int) -> bool:
        """후공 플레이어가 epp를 사용함"""
        if self.player_id == "Player2":  # 후공 플레이어만 사용 가능
            if 1 <= current_turn <= 5 and self.extra_pp_uses['1-5'] > 0:
                self.current_pp += 1
                self.extra_pp_uses['1-5'] -= 1
                print(f"{self.player_id} 엑스트라 PP 사용! 현재 PP: {self.current_pp}")
                return True
            elif current_turn >= 6 and self.extra_pp_uses['6+'] > 0:
                self.current_pp += 1
                self.extra_pp_uses['6+'] -= 1
                print(f"{self.player_id} 엑스트라 PP 사용! 현재 PP: {self.current_pp}")
                return True
        print(f"{self.player_id} 엑스트라 PP를 사용할 수 없습니다.")
        return False

    def gain_ep(self, amount: int):
        """ep가 회복됨"""
        self.current_ep = min(self.current_ep+amount, self.max_ep)
        print(f"{self.player_id} 진화 포인트 {amount} 획득. 현재 EP: {self.current_ep}")

    def spent_ep(self, amount: int):
        """ep가 소모됨"""
        if self.current_pp >= amount:
            self.current_pp -= amount
            print(f"{self.player_id} PP {amount} 소모. 남은 PP: {self.current_pp}")
            return True
        return False

    def get_type(self):
        return CardType.LEADER

    def get_cards_in_zone(self, zone: Zone) -> List[Card]:
        return self.zone_dict[zone].get_cards()

    def has_keyword(self, effect_type:EffectType):
        '''크레스트 구현용(미구현)'''
        return False