import random
import logging

import src.common.card_data as card_data
from typing import Any, List, Union

def to_target_type(val):
    """문자열 혹은 enum을 TargetType enum으로 변환합니다."""
    if isinstance(val, TargetType):
        return val
    try:
        return TargetType[val]
    except KeyError:
        raise ValueError(f"Unknown target type '{val}'")
from src.models.deck import Deck
from src.common.enums import CardType, EventType, Zone, TargetType, ProcessType, EffectType, TribeType
from src.models.card import Card
from src.engine.game_state_manager import GameStateManager
from src.models.player import Player
from src.common.effect import Effect
from src.common.event import Event, DestroyedOnFieldEvent, FollowerSuperEvolvedEvent


class EffectProcessor:
    """카드 효과를 해석하고 실행"""
    def __init__(self, event_manager: 'EventManager'):
        """EffectProcessor 클래스의 생성자입니다."""
        self.event_manager = event_manager
        # Initialize logger for unified logging
        self.logger = logging.getLogger(__name__)

        self.target_handlers = {
            TargetType.SELF: self._get_target_self,
            TargetType.OWN_LEADER: self._get_target_own_leader,
            TargetType.OPPONENT_LEADER: self._get_target_opponent_leader,
            TargetType.ALLY_FOLLOWER_CHOICE: self._get_target_ally_follower_choice,
            TargetType.ANOTHER_ALLY_FOLLOWER_CHOICE: self._get_target_another_ally_follower_choice,
            TargetType.OPPONENT_FOLLOWER_CHOICE: self._get_target_opponent_follower_choice,
            TargetType.OPPONENT_FOLLOWER_CHOICE2: self._get_target_opponent_follower_choice2,
            TargetType.OPPONENT_FOLLOWER_RANDOM: self._get_target_opponent_follower_random,
            TargetType.ALL_ALLY_FOLLOWERS: self._get_target_all_ally_followers,
            TargetType.ALL_OTHER_ALLY_FOLLOWERS: self._get_target_all_other_ally_followers,
            TargetType.ALL_OPPONENT_FOLLOWERS: self._get_target_all_opponent_followers,
            TargetType.OWN_HAND_CHOICE: self._get_target_own_hand_choice,
            TargetType.OPPONENT_FOLLOWER_MAX_ATTACK_RANDOM: self._get_target_opponent_follower_max_attack_random,
            TargetType.ALLY_FOLLOWER_CHOICE_UNEVOLVED: self._get_target_ally_follower_choice_unevolved,
            TargetType.ALL_FOLLOWERS: self._get_target_all_followers,
            TargetType.ANOTHER_ALLY_FOLLOWER_RANDOM: self._get_target_another_ally_follower_random,
            TargetType.ALL_OPPONENTS: self._get_target_all_opponents,
            TargetType.VARIABLE: self._get_target_variable,
            TargetType.OWN_DECK: self._get_target_own_deck,
            TargetType.OPPONENT_FIELD: self._get_target_opponent_field,
            TargetType.ALL_OPPONENT_FOLLOWERS_DAMAGED: self._get_target_all_opponent_followers_damaged,
        }
        self.process_handlers = {
            ProcessType.STAT_BUFF: self._process_stat_buff,
            ProcessType.DRAW: self._process_draw,
            ProcessType.HEAL: self._process_heal,
            ProcessType.ADD_CARD_TO_HAND: self._process_add_card_to_hand,
            ProcessType.SUMMON: self._process_summon,
            ProcessType.DEAL_DAMAGE: self._process_deal_damage,
            ProcessType.DESTROY: self._process_destroy,
            ProcessType.RECOVER_PP: self._process_recover_pp,
            ProcessType.SUPER_EVOLVE: self._process_super_evolve,
            ProcessType.REPLACE_DECK: self._process_replace_deck,
            ProcessType.SET_MAX_HEALTH: self._process_set_max_health,
            ProcessType.ADD_EFFECT: self._process_add_keyword,
            ProcessType.REMOVE_KEYWORD: self._process_remove_keyword,
            ProcessType.RETURN_TO_DECK: self._process_return_to_deck,
            ProcessType.RETURN_TO_HAND: self._process_return_to_hand,
            ProcessType.TRIGGER_EFFECT: self._process_trigger_effect,
            ProcessType.GAIN_CREST: self._process_gain_crest,
            ProcessType.FUSE: self._process_fuse,
            ProcessType.DISCARD: self._process_discard,
            ProcessType.REDUCE_COST: self._process_reduce_cost,
            ProcessType.INCREASE_COST: self._process_increase_cost,
            ProcessType.SET_COST: self._process_set_cost,
            ProcessType.SET_ATTACK: self._process_set_attack,
            ProcessType.ADVANCE_CREST: self._process_advance_crest,
            ProcessType.DESTROY_CREST: self._process_destroy_crest,
            ProcessType.RECOVER_EP: self._process_recover_ep,
            ProcessType.HEAL_LINKED: self._process_heal_linked,
            ProcessType.GAIN_SHADOW: self._process_gain_shadow,
            ProcessType.REANIMATE: self._process_reanimate,
            ProcessType.GAIN_EARTH_SIGIL: self._process_gain_earth_sigil,
            ProcessType.TRANSFORM: self._process_transform,
            ProcessType.CONDITIONAL_EFFECT: self._process_conditional_effect,
        }

    def _log_info(self, msg: str) -> None:
        self.logger.info(msg)

    def _log_error(self, msg: str) -> None:
        self.logger.error(msg)

    def _invoke_target_handler(self, target_type: TargetType, caster_card: Card, gsm: 'GameStateManager') -> List[Any]:
        try:
            target_type = to_target_type(target_type)
        except ValueError as e:
            self._log_error(str(e))
            return []
        handler = self.target_handlers.get(target_type)
        if not handler:
            self._log_error(f"Target type {target_type} has no handler.")
            return []
        targets = handler(caster_card, gsm)
        self._log_info(f"Target type {target_type.value} resolved to {[t.get_display_name() for t in targets]}")
        return targets

    def _can_target_with_ability(self, target_card_id: str, game_state_manager: 'GameStateManager') -> bool:
        """능력의 대상으로 추종자를 선택할 수 있는지 확인 (오라, 잠복)"""
        target_card = game_state_manager.get_entity_by_id(target_card_id)
        if target_card.has_keyword(EffectType.AURA):
            self._log_info(f"[LOG] {target_card.get_display_name()} (ID: {target_card_id})는 '오라'로 능력의 대상이 될 수 없습니다.")
            return False
        if target_card.has_keyword(EffectType.AMBUSH):
            self._log_info(f"[LOG] {target_card.get_display_name()} (ID: {target_card_id})는 '잠복'으로 능력의 대상이 될 수 없습니다.")
            return False
        return True

    def _get_target_self(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 자기 자신"""
        return [caster_card]

    def _get_target_own_leader(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 자신의 리더"""
        return [game_state_manager.players[caster_card.owner_id]]

    def _get_target_opponent_leader(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 상대방 리더"""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        return [game_state_manager.players[opponent_id]]

    def _get_target_another_ally_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 자신을 제외한 아군 추종자 선택"""
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and card.card_id != caster_card.card_id]
        if not ally_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in ally_followers}
        selected_card_id = game_state_manager.game.request_user_choice("아군 추종자를 선택하세요:", choices)
        
        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_ally_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 아군 추종자 선택"""
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]
        if not ally_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in ally_followers}
        selected_card_id = game_state_manager.game.request_user_choice("아군 추종자를 선택하세요:", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_opponent_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 상대 추종자 선택"""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER and self._can_target_with_ability(card.card_id, game_state_manager)]
        if not opponent_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in opponent_followers}
        selected_card_id = game_state_manager.game.request_user_choice("상대 추종자를 선택하세요:", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_opponent_follower_choice2(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 상대 추종자 2명 선택"""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER and self._can_target_with_ability(card.card_id, game_state_manager)]
        if len(opponent_followers) < 2: return []

        selected_targets = []
        for i in range(2):
            choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in opponent_followers if f.card_id not in selected_targets}
            if not choices: break
            selected_card_id = game_state_manager.game.request_user_choice(f"상대 추종자를 {i+1}번째 선택하세요:", choices)
            if selected_card_id:
                selected_targets.append(selected_card_id)
            else:
                return [] # 사용자가 선택을 취소한 경우

        return [game_state_manager.get_entity_by_id(card_id) for card_id in selected_targets]

    def _get_target_all_ally_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 모든 아군 추종자"""
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        return [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]

    def _get_target_all_other_ally_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 자신을 제외한 모든 아군 추종자"""
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        return [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and card.card_id != caster_card.card_id]

    def _get_target_all_opponent_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 모든 상대 추종자"""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        return [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

    def _get_target_own_hand_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 자신의 패에서 카드 선택"""
        hand_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.HAND)
        if not hand_cards: return []

        choices = {f"{c.get_display_name()} (ID: {c.card_id})": c.card_id for c in hand_cards}
        selected_card_id = game_state_manager.game.request_user_choice("패의 카드를 선택하세요:", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_opponent_follower_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 가장 공격력이 높은 상대 추종자 중 무작위 선택"""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

        random.shuffle(opponent_followers)
        selected_card = opponent_followers.pop()

        # 사용자에게 어떤 카드가 선택되었는지 보여주는 선택창 (확인 버튼만 있는)
        # choices = {f"{selected_card.get_display_name()} (ID: {selected_card.card_id})": selected_card.card_id}
        # game_state_manager.game.request_user_choice("추종자가 랜덤으로 선택되었습니다:", choices)

        return [selected_card]

    def _get_target_opponent_follower_max_attack_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 가장 공격력이 높은 상대 추종자 중 무작위 선택"""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]
        if not opponent_followers: return []
        max_attack = max(card.current_attack for card in opponent_followers)
        max_attack_followers = [card for card in opponent_followers if card.current_attack == max_attack]
        if not max_attack_followers: return []

        # 가장 공격력이 높은 추종자 중 랜덤 선택은 유지
        random.shuffle(max_attack_followers)
        selected_card = max_attack_followers.pop()

        # 사용자에게 어떤 카드가 선택되었는지 보여주는 선택창 (확인 버튼만 있는)
        # choices = {f"{selected_card.get_display_name()} (ID: {selected_card.card_id})": selected_card.card_id}
        # game_state_manager.game.request_user_choice("가장 공격력이 높은 추종자가 선택되었습니다:", choices)

        return [selected_card]

    def _get_target_ally_follower_choice_unevolved(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상: 진화하지 않은 아군 추종자 선택"""
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        unevolved_ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and not card.is_evolved]
        if not unevolved_ally_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in unevolved_ally_followers}
        selected_card_id = game_state_manager.game.request_user_choice("진화하지 않은 아군 추종자를 선택하세요:", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_all_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 모든 추종자 전체. 주석 규정을 엄격하게 준수합니다."""
        all_cards = []
        for player in game_state_manager.players.values():
            all_cards.extend([c for c in player.field.get_cards() if c.get_type() == CardType.FOLLOWER])
        return all_cards

    def _get_target_another_ally_follower_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 자신 제외 아군 추종자 중 랜덤. 주석 규정을 엄격하게 준수합니다."""
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        candidates = [c for c in ally_cards if c.get_type() == CardType.FOLLOWER and c.card_id != caster_card.card_id]
        if not candidates:
            return []
        import random
        return [random.choice(candidates)]

    def _get_target_all_opponents(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 상대 전체. 주석 규정을 엄격하게 준수합니다."""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent = game_state_manager.players[opponent_id]
        targets = [opponent]
        targets.extend([c for c in opponent.field.get_cards() if c.get_type() == CardType.FOLLOWER])
        return targets

    def _get_target_variable(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 변수. 주석 규정을 엄격하게 준수합니다."""
        return []

    def _get_target_own_deck(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 자신 덱. 주석 규정을 엄격하게 준수합니다."""
        return [game_state_manager.players[caster_card.owner_id]]

    def _get_target_opponent_field(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 상대 필드 전체. 주석 규정을 엄격하게 준수합니다."""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent = game_state_manager.players[opponent_id]
        return opponent.field.get_cards()

    def _get_target_all_opponent_followers_damaged(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 피해를 입은 상대 추종자 전체. 주석 규정을 엄격하게 준수합니다."""
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent = game_state_manager.players[opponent_id]
        opponent_followers = [c for c in opponent.field.get_cards() if c.get_type() == CardType.FOLLOWER]
        return [c for c in opponent_followers if c.current_defense < c.max_defense]

    def list_target(self, target_type: TargetType, caster_id: str,
                       game_state_manager: 'GameStateManager'):
        """타겟 타입을 해석하고 타겟 리스트를 반환합니다."""
        caster_card = game_state_manager.get_entity_by_id(caster_id)
        if not caster_card:
            self._log_error(f"list_target - caster card with id {caster_id} not found.")
            return []
        # Use unified handler invocation (string -> enum conversion handled inside)
        return self._invoke_target_handler(target_type, caster_card, game_state_manager)


    def _process_stat_buff(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 스탯 버프"""
        value = effect_data.value
        attack, defense = value
        target.current_attack += attack
        target.current_defense += defense
        target.max_defense += defense
        self._log_info(f"[LOG] 처리 내용: 스텟 버프, 타겟: {target.get_display_name()}, 증가량: {value}")

    def _process_draw(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리: 카드 드로우"""
        value = effect_data.value
        target_id = target.player_id
        condition_val = effect_data.get('condition')
        if condition_val and isinstance(condition_val, str):
            condition = lambda x: card_data.evaluate_condition(x, condition_val)
        else:
            condition = (lambda x: True)
        deck = game_state_manager.get_cards_in_zone(target_id, Zone.DECK, condition)

        for _ in range(value):
            if not deck:
                if effect_data.get('condition'):
                    self._log_info(f"[LOG] : {target_id} 덱에서 조건에 맞는 카드가 검색되지 않았습니다.")
                    return
                self._log_info(f"[LOG] : {target_id} 덱 아웃!")
                return
            drawn_card = deck.pop(0)
            game_state_manager.move_card(drawn_card.card_id, Zone.DECK, Zone.HAND)

            if 'post_action' in effect_data.attributes.keys():
                post_action = effect_data.post_action
                handler = self.process_handlers.get(post_action["process"])
                if handler:
                    handler(post_action, drawn_card, game_state_manager)
                else:
                    self._log_error(f"[ERROR] 처리 타입 {post_action['process'].value}에 대한 핸들러가 정의되지 않았습니다.")

        print(f"[LOG] 처리 내용: 카드 드로우, 타겟: {target_id}, 드로우 장수: {value}")

    def _process_heal(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 체력 회복"""
        value = effect_data.value
        target.heal_damage(value)
        print(f"[LOG] 처리 내용: 체력 회복, 타겟: {target.get_display_name()}, 회복량: {value}")

    def _process_add_card_to_hand(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리: 패에 카드 추가"""
        value = effect_data.value
        target_id = target.player_id

        if isinstance(value, card_data.CardData):
            card = game_state_manager.create_card_instance(value, target_id)
            if len(game_state_manager.get_cards_in_zone(target_id, Zone.HAND)) < 9:
                game_state_manager.add_card(card, Zone.HAND, target_id)
            else:
                game_state_manager.add_card(card, Zone.GRAVEYARD, target_id)
            print(f"[LOG] 처리 내용: 패에 카드 추가, 타겟: {target_id}, 추가 카드: {card.get_display_name()}")

        elif isinstance(value, list):
            value_copy = list(value)
            while value_copy:
                data = value_copy.pop()
                card = game_state_manager.create_card_instance(data, target_id)
                if len(game_state_manager.get_cards_in_zone(target_id, Zone.HAND)) < 9:
                    game_state_manager.add_card(card, Zone.HAND, target_id)
                else:
                    game_state_manager.add_card(card, Zone.GRAVEYARD, target_id)
                print(f"[LOG] 처리 내용: 패에 카드 추가, 타겟: {target_id}, 추가 카드: {card.get_display_name()}")

    def _process_summon(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리: 필드에 카드 소환"""
        value = effect_data.value
        target_id = target.player_id

        if isinstance(value, card_data.CardData):
            card = game_state_manager.create_card_instance(value, target_id)
            if len(game_state_manager.get_cards_in_zone(target_id, Zone.FIELD)) < 5:
                game_state_manager.add_card(card, Zone.FIELD, target_id)
            print(f"[LOG] 처리 내용: 필드에 카드 소환, 타겟: {target_id}, 소환 카드: {card.get_display_name()}")

        elif isinstance(value, list):
            value_copy = list(value)
            while value_copy:
                data = value_copy.pop()
                card = game_state_manager.create_card_instance(data, target_id)
                if len(game_state_manager.get_cards_in_zone(target_id, Zone.FIELD)) < 5:
                    game_state_manager.add_card(card, Zone.FIELD, target_id)
                print(f"[LOG] 처리 내용: 필드에 카드 소환, 타겟: {target_id}, 소환 카드: {card.get_display_name()}")

    def _process_deal_damage(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 피해 입히기"""
        value = effect_data.value

        if target.has_keyword(EffectType.BARRIER):
            print(f"[LOG] {target.get_display_name()} 배리어로 데미지 0 받음.")
            value = 0
            target.effects = [effect for effect in target.effects if effect.type != EffectType.BARRIER]

        elif target.is_super_evolved and game_state_manager.current_turn_player_id == target.owner_id:
            print(f"[LOG] {target.get_display_name()} 초진화 효과로 데미지 0 받음.")
            value = 0

        if target.take_damage(value):
            if target.get_type() == CardType.LEADER:
                # 게임 종료 처리
                pass
            else:
                target_id = target.card_id
                game_state_manager.move_card(target_id, Zone.FIELD, Zone.GRAVEYARD)
                self.event_manager.publish(DestroyedOnFieldEvent(target_id))
        print(f"[LOG] 처리 내용: 피해 입히기, 타겟: {target.get_display_name()}, 피해량: {value}")

    def _process_destroy(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 파괴"""
        if target.is_super_evolved and game_state_manager.current_turn_player_id == target.owner_id:
            print(f"[LOG] 처리 내용: 파괴, 타겟: {target.get_display_name()}")
            print(f"[LOG] {target.get_display_name()} 초진화 효과로 파괴되지 않음.")
            return
        game_state_manager.move_card(target.card_id, Zone.FIELD, Zone.GRAVEYARD)
        self.event_manager.publish(DestroyedOnFieldEvent(target.card_id))
        print(f"[LOG] 처리 내용: 파괴, 타겟: {target.get_display_name()}")

    def _process_recover_pp(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리: PP 회복"""
        value = effect_data.value
        target.gain_pp(value)
        print(f"[LOG] 처리 내용: PP 회복, 타겟: {target.player_id}, 회복량: {value}")

    def _process_super_evolve(self, effect_data: Effect, target: Card, game_state_manager: 'GameStateManager'):
        """처리: 초진화"""
        game_state_manager.super_evolve_card(target.card_id)
        self.event_manager.publish(FollowerSuperEvolvedEvent(target.card_id, spend_sep="False"))
        print(f"[LOG] 처리 내용: 초진화, 타겟: {target.get_display_name()}")

    def _process_replace_deck(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리: 덱 교체"""
        value = effect_data.value
        target_id = target.player_id
        replaced_deck_list = []
        for card_data_item in value:
            card_data_to_add = game_state_manager.create_card_instance(card_data_item, target_id)
            replaced_deck_list.append(card_data_to_add)
        random.shuffle(replaced_deck_list)
        replaced_deck = Deck(replaced_deck_list)
        target.deck = replaced_deck
        print(f"[LOG] 처리 내용: 덱 교체, 타겟: {target.player_id}, 덱 사이즈: {len(replaced_deck)}")

    def _process_set_max_health(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 최대 체력 설정"""
        value = effect_data.value
        target.max_defense = value
        print(f"[LOG] 처리 내용: 최대 체력 설정, 타겟: {target.get_display_name()}, 설정값: {value}")

    def _process_add_keyword(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 키워드 부여"""
        value = effect_data.value # value 자체가 Effect 객체
        target.effects.append(value)
        print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name()}, 키워드: {value.type.value}")

    def _process_remove_keyword(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 키워드 제거"""
        value = effect_data.value
        target.effects = [effect for effect in target.effects if not effect.type == value]
        print(f"[LOG] 처리 내용: 키워드 제거, 타겟: {target.get_display_name()}, 키워드: {value.value}")

    def _process_return_to_deck(self, effect_data: Effect, target: Card, game_state_manager: 'GameStateManager'):
        """처리: 덱으로 되돌리기"""
        game_state_manager.move_card(target.card_id, Zone.HAND, Zone.DECK)
        print(f"[LOG] 처리 내용: 덱으로 되돌리기, 타겟: {target.get_display_name()}")

    def _process_return_to_hand(self, effect_data: Effect, target: Card, game_state_manager: 'GameStateManager'):
        """처리: 패로 되돌리기"""
        game_state_manager.move_card(target.card_id, Zone.FIELD, Zone.HAND)
        target.current_cost = target.card_data['cost']
        print(f"[LOG] 처리 내용: 패로 되돌리기, 타겟: {target.get_display_name()}")

    def _process_trigger_effect(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 다른 효과 발동"""
        value = effect_data.value
        for effect in target.effects:
            if effect.type == value:
                self.resolve_effect(effect, target.card_id, game_state_manager, None)
        print(f"[LOG] 처리 내용: 다른 효과 발동, 타겟: {target.get_display_name()}, 발동 효과: {value.value}")

    def _process_gain_crest(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """문장 획득 효과를 처리하고 전역 리스너를 바인딩합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target
        
        crest_name = effect_data.value
        if not any(c.name == crest_name for c in player.crests):
            from src.models.crest import create_crest
            game = game_state_manager.game
            crest_obj = create_crest(crest_name, player.player_id)
            player.crests.append(crest_obj)
            crest_obj.register_listeners(game)
            print(f"[LOG] 처리 내용: 문장 획득, 타겟: {player.player_id}, 문장명: {crest_name}")

    def _process_fuse(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """융합 효과를 처리합니다."""
        if not isinstance(target, Card):
            return
            
        player_id = target.owner_id
        game = game_state_manager.game
        
        from src.engine.main_game_logic import validate_fuse_material
        
        hand = game_state_manager.get_cards_in_zone(player_id, Zone.HAND)
        fuse_condition = getattr(target.card_data, "fuse_condition", None)
        fusible_cards = [c for c in hand if c.card_id != target.card_id and validate_fuse_material(c, fuse_condition)]
        if not fusible_cards:
            print(f"[LOG] {player_id}의 패에 융합할 수 있는 카드가 존재하지 않습니다.")
            return

        material_ids = game.gui.get_fuse_choices(player_id, target, fusible_cards)
        if material_ids:
            game.fuse_cards(player_id, target.card_id, material_ids)

    def _process_discard(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """버리기 효과를 처리합니다."""
        game = game_state_manager.game
        if isinstance(target, Card):
            game.discard_card(target.owner_id, target.card_id)
        elif isinstance(target, Player):
            count = effect_data.value if isinstance(effect_data.value, int) else 1
            player_id = target.player_id
            import random
            for _ in range(count):
                hand_ids = game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)
                if hand_ids:
                    chosen_id = random.choice(hand_ids)
                    game.discard_card(player_id, chosen_id)
                else:
                    break

    def resolve_effect(self, effect_data: Effect, caster_id: str,
                       game_state_manager: 'GameStateManager', target_id: str):
        """효과를 해결하고 게임 상태에 적용합니다."""
        caster_card = game_state_manager.get_entity_by_id(caster_id)
        if not caster_card:
            print(f"[ERROR] resolve_effect - caster card with id {caster_id} not found.")
            return

        effect_data.update(caster_id=caster_id)

        if effect_data.type == EffectType.NECROMANCY:
            player = game_state_manager.players[caster_card.owner_id]
            req_shadows = int(effect_data.value) if effect_data.value is not None else 0
            if player.graveyard.shadows_count >= req_shadows:
                player.graveyard.shadows_count -= req_shadows
                print(f"[LOG] 사령술 {req_shadows} 발동. 남은 그림자 수 {player.graveyard.shadows_count}.")
            else:
                print(f"[LOG] 그림자 수 부족으로 사령술 {req_shadows} 발동 실패. 현재 그림자 수 {player.graveyard.shadows_count}.")
                return

        if effect_data.type == EffectType.EARTH_RITE:
            player = game_state_manager.players[caster_card.owner_id]
            field_cards = player.field.get_cards()
            sigils = [c for c in field_cards if TribeType.EARTH_SIGIL in c.card_data.get("tribes", [])]
            if sigils:
                target_sigil = sigils[0]
                game_state_manager.move_card(target_sigil.card_id, Zone.FIELD, Zone.GRAVEYARD)
                from src.common.event import DestroyedOnFieldEvent
                self.event_manager.publish(DestroyedOnFieldEvent(target_sigil.card_id))
                print(f"[LOG] 흙의 비술 발동. {target_sigil.get_display_name()} 소모(파괴).")
            else:
                print(f"[LOG] 필드에 비술 마법진(Earth Sigil)이 존재하지 않아 흙의 비술 발동 실패.")
                return

        if effect_data.get('process') == ProcessType.CHOOSE:
            effect_data.update(caster_id=caster_id)  # caster_id를 Effect 객체에 저장
            game_state_manager.is_awaiting_choice = True
            game_state_manager.pending_choice = effect_data
            game_state_manager.player_awaiting_choice = caster_card.owner_id
            print(f"[LOG] {caster_card.owner_id}의 선택 대기. 선택지: {effect_data.choices}")
            return  # 여기서 처리를 중단하고 플레이어의 입력을 기다림

        effect_type = effect_data.type
        process_type = effect_data.process
        handler = self.process_handlers.get(process_type)
        if not handler:
            print(f"[ERROR] 처리 타입 {process_type.value}에 대한 핸들러가 정의되지 않았습니다.")

        print(f"[LOG] {caster_card.get_display_name()} (ID: {caster_id})의 키워드 {effect_type.value} 처리 시작")

        if target_id:
            target = game_state_manager.get_entity_by_id(target_id)
            handler(effect_data, target, game_state_manager)
            return

        target_type = effect_data.get('target')
        target_list = self.list_target(target_type, caster_id, game_state_manager)

        for target in target_list:
            handler(effect_data, target, game_state_manager)

    def _process_reduce_cost(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 코스트 감소. 주석 규정을 엄격하게 준수합니다."""
        value = effect_data.value
        # target이 Card 인스턴스인지 확인합니다.
        if hasattr(target, "current_cost"):
            if value == "halve":
                # 코스트를 절반으로 줄이며 홀수인 경우 올림 처리합니다.
                target.current_cost = (target.current_cost + 1) // 2
            else:
                try:
                    val = int(value)
                except (ValueError, TypeError):
                    val = 0
                target.current_cost = max(0, target.current_cost - val)
            print(f"[LOG] 처리 내용 코스트 감소, 타겟 {target.get_display_name()}, 현재 코스트 {target.current_cost}.")

    def _process_increase_cost(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 코스트 증가. 주석 규정을 엄격하게 준수합니다."""
        value = effect_data.value
        if hasattr(target, "current_cost"):
            try:
                val = int(value)
            except (ValueError, TypeError):
                val = 0
            target.current_cost = target.current_cost + val
            print(f"[LOG] 처리 내용 코스트 증가, 타겟 {target.get_display_name()}, 현재 코스트 {target.current_cost}.")

    def _process_set_cost(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 코스트 설정. 주석 규정을 엄격하게 준수합니다."""
        value = effect_data.value
        if hasattr(target, "current_cost"):
            try:
                val = int(value)
            except (ValueError, TypeError):
                val = 0
            target.current_cost = val
            print(f"[LOG] 처리 내용 코스트 설정, 타겟 {target.get_display_name()}, 현재 코스트 {target.current_cost}.")

    def _process_set_attack(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 공격력 설정. 주석 규정을 엄격하게 준수합니다."""
        value = effect_data.value
        if hasattr(target, "current_attack"):
            try:
                val = int(value)
            except (ValueError, TypeError):
                val = 0
            target.current_attack = val
            print(f"[LOG] 처리 내용 공격력 설정, 타겟 {target.get_display_name()}, 현재 공격력 {target.current_attack}.")

    def _process_advance_crest(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 문장 카운트 변경. 주석 규정을 엄격하게 준수합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        value = effect_data.value
        value2 = getattr(effect_data, "value2", None)

        if isinstance(value, list) and len(value) == 2:
            crest_name = value[0]
            try:
                amount = int(value[1])
            except (ValueError, TypeError):
                amount = 0
            for crest in player.crests:
                if crest.name == crest_name:
                    crest.count += amount
                    print(f"[LOG] {crest.name} 문장 카운트 {amount}만큼 변경. 현재 카운트 {crest.count}.")
        else:
            try:
                amount = int(value)
            except (ValueError, TypeError):
                amount = 0
            if value2 == "-0" or (isinstance(value2, str) and value2.startswith("-")):
                amount = -amount
            for crest in player.crests:
                crest.count += amount
                print(f"[LOG] {crest.name} 문장 카운트 {amount}만큼 변경. 현재 카운트 {crest.count}.")

    def _process_destroy_crest(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 문장 파괴. 주석 규정을 엄격하게 준수합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        crest_name = effect_data.value
        crests_to_remove = [c for c in player.crests if c.name == crest_name]
        for crest in crests_to_remove:
            crest.unregister_listeners(game_state_manager.game)
            player.crests.remove(crest)
            print(f"[LOG] 처리 내용 문장 파괴, 타겟 {player.player_id}, 문장명 {crest_name}.")

    def _process_recover_ep(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 EP 회복. 주석 규정을 엄격하게 준수합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        try:
            value = int(effect_data.value)
        except (ValueError, TypeError):
            value = 1
        player.gain_ep(value)
        print(f"[LOG] 처리 내용 EP 회복, 타겟 {player.player_id}, 회복량 {value}.")

    def _process_heal_linked(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 연계 회복. 주석 규정을 엄격하게 준수합니다."""
        if hasattr(target, "current_defense") and hasattr(target, "max_defense"):
            heal_amount = max(0, target.max_defense - target.current_defense)
            target.heal_damage(heal_amount)
            leader = game_state_manager.players[target.owner_id]
            leader.heal_damage(heal_amount)
            print(f"[LOG] 처리 내용 연계 회복, 타겟 {target.get_display_name()}, 회복량 {heal_amount}.")

    def _process_gain_shadow(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 묘지 그림자 증가. 주석 규정을 엄격하게 준수합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        try:
            val = int(effect_data.value)
        except (ValueError, TypeError):
            val = 0
        player.graveyard.shadows_count += val
        print(f"[LOG] 처리 내용 묘지 그림자 증가, 타겟 {player.player_id}, 증가량 {val}.")

    def _process_reanimate(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 사령 재생. 주석 규정을 엄격하게 준수합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        try:
            max_cost = int(effect_data.value)
        except (ValueError, TypeError):
            max_cost = 0

        graveyard_cards = player.graveyard.get_cards()
        candidates = [c for c in graveyard_cards if c.get_type() == CardType.FOLLOWER and c.current_cost <= max_cost]
        if not candidates:
            print(f"[LOG] 사령 재생 {max_cost} 실패. 조건에 부합하는 추종자가 묘지에 없습니다.")
            return

        max_found_cost = max(c.current_cost for c in candidates)
        best_candidates = [c for c in candidates if c.current_cost == max_found_cost]
        import random
        selected_card = random.choice(best_candidates)

        player.graveyard._cards.remove(selected_card)
        game_state_manager.add_card(selected_card, Zone.FIELD, player.player_id)
        print(f"[LOG] 사령 재생 {max_cost} 발동, 소환된 추종자 {selected_card.get_display_name()}.")

    def _process_gain_earth_sigil(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 비술 마법진 획득. 주석 규정을 엄격하게 준수합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        from src.common.card_data import CardData
        sigil_data = CardData(
            card_id="earth_sigil_token",
            name="Earth Sigil",
            cost=1,
            card_type=CardType.AMULET,
            class_type=ClassType.RUNECRAFT,
            tribes=[TribeType.EARTH_SIGIL]
        )
        card = game_state_manager.create_card_instance(sigil_data, player.player_id)
        if len(game_state_manager.get_cards_in_zone(player.player_id, Zone.FIELD)) < 5:
            game_state_manager.add_card(card, Zone.FIELD, player.player_id)
            print(f"[LOG] 비술 마법진 획득 발동, 필드에 Earth Sigil 소환.")

    def _process_transform(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 변신. 주석 규정을 엄격하게 준수합니다."""
        if not isinstance(target, Card) or target.current_zone != Zone.FIELD:
            return

        new_card_data = effect_data.value
        owner_id = target.owner_id
        player = game_state_manager.players[owner_id]

        new_card = game_state_manager.create_card_instance(new_card_data, owner_id)
        new_card.current_zone = Zone.FIELD

        game_state_manager.game._unregister_card_listeners(target)

        field_cards = player.field._cards
        if target in field_cards:
            idx = field_cards.index(target)
            field_cards[idx] = new_card
        else:
            field_cards.append(new_card)

        game_state_manager.game._register_card_listeners(new_card)
        print(f"[LOG] 변신 완료, {target.get_display_name()}이(가) {new_card.get_display_name()}으로 변신하였습니다.")

    def _process_conditional_effect(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 조건부 효과. 주석 규정을 엄격하게 준수합니다."""
        val = effect_data.value
        if not isinstance(val, dict) or "condition" not in val:
            return

        condition_fn = val["condition"]
        condition_met = False
        try:
            condition_met = condition_fn(game_state_manager)
        except Exception as e:
            print(f"[ERROR] 조건부 효과 조건식 검사 중 오류 발생 {str(e)}.")

        caster_id = getattr(effect_data, "caster_id", None)

        if condition_met:
            if_true_effect = val.get("if_true")
            if if_true_effect:
                # caster_id를 유지하여 resolve_effect를 재귀 호출합니다.
                self.resolve_effect(if_true_effect, caster_id, game_state_manager, getattr(target, "card_id", None) or getattr(target, "player_id", None))
        else:
            if_false_effect = val.get("if_false")
            if if_false_effect:
                self.resolve_effect(if_false_effect, caster_id, game_state_manager, getattr(target, "card_id", None) or getattr(target, "player_id", None))