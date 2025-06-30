from typing import List, Dict, Any, Optional

from enums import GamePhase, CardType, EventType, Zone  # 상대 경로 임포트
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

        self.game_state_manager.players[player1_id] = Player(player1_id, self.event_manager)
        self.game_state_manager.players[player2_id] = Player(player2_id, self.event_manager)
        self.game_state_manager.current_turn_player_id = player1_id  # 선공
        self.game_state_manager.turn_number = 0

        # 초기 리더 체력, PP 설정
        self.game_state_manager.leader_hp[player1_id] = 20
        self.game_state_manager.leader_hp[player2_id] = 20
        self.game_state_manager.leader_max_hp[player1_id] = 20
        self.game_state_manager.leader_max_hp[player2_id] = 20
        self.game_state_manager.current_pp[player1_id] = 0
        self.game_state_manager.current_pp[player2_id] = 0
        self.game_state_manager.max_pp[player1_id] = 0
        self.game_state_manager.max_pp[player2_id] = 0
        self.game_state_manager.extra_pp_uses[player2_id] = {"1-5": 1, "6+": 1}  # 후공만 엑스트라 PP 사용 가능
        self.game_state_manager.earth_sigil_stacks[player1_id] = 0
        self.game_state_manager.earth_sigil_stacks[player2_id] = 0

        self._setup_listeners()
        self._initialize_decks(player1_id, player2_id)
        self._initial_draw(player1_id, player2_id)

    def _setup_listeners(self):
        """이벤트 리스너 설정"""
        # 예시: 추종자 파괴 시 유언 효과 처리
        self.event_manager.subscribe(EventType.FOLLOWER_DESTROYED, self._on_follower_destroyed)
        # 예시: 주문 사용 시 주문 증폭 처리
        self.event_manager.subscribe(EventType.SPELL_CAST, self._on_spell_cast)
        # 예시: 턴 시작 시 카운트다운 처리
        self.event_manager.subscribe(EventType.TURN_START, self._on_turn_start)
        # 예시: 공격 시 흡혈/공격시 효과 처리
        self.event_manager.subscribe(EventType.ATTACK_DECLARED, self._on_attack_declared)
        # 예시: 진화 시 진화시 효과 처리
        self.event_manager.subscribe(EventType.FOLLOWER_EVOLVED, self._on_follower_evolved)

    def _on_follower_destroyed(self, event_data: Dict[str, Any]):
        """추종자 파괴 이벤트 핸들러"""
        destroyed_card = event_data['card']
        # EffectProcessor가 이 이벤트를 처리하여 유언 효과를 찾고 발동할 것임
        # self.effect_processor.resolve_triggered_effects(EventType.FOLLOWER_DESTROYED, event_data, self.game_state_manager)
        pass  # 이미 resolve_triggered_effects에서 처리되도록 설정했으므로 중복 호출 방지

    def _on_spell_cast(self, event_data: Dict[str, Any]):
        """주문 사용 이벤트 핸들러"""
        # EffectProcessor가 이 이벤트를 처리하여 주문 증폭 효과를 찾고 스택을 쌓을 것임
        pass

    def _on_turn_start(self, event_data: Dict[str, Any]):
        """턴 시작 이벤트 핸들러"""
        # 카운트다운 마법진 처리 등
        pass

    def _on_attack_declared(self, event_data: Dict[str, Any]):
        """공격 선언 이벤트 핸들러"""
        # 흡혈, 공격시 효과 처리 등
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
                player1_deck.append(data)
                player2_deck.append(data)
        for _ in range(2):
            for data in card_data_list[12:]:
                player1_deck.append(data)
                player2_deck.append(data)

        import random
        random.shuffle(player1_deck)
        random.shuffle(player2_deck)

        self.game_state_manager.cards_in_zones[player1_id][Zone.DECK.value] = player1_deck
        self.game_state_manager.cards_in_zones[player2_id][Zone.DECK.value] = player2_deck

        print(f"DEBUG: {player1_id} 덱 사이즈: {len(player1_deck)}")
        print(f"DEBUG: {player2_id} 덱 사이즈: {len(player2_deck)}")

    def _initial_draw(self, player1_id: str, player2_id: str):

        # 선공, 후공 관계없이 각 플레이어 4장 드로우
        print("\nDEBUG: 초기 드로우 단계 시작")
        for _ in range(4):
            self._draw_card(player1_id)
        for _ in range(4):
            self._draw_card(player2_id)

        print("DEBUG: 멀리건 단계 시작 (구현 필요)")
        # TODO: 멀리건 로직 추가
        # 멀리건: 각 플레이어가 원하는 카드를 덱으로 돌려보내고 같은 수만큼 다시 드로우
        # 멀리건된 카드는 덱 맨 아래로 임의의 순서로 들어가야 함.
        # 예시:
        # self._perform_mulligan(player1_id)
        # self._perform_mulligan(player2_id)

    def _draw_card(self, player_id: str):
        """카드 드로우 로직"""
        deck = self.game_state_manager.get_cards_in_zone(player_id, Zone.DECK)
        hand = self.game_state_manager.get_cards_in_zone(player_id, Zone.HAND)
        if not deck:
            print(f"게임 종료: {player_id} 덱 아웃!")
            # 게임 종료 로직 (패배 처리)
            return

        drawn_card = deck.pop(0)
        if len(hand) >= 9:  # 패 제한 9장
            self.game_state_manager.move_card(drawn_card, Zone.DECK, Zone.GRAVEYARD, player_id)  # 10장째는 묘지로
            self.event_manager.publish(EventType.CARD_MOVED_TO_GRAVEYARD, {"card": drawn_card, "reason": "패_제한_초과"})
            print(f"DEBUG: {drawn_card.card_data['name']}이(가) 패 제한 초과로 묘지로 보내짐.")
        else:
            self.game_state_manager.move_card(drawn_card, Zone.DECK, Zone.HAND, player_id)
            self.event_manager.publish(EventType.CARD_DRAWN, {"player_id": player_id, "card": drawn_card})
            print(f"DEBUG: {player_id}가 {drawn_card.card_data['name']}을(를) 드로우함.")

    def start_turn(self, player_id: str):
        """턴 시작 단계 처리"""
        self.game_state_manager.game_phase = GamePhase.START_PHASE
        self.game_state_manager.turn_number += 1
        print(f"\n--- {player_id}의 {self.game_state_manager.turn_number}턴 시작 (시작 단계) ---")

        # 최대 PP 증가 및 회복
        current_max_pp = self.game_state_manager.get_player_max_pp(player_id)
        if current_max_pp < 10:
            self.game_state_manager.max_pp[player_id] += 1
        self.game_state_manager.set_player_pp(player_id, self.game_state_manager.get_player_max_pp(player_id))
        self.event_manager.publish(EventType.PP_GAINED, {"player_id": player_id})  # 각성 조건 확인용으로 사용될 수 있음

        # 턴 시작 시 카드 1장 드로우 (선공의 첫 턴 제외)
        if not (self.game_state_manager.turn_number == 1 and player_id == "player1"):
            self._draw_card(player_id)

        # 필드 추종자 engaged 상태 리셋 (새로 공격 가능하게)
        for card in self.game_state_manager.get_cards_in_zone(player_id, Zone.FIELD):
            if card.card_data['type'] == CardType.FOLLOWER.value:
                card.is_engaged = False
                card.has_storm_this_turn = False  # 질주/돌진 상태 리셋 (공격 안했으면 계속 유지)

        self.event_manager.publish(EventType.TURN_START,
                                   {"player_id": player_id, "turn_number": self.game_state_manager.turn_number})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)  # 턴 시작 이벤트 처리

        self.game_state_manager.game_phase = GamePhase.MAIN_PHASE
        print(f"--- {player_id}의 메인 단계 시작 ---")

    def play_card(self, player_id: str, card_id: str, target_ids: Optional[List[str]] = None):
        """카드 플레이 요청 처리"""
        hand = self.game_state_manager.get_cards_in_zone(player_id, Zone.HAND)
        card_to_play = next((c for c in hand if c.card_id == card_id), None)

        if not card_to_play:
            print(f"ERROR: {card_id} 카드 ID를 패에서 찾을 수 없음.")
            return False

        if not self.rule_engine.validate_play_card(card_to_play, player_id):
            print(f"ERROR: {card_to_play.card_data['name']} 카드 플레이 유효성 검사 실패.")
            return False

        self.game_state_manager.set_player_pp(player_id, self.game_state_manager.get_player_pp(
            player_id) - card_to_play.current_cost)
        print(
            f"DEBUG: {player_id}가 {card_to_play.card_data['name']}을(를) PP {card_to_play.current_cost} 소모하여 플레이함. 남은 PP: {self.game_state_manager.get_player_pp(player_id)}")

        # 카드 타입에 따른 처리
        if card_to_play.card_data['type'] == CardType.FOLLOWER.value or card_to_play.card_data[
            'type'] == CardType.AMULET.value:
            self.game_state_manager.move_card(card_to_play, Zone.HAND, Zone.FIELD, player_id)
            # 마법진인 경우 카운트다운 초기화
            if card_to_play.card_data['type'] == CardType.AMULET.value and '카운트다운' in [k['name'] for k in
                                                                                       card_to_play.keywords]:
                card_to_play.countdown_value = card_to_play.card_data.get("countdown_initial",
                                                                          card_to_play.countdown_value)

        elif card_to_play.card_data['type'] == CardType.SPELL.value:
            self.game_state_manager.move_card(card_to_play, Zone.HAND, Zone.GRAVEYARD, player_id)  # 주문은 사용 즉시 묘지로

        # 타겟 결정 (추후 정교화 필요)
        targets = []
        if target_ids:
            for tid in target_ids:
                # 필드의 모든 카드에서 대상 찾기
                found_target = None
                for p_id in self.game_state_manager.players:
                    for zone_type in [Zone.FIELD.value]:  # 필드의 카드만 타겟 가능하다고 가정
                        target_list = self.game_state_manager.get_cards_in_zone(p_id, Zone(zone_type))
                        for card in target_list:
                            if card.card_id == tid:
                                found_target = card
                                break
                        if found_target: break
                    if found_target: break
                if found_target:
                    targets.append(found_target)
                else:
                    print(f"WARNING: 타겟 카드 {tid}를 찾을 수 없음.")

        # 카드에 정의된 즉발 효과 해결
        if "effect" in card_to_play.card_data:
            self.effect_processor.resolve_effect(
                card_to_play.card_data["effect"],
                card_to_play, targets, self.game_state_manager, player_id
            )

        # 엑스트라 PP 사용 로직 (Player 클래스의 메서드로 캡슐화될 수 있음)
        if card_to_play.has_keyword("엑스트라 PP 사용"):  # 가정: 엑스트라 PP도 카드로 모델링
            # 실제 엑스트라 PP는 카드 플레이가 아닌 플레이어 능력임.
            # 이 부분은 PlayerManager 또는 GameStateManger에서 별도로 처리해야 함.
            print("DEBUG: 엑스트라 PP 사용 로직 (추후 구현)")

        self.event_manager.publish(EventType.CARD_PLAYED, {"player_id": player_id, "card": card_to_play})
        self.event_manager.publish(EventType.SPELL_CAST, {"player_id": player_id, "card": card_to_play,
                                                          "caster_id": card_to_play.card_id})  # 주문 증폭용
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        return True

    def attack_follower(self, attacker_id: str, target_id: str, player_id: str):
        """추종자로 추종자 공격"""
        field_cards = self.game_state_manager.get_cards_in_zone(player_id, Zone.FIELD) + \
                      self.game_state_manager.get_cards_in_zone(self._get_opponent_id(player_id), Zone.FIELD)

        attacker = next((c for c in field_cards if c.card_id == attacker_id), None)
        target = next((c for c in field_cards if c.card_id == target_id), None)

        if not attacker or not target:
            print("ERROR: 공격자 또는 대상 추종자를 찾을 수 없음.")
            return False

        if not self.rule_engine.validate_attack(attacker, target, player_id):
            print("ERROR: 공격 유효성 검사 실패.")
            return False

        print(f"DEBUG: {attacker.card_data['name']}이(가) {target.card_data['name']}을(를) 공격!")

        # 공격시 효과
        self.event_manager.publish(EventType.ATTACK_DECLARED,
                                   {"attacker": attacker, "target": target, "player_id": player_id})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 교전시 효과
        self.event_manager.publish(EventType.COMBAT_INITIATED,
                                   {"attacker": attacker, "defender": target, "player_id": player_id})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 실제 전투 데미지 처리
        # 배리어 처리
        attacker_damage_taken = target.current_attack
        target_damage_taken = attacker.current_attack

        if attacker.has_keyword("배리어"):  # 배리어: 다음에 받는 데미지를 0으로 만든다.
            # 실제 구현에서는 배리어 상태를 추적하고, 데미지 적용 전에 소비해야 함.
            print(f"DEBUG: {attacker.card_data['name']} 배리어로 데미지 0 받음.")
            attacker_damage_taken = 0
        if target.has_keyword("배리어"):
            print(f"DEBUG: {target.card_data['name']} 배리어로 데미지 0 받음.")
            target_damage_taken = 0

        attacker_destroyed = attacker.take_damage(attacker_damage_taken)
        target_destroyed = target.take_damage(target_damage_taken)

        # 흡혈 효과
        if attacker.has_keyword("흡혈"):
            self.effect_processor.resolve_effect(
                {"effect_type": "HEAL_LEADER", "value": attacker.current_attack},  # 흡혈은 공격력만큼 회복
                attacker, [], self.game_state_manager, player_id
            )

        attacker.is_engaged = True  # 공격 완료 표시

        if attacker_destroyed:
            self.game_state_manager.move_card(attacker, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.FOLLOWER_DESTROYED, {"card": attacker})
        if target_destroyed:
            self.game_state_manager.move_card(target, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.FOLLOWER_DESTROYED, {"card": target})

        self.event_manager.process_events(self.game_state_manager, self.effect_processor)
        return True

    def end_turn(self, player_id: str):
        """턴 종료 단계 처리"""
        self.game_state_manager.game_phase = GamePhase.END_PHASE
        print(f"\n--- {player_id}의 턴 종료 (종료 단계) ---")

        self.event_manager.publish(EventType.TURN_END,
                                   {"player_id": player_id, "turn_number": self.game_state_manager.turn_number})
        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 패 제한 처리 (9장 초과 시 9장으로 버림)
        hand = self.game_state_manager.get_cards_in_zone(player_id, Zone.HAND)
        while len(hand) > 9:
            # 가장 최근에 들어온 카드부터 버리는 로직 (또는 임의 선택)
            card_to_discard = hand.pop()
            self.game_state_manager.move_card(card_to_discard, Zone.HAND, Zone.GRAVEYARD)
            self.event_manager.publish(EventType.CARD_MOVED_TO_GRAVEYARD,
                                       {"card": card_to_discard, "reason": "패_제한_버림"})
            print(f"DEBUG: {card_to_discard.card_data['name']}이(가) 패 제한 초과로 버려짐.")

        self.event_manager.process_events(self.game_state_manager, self.effect_processor)

        # 다음 턴 플레이어 설정
        opponent_id = self._get_opponent_id(player_id)
        self.game_state_manager.current_turn_player_id = opponent_id
        print(f"--- {player_id} 턴 종료. {opponent_id}의 턴으로 전환. ---")

    def _get_opponent_id(self, player_id: str) -> str:
        """상대 플레이어 ID 반환"""
        return "player2" if player_id == "player1" else "player1"