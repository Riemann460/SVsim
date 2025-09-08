import random

import card_data
from typing import Any, List

from deck import Deck
from enums import CardType, EventType, Zone, TargetType, ProcessType, EffectType
from card import Card
from game_state_manager import GameStateManager
from player import Player
from effect import Effect
from event import Event, DestroyedOnFieldEvent, FollowerSuperEvolvedEvent


class EffectProcessor:
    """카드 효과를 해석하고 실행"""
    def __init__(self, event_manager: 'EventManager'):
        """EffectProcessor 클래스의 생성자입니다."""
        self.event_manager = event_manager
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
        }

    def _can_target_with_ability(self, target_card_id: str, game_state_manager: 'GameStateManager') -> bool:
        """능력의 대상으로 추종자를 선택할 수 있는지 확인 (오라, 잠복)"""
        target_card = game_state_manager.get_entity_by_id(target_card_id)
        if target_card.has_keyword(EffectType.AURA):
            print(f"[LOG] {target_card.get_display_name()} (ID: {target_card_id})는 '오라'로 능력의 대상이 될 수 없습니다.")
            return False
        if target_card.has_keyword(EffectType.AMBUSH):
            print(f"[LOG] {target_card.get_display_name()} (ID: {target_card_id})는 '잠복'으로 능력의 대상이 될 수 없습니다.")
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
        choices = {f"{selected_card.get_display_name()} (ID: {selected_card.card_id})": selected_card.card_id}
        game_state_manager.game.request_user_choice("추종자가 랜덤으로 선택되었습니다:", choices)

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
        choices = {f"{selected_card.get_display_name()} (ID: {selected_card.card_id})": selected_card.card_id}
        game_state_manager.game.request_user_choice("가장 공격력이 높은 추종자가 선택되었습니다:", choices)

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

    def list_target(self, target_type: TargetType, caster_id: str,
                       game_state_manager: 'GameStateManager'):
        """타겟 타입을 해석하고 타겟 리스트 반환"""
        caster_card = game_state_manager.get_entity_by_id(caster_id)
        if not caster_card:
            print(f"[ERROR] list_target - caster card with id {caster_id} not found.")
            return []

        handler = self.target_handlers.get(target_type)
        if handler:
            targets = handler(caster_card, game_state_manager)
            print(f"[LOG] 타겟 타입 {target_type.value}에 대한 타겟 리스트: {[t.get_display_name() for t in targets]}")
            return targets
        print(f"[ERROR] 타겟 타입 {target_type.value}에 대한 핸들러가 정의되지 않았습니다.")
        return []


    def _process_stat_buff(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리: 스탯 버프"""
        value = effect_data.value
        attack, defense = value
        target.current_attack += attack
        target.current_defense += defense
        target.max_defense += defense
        print(f"[LOG] 처리 내용: 스텟 버프, 타겟: {target.get_display_name()}, 증가량: {value}")

    def _process_draw(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리: 카드 드로우"""
        value = effect_data.value
        target_id = target.player_id
        condition = (lambda x: True)
        if 'condition' in effect_data.attributes.keys():
            condition = effect_data.condition
        deck = game_state_manager.get_cards_in_zone(target_id, Zone.DECK, condition)

        for _ in range(value):
            if not deck:
                if effect_data.condition:
                    print(f"[LOG] : {target_id} 덱에서 조건에 맞는 카드가 검색되지 않았습니다.")
                    return
                print(f"[LOG] : {target_id} 덱 아웃!")
                return
            drawn_card = deck.pop(0)
            game_state_manager.move_card(drawn_card.card_id, Zone.DECK, Zone.HAND)

            if 'post_action' in effect_data.attributes.keys():
                post_action = effect_data.post_action
                handler = self.process_handlers.get(post_action["process"])
                if handler:
                    handler(post_action, drawn_card, game_state_manager)
                else:
                    print(f"[ERROR] 처리 타입 {post_action['process'].value}에 대한 핸들러가 정의되지 않았습니다.")

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
            while value:
                data = value.pop()
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
            while value:
                data = value.pop()
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

    def resolve_effect(self, effect_data: Effect, caster_id: str,
                       game_state_manager: 'GameStateManager', target_id: str):
        """효과를 해결하고 게임 상태에 적용합니다."""
        caster_card = game_state_manager.get_entity_by_id(caster_id)
        if not caster_card:
            print(f"[ERROR] resolve_effect - caster card with id {caster_id} not found.")
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

        target_type = effect_data.target
        target_list = self.list_target(target_type, caster_id, game_state_manager)

        for target in target_list:
            handler(effect_data, target, game_state_manager)