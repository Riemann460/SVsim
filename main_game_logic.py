from typing import List, Dict, Any, Optional

from enums import GamePhase, CardType, EventType, Zone, EffectType  # 상대 경로 임포트
from event_manager import EventManager # 상대 경로 임포트
from card import Card # 상대 경로 임포트
from game_state_manager import GameStateManager
from player import Player # 상대 경로 임포트
from effect_processor import EffectProcessor # 상대 경로 임포트
from rule_engine import RuleEngine # 상대 경로 임포트
import card_data


class Game:
    def __init__(self, player1_id: str, player2_id: str):
        self.event_manager = EventManager()
        self.game_state_manager = GameStateManager()
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

    def _setup_listeners(self):
        """이벤트 리스너 설정"""
        self.event_manager.subscribe(EventType.DESTROYED_ON_FIELD, self._on_destroyed)  # 유언
        self.event_manager.subscribe(EventType.CARD_PLAYED, self._on_card_played)  # 출격 / 주문효과
        self.event_manager.subscribe(EventType.ATTACK_DECLARED, self._on_attack_declared)  # 공격시
        self.event_manager.subscribe(EventType.DAMAGE_DEALT, self._on_damage_dealt)  # 흡혈
        self.event_manager.subscribe(EventType.COMBAT_INITIATED, self._on_combat_initiated)  # 교전시

        # 예시: 주문 사용 시 주문 증폭 처리
        self.event_manager.subscribe(EventType.SPELL_CAST, self._on_spell_cast)
        # 예시: 턴 시작 시 카운트다운 처리
        self.event_manager.subscribe(EventType.TURN_START, self._on_turn_start)
        # 예시: 진화 시 진화시 효과 처리
        self.event_manager.subscribe(EventType.FOLLOWER_EVOLVED, self._on_follower_evolved)

    def _on_destroyed(self, event_data: Dict[str, Any]):
        """유언 효과 처리"""
        destroyed_card = event_data['card']
        for effect in destroyed_card.effects:
            if effect['type'] == EffectType.LAST_WORDS:
                self.effect_processor.resolve_effect(effect, destroyed_card, self.game_state_manager)

    def _on_card_played(self, event_data: Dict[str, Any]):
        """주문 or 출격 효과 처리"""
        played_card = event_data['card']
        for effect in played_card.effects:
            if effect['type'] in [EffectType.FANFARE, EffectType.SPELL] :
                self.effect_processor.resolve_effect(effect, played_card, self.game_state_manager)

    def _on_attack_declared(self, event_data: Dict[str, Any]):
        """공격시 효과 처리"""
        attacker = event_data['attacker']
        for effect in attacker.effects:
            if effect['type'] == EffectType.STRIKE:
                self.effect_processor.resolve_effect(effect, attacker, self.game_state_manager)

    def _on_damage_dealt(self, event_data: Dict[str, Any]):
        """흡혈 효과 처리"""
        attacker = event_data['attacker']
        for effect in attacker.effects:
            if effect['type'] == EffectType.DRAIN:
                owner = self.game_state_manager.players[attacker.owner_id]
                owner.heal_damage(event_data['damage'])

    def _on_combat_initiated(self, event_data: Dict[str, Any]):
        """교전시 효과 처리"""
        attacker = event_data['attacker']
        defender = event_data['defender']

        for effect in attacker.effects:
            if effect['type'] == EffectType.CLASH:
                self.effect_processor.resolve_effect(effect, attacker, self.game_state_manager)

        for effect in defender.effects:
            if effect['type'] == EffectType.CLASH:
                self.effect_processor.resolve_effect(effect, attacker, self.game_state_manager)

    def _on_spell_cast(self, event_data: Dict[str, Any]):
        """주문 증폭 이벤트 핸들러"""
        pass

    def _on_turn_start(self, event_data: Dict[str, Any]):
        """턴 시작 이벤트 핸들러"""
        # 카운트다운 마법진 처리 등
        pass

    def _on_follower_evolved(self, event_data: Dict[str, Any]):
        """추종자 진화 이벤트 핸들러"""
        # 진화시 효과 처리 등
        pass

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
                player1_deck.append(Card(data, player1_id))
                player2_deck.append(Card(data, player2_id))
        for _ in range(2):
            for data in card_data_list[12:]:
                player1_deck.append(Card(data, player1_id))
                player2_deck.append(Card(data, player2_id))

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
        hand = self.game_state_manager.get_cards_in_zone(player_id, Zone.HAND)
        if not hand:
            print("손에 카드가 없어 멀리건을 진행할 수 없습니다.")
            return

        # 1. 현재 패 보여주기
        print(f"현재 {player_id}의 패: {[c.card_data['name'] for c in hand]}")
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
        cards_to_mulligan = []

        for i in range(num_cards_in_hand - 1, -1, -1):
            if mulligan_input[i] == '1':
                card_to_move = hand[i]
                cards_to_mulligan.append(card_to_move)
                self.game_state_manager.move_card(card_to_move, Zone.HAND, Zone.DECK)

        if not cards_to_mulligan:
            print("교체할 카드를 선택하지 않았습니다. 멀리건을 종료합니다.")
            print(f"최종 손패: {[c.card_data['name'] for c in hand]}")
            print(f"DEBUG: {player_id}멀리건 종료")
            return

        print(f"\n선택한 {len(cards_to_mulligan)}장의 카드를 덱으로 돌려보냅니다.")

        # 4. 덱 셔플
        self.game_state_manager.shuffle_deck(player_id)

        # 5. 교체한 카드 수만큼 새로 드로우
        num_to_draw = len(cards_to_mulligan)
        for _ in range(num_to_draw):
            self._draw_card(player_id)

        print(f"최종 손패: {[c.card_data['name'] for c in self.game_state_manager.get_cards_in_zone(player_id, Zone.HAND)]}")
        print(f"DEBUG: {player_id}멀리건 종료")

    def _draw_card(self, player_id: str):
        deck = self.game_state_manager.get_cards_in_zone(player_id, Zone.DECK)
        if not deck:
            print(f"게임 종료: {player_id} 덱 아웃!")
            # 게임 종료 로직 (패배 처리)
            return

        drawn_card = deck.pop(0)
        self.game_state_manager.move_card(drawn_card, Zone.DECK, Zone.HAND)

    def start_turn(self, player_id: str):
        self.game_state_manager.start_turn(player_id)

        # 턴 시작 시 카드 1장 드로우
        self._draw_card(player_id)

        self.event_manager.publish(EventType.TURN_START,
                                   {"player_id": player_id, "turn_number": self.game_state_manager.turn_number})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)  # 턴 시작 이벤트 처리

        self.game_state_manager.game_phase = GamePhase.MAIN_PHASE
        print(f"--- {player_id}의 메인 단계 시작 ---")

    def play_card(self, player_id: str, card: Card):
        """카드 플레이 요청 처리"""
        if not self.rule_engine.validate_play_card(card, player_id):
            print(f"ERROR: {card.card_data['name']} 카드 플레이 유효성 검사 실패.")
            return False
        self.game_state_manager.play_card(player_id, card)

        # 카드에 정의된 즉발 효과 해결
        self.event_manager.publish(EventType.CARD_PLAYED, {"player_id": player_id, "card": card})

        if card.get_type() == CardType.SPELL:
            self.event_manager.publish(EventType.SPELL_CAST, {"player_id": player_id, "card": card,
                                                              "caster_id": card.card_id})  # 주문 증폭용

        self.event_manager.process_events(self.game_state_manager, self.effect_processor)
        return True

    def attack_leader(self, attacker):
        """추종자로 리더 공격"""
        target = self.game_state_manager.players[self.opponent_id[attacker.owner_id]]

        if not self.rule_engine.validate_attack(attacker, target):
            print("ERROR: 공격 유효성 검사 실패.")
            return False

        print(f"DEBUG: {attacker.card_data['name']}이(가) {target.player_id}을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(EventType.ATTACK_DECLARED,
                                   {"attacker": attacker, "target": target})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 실제 전투 데미지 처리
        # 배리어 처리
        target_damage_taken = attacker.current_attack
        if target.has_keyword(EffectType.BARRIER):
            print(f"DEBUG: {target.data['name']} 배리어로 데미지 0 받음.")
            target_damage_taken = 0
            target.effects = [effect for effect in target.effects if effect['type'] != EffectType.BARRIER]

        target.take_damage(target_damage_taken)

        # 흡혈 효과
        self.event_manager.publish(EventType.DAMAGE_DEALT,
                                   {"attacker": attacker, "damage": target_damage_taken})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        attacker.is_engaged = True  # 공격 완료 표시
        return True

    def attack_follower(self, attacker, target):
        """추종자로 추종자 공격"""
        if not self.rule_engine.validate_attack(attacker, target):
            print("ERROR: 공격 유효성 검사 실패.")
            return False

        print(f"DEBUG: {attacker.card_data['name']}이(가) {target.card_data['name']}을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(EventType.ATTACK_DECLARED,
                                   {"attacker": attacker, "target": target})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 교전시 효과
        self.event_manager.publish(EventType.COMBAT_INITIATED,
                                   {"attacker": attacker, "defender": target})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 교전시 효과로 파괴됐을 때 처리 추가 필요
        # 실제 전투 데미지 처리
        # 배리어 처리
        attacker_damage_taken = target.current_attack
        target_damage_taken = attacker.current_attack

        if attacker.has_keyword(EffectType.BARRIER):
            print(f"DEBUG: {attacker.card_data['name']} 배리어로 데미지 0 받음.")
            attacker_damage_taken = 0
            attacker.effects = [effect for effect in target.effects if effect['type'] != EffectType.BARRIER]
        if target.has_keyword(EffectType.BARRIER):
            print(f"DEBUG: {target.card_data['name']} 배리어로 데미지 0 받음.")
            target_damage_taken = 0
            target.effects = [effect for effect in target.effects if effect['type'] != EffectType.BARRIER]

        attacker_destroyed = attacker.take_damage(attacker_damage_taken)
        target_destroyed = target.take_damage(target_damage_taken)

        # 흡혈 효과
        self.event_manager.publish(EventType.DAMAGE_DEALT,
                                   {"attacker": attacker, "damage": target_damage_taken})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        attacker.is_engaged = True  # 공격 완료 표시

        if attacker_destroyed:
            self.game_state_manager.move_card(attacker, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card": attacker})
        if target_destroyed:
            self.game_state_manager.move_card(target, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card": target})

        self.event_manager.process_events(self.game_state_manager, self.effect_processor)
        return True

    def end_turn(self, player_id: str):
        """턴 종료 단계 처리"""
        self.game_state_manager.game_phase = GamePhase.END_PHASE
        print(f"\n--- {player_id}의 턴 종료 (종료 단계) ---")

        self.event_manager.publish(EventType.TURN_END,
                                   {"player_id": player_id, "turn_number": self.game_state_manager.turn_number})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 다음 턴 플레이어 설정
        opponent_id = self.opponent_id[player_id]
        self.game_state_manager.current_turn_player_id = opponent_id
        print(f"--- {player_id} 턴 종료. {opponent_id}의 턴으로 전환. ---")

    def get_opponent_id(self, player_id: str) -> str:
        """상대 플레이어 ID 반환"""
        return "player2" if player_id == "player1" else "player1"

    def can_evolve(self, player_id: str) -> bool:
        return self.game_state_manager.players[player_id].current_ep > 0 and not self.game_state_manager.players[player_id].spent_ep_in_turn