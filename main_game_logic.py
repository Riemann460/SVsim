from typing import Dict, Any

from card import Card
from enums import GamePhase, EventType, Zone, EffectType, CardType
from event_manager import EventManager
from game_state_manager import GameStateManager
from player import Player
from effect_processor import EffectProcessor
import card_data
from rule_engine import RuleEngine


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
        self.event_manager = EventManager()
        self.effect_processor = EffectProcessor(self.event_manager)
        self.rule_engine = RuleEngine(self.game_state_manager)
        self.opponent_id = {player1_id: player2_id, player2_id: player1_id}

        self.game_state_manager.players[player1_id] = Player(player1_id, self.event_manager)
        self.game_state_manager.players[player2_id] = Player(player2_id, self.event_manager)
        self.game_state_manager.opponent_id = self.opponent_id
        self.game_state_manager.current_turn_player_id = player1_id  # 선공
        self.game_state_manager.turn_number = 0

        self._setup_listeners()
        self._initialize_decks(player1_id, player2_id)
        self._initial_draw(player1_id, player2_id)
        self._start_turn(player1_id)

    def resolve_effect(self, effect, caster_card_id):
        self.effect_processor.resolve_effect(effect, caster_card_id, self.game_state_manager)

    def resolve_effects_type(self, caster_card_id, effect_type):
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
        self.event_manager.subscribe(EventType.DESTROYED_ON_FIELD, self._on_destroyed)  # 유언
        self.event_manager.subscribe(EventType.CARD_PLAYED, self._on_card_played)  # 출격 / 주문효과
        self.event_manager.subscribe(EventType.ATTACK_DECLARED, self._on_attack_declared)  # 공격시
        self.event_manager.subscribe(EventType.DAMAGE_DEALT, self._on_damage_dealt)  # 흡혈
        self.event_manager.subscribe(EventType.COMBAT_INITIATED, self._on_combat_initiated)  # 교전시
        self.event_manager.subscribe(EventType.SPELL_CAST, self._on_spell_cast)
        self.event_manager.subscribe(EventType.TURN_START, self._on_turn_start)
        self.event_manager.subscribe(EventType.FOLLOWER_EVOLVED, self._on_follower_evolved)
        self.event_manager.subscribe(EventType.FOLLOWER_SUPER_EVOLVED, self._on_follower_super_evolved)

    def _on_destroyed(self, event_data: Dict[str, Any]):
        """유언 효과 처리"""
        destroyed_card_id = event_data['card_id']
        self.resolve_effects_type(destroyed_card_id, EffectType.LAST_WORDS)

    def _on_card_played(self, event_data: Dict[str, Any]):
        """주문 증폭 발행, 주문/출격/증강 효과 처리"""
        played_card_id = event_data['card_id']

        # 주문 증폭 이벤트 발행
        if self.game_state_manager.get_type(played_card_id) == CardType.SPELL:
            self.event_manager.publish(EventType.SPELL_CAST, {"player_id": self.game_state_manager.get_owner(played_card_id)})
            self.process_events()

        self.resolve_effects_type(played_card_id, EffectType.FANFARE)
        self.resolve_effects_type(played_card_id, EffectType.SPELL)

        enhance_list = self.game_state_manager.get_card_effects(played_card_id, EffectType.ENHANCE)
        for effect in enhance_list:
            if event_data['enhanced_cost'] >= effect['enhance_cost']:
                self.resolve_effect(effect, played_card_id)

    def _on_attack_declared(self, event_data: Dict[str, Any]):
        """공격시 효과 처리"""
        attacker_id = event_data['attacker_id']
        self.resolve_effects_type(attacker_id, EffectType.STRIKE)

    def _on_damage_dealt(self, event_data: Dict[str, Any]):
        """흡혈 효과 처리"""
        attacker_id = event_data['attacker_id']
        attacker = self.game_state_manager.get_entity_by_id(attacker_id, Zone.FIELD)
        if attacker.has_keyword(EffectType.DRAIN):
            owner = self.game_state_manager.players[attacker.owner_id]
            owner.heal_damage(event_data['damage'])

    def _on_combat_initiated(self, event_data: Dict[str, Any]):
        """교전시 효과 처리"""
        attacker_id = event_data['attacker_id']
        defender_id = event_data['defender_id']
        self.resolve_effects_type(attacker_id, EffectType.CLASH)  # 교전 상대의 정보 추가 전달 필요!!
        self.resolve_effects_type(defender_id, EffectType.CLASH)  # 교전 상대의 정보 추가 전달 필요!!

    def _on_spell_cast(self, event_data: Dict[str, Any]):
        """주문 증폭 효과 처리"""
        player_id = event_data['player_id']
        cards_with_spellboost = self.game_state_manager.get_cards_with_spellboost(player_id)
        for card_id in cards_with_spellboost:
            self.resolve_effects_type(card_id, EffectType.SPELLBOOST)

    def _on_turn_start(self, event_data: Dict[str, Any]):
        """카운트다운 효과 처리"""
        player_id = event_data['player_id']
        cards_with_countdown = self.game_state_manager.get_cards_with_countdown(player_id)
        for card_id in cards_with_countdown:
            if self.game_state_manager.countdown(card_id):
                self.game_state_manager.move_card(card_id, Zone.FIELD, Zone.GRAVEYARD)
                self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card_id": card_id})
                self.process_events()

    def _on_follower_evolved(self, event_data: Dict[str, Any]):
        """진화시 효과 처리"""
        card_id = event_data['card_id']
        self.resolve_effects_type(card_id, EffectType.ON_EVOLVE)

    def _on_follower_super_evolved(self, event_data: Dict[str, Any]):
        """초진화시 효과 처리"""
        card_id = event_data['card_id']

        # 초진화시 효과가 있다면 진화시 효과는 무시
        if not self.resolve_effects_type(card_id, EffectType.ON_SUPER_EVOLVE):
            self.resolve_effects_type(card_id, EffectType.ON_EVOLVE)

    def _initialize_decks(self, player1_id: str, player2_id: str):
        """초기 덱 설정 (40장, 3장 제한)"""
        # 예시 카드 데이터
        card_data_list = [
            card_data.CARD_DATABASE["Indomitable Fighter"],
            card_data.CARD_DATABASE["Leah, Bellringer Angel"],
            card_data.CARD_DATABASE["Quake Goliath"],
            card_data.CARD_DATABASE["Detective's Lens"],
            card_data.CARD_DATABASE["Arriet, Luxminstrel"],
            card_data.CARD_DATABASE["Caravan Mammoth"],
            card_data.CARD_DATABASE["Adventurers' Guild"],
            card_data.CARD_DATABASE["Ruby, Greedy Cherub"],
            card_data.CARD_DATABASE["Vigilant Detective"],
            card_data.CARD_DATABASE["Goblin Foray"],
            card_data.CARD_DATABASE["Apollo, Heaven's Envoy"],
            card_data.CARD_DATABASE["Seraphic Tidings"],
            card_data.CARD_DATABASE["Phildau, Lionheart Ward"],
            card_data.CARD_DATABASE["Divine Thunder"]
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

        print(f"DEBUG: {player1_id} 덱 사이즈: {len(player1_deck)}")
        print(f"DEBUG: {player2_id} 덱 사이즈: {len(player2_deck)}")

    def _initial_draw(self, player1_id: str, player2_id: str):
        """초기 드로우 및 멀리건"""
        print("\nDEBUG: 초기 드로우 단계 시작")
        for _ in range(4):
            self._draw_card(player1_id)
            self._draw_card(player2_id)

        print("DEBUG: 멀리건 단계 시작")
        self._perform_mulligan(player1_id)
        self._perform_mulligan(player2_id)

    def _perform_mulligan(self, player_id):
        print(f"DEBUG: {player_id}멀리건 시작")
        hand = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)
        if not hand:
            print("손에 카드가 없어 멀리건을 진행할 수 없습니다.")
            return

        # 1. 현재 패 보여주기
        print(f"현재 {player_id}의 패: {[self.game_state_manager.get_card_name(card_id) for card_id in hand]}")
        num_cards_in_hand = len(hand)

        # 2. 사용자 입력 및 유효성 검사
        while True:
            prompt = f"총 {num_cards_in_hand}자리의 이진수(예: 1010)를 입력하세요: "
            mulligan_input = input(prompt)

            # 유효성 검사 1: 입력 길이 확인
            if len(mulligan_input) != num_cards_in_hand:
                print(f"오류: 입력 길이는 반드시 {num_cards_in_hand}자리여야 합니다.")
                continue

            # 유효성 검사 2: 0과 1로만 구성되었는지 확인
            if not all(c in '01' for c in mulligan_input):
                print("오류: 입력은 '0'과 '1'로만 구성되어야 합니다.")
                continue

            break  # 유효한 입력이 들어오면 루프 탈출

        # 3. 멀리건할 카드 식별 및 덱으로 이동
        cards_to_mulligan_ids = []

        for i in range(num_cards_in_hand - 1, -1, -1):
            if mulligan_input[i] == '1':
                cards_to_mulligan_ids.append(hand[i])
                self.game_state_manager.move_card(hand[i], Zone.HAND, Zone.DECK)

        if not cards_to_mulligan_ids:
            print("교체할 카드를 선택하지 않았습니다. 멀리건을 종료합니다.")
            print(f"최종 손패: {[c.card_data['name'] for c in hand]}")
            print(f"DEBUG: {player_id}멀리건 종료")
            return
        print(f"\n선택한 {len(cards_to_mulligan_ids)}장의 카드를 덱으로 돌려보냅니다.")

        # 4. 덱 셔플
        self.game_state_manager.shuffle_deck(player_id)

        # 5. 교체한 카드 수만큼 새로 드로우
        num_to_draw = len(cards_to_mulligan_ids)
        for _ in range(num_to_draw):
            self._draw_card(player_id)

        print(f"최종 손패: {[self.game_state_manager.get_card_name(card_id) for card_id in self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)]}")
        print(f"DEBUG: {player_id} 멀리건 종료")

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
        print(f"--- {player_id}의 메인 단계 시작 ---")

    def _draw_card(self, player_id: str):
        deck = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.DECK)
        if not deck:
            print(f"게임 종료: {player_id} 덱 아웃!")
            # 게임 종료 로직 (패배 처리)
            return

        drawn_card_id = deck.pop(0)
        self.game_state_manager.move_card(drawn_card_id, Zone.DECK, Zone.HAND)

    def play_card(self, player_id: str, card_id: Card, enhanced_cost=0):
        """카드 플레이 요청 처리"""
        if not self.rule_engine.validate_play_card(card_id, player_id):
            print(f"ERROR: {self.game_state_manager.get_card_name(card_id)} 카드 플레이 유효성 검사 실패.")
            return False

        # 코스트, 필드 소환은 GSM에서 처리
        self.game_state_manager.play_card(player_id, card_id, enhanced_cost)

        # 카드에 정의된 즉발 효과 해결
        self.event_manager.publish(EventType.CARD_PLAYED, {"player_id": player_id, "card_id": card_id, 'enhanced_cost': enhanced_cost})
        self.process_events()
        return True

    def attack_leader(self, attacker_id: str):
        """추종자로 리더 공격 요청 처리"""
        attacker = self.game_state_manager.get_entity_by_id(attacker_id, Zone.FIELD)
        if not attacker:
            return False

        target = self.game_state_manager.players[self.opponent_id[attacker.owner_id]]

        if not self.rule_engine.validate_attack(attacker_id, target.player_id):
            print("ERROR: 공격 유효성 검사 실패.")
            return False

        print(f"DEBUG: {attacker.get_display_name()}이(가) {target.player_id}을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(EventType.ATTACK_DECLARED,
                                   {"attacker_id": attacker_id, "target_id": target.player_id})
        self.process_events()

        # 실제 전투 데미지 처리
        # 배리어 처리
        target_damage_taken = attacker.current_attack
        if target.has_keyword(EffectType.BARRIER):
            print(f"DEBUG: {target.get_display_name()} 배리어로 데미지 0 받음.")
            target_damage_taken = 0
            target.effects = [effect for effect in target.effects if effect['type'] != EffectType.BARRIER]

        target.take_damage(target_damage_taken)

        # 흡혈 효과
        self.event_manager.publish(EventType.DAMAGE_DEALT,
                                   {"attacker_id": attacker_id, "damage": target_damage_taken})
        self.process_events()

        attacker.is_engaged = True  # 공격 완료 표시
        return True

    def attack_follower(self, attacker_id: str, target_id: str):
        """추종자로 추종자 공격 요청 처리"""
        attacker = self.game_state_manager.get_entity_by_id(attacker_id, Zone.FIELD)
        target = self.game_state_manager.get_entity_by_id(target_id, Zone.FIELD)

        if not attacker or not target:
            return False

        if not self.rule_engine.validate_attack(attacker_id, target_id):
            print("ERROR: 공격 유효성 검사 실패.")
            return False

        print(f"DEBUG: {attacker.get_display_name()}이(가) {target.get_display_name()}을(를) 공격!")

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
            print(f"DEBUG: {attacker.get_display_name()} 배리어로 데미지 0 받음.")
            attacker_damage_taken = 0
            attacker.effects = [effect for effect in target.effects if effect['type'] != EffectType.BARRIER]

        if target.has_keyword(EffectType.BARRIER):
            print(f"DEBUG: {target.card_data['name']} 배리어로 데미지 0 받음.")
            target_damage_taken = 0
            target.effects = [effect for effect in target.effects if effect['type'] != EffectType.BARRIER]

        target_destroyed = target.take_damage(target_damage_taken)

        if attacker.has_keyword(EffectType.BANE):
            print(f"DEBUG: {attacker.get_display_name()} 필살 능력으로 {target.get_display_name()} 파괴됨.")
            target_destroyed = True

        if attacker.is_super_evolved and target_destroyed:
            print(f"DEBUG: {attacker.get_display_name()} 초진화 효과로 데미지 0 받고, 리더에 1 데미지.")
            attacker_damage_taken = 0
            self.game_state_manager.players[target.owner_id].take_damage(1)

        elif attacker.is_super_evolved_turn:
            print(f"DEBUG: {attacker.get_display_name()} 초진화 효과로 데미지 0 받음.")
            attacker_damage_taken = 0

        attacker_destroyed = attacker.take_damage(attacker_damage_taken)

        # 흡혈 효과
        self.event_manager.publish(EventType.DAMAGE_DEALT,
                                   {"attacker_id": attacker_id, "damage": target_damage_taken})
        self.process_events()

        attacker.is_engaged = True  # 공격 완료 표시

        # 필살 효과
        if target.has_keyword(EffectType.BANE):
            print(f"DEBUG: {target.get_display_name()} 필살 능력으로 {attacker.get_display_name()} 파괴됨.")
            attacker_destroyed = True

        # 파괴된 추종자 묘지로 이동 및 유언 처리
        if attacker_destroyed:
            self.game_state_manager.move_card(attacker_id, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card_id": attacker_id})
        if target_destroyed:
            self.game_state_manager.move_card(target_id, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card_id": target_id})
        self.process_events()
        return True

    def end_turn(self, player_id: str):
        """턴 종료 요청 처리"""
        self.game_state_manager.game_phase = GamePhase.END_PHASE
        print(f"\n--- {player_id}의 턴 종료 (종료 단계) ---")

        self.event_manager.publish(EventType.TURN_END, {"player_id": player_id})
        self.process_events()

        self.game_state_manager.turn_off_super_evolve(player_id)  # 초진화 면역 무력화

        # 다음 턴 플레이어 설정
        opponent_id = self.opponent_id[player_id]
        self.game_state_manager.current_turn_player_id = opponent_id
        print(f"--- {player_id} 턴 종료. {opponent_id}의 턴으로 전환. ---")
        self._start_turn(opponent_id)

    def get_opponent_id(self, player_id: str) -> str:
        """상대 플레이어 ID 반환"""
        return self.opponent_id[player_id]

    def evolve_follower(self, card_id: str, player_id: str):
        """EP를 소모하는 진화 처리"""
        self.game_state_manager.evolve_card_with_ep(card_id, player_id)
        self.event_manager.publish(EventType.FOLLOWER_EVOLVED, {"card_id": card_id})
        self.process_events()

    def super_evolve_follower(self, card_id: str, player_id: str):
        """SEP를 소모하는 초진화 처리"""
        self.game_state_manager.super_evolve_card_with_sep(card_id, player_id)
        self.event_manager.publish(EventType.FOLLOWER_SUPER_EVOLVED, {"card_id": card_id})
        self.process_events()

    def get_start_turn_ifo(self, player_id: str):
        current_pp, max_pp = self.game_state_manager.get_pp_info(player_id)
        player_field_card_ids = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.FIELD)
        opponent_field_card_ids = self.game_state_manager.get_card_ids_in_zone(self.opponent_id[player_id], Zone.FIELD)
        return current_pp, max_pp, player_field_card_ids, opponent_field_card_ids

    def get_playable_cards_id(self, player_id: str):
        player_hand_id = self.game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)
        return player_hand_id, [self.rule_engine.validate_play_card(card_id, player_id) for card_id in player_hand_id]