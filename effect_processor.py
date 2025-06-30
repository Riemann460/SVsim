import random
from typing import Any, Dict, TYPE_CHECKING, List
from enums import CardType, EventType, Zone  # 상대 경로 임포트
from card import Card


class EffectProcessor:
    """카드 효과를 해석하고 실행"""

    def __init__(self, event_manager: 'EventManager'):
        self.event_manager = event_manager

    def resolve_effect(self, effect_data: Dict[str, Any], caster_card: Card, target_cards: List[Card],
                       game_state_manager: 'GameStateManager', player_id: str):
        """단일 효과를 해결"""
        effect_type = effect_data.get("effect_type")
        value = effect_data.get("value")
        target_type = effect_data.get("target_type")
        condition = effect_data.get("condition")
        keyword_name = effect_data.get("keyword_name")  # 키워드 능력의 경우 해당 키워드 이름

        print(f"DEBUG: 효과 {effect_type} 해결 시작 (키워드: {keyword_name if keyword_name else '없음'})")

        # 조건 확인 (예: 각성)
        if condition == "각성":  # 각성: 자신의 최대PP가 7 이상인 상태
            if game_state_manager.get_player_max_pp(player_id) < 7:
                print("DEBUG: '각성' 조건 불충족. 효과 발동 실패.")
                return

        # 대지의 비술 비용 확인 및 소비
        if keyword_name == "대지의 비술":  # 대지의 비술: 자기 필드의 대지의 인장 스택을 적힌 숫자만큼 소비하여 발동
            earthrite_cost = effect_data.get("cost", 0)
            if not game_state_manager.consume_earth_sigils(player_id, earthrite_cost):
                print(f"DEBUG: 대지의 비술 비용 {earthrite_cost} 불충분. 효과 발동 실패.")
                return

        # 사령술 비용 확인 (소비만, 제거는 아님)
        if keyword_name == "사령술":  # 사령술: 묘지의 카드 수를 소비해서 발동하는 능력
            necromancy_cost = effect_data.get("cost", 0)
            if game_state_manager.get_graveyard_size(player_id) < necromancy_cost:
                print(f"DEBUG: 사령술 비용 {necromancy_cost} 불충분 (묘지 카드 부족). 효과 발동 실패.")
                return
            print(f"DEBUG: 사령술 비용 {necromancy_cost} 지불 (묘지 카드 수: {game_state_manager.get_graveyard_size(player_id)}).")

        # 실제 효과 적용
        if effect_type == "DEAL_DAMAGE":
            for target_card in target_cards:
                if target_card.take_damage(value):
                    self.event_manager.publish(EventType.FOLLOWER_DESTROYED,
                                               {"card": target_card, "destroyer_id": caster_card.card_id})
            # 리더에게 피해 주는 경우
            if target_type == "leader":
                target_player_id = target_cards[0]  # 가정: target_cards 첫 번째 요소가 대상 플레이어 ID
                game_state_manager.deal_damage_to_leader(target_player_id, value)

        elif effect_type == "HEAL_LEADER":  # 흡혈 효과
            game_state_manager.heal_leader(player_id, value)

        elif effect_type == "DRAW_CARD":
            # 카드 드로우 로직은 GameStateManager/PlayerManager에서 처리될 것임
            print(f"DEBUG: {player_id}가 카드 {value}장 드로우.")

        elif effect_type == "BUFF_STATS":
            attack_buff = effect_data.get("attack_buff", 0)
            defense_buff = effect_data.get("defense_buff", 0)
            for target_card in target_cards:
                target_card.current_attack += attack_buff
                target_card.current_defense += defense_buff
                print(f"DEBUG: {target_card.card_data['name']}이(가) 공격력 {attack_buff}, 체력 {defense_buff}만큼 버프됨.")

        elif effect_type == "REANIMATE_FOLLOWER":  # 소생
            reanimate_cost = effect_data.get("cost", 0)  # 소생시킬 추종자의 최대 코스트
            reanimated_card = game_state_manager.get_max_cost_follower_in_graveyard(player_id, reanimate_cost)
            if reanimated_card:
                game_state_manager.move_card(reanimated_card, Zone.GRAVEYARD, Zone.FIELD, player_id)
                # 소생된 추종자의 상태 초기화 등 추가 로직 필요
                print(f"DEBUG: {player_id}의 묘지에서 {reanimated_card.card_data['name']}이(가) 소생됨.")
            else:
                print(f"DEBUG: 묘지에서 소생시킬 추종자를 찾을 수 없음 (최대 코스트 {reanimate_cost} 이하).")

        elif effect_type == "DESTROY_AMULET":  # 카운트다운 0이 되었을 때 마법진 파괴
            for target_card in target_cards:
                if target_card.card_data['type'] == CardType.AMULET.value:
                    game_state_manager.move_card(target_card, Zone.FIELD, Zone.GRAVEYARD)
                    self.event_manager.publish(EventType.FOLLOWER_DESTROYED,
                                               {"card": target_card, "destroyer_id": None})  # 마법진 파괴 이벤트
                    print(f"DEBUG: 마법진 {target_card.card_data['name']}이(가) 파괴됨 (카운트다운 0).")

        elif effect_type == "APPLY_CREST_EFFECT":  # 크레스트 효과
            crest_effect_data = effect_data.get("crest_effect", {})
            # 크레스트 효과는 리더에게 직접 적용되거나, 게임 규칙을 변경할 수 있음
            # 예: 리더 체력 회복, 리더 공격력 증가 등
            print(f"DEBUG: {player_id} 리더에게 크레스트 효과 {crest_effect_data} 적용됨.")
            # 실제 리더에게 효과 적용 로직
            if crest_effect_data.get("type") == "HEAL_LEADER_PER_TURN":
                # 턴마다 리더를 회복시키는 지속 효과를 등록
                print(f"DEBUG: {player_id} 리더가 턴마다 체력 {crest_effect_data['value']} 회복 효과를 받음.")

        # 기타 효과 처리 로직...

    def resolve_triggered_effects(self, event_type: EventType, event_data: Dict[str, Any],
                                  game_state_manager: 'GameStateManager'):
        """이벤트 발생 시 트리거되는 모든 효과를 해결"""
        # 필드, 패, 묘지 등 모든 영역의 카드에서 트리거 효과를 찾음
        all_cards = []
        for player_id in game_state_manager.players:
            for zone_type in game_state_manager.cards_in_zones[player_id]:
                all_cards.extend(game_state_manager.get_cards_in_zone(player_id, Zone(zone_type)))

        for card in all_cards:
            for keyword in card.keywords:
                if 'trigger' in keyword and keyword['trigger']['event'] == event_type.value:
                    condition_met = True
                    # 콤보 조건 확인
                    if keyword['name'] == '콤보':  # 콤보: 이 턴 중 플레이한 카드 매 수
                        combo_count = game_state_manager.players[
                            card.owner_id].cards_played_this_turn  # Player 클래스에 추가될 필드
                        required_combo = keyword['trigger'].get("min_combo", 0)
                        if combo_count < required_combo:
                            condition_met = False
                            print(f"DEBUG: 콤보 조건 불충족 (현재 {combo_count}, 필요 {required_combo}).")

                    if condition_met:
                        print(f"DEBUG: 카드 {card.card_data['name']}의 키워드 {keyword['name']} 트리거 발동.")
                        # 특정 키워드에 대한 특별 처리
                        if keyword['name'] == "유언":  # 유언: 파괴되어 묘지에 보내질 때 발동
                            if event_type == EventType.FOLLOWER_DESTROYED and event_data['card'] == card:
                                self.resolve_effect(keyword['effect'], card, [], game_state_manager, card.owner_id)
                        elif keyword['name'] == "교전시":  # 교전시: 추종자가 공격하거나 공격받을 때 발동하는 능력
                            if event_type == EventType.COMBAT_INITIATED and (
                                    event_data['attacker'] == card or event_data['defender'] == card):
                                self.resolve_effect(keyword['effect'], card,
                                                    [event_data['attacker'], event_data['defender']],
                                                    game_state_manager, card.owner_id)
                        elif keyword['name'] == "공격시":  # 공격시: 추종자가 공격할 때 발동하는 능력
                            if event_type == EventType.ATTACK_DECLARED and event_data['attacker'] == card:
                                self.resolve_effect(keyword['effect'], card, [event_data['target']], game_state_manager,
                                                    card.owner_id)
                        elif keyword['name'] == "주문 증폭":  # 주문 증폭: 핸드에 쥐고 있을 때 다른 주문을 사용하면 수치가 스택되어 효과가 강화된다.
                            if event_type == EventType.SPELL_CAST and card.current_zone == Zone.HAND.value and \
                                    event_data['caster_id'] != card.card_id:  # 다른 주문 사용 시
                                card.spellboost_stacks += 1
                                print(f"DEBUG: 카드 {card.card_data['name']}의 주문 증폭 스택 증가 ({card.spellboost_stacks}).")
                                # 주문 증폭에 따라 코스트 감소 효과가 있다면 여기서 처리
                                if "cost_reduction_per_stack" in keyword['effect']:
                                    cost_reduction = keyword['effect']['cost_reduction_per_stack']
                                    card.current_cost = max(0, card.card_data.get("cost", 0) - (
                                                card.spellboost_stacks * cost_reduction))
                                    print(f"DEBUG: {card.card_data['name']} 코스트가 주문 증폭으로 {card.current_cost}로 감소.")
                        elif keyword['name'] == "진화시":  # 진화시: EP를 사용해서 진화했을 때 발동
                            if event_type == EventType.FOLLOWER_EVOLVED and event_data['card'] == card:
                                self.resolve_effect(keyword['effect'], card, [], game_state_manager, card.owner_id)
                        elif keyword['name'] == "카운트다운":  # 카운트다운: (마법진 대상) 자신의 턴 시작 시 카운트가 1감소하고 0이되면 파괴되는 능력
                            if event_type == EventType.TURN_START and event_data['player_id'] == card.owner_id and \
                                    card.card_data['type'] == CardType.AMULET.value:
                                if card.countdown_value is not None:
                                    card.countdown_value -= 1
                                    print(f"DEBUG: 마법진 {card.card_data['name']}의 카운트다운: {card.countdown_value}")
                                    if card.countdown_value <= 0:
                                        self.resolve_effect(
                                            {"effect_type": "DESTROY_AMULET", "target_type": "self"},
                                            card, [card], game_state_manager, card.owner_id
                                        )
                                        # 카운트다운 마법진의 유언 효과가 있다면 여기서 추가로 처리해야 함
                                        for kw in card.keywords:
                                            if kw['name'] == "유언" and kw['trigger'][
                                                'event'] == EventType.FOLLOWER_DESTROYED.value:
                                                self.resolve_effect(kw['effect'], card, [], game_state_manager,
                                                                    card.owner_id)
