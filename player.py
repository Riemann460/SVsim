from typing import List

import card_data
from card import Card
from enums import CardType, EffectType, Zone, ClassType
from event_manager import EventManager
from deck import Deck
from hand import Hand
from field import Field
from graveyard import Graveyard
from effect import Effect

class Player:
    """개별 플레이어의 상태와 자원을 관리합니다."""
    STARTING_LEADER_HP = 20 # [7, 6]
    MAX_PP = 10 # [7, 6]

    def __init__(self, player_id: str, event_manager: EventManager):
        """Player 클래스의 생성자입니다."""
        self.player_id = player_id
        self.current_defense = self.STARTING_LEADER_HP
        self.max_defense = self.STARTING_LEADER_HP
        self.current_pp = 0
        self.max_pp = 0
        self.current_ep = 0
        self.max_ep = 2
        self.current_sep = 0
        self.max_sep = 2
        self.extra_pp = 0
        self.max_extra_pp = 1
        self.event_manager = event_manager
        self.spent_ep_in_turn = False
        self.effects: List[Effect] = []  # 크레스트 효과 인스턴스
        self.card_data = card_data.CardData('Leader', self.player_id, 0, CardType.LEADER, ClassType.NEUTRAL, 0, self.max_defense, effects=self.effects)

        # 영역 초기화
        self.hand = Hand()
        self.graveyard = Graveyard()
        self.field = Field()
        self.deck = Deck([])  # 덱은 게임 시작 시 할당됨
        self.zone_dict = {Zone.HAND: self.hand, Zone.GRAVEYARD: self.graveyard, Zone.FIELD: self.field, Zone.DECK: self.deck}

    def take_damage(self, amount: int):
        """리더가 피해를 입음"""
        self.current_defense -= amount
        print(f"[LOG] {self.player_id} 리더가 {amount} 피해를 입었습니다. 현재 체력: {self.current_defense}")
        if self.current_defense <= 0:
            print(f"[LOG] {self.player_id} 리더의 체력이 0 이하가 되어 게임 종료 조건 충족.")
            return True  # 게임 종료
        return False

    def heal_damage(self, amount: int):
        """리더가 회복됨"""
        self.current_defense = min(self.current_defense+amount, self.max_defense)
        print(f"[LOG] {self.player_id} 리더가 {amount} 체력을 회복했습니다. 현재 체력: {self.current_defense}")

    def gain_pp(self, amount: int):
        """pp가 회복됨"""
        self.current_pp = min(self.current_pp + amount, self.max_pp)
        print(f"[LOG] {self.player_id} PP가 {amount} 증가했습니다. 현재 PP: {self.current_pp}")

    def spend_pp(self, amount: int):
        """pp가 소모됨"""
        if self.current_pp >= amount:
            self.current_pp -= amount
            print(f"[LOG] {self.player_id} PP {amount} 소모. 남은 PP: {self.current_pp}")
            return

        if self.current_pp + self.extra_pp >= amount:
            print(f"[LOG] {self.player_id} PP {self.current_pp} 소모. 남은 PP: {0}")
            extra_amount = amount - self.current_pp
            self.current_pp = 0
            self.spend_extra_pp(extra_amount)
            return

        print(f"[ERROR] 처리 불가능한 PP 사용 요청! 남은 PP: {self.current_pp} 요청 PP: {amount}")

    def refresh_pp(self):
        """pp가 전부 회복됨"""
        amount = self.max_pp - self.current_pp
        self.current_pp = self.max_pp
        print(f"[LOG] {self.player_id} PP가 {amount} 증가했습니다. 현재 PP: {self.current_pp}")

    def gain_epp(self, amount: int):
        """epp가 회복됨"""
        self.extra_pp = min(self.extra_pp + amount, self.max_extra_pp)
        print(f"[LOG] {self.player_id} EPP가 {amount} 증가했습니다. 현재 EPP: {self.extra_pp}")

    def spend_extra_pp(self, amount: int) -> bool:
        """epp를 사용함"""
        if self.extra_pp >= amount:
            self.extra_pp -= amount
            print(f"[LOG] {self.player_id} EXTRA PP {amount} 소모. 남은 EXTRA PP: {self.extra_pp}")

    def gain_ep(self, amount: int):
        """ep가 회복됨"""
        self.current_ep = min(self.current_ep+amount, self.max_ep)
        print(f"[LOG] {self.player_id} 진화 포인트 {amount} 획득. 현재 EP: {self.current_ep}")

    def spend_ep(self, amount: int):
        """ep가 소모됨"""
        if self.current_ep >= amount:
            self.current_ep -= amount
            print(f"[LOG] {self.player_id} EP {amount} 소모. 남은 EP: {self.current_ep}")
        else:
            print(f"[ERROR] 처리 불가능한 EP 사용 요청! 남은 EP: {self.current_ep} 요청 EP: {amount}")

    def gain_sep(self, amount: int):
        """sep가 회복됨"""
        self.current_sep = min(self.current_sep+amount, self.max_sep)
        print(f"[LOG] {self.player_id} 초진화 포인트 {amount} 획득. 현재 SEP: {self.current_sep}")

    def spend_sep(self, amount: int):
        """sep가 소모됨"""
        if self.current_sep >= amount:
            self.current_sep -= amount
            print(f"[LOG] {self.player_id} SEP {amount} 소모. 남은 SEP: {self.current_sep}")
        else:
            print(f"[ERROR] 처리 불가능한 SEP 사용 요청! 남은 SEP: {self.current_sep} 요청 SEP: {amount}")

    def get_type(self):
        """플레이어의 타입을 반환합니다 (리더)."""
        return CardType.LEADER

    def get_display_name(self):
        """플레이어의 ID를 표시 이름으로 반환합니다."""
        return self.player_id

    def get_cards_in_zone(self, zone: Zone) -> List[Card]:
        """지정된 영역에 있는 모든 카드의 리스트를 반환합니다."""
        return self.zone_dict[zone].get_cards()

    def has_keyword(self, effect_type:EffectType):
        '''크레스트 구현용(미구현)'''
        return False