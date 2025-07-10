from typing import Dict, Any

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


class Game:
    """
    게임 전체 흐름을 관리하는 객체

    주요 역할:
    1. 플레이어의 요청 처리
    2. 게임 보드의 이벤트에 따른 효과 처리
    3. 효과 처리로 인한 변화를 게임 보드에 적용
    """
    def __init__(self, player1_id: str, player2_id: str):
        self.game_state_manager = GameStateManager()
        self.game_state_manager.game = self # Game 인스턴스 전달
        self.event_manager = EventManager()
        self.effect_processor = EffectProcessor(self.event_manager)
        self.rule_engine = RuleEngine(self.game_state_manager)
        self.opponent_id = {player1_id: player2_id, player2_id: player1_id}
        self.gui = GameGUI(self.game_state_manager)

        self.EVENT_TO_EFFECT_TRIGGER_MAP = {
            EventType.CARD_PLAYED: [EffectType.FANFARE, EffectType.SPELL],
            EventType.DESTROYED_ON_FIELD: [EffectType.LAST_WORDS],
            EventType.ATTACK_DECLARED: [EffectType.STRIKE],
            EventType.COMBAT_INITIATED: [EffectType.CLASH],
            EventType.FOLLOWER_EVOLVED: [EffectType.ON_EVOLVE, EffectType.EVOLVED],
            EventType.FOLLOWER_SUPER_EVOLVED: [EffectType.ON_SUPER_EVOLVE, EffectType.SUPER_EVOLVED],
            EventType.AMULET_ACTIVATED: [EffectType.ACTIVATE],
            EventType.TURN_END: [EffectType.ON_MY_TURN_END, EffectType.ON_OPPONENTS_TURN_END],
            EventType.FOLLOWER_ENTER_FIELD: [EffectType.ON_FOLLOWER_ENTER_FIELD]
        }

        self.game_state_manager.players[player1_id] = Player(player1_id, self.event_manager)
        self.game_state_manager.players[player2_id] = Player(player2_id, self.event_manager)
        self.game_state_manager.opponent_id = self.opponent_id
        self.game_state_manager.current_turn_player_id = player1_id  # 선공
        self.game_state_manager.turn_number = 0

        self._setup_listeners()
        self._initialize_decks(player1_id, player2_id)
        self._initial_draw(player1_id, player2_id)
        self._start_turn(player1_id)
        self.gui.update()

    def request_user_choice(self, prompt: str, choices: Dict[str, Any]) -> Any:
        return self.gui.get_user_choice(prompt, choices)

    def resolve_effect(self, effect: Effect, caster_card_id: str):
        self.effect_processor.resolve_effect(effect, caster_card_id, self.game_state_manager)

    def resolve_effects_type(self, caster_card_id: str, effect_type: EffectType):
        effect_list = self.game_state_manager.get_card_effects(caster_card_id, effect_type)
        if effect_list:
            for effect in effect_list:
                self.resolve_effect(effect, caster_card_id)
            return True
        return False

    def process_events(self):
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

    def _setup_listeners(self):
        """이벤트 리스너 설정"""
        for event_type in self.EVENT_TO_EFFECT_TRIGGER_MAP.keys():
            self.event_manager.subscribe(event_type, self._handle_triggered_effect)

        # 범용 핸들러로 처리되지 않는 나머지 이벤트들은 그대로 둠
        self.event_manager.subscribe(EventType.SPELL_CAST, self._on_spell_cast)
        self.event_manager.subscribe(EventType.TURN_START, self._on_turn_start)
        self.event_manager.subscribe(EventType.DAMAGE_DEALT, self._on_damage_dealt)

    def _handle_triggered_effect(self, event_data: Dict[str, Any]):
        event_type = event_data.get('event_type')
        if event_type not in self.EVENT_TO_EFFECT_TRIGGER_MAP:
            return

        effect_trigger_types = self.EVENT_TO_EFFECT_TRIGGER_MAP[event_type]
        
        for effect_trigger_type in effect_trigger_types:
            print(f"[LOG] Universal handler processing: Event '{event_type.name}' -> Effect Trigger '{effect_trigger_type.name}'")

            # 모든 플레이어의 모든 필드 카드를 확인
            for player in self.game_state_manager.players.values():
                for card in player.field.get_cards():
                    self.resolve_effects_type(card.card_id, effect_trigger_type)

    def _on_spell_cast(self, event_data: Dict[str, Any]):
        """주문 증폭 효과 처리"""
        player_id = event_data['player_id']
        cards_with_spellboost = self.game_state_manager.get_cards_with_keyword(player_id, Zone.FIELD, EffectType.SPELLBOOST)
        if cards_with_spellboost:
            print(f"[LOG] {player_id}의 주문 증폭 효과 처리. 대상 카드: {[self.game_state_manager.get_card_name(card_id) for card_id in cards_with_spellboost]}")
        for card_id in cards_with_spellboost:
            self.resolve_effects_type(card_id, EffectType.SPELLBOOST)

    def _on_turn_start(self, event_data: Dict[str, Any]):
        """카운트다운 효과 처리"""
        player_id = event_data['player_id']
        cards_with_countdown = self.game_state_manager.get_cards_with_keyword(player_id, Zone.FIELD, EffectType.COUNTDOWN)
        for card_id in cards_with_countdown:
            print(f"[LOG] {self.game_state_manager.get_card_name(card_id)} (ID: {card_id}) 카운트다운 감소.")
            if self.game_state_manager.countdown(card_id):
                print(f"[LOG] {self.game_state_manager.get_card_name(card_id)} (ID: {card_id}) 카운트다운 0. 필드에서 묘지로 이동.")
                self.game_state_manager.move_card(card_id, Zone.FIELD, Zone.GRAVEYARD)
                self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card_id": card_id})
                self.process_events()
    
    def _on_damage_dealt(self, event_data: Dict[str, Any]):
        """흡혈 효과 처리"""
        attacker_id = event_data['attacker_id']
        attacker = self.game_state_manager.get_entity_by_id(attacker_id, Zone.FIELD)
        if attacker and attacker.has_keyword(EffectType.DRAIN):
            owner = self.game_state_manager.players[attacker.owner_id]
            owner.heal_damage(event_data['damage'])
            print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 흡혈 효과 발동. {owner.player_id} {event_data['damage']}만큼 회복.")

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

    def _perform_mulligan(self, player_id):
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
        print(f"[LOG] 멀리건할 카드 ID: {cards_to_mulligan_ids}") # DEBUG
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
        print(f"[LOG] {player_id} 멀리건 종료. 최종 손패: {[self.game_state_manager.get_card_name(card_id) for card_id in self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)]}")

    def _start_turn(self, player_id: str):
        self.game_state_manager.game_phase = GamePhase.START_PHASE
        self.game_state_manager.start_turn(player_id)

        # 턴 시작 시 카드 1장 드로우
        self._draw_card(player_id)

        # 턴 시작 이벤트 처리
        self.event_manager.publish(EventType.TURN_START,
                                   {"player_id": player_id, "turn_number": self.game_state_manager.turn_number})
        self.process_events()

        self.game_state_manager.game_phase = GamePhase.MAIN_PHASE

    def _draw_card(self, player_id: str):
        deck = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.DECK)
        if not deck:
            print(f"[LOG] 게임 종료: {player_id} 덱 아웃!")
            # 게임 종료 로직 (패배 처리)
            return

        drawn_card_id = deck.pop(0)
        self.game_state_manager.move_card(drawn_card_id, Zone.DECK, Zone.HAND)
        print(f"[LOG] {player_id}가 {self.game_state_manager.get_card_name(drawn_card_id)} (ID: {drawn_card_id})를 드로우했습니다.")

    def play_card(self, player_id: str, card_id: str, enhanced_cost=0, use_extra_pp=False):
        """카드 플레이 요청 처리"""
        if not self.rule_engine.validate_play_card(card_id, player_id, use_extra_pp):
            print(f"[LOG] {self.game_state_manager.get_card_name(card_id)} (ID: {card_id}) 카드 플레이 유효성 검사 실패.")
            return False

        # 코스트, 필드 소환은 GSM에서 처리
        self.game_state_manager.play_card(player_id, card_id, enhanced_cost)

        # 카드에 정의된 즉발 효과 해결
        self.event_manager.publish(EventType.CARD_PLAYED, {"player_id": player_id, "card_id": card_id, 'enhanced_cost': enhanced_cost})
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

        print(f"[LOG] {self.game_state_manager.get_card_name(attacker_id)} (ID: {attacker_id})이(가) {target.player_id}을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(EventType.ATTACK_DECLARED,
                                   {"attacker_id": attacker_id, "target_id": target.player_id})
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
        self.event_manager.publish(EventType.DAMAGE_DEALT,
                                   {"attacker_id": attacker_id, "damage": target_damage_taken})
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
            print(f"[LOG] {self.game_state_manager.get_card_name(attacker_id)} (ID: {attacker_id})의 {self.game_state_manager.get_card_name(target_id)} (ID: {target_id}) 공격 유효성 검사 실패.")
            return False

        print(f"[LOG] {self.game_state_manager.get_card_name(attacker_id)} (ID: {attacker_id})이(가) {self.game_state_manager.get_card_name(target_id)} (ID: {target_id})을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(EventType.ATTACK_DECLARED,
                                   {"attacker_id": attacker_id, "target_id": target_id})
        self.process_events()

        # 교전시 효과
        self.event_manager.publish(EventType.COMBAT_INITIATED,
                                   {"attacker_id": attacker.card_id, "defender_id": target.card_id})
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
            print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 필살 능력으로 {target.get_display_name()} (ID: {target_id}) 파괴됨.")
            target_destroyed = True

        if attacker.is_super_evolved:
            print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 초진화 효과로 데미지 0 받음.")
            attacker_damage_taken = 0
            if target_destroyed:
                print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id}) 초진화 효과로 상대 리더에게 데미지 1.")
                self.game_state_manager.players[target.owner_id].take_damage(1)

        attacker_destroyed = attacker.take_damage(attacker_damage_taken)

        # 흡혈 효과
        self.event_manager.publish(EventType.DAMAGE_DEALT,
                                   {"attacker_id": attacker_id, "damage": target_damage_taken})
        self.process_events()

        attacker.is_engaged = True  # 공격 완료 표시

        # 필살 효과
        if target.has_keyword(EffectType.BANE):
            print(f"[LOG] {target.get_display_name()} (ID: {target_id}) 필살 능력으로 {attacker.get_display_name()} (ID: {attacker_id}) 파괴됨.")
            attacker_destroyed = True

        # 파괴된 추종자 묘지로 이동 및 유언 처리
        if attacker_destroyed:
            self.game_state_manager.move_card(attacker_id, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card_id": attacker_id})
        if target_destroyed:
            self.game_state_manager.move_card(target_id, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card_id": target_id})
        self.process_events()
        self.gui.update()
        return True

    def end_turn(self, player_id: str):
        """턴 종료 요청 처리"""
        self.game_state_manager.game_phase = GamePhase.END_PHASE
        print(f"[LOG] {player_id}의 턴 종료 (종료 단계)")

        self.event_manager.publish(EventType.TURN_END, {"player_id": player_id})
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
        self.event_manager.publish(EventType.FOLLOWER_EVOLVED, {"card_id": card_id, "spend_ep": True})
        self.process_events()
        self.gui.update()

    def super_evolve_follower(self, card_id: str, player_id: str):
        """SEP를 소모하는 초진화 처리"""
        self.game_state_manager.super_evolve_card_with_sep(card_id, player_id)
        self.event_manager.publish(EventType.FOLLOWER_SUPER_EVOLVED, {"card_id": card_id, "spend_sep": True})
        self.process_events()
        self.gui.update()

    def activate_amulet(self, card_id: str, player_id: str):
        """마법진 활성화 처리"""
        self.game_state_manager.activate_amulet(card_id, player_id)
        self.event_manager.publish(EventType.AMULET_ACTIVATED, {"card_id": card_id})
        self.process_events()
        self.gui.update()

    def get_start_turn_ifo(self, player_id: str):
        current_pp, max_pp = self.game_state_manager.get_pp_info(player_id)
        player_field_card_ids = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.FIELD)
        opponent_field_card_ids = self.game_state_manager.get_card_ids_in_zone(self.opponent_id[player_id], Zone.FIELD)
        return current_pp, max_pp, player_field_card_ids, opponent_field_card_ids

    def get_playable_cards_id(self, player_id: str, use_extra_pp: bool):
        player_hand_id = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)
        return player_hand_id, [self.rule_engine.validate_play_card(card_id, player_id, use_extra_pp) for card_id in player_hand_id]

    def has_extra_pp(self, player_id: str):
        return self.game_state_manager.get_entity_by_id(player_id).extra_pp > 0

    def get_available_actions(self, card_id: str, player_id: str):
        """대상 필드 카드의 가능한 조작 목록을 출력"""
        card_name, card_type, can_attack_leader, can_attack_follower, _, _, is_evolved, _ = self.game_state_manager.get_card_attack_info_field(card_id)
        available_actions = []

        if card_type == CardType.FOLLOWER and can_attack_follower:
            available_actions.append("추종자 공격")

        if card_type == CardType.FOLLOWER and not is_evolved and self.game_state_manager.can_evolve(player_id):
            available_actions.append("추종자 진화")

        if card_type == CardType.FOLLOWER and not is_evolved and self.game_state_manager.can_super_evolve(player_id):
            available_actions.append("추종자 초진화")

        if card_type == CardType.AMULET and self.game_state_manager.has_keyword(card_id, EffectType.ACTIVATE) and self.rule_engine.validate_activate_amulet(card_id, player_id):
            available_actions.append("마법진 활성화")

        return available_actions, card_name