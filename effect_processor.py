import random

import card_data
from typing import Any, Dict, List

from deck import Deck
from enums import CardType, EventType, Zone, TargetType, ProcessType, EffectType  # 상대 경로 임포트
from card import Card
from game_state_manager import GameStateManager
from player import Player


class EffectProcessor:
    """카드 효과를 해석하고 실행"""
    def __init__(self, event_manager: 'EventManager'):
        self.event_manager = event_manager
        self.target_handlers = {
            TargetType.SELF: self._get_target_self,
            TargetType.OWN_LEADER: self._get_target_own_leader,
            TargetType.OPPONENT_LEADER: self._get_target_opponent_leader,
            TargetType.ALLY_FOLLOWER_CHOICE: self._get_target_ally_follower_choice,
            TargetType.OPPONENT_FOLLOWER_CHOICE: self._get_target_opponent_follower_choice,
            TargetType.OPPONENT_FOLLOWER_CHOICE2: self._get_target_opponent_follower_choice2,
            TargetType.ALL_ALLY_FOLLOWERS: self._get_target_all_ally_followers,
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
            ProcessType.EVOLVE_SUPER: self._process_evolve_super,
            ProcessType.REPLACE_DECK: self._process_replace_deck,
            ProcessType.SET_MAX_HEALTH: self._process_set_max_health,
            ProcessType.ADD_KEYWORD: self._process_add_keyword,
            ProcessType.REMOVE_KEYWORD: self._process_remove_keyword,
            ProcessType.RETURN_TO_DECK: self._process_return_to_deck,
            ProcessType.TRIGGER_EFFECT: self._process_trigger_effect,
        }

    def _can_target_with_ability(self, target_card_id: str, game_state_manager: 'GameStateManager') -> bool:
        """능력의 대상으로 추종자를 선택할 수 있는지 확인 (오라, 잠복)"""
        target_card = game_state_manager.get_entity_by_id(target_card_id)

        # 오라: 이 추종자는 상대방 능력의 대상으로 선택될 수 없다.
        if target_card.has_keyword(EffectType.AURA):
            print(f"DEBUG: {target_card.card_data['name']}은(는) '오라'로 능력 대상이 될 수 없음.")
            return False

        # 잠복: 상대방의 능력 대상으로 선택되지 않는다.
        if target_card.has_keyword(EffectType.AMBUSH):
            print(f"DEBUG: {target_card.card_data['name']}은(는) '잠복'으로 능력 대상이 될 수 없음.")
            return False
        return True

    def _get_target_self(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        return [caster_card]

    def _get_target_own_leader(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        return [game_state_manager.players[caster_card.owner_id]]

    def _get_target_opponent_leader(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        return [game_state_manager.players[opponent_id]]

    def _get_target_ally_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]
        if not ally_followers: return []
        random.shuffle(ally_followers)
        return [ally_followers.pop()]

    def _get_target_opponent_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER and self._can_target_with_ability(card.card_id, game_state_manager)]
        if not opponent_followers: return []
        random.shuffle(opponent_followers)
        return [opponent_followers.pop()]

    def _get_target_opponent_follower_choice2(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER and self._can_target_with_ability(card.card_id, game_state_manager)]
        if len(opponent_followers) < 2: return [] # Changed from < 3 to < 2 to ensure at least two targets
        random.shuffle(opponent_followers)
        return [opponent_followers.pop(), opponent_followers.pop()]

    def _get_target_all_ally_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        return [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]

    def _get_target_all_opponent_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        return [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

    def _get_target_own_hand_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        hand_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.HAND)
        if not hand_cards: return []
        random.shuffle(hand_cards)
        return [hand_cards.pop()]

    def _get_target_opponent_follower_max_attack_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        opponent_id = game_state_manager.opponent_id[caster_card.owner_id]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]
        if not opponent_followers: return []
        max_attack = max(card.current_attack for card in opponent_followers)
        max_attack_followers = [card for card in opponent_followers if card.current_attack == max_attack]
        if not max_attack_followers: return []
        random.shuffle(max_attack_followers)
        return [max_attack_followers.pop()]

    def _get_target_ally_follower_choice_unevolved(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        ally_cards = game_state_manager.get_cards_in_zone(caster_card.owner_id, Zone.FIELD)
        unevolved_ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and not card.is_evolved]
        if not unevolved_ally_followers: return []
        random.shuffle(unevolved_ally_followers)
        return [unevolved_ally_followers.pop()]

    def list_target(self, target_type: TargetType, caster_id: str,
                       game_state_manager: 'GameStateManager'):
        """타겟 타입을 해석하고 타겟 리스트 반환"""
        caster_card = game_state_manager.get_entity_by_id(caster_id)
        if not caster_card:
            print(f"ERROR: list_target - caster card with id {caster_id} not found.")
            return []

        handler = self.target_handlers.get(target_type)
        if handler:
            return handler(caster_card, game_state_manager)
        print(f"타겟 타입 {target_type.value}에 대한 핸들러가 정의되지 않았습니다.")
        return []


    def _process_stat_buff(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        attack, defense = value
        target.current_attack += attack
        target.current_defense += defense
        target.max_defense += defense
        print(f"DEBUG: 처리 내용: 스텟 버프, 타겟: {target.card_data['name']}, 증가량: {value}")

    def _process_draw(self, effect_data: Dict[str, Any], target: Player, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target_id = target.player_id
        for _ in range(value):
            deck = game_state_manager.get_cards_in_zone(target_id, Zone.DECK)
            if not deck:
                print(f"게임 종료: {target_id} 덱 아웃!")
                return
            drawn_card = deck.pop(0)
            game_state_manager.move_card(drawn_card.card_id, Zone.DECK, Zone.HAND)
        print(f"DEBUG: 처리 내용: 카드 드로우, 타겟: {target_id}, 드로우 장수: {value}")

    def _process_heal(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target.heal_damage(value)
        print(f"DEBUG: 처리 내용: 체력 회복, 타겟: {target.card_data['name']}, 회복량: {value}")

    def _process_add_card_to_hand(self, effect_data: Dict[str, Any], target: Player, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target_id = target.player_id
        card = game_state_manager.create_card_instance(card_data.CARD_DATABASE[value], target_id)
        if len(game_state_manager.get_cards_in_zone(target_id, Zone.HAND)) < 9:
            game_state_manager.add_card(card, Zone.HAND, target_id)
        else:
            game_state_manager.add_card(card, Zone.GRAVEYARD, target_id)
        print(f"DEBUG: 처리 내용: 패에 카드 추가, 타겟: {target_id}, 추가 카드: {card.card_data['name']}")

    def _process_summon(self, effect_data: Dict[str, Any], target: Player, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target_id = target.player_id
        card = game_state_manager.create_card_instance(card_data.CARD_DATABASE[value], target_id)
        if len(game_state_manager.get_cards_in_zone(target_id, Zone.FIELD)) < 5:
            game_state_manager.add_card(card, Zone.FIELD, target_id)
        print(f"DEBUG: 처리 내용: 필드에 카드 소환, 타겟: {target_id}, 소환 카드: {card.card_data['name']}")

    def _process_deal_damage(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        if target.has_keyword(EffectType.BARRIER):
            print(f"DEBUG: {target.get_display_name()} 배리어로 데미지 0 받음.")
            value = 0
            target.effects = [effect for effect in target.effects if effect['type'] != EffectType.BARRIER]
        target.take_damage(value)
        print(f"DEBUG: 처리 내용: 피해 입히기, 타겟: {target.card_data['name']}, 피해량: {value}")

    def _process_destroy(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        game_state_manager.move_card(target.card_id, Zone.FIELD, Zone.GRAVEYARD)
        self.event_manager.publish(EventType.DESTROYED_ON_FIELD, {"card_id": target.card_id})
        self.event_manager.process_events(game_state_manager, self)
        print(f"DEBUG: 처리 내용: 파괴, 타겟: {target.get_display_name()}")

    def _process_recover_pp(self, effect_data: Dict[str, Any], target: Player, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target.gain_pp(value)
        print(f"DEBUG: 처리 내용: PP 회복, 타겟: {target.player_id}, 회복량: {value}")

    def _process_evolve_super(self, effect_data: Dict[str, Any], target: Card, game_state_manager: 'GameStateManager'):
        print(f"DEBUG: 처리 내용: 초진화, 타겟: {target.card_data['name']}")

    def _process_replace_deck(self, effect_data: Dict[str, Any], target: Player, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target_id = target.player_id
        replaced_deck_list = []
        for card_name in value:
            card_data_to_add = Card(card_data.CARD_DATABASE[card_name], target_id)
            replaced_deck_list.append(card_data_to_add)
        random.shuffle(replaced_deck_list)
        replaced_deck = Deck(replaced_deck_list)
        target.deck = replaced_deck
        print(f"DEBUG: 처리 내용: 덱 교체, 타겟: {target.player_id}, 덱 사이즈: {len(replaced_deck)}")

    def _process_set_max_health(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target.max_defense = value
        print(f"DEBUG: 처리 내용: 최대 체력 설정, 타겟: {target.card_data['name']}, 설정값: {value}")

    def _process_add_keyword(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target.effects.append(value)
        print(f"DEBUG: 처리 내용: 키워드 부여, 타겟: {target.card_data['name']}, 키워드: {value['type'].value}")

    def _process_remove_keyword(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        target.effects = [effect for effect in target.effects if not effect['type'] == value]
        print(f"DEBUG: 처리 내용: 키워드 제거, 타겟: {target.card_data['name']}, 키워드: {value.value}")

    def _process_return_to_deck(self, effect_data: Dict[str, Any], target: Card, game_state_manager: 'GameStateManager'):
        game_state_manager.move_card(target.card_id, Zone.HAND, Zone.DECK)

    def _process_trigger_effect(self, effect_data: Dict[str, Any], target: Any, game_state_manager: 'GameStateManager'):
        value = effect_data.get("value")
        for effect in target.effects:
            if effect['type'] == value:
                self.resolve_effect(effect, target.card_id, game_state_manager)
        print(f"DEBUG: 처리 내용: 다른 효과 발동, 타겟: {target.card_data['name']}, 발동 효과: {value.value}")

    def resolve_effect(self, effect_data: Dict[str, Any], caster_id: str,
                       game_state_manager: 'GameStateManager'):
        caster_card = game_state_manager.get_entity_by_id(caster_id)
        if not caster_card:
            print(f"ERROR: resolve_effect - caster card with id {caster_id} not found.")
            return
        
        effect_type = effect_data.get("type")
        target_type = effect_data.get("target")
        process_type = effect_data.get("process")

        target_list = self.list_target(target_type, caster_id, game_state_manager)

        print(f"DEBUG: {caster_card.get_display_name()}의 키워드 {effect_type.value} 처리 시작")

        for target in target_list:
            handler = self.process_handlers.get(process_type)
            if handler:
                handler(effect_data, target, game_state_manager)
            else:
                print(f"처리 타입 {process_type.value}에 대한 핸들러가 정의되지 않았습니다.")