from typing import TYPE_CHECKING, List, Dict, Any, Optional

from enums import GamePhase, CardType, Zone, EffectType, EventType
from card import Card
from player import Player


class GameStateManager:
    """게임 보드 상태를 관리하는 객체"""

    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.opponent_id: Dict[str, str] = {}
        self.current_turn_player_id: Optional[str] = None
        self.turn_number: int = 0
        self.game_phase: Optional[GamePhase] = None
        self._next_card_instance_id = 0

    def create_card_instance(self, card_data, owner_id):
        new_card_id = str(self._next_card_instance_id)
        self._next_card_instance_id += 1
        return Card(card_data, owner_id, new_card_id)

    def get_cards_in_zone(self, player_id: str, zone: Zone) -> List[Card]:
        """특정 플레이어의 특정 영역에 있는 카드 조회"""
        player = self.players[player_id]
        return player.get_cards_in_zone(zone)

    def move_card(self, card_id: str, from_zone: Zone, to_zone: Zone):
        """카드를 한 영역에서 다른 영역으로 이동"""
        card = self.get_entity_by_id(card_id, from_zone)
        player = self.players[card.owner_id]
        player.zone_dict[from_zone].remove_card(card_id)

        if not player.zone_dict[to_zone].add_card(card):
            if to_zone == Zone.HAND:
                player.graveyard.add_card(card)
                print(f"DEBUG: 손패 소지 제한 매수를 초과하여 묘지로 보내짐.")
            elif to_zone == Zone.FIELD:
                to_zone = "소멸"
                print(f"DEBUG: 필드 소환 제한 매수를 초과하여 소멸함.")
        print(f"DEBUG: 카드 {card.card_data['name']}이(가) {from_zone.value}에서 {to_zone.value}로 이동됨.")

    def add_card(self, card: Card, to_zone: Zone, player_id: str):
        """카드를 지정 영역에 추가"""
        player = self.players[player_id]
        if not player.zone_dict[to_zone].add_card(card):
            if to_zone == Zone.HAND:
                player.graveyard.add_card(card)
                print(f"DEBUG: 손패 소지 제한 매수를 초과하여 묘지로 보내짐.")
            elif to_zone == Zone.FIELD:
                to_zone = "소멸"
                print(f"DEBUG: 필드 소환 제한 매수를 초과하여 소멸함.")
        print(f"DEBUG: 카드 {card.card_data['name']}이(가) {to_zone.value}로 추가됨.")

    def shuffle_deck(self, player_id: str):
        """지정 플레이어의 덱 셔플"""
        player = self.players[player_id]
        player.deck.shuffle()

    def start_turn(self, player_id: str):
        print(self.players.keys())
        """턴 시작 단계 처리"""
        player = self.players[player_id]
        self.game_phase = GamePhase.START_PHASE
        self.turn_number += 1
        self.current_turn_player_id = player_id
        print(f"\n--- {player_id}의 {self.turn_number}턴 시작 (시작 단계) ---")

        # 최대 PP 증가 및 회복
        if player.max_pp < player.MAX_PP:
            player.max_pp += 1
        player.refresh_pp()

        # 진화 가능 턴 처리
        if self.turn_number in [8, 9]:
            player.current_ep = 2

        # 필드 추종자 engaged 상태 리셋 (새로 공격 가능하게)
        for card in self.get_cards_in_zone(player_id, Zone.FIELD):
            if card.card_data['card_type'] == CardType.FOLLOWER:
                card.is_engaged = False
                card.is_summoned = False

    def play_card(self, player_id, card_id):
        """지정 카드를 사용"""
        card = self.get_entity_by_id(card_id)
        if not card:
            print(f"ERROR: play_card - card with id {card_id} not found.")
            return

        player = self.players[player_id]
        player.spend_pp(card.current_cost)
        print(
            f"DEBUG: {player_id}가 {card.card_data['name']}을(를) PP {card.current_cost} 소모하여 플레이함. 남은 PP: {player.current_pp}")

        # 카드 타입에 따른 처리
        if card.get_type() in [CardType.FOLLOWER, CardType.AMULET]:
            self.move_card(card_id, Zone.HAND, Zone.FIELD)
            # 마법진인 경우 카운트다운 초기화
            if card.get_type() == CardType.AMULET and card.has_keyword(EffectType.COUNTDOWN):
                for effect in card.effects:
                    if effect['type'] == EffectType.COUNTDOWN:
                        card.countdown_value = effect['value']

        elif card.get_type() == CardType.SPELL:
            self.move_card(card_id, Zone.HAND, Zone.GRAVEYARD)  # 주문은 사용 즉시 묘지로

    def get_entity_by_id(self, entity_id: str, zone: Zone = None) -> Optional[Any]:
        """Player나 Card의 ID로 인스턴스 조회"""
        if entity_id in self.players:
            return self.players[entity_id]

        for player in self.players.values():
            if zone:
                for card in player.zone_dict[zone].get_cards():
                    if card.card_id == entity_id:
                        return card

            for zone_obj in player.zone_dict.values():
                for card in zone_obj.get_cards():
                    if card.card_id == entity_id:
                        return card
        return None

    def get_card_name(self, entity_id: str) -> str:
        entity = self.get_entity_by_id(entity_id)
        if entity:
            return entity.card_data['name']
        return "Unknown Entity"