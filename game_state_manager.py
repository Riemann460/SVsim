from typing import List, Dict, Any, Optional

from enums import GamePhase, CardType, Zone, EffectType, TargetType
from card import Card
from player import Player
from effect import Effect
from event import FollowerEnterFieldEvent


class GameStateManager:
    """게임 보드 상태를 관리하는 객체"""

    def __init__(self):
        """GameStateManager 클래스의 생성자입니다."""
        self.players: Dict[str, Player] = {}
        self.opponent_id: Dict[str, str] = {}
        self.current_turn_player_id: Optional[str] = None
        self.turn_number: int = 0
        self.game_phase: Optional[GamePhase] = None
        self.cards = []
        self._next_card_instance_id = 0
        self.game = None # Game 인스턴스를 참조하기 위한 필드 추가

    def create_card_instance(self, card_data, owner_id):
        """새로운 카드 인스턴스를 생성하고 게임에 추가합니다."""
        new_card_id = str(self._next_card_instance_id)
        card = Card(card_data, owner_id, new_card_id)
        self.cards.append(card)
        self._next_card_instance_id += 1
        return card

    def get_card_ids_in_zone(self, player_id: str, zone: Zone) -> List[str]:
        """특정 플레이어의 특정 영역에 있는 카드 ID 조회"""
        player = self.players[player_id]
        return [card.card_id for card in player.get_cards_in_zone(zone)]

    def get_cards_in_zone(self, player_id: str, zone: Zone, condition=lambda x: True) -> List[Card]:
        """특정 플레이어의 특정 영역에 있는 카드 직접 반환"""
        player = self.players[player_id]
        return [card for card in player.get_cards_in_zone(zone) if condition(card)]

    def move_card(self, card_id: str, from_zone: Zone, to_zone: Zone):
        """카드를 한 영역에서 다른 영역으로 이동"""
        card = self.get_entity_by_id(card_id, from_zone)
        if not card:
            print(f"[ERROR] move_card - card with id {card_id} from zone {from_zone} not found.")
            return

        player = self.players[card.owner_id]
        
        # 필드를 벗어날 때 리스너 해제
        if from_zone == Zone.FIELD:
            self.game._unregister_card_listeners(card)

        player.zone_dict[from_zone].remove_card(card_id)

        if not player.zone_dict[to_zone].add_card(card):
            if to_zone == Zone.HAND:
                player.graveyard.add_card(card)
                print(f"[LOG] {card.get_display_name()} (ID: {card_id}) 손패 소지 제한 매수 초과로 묘지로 이동.")
            elif to_zone == Zone.FIELD:
                print(f"[LOG] {card.get_display_name()} (ID: {card_id}) 필드 소환 제한 매수 초과로 소멸.")
        else:
            # 필드에 들어올 때 리스너 등록
            if to_zone == Zone.FIELD:
                self.game._register_card_listeners(card)
                if card.get_type() == CardType.FOLLOWER:
                    self.game.event_manager.publish(FollowerEnterFieldEvent(card_id=card.card_id, player_id=card.owner_id))
            
            print(f"[LOG] 카드 {card.get_display_name()} (ID: {card_id})이(가) {from_zone.value}에서 {to_zone.value}로 이동됨.")

    def add_card(self, card: Card, to_zone: Zone, player_id: str):
        """카드를 지정 영역에 추가"""
        player = self.players[player_id]
        if not player.zone_dict[to_zone].add_card(card):
            if to_zone == Zone.HAND:
                player.graveyard.add_card(card)
                print(f"[LOG] {card.get_display_name()} (ID: {card.card_id}) 손패 소지 제한 매수 초과로 묘지로 보내짐.")
            elif to_zone == Zone.FIELD:
                print(f"[LOG] {card.get_display_name()} (ID: {card.card_id}) 필드 소환 제한 매수 초과로 소멸.")
        else:
            # 필드에 들어올 때 리스너 등록
            if to_zone == Zone.FIELD:
                self.game._register_card_listeners(card)
                if card.get_type() == CardType.FOLLOWER:
                    self.game.event_manager.publish(FollowerEnterFieldEvent(card_id=card.card_id, player_id=card.owner_id))

            print(f"[LOG] 카드 {card.get_display_name()} (ID: {card.card_id})이(가) {to_zone.value}로 추가됨.")

    def shuffle_deck(self, player_id: str):
        """지정 플레이어의 덱 셔플"""
        player = self.players[player_id]
        player.deck.shuffle()

    def start_turn(self, player_id: str):
        """지정된 플레이어의 턴을 시작합니다."""
        self.game_phase = GamePhase.START_PHASE
        self.turn_number += 1
        self.current_turn_player_id = player_id
        player = self.players[player_id]
        print(f"[LOG] {player_id}의 {self.turn_number}턴 시작 (시작 단계)")

        # 최대 PP 증가 및 회복
        if player.max_pp < player.MAX_PP:
            player.max_pp += 1
        player.refresh_pp()

        # 진화 가능 턴 처리
        if self.turn_number in [8, 9]:
            player.gain_ep(2)

        # 초진화 가능 턴 처리
        if self.turn_number in [12, 13]:
            player.gain_sep(2)

        # EPP 처리
        if self.turn_number in [2, 12]:
            player.gain_epp(1)

        # 플레이어 EP 소모 상태 리셋
        player.spent_ep_in_turn = False

        # 필드 카드 상태 리셋 (공격/활성화)
        for card in self.get_cards_in_zone(player_id, Zone.FIELD):
            card.is_engaged = False
            card.is_summoned = False
            card.is_activated = False

    def play_card(self, player_id, card_id, enhanced_cost=0):
        """지정 카드를 사용"""
        player = self.players[player_id]
        card = self.get_entity_by_id(card_id, Zone.HAND)
        if not card:
            print(f"[ERROR] play_card - card with id {card_id} not found.")
            return

        if enhanced_cost:
            player.spend_pp(enhanced_cost)
            print(f"[LOG] {player_id}가 {card.get_display_name()} (ID: {card_id})을(를) PP {enhanced_cost} 소모하여 플레이함. 남은 PP: {player.current_pp}")
        else:
            player.spend_pp(card.current_cost)
            print(f"[LOG] {player_id}가 {card.get_display_name()} (ID: {card_id})을(를) PP {card.current_cost} 소모하여 플레이함. 남은 PP: {player.current_pp}")

        # 카드 타입에 따른 처리
        if card.get_type() in [CardType.FOLLOWER, CardType.AMULET]:
            self.move_card(card_id, Zone.HAND, Zone.FIELD)
            # 마법진인 경우 카운트다운 초기화
            if card.get_type() == CardType.AMULET and card.has_keyword(EffectType.COUNTDOWN):
                for effect in card.effects:
                    if effect.type == EffectType.COUNTDOWN:
                        card.countdown_value = effect.value

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
        print(f"[ERROR] get_entity_by_id - ID {entity_id}를 찾을 수 없습니다.")

    def get_card_name(self, entity_id: str) -> str:
        """Player나 Card의 ID로 이름 조회"""
        entity = self.get_entity_by_id(entity_id)
        if entity:
            return entity.get_display_name()
        print(f"[ERROR] get_card_name - ID {entity_id}를 찾을 수 없습니다.")

    def get_type(self, entity_id: str) -> str:
        """Player나 Card의 ID로 타입 조회"""
        entity = self.get_entity_by_id(entity_id)
        if entity:
            return entity.get_type()
        print(f"[ERROR] get_type - ID {entity_id}를 찾을 수 없습니다.")

    def get_card_effects(self, entity_id: str, effect_type: EffectType) -> List[Effect]:
        """Player나 Card의 ID로 키워드 효과 조회"""
        entity = self.get_entity_by_id(entity_id)
        if entity:
            return [effect for effect in entity.effects if effect.type == effect_type]
        print(f"[ERROR] get_card_effects - ID {entity_id}를 찾을 수 없습니다.")
        return []

    def get_owner(self, card_id: str):
        """Card의 ID로 owner ID 조회"""
        entity = self.get_entity_by_id(card_id)
        if entity:
            return entity.owner_id
        print(f"[ERROR] get_owner - ID {card_id}를 찾을 수 없습니다.")


    def evolve_card(self, card_id: str):
        """지정 카드 진화"""
        card: Card
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            card.is_evolved = True
            card.current_attack += 2
            card.current_defense += 2
            card.max_defense += 2

    def super_evolve_card(self, card_id: str):
        """지정 카드 초진화"""
        card: Card
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            card.is_evolved = True
            card.is_super_evolved = True
            card.current_attack += 3
            card.current_defense += 3
            card.max_defense += 3

    def get_cards_with_keyword(self, player_id: str, zone: Zone, keyword: EffectType):
        """지정 플레이어의 특정 필드에서 해당 키워드를 가진 카드 리스트 반환"""
        return [card.card_id for card in self.players[player_id].zone_dict[zone].get_cards() if card.has_keyword(keyword)]

    def countdown(self, card_id: str):
        """지정 카드의 카운트다운 처리"""
        entity = self.get_entity_by_id(card_id, Zone.FIELD)
        if entity:
            entity.countdown_value -= 1
            if entity.countdown_value == 0:
                return True
            return False
        print(f"[ERROR] countdown - 카드 ID {card_id}를 찾을 수 없습니다.")
        return False

    def get_card_info_hand(self, card_id: str):
        """지정 카드의 정보 전달(name, type, cost)"""
        entity: Card
        entity = self.get_entity_by_id(card_id, Zone.HAND)
        if entity:
            return entity.get_display_name(), entity.get_type(), entity.current_cost
        print(f"[ERROR] get_card_info_hand - 카드 ID {card_id}를 찾을 수 없습니다.")
        return None, None, None


    def get_card_info_field(self, card_id: str):
        """지정 카드의 정보 전달(name, type, attack, defense, countdown_value, effect_types)"""
        entity: Card
        entity = self.get_entity_by_id(card_id, Zone.FIELD)
        if entity:
            return entity.get_display_name(), entity.get_type(), entity.current_attack, entity.current_defense, entity.countdown_value, [effect.type for effect in entity.effects]
        print(f"[ERROR] get_card_info_field - 카드 ID {card_id}를 찾을 수 없습니다.")
        return None, None, None, None, None, None

    def get_pp_info(self, player_id: str):
        """지정 플레이어의 pp 정보 전달(current_pp, max_pp)"""
        player = self.players[player_id]
        if player:
            return player.current_pp, player.max_pp
        print(f"[ERROR] get_pp_info - 플레이어 ID {player_id}를 찾을 수 없습니다.")
        return None, None

    def get_card_attack_info_field(self, card_id: str):
        """지정 카드의 정보 전달(name, type, can_attack_leader, can_attack_follower, attack, defense, is_evolved, is_super_evolved)"""
        card: Card
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            return card.get_display_name(), card.get_type(), card.can_attack(TargetType.OPPONENT_LEADER), card.can_attack(TargetType.OPPONENT_FOLLOWER_CHOICE), card.current_attack, card.current_defense, card.is_evolved, card.is_super_evolved
        print(f"[ERROR] get_card_attack_info_field - 카드 ID {card_id}를 찾을 수 없습니다.")
        return None, None, None, None, None, None, None, None

    def can_evolve(self, player_id: str) -> bool:
        """플레이어의 진화 가능 여부 전달"""
        player = self.players[player_id]
        if player:
            return self.players[player_id].current_ep > 0 and not self.players[player_id].spent_ep_in_turn
        print(f"[ERROR] can_evolve - 플레이어 ID {player_id}를 찾을 수 없습니다.")
        return False

    def can_super_evolve(self, player_id: str) -> bool:
        """플레이어의 초진화 가능 여부 전달"""
        player = self.players[player_id]
        if player:
            return self.players[player_id].current_sep > 0 and not self.players[player_id].spent_ep_in_turn
        print(f"[ERROR] can_super_evolve - 플레이어 ID {player_id}를 찾을 수 없습니다.")
        return False

    def has_keyword(self, card_id: str, effect_type: EffectType):
        """지정 카드의 특정 키워드 보유 여부 전달"""
        card: Card
        card = self.get_entity_by_id(card_id)
        if card:
            return card.has_keyword(effect_type)
        print(f"[ERROR] has_keyword - 카드 ID {card_id}를 찾을 수 없습니다.")
        return False

    def evolve_card_with_ep(self, card_id: str, player_id:str):
        """EP를 사용한 지정 카드 진화
        :rtype: object
        """
        card: Card
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            if self.can_evolve(player_id) and not card.is_evolved:
                player = self.players[player_id]
                player.spend_ep(1)
                player.spent_ep_in_turn = True
                self.evolve_card(card_id)
            else:
                print(f"[LOG] 규칙상 처리 불가능한 진화 요청 (카드 ID: {card_id}, 플레이어 ID: {player_id})")
        else:
            print(f"[ERROR] evolve_card_with_ep - 카드 ID {card_id}를 찾을 수 없습니다.")

    def turn_off_super_evolve(self, player_id: str):
        """턴 종료로 초진화턴 면역 버프 무력화"""
        player = self.players[player_id]
        if player:
            for card in self.players[player_id].field.get_cards():
                card.is_super_evolved_turn = False
        else:
            print(f"[ERROR] turn_off_super_evolve - 플레이어 ID {player_id}를 찾을 수 없습니다.")

    def super_evolve_card_with_sep(self, card_id: str, player_id: str):
        """SEP를 사용한 지정 카드 초진화"""
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            if self.can_super_evolve(player_id) and not card.is_evolved:
                player = self.players[player_id]
                player.spend_sep(1)
                player.spent_ep_in_turn = True
                self.super_evolve_card(card_id)
            else:
                print(f"[LOG] 규칙상 처리 불가능한 초진화 요청 (카드 ID: {card_id}, 플레이어 ID: {player_id})")
        else:
            print(f"[ERROR] super_evolve_card_with_sep - 카드 ID {card_id}를 찾을 수 없습니다.")

    def get_player_defense(self, player_id: str) -> int:
        """지정된 플레이어의 현재 체력을 반환합니다."""
        return self.players[player_id].current_defense

    def activate_amulet(self, card_id: str, player_id: str):
        """지정된 마법진 카드를 활성화합니다."""
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        player = self.players[player_id]
        card.is_activated = True

        # 활성화에 코스트가 있고 PP 부족
        activate_effect: Effect = self.get_card_effects(card_id, EffectType.ACTIVATE)[0]
        if activate_effect.cost is not None:
            cost = activate_effect.cost
            player.spend_pp(cost)