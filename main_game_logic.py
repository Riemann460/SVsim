from functools import partial
from typing import Dict, Any
from collections import defaultdict

from card import Card
from enums import GamePhase, EventType, Zone, EffectType, CardType
from event_manager import EventManager
from game_state_manager import GameStateManager
from player import Player
from effect_processor import EffectProcessor
import card_data
from rule_engine import RuleEngine
from gui import GameGUI
from effect import Effect
from listener import Listener
from event import (
    Event,
    CardPlayedEvent,
    DestroyedOnFieldEvent,
    AttackDeclaredEvent,
    CombatInitiatedEvent,
    FollowerEvolvedEvent,
    AmuletActivatedEvent,
    FollowerSuperEvolvedEvent,
    SpellCastEvent,
    TurnStartEvent,
    TurnEndEvent,
    DamageDealtByCombatEvent,
    FollowerEnterFieldEvent
)


class Game:
    """
    게임 전체 흐름을 관리하는 객체
    주요 역할:
    1. 플레이어의 요청 처리
    2. 게임 보드의 이벤트에 따른 효과 처리
    3. 효과 처리로 인한 변화를 게임 보드에 적용
    """

    def __init__(self, player1_id: str, player2_id: str):
        """Game 클래스의 생성자입니다."""
        self.game_state_manager = GameStateManager()
        self.game_state_manager.game = self  # Game 인스턴스 전달
        self.event_manager = EventManager()
        self.listener_ref_counts = defaultdict(int)
        self.effect_processor = EffectProcessor(self.event_manager)
        self.rule_engine = RuleEngine(self.game_state_manager)
        self.opponent_id = {player1_id: player2_id, player2_id: player1_id}
        self.gui = GameGUI(self.game_state_manager)

        self.game_state_manager.players[player1_id] = Player(player1_id, self.event_manager)
        self.game_state_manager.players[player2_id] = Player(player2_id, self.event_manager)
        self.game_state_manager.opponent_id = self.opponent_id
        self.game_state_manager.current_turn_player_id = player1_id  # 선공
        self.game_state_manager.turn_number = 0

        self._setup_global_listeners()
        self._initialize_decks(player1_id, player2_id)
        self._initial_draw(player1_id, player2_id)
        self._start_turn(player1_id)
        self.gui.update()

    def request_user_choice(self, prompt: str, choices: Dict[str, Any]) -> Any:
        """사용자에게 선택을 요청하고 그 결과를 반환합니다."""
        return self.gui.get_user_choice(prompt, choices)

    def resolve_effects_type(self, caster_card_id: str, effect_type: EffectType, target_id: str):
        """특정 카드에 대해 지정된 타입의 모든 효과를 해결합니다."""
        effect_list = self.game_state_manager.get_card_effects(caster_card_id, effect_type)
        if effect_list:
            for effect in effect_list:
                self.effect_processor.resolve_effect(effect, caster_card_id, self.game_state_manager, target_id)
            return True
        return False

    def process_events(self):
        """이벤트 큐에 있는 모든 이벤트를 처리합니다."""
        self.event_manager.process_events()

    def _setup_global_listeners(self):
        """전역 이벤트 리스너 설정 (필드 카드에 귀속되지 않음)"""
        self.event_manager.subscribe(
            Listener('global_spell_cast', EventType.SPELL_CAST, self._on_spell_cast))

    def _register_card_listeners(self, card: Card):
        """카드의 능력에 따라 이벤트 리스너를 동적으로 등록합니다."""
        for event_type, effect in card.card_data.required_listeners:
            # Card-specific listeners
            if event_type in [EventType.CARD_PLAYED, EventType.DESTROYED_ON_FIELD, EventType.ATTACK_DECLARED,
                              EventType.COMBAT_INITIATED, EventType.FOLLOWER_EVOLVED, EventType.AMULET_ACTIVATED,
                              EventType.DAMAGE_DEALT_BY_COMBAT]:
                handler = partial(self._handle_card_effect, effect_to_resolve=effect)
                listener_id = f"{card.card_id}_{effect.type.name}_{id(effect)}"
                condition = lambda event: True
                if effect.type == EffectType.ENHANCE:
                    condition = lambda event: event.enhanced_cost >= effect.enhance_cost
                elif effect.type == EffectType.ON_EVOLVE:
                    condition = lambda event: event.spend_ep
                self.event_manager.subscribe(
                    Listener(id=listener_id, event_type=event_type, callback=handler, card_id=card.card_id,
                             condition=condition))

            elif event_type == EventType.FOLLOWER_SUPER_EVOLVED:
                handler = self._on_follower_super_evolved
                listener_id = f"{card.card_id}_{effect.type.name}_{id(effect)}"
                condition = lambda event: True
                if effect.type in [EffectType.ON_EVOLVE, EffectType.ON_SUPER_EVOLVE]:
                    condition = lambda event: event.spend_sep
                self.event_manager.subscribe(
                    Listener(id=listener_id, event_type=event_type, callback=handler, card_id=card.card_id,
                             condition=condition))

            # Player-specific listeners
            else:
                listener_id, callback = {
                    EventType.TURN_START: ('global_turn_start', self._on_turn_start),
                    EventType.TURN_END: ('global_turn_end', self._on_turn_end),
                    EventType.FOLLOWER_ENTER_FIELD: ('global_follower_enter', self._on_follower_enter_field)
                }.get(event_type)

                if self.listener_ref_counts[listener_id] == 0:
                    self.event_manager.subscribe(Listener(listener_id, event_type, callback))
                self.listener_ref_counts[listener_id] += 1

    def _unregister_card_listeners(self, card: Card):
        """필드에서 벗어나는 카드의 모든 리스너를 해제합니다."""
        for event_type, effect in card.card_data.required_listeners:
            # Card-specific listeners
            if event_type in [EventType.CARD_PLAYED, EventType.DESTROYED_ON_FIELD, EventType.ATTACK_DECLARED,
                              EventType.COMBAT_INITIATED, EventType.FOLLOWER_EVOLVED, EventType.FOLLOWER_SUPER_EVOLVED,
                              EventType.AMULET_ACTIVATED, EventType.DAMAGE_DEALT_BY_COMBAT]:
                listener_id = f"{card.card_id}_{effect.type.name}_{id(effect)}"
                self.event_manager.unsubscribe(event_type, listener_id)

            # Player-specific listeners
            else:
                listener_id, _ = {
                    EventType.TURN_START: ('global_turn_start', self._on_turn_start),
                    EventType.TURN_END: ('global_turn_end', self._on_turn_end),
                    EventType.FOLLOWER_ENTER_FIELD: ('global_follower_enter', self._on_follower_enter_field)
                }.get(event_type)

                self.listener_ref_counts[listener_id] -= 1
                if self.listener_ref_counts[listener_id] == 0:
                    self.event_manager.unsubscribe(event_type, listener_id)

    def _handle_card_effect(self, event: Event, effect_to_resolve: Effect):
        """카드 효과를 처리하는 콜백 핸들러입니다."""
        card_id = event.card_id
        target_id = getattr(event, 'target_id', None)
        print(f"[LOG] 핸들러 처리: 이벤트 '{event.event_type.name}' -> 카드 ID '{card_id}'의 이펙트 '{effect_to_resolve.type.name}'")
        self.effect_processor.resolve_effect(effect_to_resolve, card_id, self.game_state_manager, target_id)

    def _on_follower_super_evolved(self, event: FollowerSuperEvolvedEvent):
        """초진화 효과 처리"""
        card_id = event.card_id
        effect_trigger_types = [EffectType.ON_SUPER_EVOLVE, EffectType.SUPER_EVOLVED, EffectType.ON_EVOLVE,
                                EffectType.EVOLVED]

        for effect_trigger_type in effect_trigger_types:
            if self.game_state_manager.has_keyword(card_id, effect_trigger_type):
                print(
                    f"[LOG] 초진화 효과 처리: 대상 카드: {self.game_state_manager.get_card_name(card_id)} -> 이펙트 '{effect_trigger_type.name}'")
                self.resolve_effects_type(card_id, effect_trigger_type)
                break  # 초진화시 효과가 있다면, 진화시 효과는 발동하지 않게 설정

    def _on_spell_cast(self, event: SpellCastEvent):
        """주문 증폭 효과 처리"""
        player_id = event.player_id
        cards_with_spellboost = self.game_state_manager.get_cards_with_keyword(player_id, Zone.FIELD,
                                                                               EffectType.SPELLBOOST)
        if cards_with_spellboost:
            print(
                f"[LOG] {player_id}의 주문 증폭 효과 처리. 대상 카드: {[self.game_state_manager.get_card_name(card_id) for card_id in cards_with_spellboost]}")
        for card_id in cards_with_spellboost:
            self.resolve_effects_type(card_id, EffectType.SPELLBOOST)

    def _on_turn_start(self, event: TurnStartEvent):
        """카운트다운 효과 처리"""
        player_id = event.player_id
        cards_with_countdown = self.game_state_manager.get_cards_with_keyword(player_id, Zone.FIELD,
                                                                              EffectType.COUNTDOWN)
        for card_id in cards_with_countdown:
            print(f"[LOG] {self.game_state_manager.get_card_name(card_id)} (ID: {card_id}) 카운트다운 감소.")
            if self.game_state_manager.countdown(card_id):
                print(f"[LOG] {self.game_state_manager.get_card_name(card_id)} (ID: {card_id}) 카운트다운 0. 필드에서 묘지로 이동.")
                self.game_state_manager.move_card(card_id, Zone.FIELD, Zone.GRAVEYARD)
                self.event_manager.publish(DestroyedOnFieldEvent(card_id=card_id))
                self.process_events()

    def _on_turn_end(self, event: TurnEndEvent):
        """턴 종료 효과 처리"""
        player_id = event.player_id
        opponent_id = self.opponent_id[player_id]

        cards_with_my_turn_end = self.game_state_manager.get_cards_with_keyword(player_id, Zone.FIELD,
                                                                                EffectType.ON_MY_TURN_END)
        for card_id in cards_with_my_turn_end:
            self.resolve_effects_type(card_id, EffectType.ON_MY_TURN_END)

        cards_with_opponent_turn_end = self.game_state_manager.get_cards_with_keyword(opponent_id, Zone.FIELD,
                                                                                      EffectType.ON_OPPONENTS_TURN_END)
        for card_id in cards_with_opponent_turn_end:
            self.resolve_effects_type(card_id, EffectType.ON_OPPONENTS_TURN_END)

    def _on_damage_dealt(self, event: DamageDealtByCombatEvent):
        """흡혈 효과 처리"""
        attacker_id = event.attacker_id
        attacker = self.game_state_manager.get_entity_by_id(attacker_id, Zone.FIELD)
        if attacker and attacker.has_keyword(EffectType.DRAIN):
            owner = self.game_state_manager.players[attacker.owner_id]
            owner.heal_damage(event.damage)
            print(
                f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 흡혈 효과 발동. {owner.player_id} {event.damage}만큼 회복.")

    def _on_follower_enter_field(self, event: FollowerEnterFieldEvent):
        """필드 소환 효과 처리"""
        player_id = event.player_id
        cards_with_enter_field = self.game_state_manager.get_cards_with_keyword(player_id, Zone.FIELD,
                                                                                EffectType.ON_FOLLOWER_ENTER_FIELD)
        if cards_with_enter_field:
            print(
                f"[LOG] {player_id}의 필드 소환 처리. 대상 카드: {[self.game_state_manager.get_card_name(card_id) for card_id in cards_with_enter_field]}")
        for card_id in cards_with_enter_field:
            self.resolve_effects_type(card_id, EffectType.ON_FOLLOWER_ENTER_FIELD, target_id=event.card_id)

    def _initialize_decks(self, player1_id: str, player2_id: str):
        """초기 덱 설정 (40장, 3장 제한)"""
        # 예시 카드 데이터
        card_data_list = [
            card_data.BASIC_CARD_DATABASE["Indomitable Fighter"],
            card_data.BASIC_CARD_DATABASE["Leah, Bellringer Angel"],
            card_data.BASIC_CARD_DATABASE["Quake Goliath"],
            card_data.BASIC_CARD_DATABASE["Detective's Lens"],
            card_data.BASIC_CARD_DATABASE["Arriet, Luxminstrel"],
            card_data.BASIC_CARD_DATABASE["Caravan Mammoth"],
            card_data.BASIC_CARD_DATABASE["Adventurers' Guild"],
            card_data.LEGENDS_RISE_CARD_DATABASE["Ruby, Greedy Cherub"],
            card_data.LEGENDS_RISE_CARD_DATABASE["Vigilant Detective"],
            card_data.LEGENDS_RISE_CARD_DATABASE["Goblin Foray"],
            card_data.LEGENDS_RISE_CARD_DATABASE["Apollo, Heaven's Envoy"],
            card_data.LEGENDS_RISE_CARD_DATABASE["Seraphic Tidings"],
            card_data.LEGENDS_RISE_CARD_DATABASE["Phildau, Lionheart Ward"],
            card_data.LEGENDS_RISE_CARD_DATABASE["Divine Thunder"]
        ]
        player1_deck = []
        player2_deck = []
        for _ in range(3):
            for data in card_data_list[:12]:
                player1_deck.append(self.game_state_manager.create_card_instance(data, player1_id))
                player2_deck.append(self.game_state_manager.create_card_instance(data, player2_id))
        for _ in range(2):
            for data in card_data_list[12:]:
                player1_deck.append(self.game_state_manager.create_card_instance(data, player1_id))
                player2_deck.append(self.game_state_manager.create_card_instance(data, player2_id))

        for card in player1_deck:
            self.game_state_manager.add_card(card, Zone.DECK, player1_id)
        for card in player2_deck:
            self.game_state_manager.add_card(card, Zone.DECK, player2_id)

        self.game_state_manager.shuffle_deck(player1_id)
        self.game_state_manager.shuffle_deck(player2_id)

    def _initial_draw(self, player1_id: str, player2_id: str):
        """초기 드로우 및 멀리건"""
        print("[LOG] 초기 드로우 단계 시작")
        for _ in range(4):
            self._draw_card(player1_id)
            self._draw_card(player2_id)
        print("[LOG] 멀리건 단계 시작")
        self._perform_mulligan(player1_id)
        self._perform_mulligan(player2_id)

    def _perform_mulligan(self, player_id: str):
        """플레이어의 멀리건을 수행합니다."""
        print(f"[LOG] {player_id} 멀리건 시작")
        hand = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)
        if not hand:
            print(f"[LOG] {player_id} 손에 카드가 없어 멀리건을 진행할 수 없습니다.")
            return

        # 1. 현재 패 보여주기
        hand_cards_obj = [self.game_state_manager.get_entity_by_id(card_id, Zone.HAND) for card_id in hand]

        # 2. GUI를 통해 멀리건할 카드 선택
        cards_to_mulligan_ids = self.gui.get_mulligan_choices(player_id, hand_cards_obj)

        # 3. 멀리건할 카드 식별 및 덱으로 이동
        print(f"[LOG] 멀리건할 카드 ID: {cards_to_mulligan_ids}")  # DEBUG
        for card_id in cards_to_mulligan_ids:
            self.game_state_manager.move_card(card_id, Zone.HAND, Zone.DECK)

        # 4. 덱 셔플
        print(f"[LOG] {player_id} 덱 셔플.")
        self.game_state_manager.shuffle_deck(player_id)

        # 5. 교체한 카드 수만큼 새로 드로우
        num_to_draw = len(cards_to_mulligan_ids)
        if num_to_draw > 0:
            print(f"[LOG] {player_id} {num_to_draw}장 카드 새로 드로우.")
        for _ in range(num_to_draw):
            self._draw_card(player_id)
        print(
            f"[LOG] {player_id} 멀리건 종료. 최종 손패: {[self.game_state_manager.get_card_name(card_id) for card_id in self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)]}")

    def _start_turn(self, player_id: str):
        """플레이어의 턴을 시작합니다."""
        self.game_state_manager.game_phase = GamePhase.START_PHASE
        self.game_state_manager.start_turn(player_id)

        # 턴 시작 시 카드 1장 드로우
        self._draw_card(player_id)

        # 턴 시작 이벤트 처리
        self.event_manager.publish(TurnStartEvent(player_id=player_id, turn_number=self.game_state_manager.turn_number))
        self.process_events()

        self.game_state_manager.game_phase = GamePhase.MAIN_PHASE

    def _draw_card(self, player_id: str):
        """플레이어가 덱에서 카드를 한 장 뽑습니다."""
        deck = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.DECK)
        if not deck:
            print(f"[LOG] 게임 종료: {player_id} 덱 아웃!")
            # 게임 종료 로직 (패배 처리)
            return

        drawn_card_id = deck.pop(0)
        self.game_state_manager.move_card(drawn_card_id, Zone.DECK, Zone.HAND)
        print(
            f"[LOG] {player_id}가 {self.game_state_manager.get_card_name(drawn_card_id)} (ID: {drawn_card_id})를 드로우했습니다.")

    def play_card(self, player_id: str, card_id: str, enhanced_cost=0, use_extra_pp=False):
        """카드 플레이 요청 처리"""
        if not self.rule_engine.validate_play_card(card_id, player_id, use_extra_pp):
            print(f"[LOG] {self.game_state_manager.get_card_name(card_id)} (ID: {card_id}) 카드 플레이 유효성 검사 실패.")
            return False

        # 코스트, 필드 소환은 GSM에서 처리
        self.game_state_manager.play_card(player_id, card_id, enhanced_cost)

        # 카드에 정의된 즉발 효과 해결
        self.event_manager.publish(CardPlayedEvent(card_id=card_id, enhanced_cost=enhanced_cost))
        self.process_events()
        self.gui.update()
        return True

    def attack_leader(self, attacker_id: str):
        """추종자로 리더 공격 요청 처리"""
        attacker = self.game_state_manager.get_entity_by_id(attacker_id, Zone.FIELD)
        if not attacker:
            return False

        target = self.game_state_manager.players[self.opponent_id[attacker.owner_id]]

        if not self.rule_engine.validate_attack(attacker_id, target.player_id):
            print(f"[LOG] {self.game_state_manager.get_card_name(attacker_id)} (ID: {attacker_id})의 리더 공격 유효성 검사 실패.")
            return False

        print(
            f"[LOG] {self.game_state_manager.get_card_name(attacker_id)} (ID: {attacker_id})이(가) {target.player_id}을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(AttackDeclaredEvent(card_id=attacker_id, target_id=target.player_id))
        self.process_events()

        # 실제 전투 데미지 처리
        # 배리어 처리
        target_damage_taken = attacker.current_attack
        if target.has_keyword(EffectType.BARRIER):
            print(f"[LOG] {target.get_display_name()} (ID: {target.player_id}) 배리어로 데미지 0 받음.")
            target_damage_taken = 0
            target.effects = [effect for effect in target.effects if effect.type != EffectType.BARRIER]

        target.take_damage(target_damage_taken)

        # 흡혈 효과
        self.event_manager.publish(DamageDealtByCombatEvent(card_id=attacker_id, damage=target_damage_taken))
        self.process_events()

        self.process_events()

        attacker.is_engaged = True  # 공격 완료 표시
        self.gui.update()
        return True

    def attack_follower(self, attacker_id: str, target_id: str):
        """추종자로 추종자 공격 요청 처리"""
        attacker = self.game_state_manager.get_entity_by_id(attacker_id, Zone.FIELD)
        target = self.game_state_manager.get_entity_by_id(target_id, Zone.FIELD)

        if not attacker or not target:
            return False

        if not self.rule_engine.validate_attack(attacker_id, target_id):
            print(
                f"[LOG] {self.game_state_manager.get_card_name(attacker_id)} (ID: {attacker_id})의 {self.game_state_manager.get_card_name(target_id)} (ID: {target_id}) 공격 유효성 검사 실패.")
            return False

        print(
            f"[LOG] {self.game_state_manager.get_card_name(attacker_id)} (ID: {attacker_id})이(가) {self.game_state_manager.get_card_name(target_id)} (ID: {target_id})을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(AttackDeclaredEvent(card_id=attacker_id, target_id=target_id))
        self.process_events()

        # 교전시 효과
        self.event_manager.publish(CombatInitiatedEvent(card_id=attacker_id, target_id=target_id))
        self.process_events()

        # 교전시 효과로 파괴됐을 때 처리 추가 필요
        # 실제 전투 데미지 처리
        # 배리어 처리
        attacker_damage_taken = target.current_attack
        target_damage_taken = attacker.current_attack

        if attacker.has_keyword(EffectType.BARRIER):
            print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 배리어로 데미지 0 받음.")
            attacker_damage_taken = 0
            attacker.effects = [effect for effect in target.effects if effect.type != EffectType.BARRIER]

        if target.has_keyword(EffectType.BARRIER):
            print(f"[LOG] {target.card_data['name']} (ID: {target_id}) 배리어로 데미지 0 받음.")
            target_damage_taken = 0
            target.effects = [effect for effect in target.effects if effect.type != EffectType.BARRIER]

        target_destroyed = target.take_damage(target_damage_taken)

        if attacker.has_keyword(EffectType.BANE):
            print(
                f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 필살 능력으로 {target.get_display_name()} (ID: {target_id}) 파괴됨.")
            target_destroyed = True

        if attacker.is_super_evolved:
            print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 초진화 효과로 데미지 0 받음.")
            attacker_damage_taken = 0
            if target_destroyed:
                print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 초진화 효과로 상대 리더에게 데미지 1.")
                self.game_state_manager.players[target.owner_id].take_damage(1)

        attacker_destroyed = attacker.take_damage(attacker_damage_taken)

        # 흡혈 효과
        self.event_manager.publish(DamageDealtByCombatEvent(card_id=attacker_id, damage=target_damage_taken))
        self.process_events()

        attacker.is_engaged = True  # 공격 완료 표시

        # 필살 효과
        if target.has_keyword(EffectType.BANE):
            print(
                f"[LOG] {target.get_display_name()} (ID: {target_id}) 필살 능력으로 {attacker.get_display_name()} (ID: {attacker_id}) 파괴됨.")
            attacker_destroyed = True

        # 파괴된 추종자 묘지로 이동 및 유언 처리
        if target_destroyed:
            self.event_manager.publish(DestroyedOnFieldEvent(card_id=target_id))
            self.process_events()
            self.game_state_manager.move_card(target_id, Zone.FIELD, Zone.GRAVEYARD)
        if attacker_destroyed:
            self.event_manager.publish(DestroyedOnFieldEvent(card_id=attacker_id))
            self.process_events()
            self.game_state_manager.move_card(attacker_id, Zone.FIELD, Zone.GRAVEYARD)
        self.gui.update()
        return True

    def end_turn(self, player_id: str):
        """턴 종료 요청 처리"""
        self.game_state_manager.game_phase = GamePhase.END_PHASE
        print(f"[LOG] {player_id}의 턴 종료 (종료 단계)")

        self.event_manager.publish(TurnEndEvent(player_id=player_id))
        self.process_events()

        self.game_state_manager.turn_off_super_evolve(player_id)  # 초진화 면역 무력화

        # 다음 턴 플레이어 설정
        opponent_id = self.opponent_id[player_id]
        self.game_state_manager.current_turn_player_id = opponent_id
        print(f"[LOG] {player_id} 턴 종료. {opponent_id}의 턴으로 전환.")
        self._start_turn(opponent_id)
        self.gui.update()

    def get_opponent_id(self, player_id: str) -> str:
        """상대 플레이어 ID 반환"""
        return self.opponent_id[player_id]

    def evolve_follower(self, card_id: str, player_id: str):
        """EP를 소모하는 진화 처리"""
        self.game_state_manager.evolve_card_with_ep(card_id, player_id)
        self.event_manager.publish(FollowerEvolvedEvent(card_id=card_id, spend_ep=True))
        self.process_events()
        self.gui.update()

    def super_evolve_follower(self, card_id: str, player_id: str):
        """SEP를 소모하는 초진화 처리"""
        self.game_state_manager.super_evolve_card_with_sep(card_id, player_id)
        self.event_manager.publish(FollowerSuperEvolvedEvent(card_id=card_id, spend_sep=True))
        self.process_events()
        self.gui.update()

    def activate_amulet(self, card_id: str, player_id: str):
        """마법진 활성화 처리"""
        self.game_state_manager.activate_amulet(card_id, player_id)
        self.event_manager.publish(AmuletActivatedEvent(card_id=card_id))
        self.process_events()
        self.gui.update()

    def get_start_turn_ifo(self, player_id: str):
        """턴 시작 시 필요한 정보를 가져옵니다."""
        current_pp, max_pp = self.game_state_manager.get_pp_info(player_id)
        player_field_card_ids = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.FIELD)
        opponent_field_card_ids = self.game_state_manager.get_card_ids_in_zone(self.opponent_id[player_id], Zone.FIELD)
        return current_pp, max_pp, player_field_card_ids, opponent_field_card_ids

    def get_playable_cards_id(self, player_id: str, use_extra_pp: bool):
        """플레이 가능한 카드의 ID 목록을 가져옵니다."""
        player_hand_id = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)
        return player_hand_id, [self.rule_engine.validate_play_card(card_id, player_id, use_extra_pp) for card_id in
                                player_hand_id]

    def has_extra_pp(self, player_id: str):
        """플레이어가 엑스트라 PP를 가지고 있는지 확인합니다."""
        return self.game_state_manager.get_entity_by_id(player_id).extra_pp > 0

    def get_available_actions(self, card_id: str, player_id: str):
        """대상 필드 카드의 가능한 조작 목록을 출력"""
        card_name, card_type, can_attack_leader, can_attack_follower, _, _, is_evolved, _ = self.game_state_manager.get_card_attack_info_field(
            card_id)
        available_actions = []

        if card_type == CardType.FOLLOWER and can_attack_follower:
            available_actions.append("추종자 공격")

        if card_type == CardType.FOLLOWER and not is_evolved and self.game_state_manager.can_evolve(player_id):
            available_actions.append("추종자 진화")

        if card_type == CardType.FOLLOWER and not is_evolved and self.game_state_manager.can_super_evolve(player_id):
            available_actions.append("추종자 초진화")

        if card_type == CardType.AMULET and self.game_state_manager.has_keyword(card_id,
                                                                                EffectType.ACTIVATE) and self.rule_engine.validate_activate_amulet(
                card_id, player_id):
            available_actions.append("마법진 활성화")

        return available_actions, card_name
