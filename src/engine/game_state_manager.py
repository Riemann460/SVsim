# 역할 정의. 게임의 전반적인 상태를 추적하고 조작하는 클래스입니다.

from typing import List, Dict, Any, Optional

from src.common.enums import GamePhase, CardType, Zone, EffectType, TargetType
from src.models.card import Card
from src.models.player import Player
from src.common.effect import Effect
from src.common.event import FollowerEnterFieldEvent


class GameStateManager:
    """게임 보드 상태를 관리하는 객체입니다."""

    def __init__(self):
        """GameStateManager 클래스의 생성자입니다."""
        self.players: Dict[str, Player] = {}
        self.opponent_id: Dict[str, str] = {}
        self.current_turn_player_id: Optional[str] = None
        self.turn_number: int = 0
        self.game_phase: Optional[GamePhase] = None
        self.cards = []
        self._next_card_instance_id = 0
        self.game = None  # Game 인스턴스를 참조하기 위한 필드를 추가합니다.
        self.is_awaiting_choice: bool = False
        self.pending_choice: Optional[Effect] = None
        self.player_awaiting_choice: Optional[str] = None

    def create_card_instance(self, card_data_obj, owner_id):
        """새로운 카드 인스턴스를 생성하고 게임에 추가합니다."""
        # card_data_obj 가 str 인 경우 정적 데이터베이스에서 조회하여 치환합니다.
        if isinstance(card_data_obj, str):
            from src.common import card_data as cd
            # 1. card_id 로 먼저 조회해 봅니다.
            resolved = cd.get_card_data_by_id(card_data_obj)
            if not resolved:
                # 2. card_id 가 아니면 카드 영문명 또는 한글명으로 조회해 봅니다.
                # 오염된 찌꺼기 텍스트(예 - "d Rotting Zombie")를 제거하고 원본 매칭을 시도합니다.
                clean_name = card_data_obj.strip()
                if clean_name.startswith("d "):
                    clean_name = clean_name[2:].strip()
                elif clean_name.startswith("and "):
                    clean_name = clean_name[4:].strip()

                for db in [cd.BASIC_CARD_DATABASE, cd.LEGENDS_RISE_CARD_DATABASE, cd.TOKEN_CARD_DATABASE]:
                    for c_data in db.values():
                        if c_data.name == clean_name or c_data.name_ko == clean_name:
                            resolved = c_data
                            break
                    if resolved:
                        break
            if resolved:
                card_data_obj = resolved
            else:
                print(f"[ERROR] create_card_instance - '{card_data_obj}'에 해당하는 카드 데이터를 찾을 수 없습니다.")

        new_card_id = str(self._next_card_instance_id)
        card = Card(card_data_obj, owner_id, new_card_id)
        self.cards.append(card)
        self._next_card_instance_id += 1
        return card

    def get_card_ids_in_zone(self, player_id: str, zone: Zone) -> List[str]:
        """특정 플레이어의 특정 영역에 있는 카드의 ID 목록을 조회합니다."""
        player = self.players[player_id]
        return [card.card_id for card in player.get_cards_in_zone(zone)]

    def get_cards_in_zone(self, player_id: str, zone: Zone, condition=lambda x: True) -> List[Card]:
        """특정 플레이어의 특정 영역에 있는 카드 객체 목록을 반환합니다."""
        player = self.players[player_id]
        return [card for card in player.get_cards_in_zone(zone) if condition(card)]

    def move_card(self, card_id: str, from_zone: Zone, to_zone: Zone):
        """카드를 한 영역에서 다른 영역으로 이동시킵니다."""
        card = self.get_entity_by_id(card_id, from_zone)
        if not card:
            print(f"[ERROR] move_card - card with id {card_id} from zone {from_zone} not found.")
            return

        player = self.players[card.owner_id]
        
        # 필드를 벗어날 때 리스너를 해제합니다.
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
            card.current_zone = to_zone
            # 필드에 들어올 때 리스너를 등록합니다.
            if to_zone == Zone.FIELD:
                self.game._register_card_listeners(card)
                if card.get_type() == CardType.FOLLOWER:
                    self.game.event_manager.publish(FollowerEnterFieldEvent(card_id=card.card_id, player_id=card.owner_id))
                    player.rally_count += 1
            
            print(f"[LOG] 카드 {card.get_display_name()} (ID: {card_id})이(가) {from_zone.value}에서 {to_zone.value}로 이동됨.")

    def add_card(self, card: Card, to_zone: Zone, player_id: str):
        """카드를 지정 영역에 추가합니다."""
        player = self.players[player_id]
        if not player.zone_dict[to_zone].add_card(card):
            if to_zone == Zone.HAND:
                player.graveyard.add_card(card)
                print(f"[LOG] {card.get_display_name()} (ID: {card.card_id}) 손패 소지 제한 매수 초과로 묘지로 보내짐.")
            elif to_zone == Zone.FIELD:
                print(f"[LOG] {card.get_display_name()} (ID: {card.card_id}) 필드 소환 제한 매수 초과로 소멸.")
        else:
            card.current_zone = to_zone
            # 필드에 들어올 때 리스너를 등록합니다.
            if to_zone == Zone.FIELD:
                self.game._register_card_listeners(card)
                if card.get_type() == CardType.FOLLOWER:
                    self.game.event_manager.publish(FollowerEnterFieldEvent(card_id=card.card_id, player_id=card.owner_id))
                    player.rally_count += 1

            print(f"[LOG] 카드 {card.get_display_name()} (ID: {card.card_id})이(가) {to_zone.value}로 추가됨.")

    def shuffle_deck(self, player_id: str):
        """지정 플레이어의 덱을 셔플합니다."""
        player = self.players[player_id]
        player.deck.shuffle()

    def start_turn(self, player_id: str):
        """지정된 플레이어의 턴을 시작합니다."""
        self.game_phase = GamePhase.START_PHASE
        self.turn_number += 1
        self.current_turn_player_id = player_id
        player = self.players[player_id]
        print(f"[LOG] {player_id}의 {self.turn_number}턴 시작 (시작 단계)")

        # 최대 PP를 증가시키고 회복시킵니다.
        if player.max_pp < player.MAX_PP:
            player.max_pp += 1
        player.refresh_pp()

        # 진화 가능 턴을 처리합니다.
        if self.turn_number in [8, 9]:
            player.gain_ep(2)

        # 초진화 가능 턴을 처리합니다.
        if self.turn_number in [12, 13]:
            player.gain_sep(2)

        # EPP를 처리합니다.
        if self.turn_number in [2, 12]:
            player.gain_epp(1)

        # 플레이어 EP 소모 상태를 리셋합니다.
        player.spent_ep_in_turn = False

        # 필드 카드 상태를 리셋합니다. 공격 및 활성화 여부를 초기화합니다.
        for card in self.get_cards_in_zone(player_id, Zone.FIELD):
            card.is_engaged = False
            card.is_summoned = False
            card.attack_count_this_turn = 0

    def play_card(self, player_id, card_id, enhanced_cost=0):
        """지정 카드를 사용합니다."""
        player = self.players[player_id]
        player.combo_count += 1
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

        # 카드 타입에 따른 처리를 수행합니다.
        if card.get_type() in [CardType.FOLLOWER, CardType.AMULET]:
            self.move_card(card_id, Zone.HAND, Zone.FIELD)
            # 마법진인 경우 카운트다운을 초기화합니다.
            if card.get_type() == CardType.AMULET and card.has_keyword(EffectType.COUNTDOWN):
                for effect in card.effects:
                    if effect.type == EffectType.COUNTDOWN:
                        card.countdown_value = effect.value

        elif card.get_type() == CardType.SPELL:
            self.move_card(card_id, Zone.HAND, Zone.GRAVEYARD)  # 주문은 사용 즉시 묘지로 이동합니다.

    def get_entity_by_id(self, entity_id: str, zone: Zone = None) -> Optional[Any]:
        """Player나 Card의 ID로 인스턴스를 조회합니다."""
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
        """Player나 Card의 ID로 이름을 조회합니다."""
        entity = self.get_entity_by_id(entity_id)
        if entity:
            return entity.get_display_name()
        print(f"[ERROR] get_card_name - ID {entity_id}를 찾을 수 없습니다.")

    def get_type(self, entity_id: str) -> str:
        """Player나 Card의 ID로 타입을 조회합니다."""
        entity = self.get_entity_by_id(entity_id)
        if entity:
            return entity.get_type()
        print(f"[ERROR] get_type - ID {entity_id}를 찾을 수 없습니다.")

    def get_card_effects(self, entity_id: str, effect_type: EffectType) -> List[Effect]:
        """Player나 Card의 ID로 키워드 효과들을 조회합니다."""
        entity = self.get_entity_by_id(entity_id)
        if entity:
            return [effect for effect in entity.effects if effect.type == effect_type]
        print(f"[ERROR] get_card_effects - ID {entity_id}를 찾을 수 없습니다.")
        return []

    def get_owner(self, card_id: str):
        """Card의 ID로 소유자 ID를 조회합니다."""
        entity = self.get_entity_by_id(card_id)
        if entity:
            return entity.owner_id
        print(f"[ERROR] get_owner - ID {card_id}를 찾을 수 없습니다.")


    def evolve_card(self, card_id: str):
        """지정 카드를 진화시킵니다."""
        card: Card
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            card.is_evolved = True
            card.current_attack += 2
            card.current_defense += 2
            card.max_defense += 2

    def super_evolve_card(self, card_id: str):
        """지정 카드를 초진화시킵니다."""
        card: Card
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            card.is_evolved = True
            card.is_super_evolved = True
            card.current_attack += 3
            card.current_defense += 3
            card.max_defense += 3

    def get_cards_with_keyword(self, player_id: str, zone: Zone, keyword: EffectType):
        """지정 플레이어의 특정 필드에서 해당 키워드를 가진 카드 리스트를 반환합니다."""
        return [card.card_id for card in self.players[player_id].zone_dict[zone].get_cards() if card.has_keyword(keyword)]

    def countdown(self, card_id: str):
        """지정 카드의 카운트다운을 처리합니다. 카운트다운 수치가 존재할 때만 처리합니다."""
        entity = self.get_entity_by_id(card_id, Zone.FIELD)
        if entity:
            if entity.countdown_value is not None:
                entity.countdown_value -= 1
                if entity.countdown_value == 0:
                    return True
            return False
        print(f"[ERROR] countdown - 카드 ID {card_id}를 찾을 수 없습니다.")
        return False

    def get_card_info_hand(self, card_id: str):
        """지정 카드의 정보를 반환합니다. 이름, 타입, 비용을 포함합니다."""
        entity: Card
        entity = self.get_entity_by_id(card_id, Zone.HAND)
        if entity:
            return entity.get_display_name(), entity.get_type(), entity.current_cost
        print(f"[ERROR] get_card_info_hand - 카드 ID {card_id}를 찾을 수 없습니다.")
        return None, None, None


    def get_card_info_field(self, card_id: str):
        """지정 카드의 정보를 반환합니다. 이름, 타입, 공격력, 체력, 카운트다운 값, 효과 목록을 포함합니다."""
        entity: Card
        entity = self.get_entity_by_id(card_id, Zone.FIELD)
        if entity:
            return entity.get_display_name(), entity.get_type(), entity.current_attack, entity.current_defense, entity.countdown_value, [effect.type for effect in entity.effects]
        print(f"[ERROR] get_card_info_field - 카드 ID {card_id}를 찾을 수 없습니다.")
        return None, None, None, None, None, None

    def get_pp_info(self, player_id: str):
        """지정 플레이어의 PP 정보를 반환합니다. 현재 PP와 최대 PP를 포함합니다."""
        player = self.players[player_id]
        if player:
            return player.current_pp, player.max_pp
        print(f"[ERROR] get_pp_info - 플레이어 ID {player_id}를 찾을 수 없습니다.")
        return None, None

    def get_card_attack_info_field(self, card_id: str):
        """지정 카드의 공격 관련 정보를 반환합니다."""
        card: Card
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        if card:
            return card.get_display_name(), card.get_type(), card.can_attack(TargetType.OPPONENT_LEADER), card.can_attack(TargetType.OPPONENT_FOLLOWER_CHOICE), card.current_attack, card.current_defense, card.is_evolved, card.is_super_evolved
        print(f"[ERROR] get_card_attack_info_field - 카드 ID {card_id}를 찾을 수 없습니다.")
        return None, None, None, None, None, None, None, None

    def can_evolve(self, player_id: str) -> bool:
        """플레이어의 진화 가능 여부를 판단합니다."""
        player = self.players[player_id]
        if player:
            return self.players[player_id].current_ep > 0 and not self.players[player_id].spent_ep_in_turn
        print(f"[ERROR] can_evolve - 플레이어 ID {player_id}를 찾을 수 없습니다.")
        return False

    def can_super_evolve(self, player_id: str) -> bool:
        """플레이어의 초진화 가능 여부를 판단합니다."""
        player = self.players[player_id]
        if player:
            return self.players[player_id].current_sep > 0 and not self.players[player_id].spent_ep_in_turn
        print(f"[ERROR] can_super_evolve - 플레이어 ID {player_id}를 찾을 수 없습니다.")
        return False

    def has_keyword(self, card_id: str, effect_type: EffectType):
        """지정 카드가 특정 키워드를 보유하고 있는지 판단합니다."""
        card: Card
        card = self.get_entity_by_id(card_id)
        if card:
            return card.has_keyword(effect_type)
        print(f"[ERROR] has_keyword - 카드 ID {card_id}를 찾을 수 없습니다.")
        return False

    def evolve_card_with_ep(self, card_id: str, player_id:str):
        """EP를 사용하여 지정된 카드를 진화시킵니다."""
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
        """턴 종료 시점에 초진화턴 면역 버프를 무력화합니다."""
        player = self.players[player_id]
        if player:
            for card in self.players[player_id].field.get_cards():
                card.is_super_evolved_turn = False
        else:
            print(f"[ERROR] turn_off_super_evolve - 플레이어 ID {player_id}를 찾을 수 없습니다.")

    def super_evolve_card_with_sep(self, card_id: str, player_id: str):
        """SEP를 사용하여 지정된 카드를 초진화시킵니다."""
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

    def engage_card(self, card_id: str, player_id: str):
        """지정된 마법진/추종자 카드를 활성화(Engage)합니다."""
        card = self.get_entity_by_id(card_id, Zone.FIELD)
        player = self.players[player_id]
        card.is_engaged = True

        # 활성화 효과 리스트가 비어있다면 조기 리턴합니다.
        engage_effects = self.get_card_effects(card_id, EffectType.ENGAGE)
        if not engage_effects:
            return

        # 활성화에 코스트가 있으면 PP를 소모합니다.
        engage_effect: Effect = engage_effects[0]
        cost = engage_effect.get("cost")
        if cost is not None:
            player.spend_pp(cost)