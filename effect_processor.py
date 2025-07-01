import random

import card_data
import event_manager
import game_state_manager
from typing import Any, Dict, TYPE_CHECKING, List
from enums import CardType, EventType, Zone, TargetType, ProcessType, EffectType  # 상대 경로 임포트
from card import Card


class EffectProcessor:
    """카드 효과를 해석하고 실행"""

    def __init__(self, event_manager: 'EventManager'):
        self.event_manager = event_manager

    def list_target(self, target_type: TargetType, caster_card: Card,
                       game_state_manager: 'GameStateManager', player_id: str):
        """타겟 타입을 해석하고 타겟 리스트 반환"""
        opponent_id = game_state_manager.opponent_id[player_id]

        if target_type == TargetType.SELF:
            return [caster_card]

        if target_type == TargetType.OWN_LEADER:
            return [game_state_manager.players[player_id]]

        if target_type == TargetType.OPPONENT_LEADER:
            return [game_state_manager.players[opponent_id]]

        if target_type == TargetType.ALLY_FOLLOWER_CHOICE:
            #일단은 랜덤
            ally_cards = game_state_manager.get_cards_in_zone(player_id, Zone.FIELD)
            ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]

            if not ally_followers: return list()

            random_target = random.shuffle(ally_followers).pop()
            return [random_target]

        if target_type == TargetType.OPPONENT_FOLLOWER_CHOICE:
            # 일단은 랜덤
            opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
            opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

            if not opponent_followers: return list()

            random.shuffle(opponent_followers)
            random_target = opponent_followers.pop()
            return [random_target]

        if target_type == TargetType.OPPONENT_FOLLOWER_CHOICE2:
            # 일단은 랜덤
            opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
            opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

            if not len(opponent_followers) < 3: return opponent_followers

            random.shuffle(opponent_followers)
            return [opponent_followers.pop(), opponent_followers.pop()]

        if target_type == TargetType.ALL_ALLY_FOLLOWERS:
            ally_cards = game_state_manager.get_cards_in_zone(player_id, Zone.FIELD)
            return [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]

        if target_type == TargetType.ALL_OPPONENT_FOLLOWERS:
            opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
            return [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

        if target_type == TargetType.OWN_HAND_CHOICE:
            # 일단은 랜덤
            hand_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.HAND)
            random.shuffle(hand_cards)
            return [hand_cards.pop()]

        if target_type == TargetType.OPPONENT_FOLLOWER_MAX_ATTACK_RANDOM:
            opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
            opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]
            max_attack = max(card.current_attack for card in opponent_followers)

            random.shuffle(opponent_followers)

            for card in opponent_followers:
                if card.current_attack == max_attack: return [card]

            return []

        if target_type == TargetType.ALLY_FOLLOWER_CHOICE_UNEVOLVED:
            #일단은 랜덤
            ally_cards = game_state_manager.get_cards_in_zone(player_id, Zone.FIELD)
            unevolved_ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and not card.is_evolved]

            random_target = random.shuffle(unevolved_ally_followers).pop()
            return [random_target]

        print("타겟 타입이 올바르게 지정되지 않았습니다.")
        return []


    def resolve_effect(self, effect_data: Dict[str, Any], caster_card: Card,
                       game_state_manager: 'GameStateManager'):
        player_id = caster_card.owner_id
        """단일 효과를 실행"""
        effect_type = effect_data.get("type")
        target_type = effect_data.get("target")
        process_type = effect_data.get("process")

        target_list = self.list_target(target_type, caster_card, game_state_manager, player_id)

        print(f"DEBUG: {caster_card.card_data.name}의 키워드 {effect_type.value} 처리 시작")

        for target in target_list:
            # 스탯 버프
            if process_type == ProcessType.STAT_BUFF:
                value = effect_data.get("value")
                attack, defense = value

                target.current_attack += attack
                target.current_defense += defense
                target.max_defense += defense
                print(f"DEBUG: {target.card_data.name}의 스텟을 +{value} 증가시켜 ({target.current_attack}, {target.current_defense})로 변화함.")

            # 카드 드로우
            if process_type == ProcessType.DRAW:
                value = effect_data.get("value")
                target_id = target.player_id

                for _ in range(value):
                    """카드 드로우 로직"""
                    deck = game_state_manager.get_cards_in_zone(target_id, Zone.DECK)
                    if not deck:
                        print(f"게임 종료: {target_id} 덱 아웃!")
                        # 게임 종료 로직 (패배 처리)
                        return

                    drawn_card = deck.pop(0)
                    game_state_manager.move_card(drawn_card, Zone.DECK, Zone.HAND)

            # 체력 회복
            if process_type == ProcessType.HEAL:
                value = effect_data.get("value")
                target.current_defense = min(target.max_defense, target.current_defense + value)

            # 패에 카드 추가
            if process_type == ProcessType.ADD_CARD_TO_HAND:
                value = effect_data.get("value")
                target_id = target.player_id
                card = Card(card_data.CARD_DATABASE[value], target_id)

                if len(game_state_manager.get_cards_in_zone(target_id, Zone.HAND)) < 9:
                    game_state_manager.add_card(card, Zone.HAND, target_id)
                else:
                    game_state_manager.add_card(card, Zone.GRAVEYARD, target_id)

            # 필드에 소환
            if process_type == ProcessType.SUMMON:
                value = effect_data.get("value")
                target_id = target.player_id
                card = Card(card_data.CARD_DATABASE[value], target_id)

                if len(game_state_manager.get_cards_in_zone(target_id, Zone.HAND)) < 5:
                    game_state_manager.add_card(card, Zone.FIELD, target_id)

            # 피해 입히기
            if process_type == ProcessType.DEAL_DAMAGE:
                value = effect_data.get("value")

                # 배리어 처리
                if target.has_keyword(EffectType.BARRIER):
                    print(f"DEBUG: {target.card_data['name']} 배리어로 데미지 0 받음.")
                    value = 0

                target.take_damage(value)

            # 파괴
            if process_type == ProcessType.DESTROY:
                game_state_manager.move_card(target, Zone.FIELD, Zone.GRAVEYARD)
                event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card": target})
                event_manager.process_events(game_state_manager, self)

            # PP 회복
            if process_type == ProcessType.RECOVER_PP:
                value = effect_data.get("value")
                target.gain_pp(value)

            # 초진화
            if process_type == ProcessType.EVOLVE_SUPER:
                # target.evole_super(value)  # 초진화 미구현
                continue

            # 덱 교체
            if process_type == ProcessType.REPLACE_DECK:
                value = effect_data.get("value")
                replaced_deck = []
                for card_name in value:
                    card_data_to_add = Card(card_data.CARD_DATABASE[card_name], target_id)
                    replaced_deck.append(card_data_to_add)

                random.shuffle(replaced_deck)

                game_state_manager.cards_in_zones[target_id][Zone.DECK.value] = replaced_deck

                print(f"DEBUG: {target_id} 덱 사이즈: {len(replaced_deck)}")

            # 최대 체력 설정
            if process_type == ProcessType.SET_MAX_HEALTH:
                value = effect_data.get("value")
                target.max_defense = value

            # ADD_KEYWORD = "키워드 부여"
            # REMOVE_KEYWORD = "키워드 제거"
            # RETURN_TO_DECK = "카드를 덱으로 되돌림"
            # TRIGGER_EFFECT = "다른 효과 발동"