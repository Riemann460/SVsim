from typing import TYPE_CHECKING, List, Dict, Any, Optional

from enums import GamePhase, CardType, Zone # 상대 경로 임포트
from card import Card # 상대 경로 임포트
from player import Player # 상대 경로 임포트

class GameStateManager:
    """모든 게임 상태를 관리하는 중앙 권한 객체"""
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.current_turn_player_id: Optional[str] = None
        self.turn_number: int = 0
        self.game_phase: Optional[GamePhase] = None
        self.cards_in_zones: Dict[str, Dict[str, List[Card]]] = { # player_id: {zone_type: [cards]}
            "player1": {
                Zone.DECK.value: [],
                Zone.HAND.value: [],
                Zone.FIELD.value: [],
                Zone.GRAVEYARD.value: [],
                Zone.BANISHED.value: []
            },
            "player2": {
                Zone.DECK.value: [],
                Zone.HAND.value: [],
                Zone.FIELD.value: [],
                Zone.GRAVEYARD.value: [],
                Zone.BANISHED.value: []
            }
        }
        self.leader_hp: Dict[str, int] = {} # 플레이어별 리더 체력
        self.leader_max_hp: Dict[str, int] = {} # 플레이어별 리더 체력
        self.current_pp: Dict[str, int] = {} # 플레이어별 현재 PP
        self.max_pp: Dict[str, int] = {} # 플레이어별 최대 PP
        self.current_ep: Dict[str, int] = {} # 플레이어별 현재 EP
        self.max_ep: Dict[str, int] = {} # 플레이어별 최대 EP
        self.spend_ep_in_turn: Dict[str, bool] = {} # 플레이어별 EP 소모 여부
        self.extra_pp_uses: Dict[str, Dict[str, int]] = {} # 후공 엑스트라 PP 사용 횟수 {player_id: {phase: count}}
        self.earth_sigil_stacks: Dict[str, int] = {} # 플레이어별 대지의 인장 스택

    def get_cards_in_zone(self, player_id: str, zone: Zone) -> List[Card]:
        """특정 플레이어의 특정 영역에 있는 카드 목록 반환"""
        return self.cards_in_zones.get(player_id, {}).get(zone.value, [])

    def move_card(self, card: Card, from_zone: Zone, to_zone: Zone, player_id: str = None):
        """카드를 한 영역에서 다른 영역으로 이동"""
        target_player_id = player_id if player_id else card.owner_id
        if card in self.cards_in_zones[target_player_id][from_zone.value]:
            self.cards_in_zones[target_player_id][from_zone.value].remove(card)
        self.cards_in_zones[target_player_id][to_zone.value].append(card)
        card.current_zone = to_zone.value
        print(f"DEBUG: 카드 {card.data['name']}이(가) {from_zone.value}에서 {to_zone.value}로 이동됨.")



    def get_player_pp(self, player_id: str) -> int:
        """플레이어의 현재 PP 반환"""
        return self.current_pp.get(player_id, 0)

    def get_player_max_pp(self, player_id: str) -> int:
        """플레이어의 최대 PP 반환"""
        return self.max_pp.get(player_id, 0)

    def set_player_pp(self, player_id: str, amount: int):
        """플레이어의 PP 설정"""
        self.current_pp[player_id] = amount
        print(f"DEBUG: {player_id}의 현재 PP가 {amount}으로 설정됨.")

    def get_leader_hp(self, player_id: str) -> int:
        """리더 체력 반환"""
        return self.leader_hp.get(player_id, 0)

    def deal_damage_to_leader(self, player_id: str, amount: int):
        """리더에게 피해를 입힘"""
        self.leader_hp[player_id] -= amount
        print(f"DEBUG: {player_id} 리더가 {amount} 피해를 입음. 남은 체력: {self.leader_hp[player_id]}")

    def heal_leader(self, player_id: str, amount: int):
        """리더 체력을 회복시킴"""
        self.leader_hp[player_id] += amount
        print(f"DEBUG: {player_id} 리더 체력이 {amount} 회복됨. 현재 체력: {self.leader_hp[player_id]}")

    def get_earth_sigil_stacks(self, player_id: str) -> int:
        """플레이어의 대지의 인장 스택 반환"""
        return self.earth_sigil_stacks.get(player_id, 0)

    def consume_earth_sigils(self, player_id: str, amount: int) -> bool:
        """대지의 인장 스택을 소비"""
        if self.earth_sigil_stacks.get(player_id, 0) >= amount:
            self.earth_sigil_stacks[player_id] -= amount
            print(f"DEBUG: {player_id}가 대지의 인장 {amount}개를 소비. 남은 스택: {self.earth_sigil_stacks[player_id]}")
            return True
        return False

    def add_earth_sigil(self, player_id: str, amount: int = 1):
        """대지의 인장 스택 추가"""
        self.earth_sigil_stacks[player_id] = self.earth_sigil_stacks.get(player_id, 0) + amount
        print(f"DEBUG: {player_id}가 대지의 인장 {amount}개를 획득. 현재 스택: {self.earth_sigil_stacks[player_id]}")

    def get_graveyard_size(self, player_id: str) -> int:
        """묘지에 있는 카드 수 반환"""
        return len(self.get_cards_in_zone(player_id, Zone.GRAVEYARD))

    def get_max_cost_follower_in_graveyard(self, player_id: str, max_cost: int) -> Optional[Card]:
        """묘지에서 특정 코스트 이하의 가장 높은 코스트 추종자 반환"""
        graveyard = self.get_cards_in_zone(player_id, Zone.GRAVEYARD)
        eligible_followers = [
            card for card in graveyard
            if card.data['type'] == CardType.FOLLOWER.value and card.data['cost'] <= max_cost
        ]
        if not eligible_followers:
            return None
        # 코스트가 높은 순, 그 다음은 임의로 선택 (실제 게임은 특정 규칙 따름)
        eligible_followers.sort(key=lambda c: c.data['cost'], reverse=True)
        return eligible_followers[0]
