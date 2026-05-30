# 역할 정의. 카드 효과를 해석하고 처리하는 클래스입니다.

import random
import logging

import src.common.card_data as card_data
from typing import Any, List, Union

def to_target_type(val):
    """문자열 혹은 enum을 TargetType enum으로 변환합니다."""
    if val is None:
        return TargetType.SELF
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
    """카드 효과를 해석하고 실행합니다."""
    def __init__(self, event_manager: 'EventManager'):
        """EffectProcessor 클래스의 생성자입니다."""
        self.event_manager = event_manager
        # 통합 로깅을 위한 로거를 초기화합니다.
        self.logger = logging.getLogger(__name__)

        self.target_handlers = {
            TargetType.SELF: self._get_target_self,
            TargetType.OWN_LEADER: self._get_target_own_leader,
            TargetType.OPPONENT_LEADER: self._get_target_opponent_leader,
            TargetType.ALLY_FOLLOWER_CHOICE: self._get_target_ally_follower_choice,
            TargetType.ANOTHER_ALLY_FOLLOWER_CHOICE: self._get_target_another_ally_follower_choice,
            TargetType.ALLY_CARD_CHOICE: self._get_target_ally_card_choice,
            TargetType.ANOTHER_ALLY_CARD_CHOICE: self._get_target_another_ally_card_choice,
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
            TargetType.ALL_LEADERS_MAX_DEFENSE: self._get_target_all_leaders_max_defense,
            TargetType.ALL_LEADERS_MIN_DEFENSE: self._get_target_all_leaders_min_defense,
            TargetType.ANOTHER_ALLY_FOLLOWER_RANDOM_UNEVOLVED: self._get_target_another_ally_follower_random_unevolved,
            TargetType.ALLY_FOLLOWER_RANDOM_SUPER_EVOLVED: self._get_target_ally_follower_random_super_evolved,
            TargetType.OWN_HAND_RANDOM: self._get_target_own_hand_random,
            TargetType.SUMMONED_FOLLOWERS: self._get_target_summoned_followers,
            TargetType.EXACT_COPY: self._get_target_summoned_followers,
        }
        self.process_handlers = {
            ProcessType.STAT_BUFF: self._process_stat_buff,
            ProcessType.DRAW: self._process_draw,
            ProcessType.HEAL: self._process_heal,
            ProcessType.ADD_CARD_TO_HAND: self._process_add_card_to_hand,
            ProcessType.SUMMON: self._process_summon,
            ProcessType.DEAL_DAMAGE: self._process_deal_damage,
            ProcessType.DESTROY: self._process_destroy,
            ProcessType.BANISH: self._process_banish,
            ProcessType.RECOVER_PP: self._process_recover_pp,
            ProcessType.EVOLVE: self._process_evolve,
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
            ProcessType.SPELLBOOST_HAND: self._process_spellboost_hand,
            ProcessType.GAIN_MAX_PP: self._process_gain_max_pp,
            ProcessType.ADVANCE_COUNTDOWN: self._process_advance_countdown,
            ProcessType.INCREASE_COMBO: self._process_increase_combo,
            ProcessType.MULTI_ATTACK: self._process_multi_attack,
            ProcessType.SELECT: self._process_select,
            ProcessType.INCREASE_SKYBOUND_ART_GAUGE: self._process_increase_skybound_art_gauge,
            ProcessType.SUMMON_COPY: self._process_summon_copy,
        }

    def _get_owner_id(self, caster_card: Any) -> str:
        """시전자 카드 또는 플레이어로부터 소유자 ID를 추출합니다."""
        if hasattr(caster_card, "owner_id"):
            return caster_card.owner_id
        if hasattr(caster_card, "player_id"):
            return caster_card.player_id
        return ""

    def _resolve_val(self, val, x_val):
        """동적 변수 X, Y, Z가 포함된 값을 실제 정수로 변환합니다."""
        if x_val is None:
            return val
        from src.common.enums import TargetType
        if val == TargetType.VARIABLE:
            if isinstance(x_val, dict):
                return x_val.get('X', 0)
            return x_val
        if isinstance(val, str):
            val_clean = val.replace('+', '').replace('-', '').strip()
            if isinstance(x_val, dict):
                if val_clean in x_val:
                    factor = -1 if '-' in val else 1
                    return factor * x_val[val_clean]
            else:
                if val_clean == 'X':
                    factor = -1 if '-' in val else 1
                    return factor * x_val
            try:
                return int(val)
            except ValueError:
                return val
        elif isinstance(val, list):
            return [self._resolve_val(item, x_val) for item in val]
        return val

    def _resolve_effect_variables(self, effect: Effect, x_val: Any) -> None:
        """효과 내의 모든 동적 변수를 재귀적으로 해석하여 업데이트합니다."""
        if not effect:
            return
        for key in list(effect.attributes.keys()):
            val = effect.attributes[key]
            if isinstance(val, Effect):
                self._resolve_effect_variables(val, x_val)
            elif isinstance(val, list):
                new_list = []
                for item in val:
                    if isinstance(item, Effect):
                        self._resolve_effect_variables(item, x_val)
                        new_list.append(item)
                    else:
                        new_list.append(self._resolve_val(item, x_val))
                effect.update(**{key: new_list})
            else:
                resolved = self._resolve_val(val, x_val)
                effect.update(**{key: resolved})

    def _get_variable_value(self, caster_card, game_state_manager):
        """카드 정보 및 텍스트를 기반으로 동적 변수 X의 값을 계산합니다."""
        definition = None
        if isinstance(caster_card, Card):
            for e in caster_card.effects:
                if getattr(e, 'process', None) == ProcessType.DEFINE_VARIABLE:
                    definition = e.value
                    break
            if not definition and caster_card.card_data.raw_effects_text:
                import re
                match = re.search(r"X is (.*?)(?:\.|$)", caster_card.card_data.raw_effects_text, re.IGNORECASE)
                if match:
                    definition = match.group(1).strip()

        if not definition:
            return None

        player_id = self._get_owner_id(caster_card)
        player = game_state_manager.players[player_id]

        def_lower = definition.lower()
        if def_lower == "random_split_faith":
            if not hasattr(caster_card, "x_val"):
                faith_val = getattr(player, "faith", 0)
                if faith_val == 0:
                    faith_val = 5
                v1 = random.randint(0, faith_val)
                v2 = random.randint(0, faith_val - v1)
                v3 = faith_val - v1 - v2
                vals = [v1, v2, v3]
                random.shuffle(vals)
                caster_card.x_val = vals[0]
                caster_card.y_val = vals[1]
                caster_card.z_val = vals[2]
                print(f"[LOG] Depths of the Eld Crystals 변수 할당 - X {caster_card.x_val}, Y {caster_card.y_val}, Z {caster_card.z_val}")
            return {'X': caster_card.x_val, 'Y': caster_card.y_val, 'Z': caster_card.z_val}
        elif def_lower == "destroyed_shikigami_stats":
            game = game_state_manager.game
            destroyed_list = getattr(game, "destroyed_this_turn", [])
            shikigami_followers = [
                c for c in destroyed_list
                if c.owner_id == player_id and c.get_type() == CardType.FOLLOWER and
                (TribeType.SHIKIGAMI in c.card_data.tribes or "shikigami" in c.card_data.name.lower())
            ]
            total_atk = sum(c.card_data.get("attack", 0) for c in shikigami_followers)
            total_def = sum(c.card_data.get("defense", 0) for c in shikigami_followers)
            caster_card.x_val = total_atk
            caster_card.y_val = total_def
            print(f"[LOG] Noble Shikigami 변수 할당 - X {total_atk}, Y {total_def}")
            return {'X': total_atk, 'Y': total_def}
        elif "combo" in def_lower:
            return player.combo_count
        elif "cards in your hand" in def_lower or "cards in hand" in def_lower:
            return len(game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND))
        elif "allied followers on the field" in def_lower:
            followers = [c for c in player.field.get_cards() if c.get_type() == CardType.FOLLOWER]
            if isinstance(caster_card, Card) and caster_card in followers:
                return len(followers) - 1
            return len(followers)
        elif "crests you have" in def_lower or "crests" in def_lower:
            return len(player.crests) if hasattr(player, 'crests') else 0
        elif "this follower's attack" in def_lower:
            return caster_card.current_attack if isinstance(caster_card, Card) else 0
        elif "pixie followers in your hand" in def_lower:
            hand_cards = [game_state_manager.get_entity_by_id(cid) for cid in game_state_manager.get_card_ids_in_zone(player_id, Zone.HAND)]
            return len([c for c in hand_cards if c and "Pixie" in c.card_data.name])

        return 0

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
        """능력의 대상으로 추종자를 선택할 수 있는지 확인합니다. 오라나 잠복 상태를 고려합니다."""
        target_card = game_state_manager.get_entity_by_id(target_card_id)
        if target_card.has_keyword(EffectType.AURA):
            self._log_info(f"[LOG] {target_card.get_display_name()} (ID: {target_card_id})는 '오라'로 능력의 대상이 될 수 없습니다.")
            return False
        if target_card.has_keyword(EffectType.AMBUSH):
            self._log_info(f"[LOG] {target_card.get_display_name()} (ID: {target_card_id})는 '잠복'으로 능력의 대상이 될 수 없습니다.")
            return False
        return True

    def _get_target_self(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 자기 자신"""
        return [caster_card]

    def _get_target_own_leader(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 자신의 리더"""
        return [game_state_manager.players[self._get_owner_id(caster_card)]]

    def _get_target_opponent_leader(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 상대방 리더"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        return [game_state_manager.players[opponent_id]]

    def _get_target_another_ally_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 자신을 제외한 아군 추종자 선택"""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and card.card_id != caster_card.card_id]
        if not ally_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in ally_followers}
        selected_card_id = game_state_manager.game.request_user_choice("아군 추종자를 선택하세요:", choices)
        
        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_ally_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 아군 추종자 선택"""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]
        if not ally_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in ally_followers}
        selected_card_id = game_state_manager.game.request_user_choice("아군 추종자를 선택하세요:", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_ally_card_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """아군 필드 카드를 선택합니다."""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        if not ally_cards:
            return []

        choices = {f"{c.get_display_name()} (ID {c.card_id})": c.card_id for c in ally_cards}
        selected_card_id = game_state_manager.game.request_user_choice("아군 카드를 선택하십시오.", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_another_ally_card_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """자신을 제외한 아군 필드 카드를 선택합니다."""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        # 자신을 제외한 아군 카드들을 필터링합니다.
        valid_cards = [c for c in ally_cards if c.card_id != caster_card.card_id]
        if not valid_cards:
            return []

        choices = {f"{c.get_display_name()} (ID {c.card_id})": c.card_id for c in valid_cards}
        selected_card_id = game_state_manager.game.request_user_choice("아군 카드를 선택하십시오.", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_opponent_follower_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 상대 추종자 선택"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER and self._can_target_with_ability(card.card_id, game_state_manager)]
        if not opponent_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in opponent_followers}
        selected_card_id = game_state_manager.game.request_user_choice("상대 추종자를 선택하세요:", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_opponent_follower_choice2(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 상대 추종자 2명 선택"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
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
                return []  # 사용자가 선택을 취소한 경우

        return [game_state_manager.get_entity_by_id(card_id) for card_id in selected_targets]

    def _get_target_all_ally_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 모든 아군 추종자"""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        return [card for card in ally_cards if card.get_type() == CardType.FOLLOWER]

    def _get_target_all_other_ally_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 자신을 제외한 모든 아군 추종자"""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        return [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and card.card_id != caster_card.card_id]

    def _get_target_all_opponent_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 모든 상대 추종자"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        return [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

    def _get_target_own_hand_choice(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 자신의 패에서 카드 선택"""
        owner_id = self._get_owner_id(caster_card)
        hand_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.HAND)
        if not hand_cards:
            return []

        # 동적 타겟 조건 필터링 (Tribe, CardType, Cost 조건 처리)
        if hasattr(self, 'current_effect') and self.current_effect:
            eff = self.current_effect
            target_tribe = getattr(eff, 'target_tribe', None)
            target_class = getattr(eff, 'target_class', None)
            target_card_type = getattr(eff, 'target_card_type', None)
            target_cost = getattr(eff, 'target_cost', None)
            target_cost_condition = getattr(eff, 'target_cost_condition', None)

            if target_tribe:
                from src.common.enums import TribeType
                try:
                    tribe_enum = TribeType[target_tribe]
                    hand_cards = [c for c in hand_cards if tribe_enum in c.card_data.tribes]
                except KeyError:
                    pass

            if target_class:
                from src.common.enums import ClassType
                try:
                    class_enum = ClassType[target_class]
                    hand_cards = [c for c in hand_cards if c.class_type == class_enum]
                except KeyError:
                    pass

            if target_card_type:
                from src.common.enums import CardType
                try:
                    type_enum = CardType[target_card_type]
                    hand_cards = [c for c in hand_cards if c.get_type() == type_enum]
                except KeyError:
                    pass

            if target_cost is not None:
                if target_cost_condition == 'LESS':
                    hand_cards = [c for c in hand_cards if c.current_cost <= target_cost]
                elif target_cost_condition == 'MORE':
                    hand_cards = [c for c in hand_cards if c.current_cost >= target_cost]
                else:
                    hand_cards = [c for c in hand_cards if c.current_cost == target_cost]

        count = getattr(self.current_effect, 'value', 1) if hasattr(self, 'current_effect') and self.current_effect else 1
        if not isinstance(count, int):
            count = 1

        selected_targets = []
        for i in range(count):
            choices = {f"{c.get_display_name()} (ID {c.card_id})": c.card_id for c in hand_cards if c.card_id not in selected_targets}
            if not choices:
                break
            selected_card_id = game_state_manager.game.request_user_choice(f"패의 카드를 선택하세요 ({i+1}/{count}).", choices)
            if selected_card_id:
                selected_targets.append(selected_card_id)
            else:
                break

        return [game_state_manager.get_entity_by_id(cid) for cid in selected_targets]


    def _get_target_own_hand_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """자신의 패에서 무작위 카드를 선택합니다."""
        owner_id = self._get_owner_id(caster_card)
        hand_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.HAND)
        if not hand_cards:
            return []
        selectable_cards = [c for c in hand_cards if c.card_id != caster_card.card_id]
        if not selectable_cards:
            return []
        selected_card = random.choice(selectable_cards)
        return [selected_card]

    def _get_target_opponent_follower_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 상대 추종자 중 무작위 선택"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]

        if not opponent_followers:
            return []

        random.shuffle(opponent_followers)
        count = 1
        if hasattr(self, 'current_effect') and self.current_effect:
            count = getattr(self.current_effect, 'target_count', 1)
            try:
                count = int(count)
            except (ValueError, TypeError):
                count = 1
        selected_cards = []
        for _ in range(min(count, len(opponent_followers))):
            selected_cards.append(opponent_followers.pop())
        return selected_cards

    def _get_target_opponent_follower_max_attack_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 가장 공격력이 높은 상대 추종자 중 무작위 선택"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        opponent_cards = game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
        opponent_followers = [card for card in opponent_cards if card.get_type() == CardType.FOLLOWER]
        if not opponent_followers: return []
        max_attack = max(card.current_attack for card in opponent_followers)
        max_attack_followers = [card for card in opponent_followers if card.current_attack == max_attack]
        if not max_attack_followers: return []

        # 가장 공격력이 높은 추종자 중 랜덤 선택은 유지합니다.
        random.shuffle(max_attack_followers)
        selected_card = max_attack_followers.pop()

        return [selected_card]

    def _get_target_ally_follower_choice_unevolved(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 진화하지 않은 아군 추종자 선택"""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        unevolved_ally_followers = [card for card in ally_cards if card.get_type() == CardType.FOLLOWER and not card.is_evolved]
        if not unevolved_ally_followers: return []

        choices = {f"{f.get_display_name()} (ID: {f.card_id})": f.card_id for f in unevolved_ally_followers}
        selected_card_id = game_state_manager.game.request_user_choice("진화하지 않은 아군 추종자를 선택하세요:", choices)

        if selected_card_id:
            return [game_state_manager.get_entity_by_id(selected_card_id)]
        return []

    def _get_target_all_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 모든 추종자 전체"""
        all_cards = []
        for player in game_state_manager.players.values():
            all_cards.extend([c for c in player.field.get_cards() if c.get_type() == CardType.FOLLOWER])
        return all_cards

    def _get_target_another_ally_follower_random(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 자신 제외 아군 추종자 중 랜덤"""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        candidates = [c for c in ally_cards if c.get_type() == CardType.FOLLOWER and c.card_id != caster_card.card_id]
        if not candidates:
            return []
        import random
        return [random.choice(candidates)]

    def _get_target_all_opponents(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 상대 전체"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        opponent = game_state_manager.players[opponent_id]
        targets = [opponent]
        targets.extend([c for c in opponent.field.get_cards() if c.get_type() == CardType.FOLLOWER])
        return targets

    def _get_target_variable(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 변수"""
        return []

    def _get_target_own_deck(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 자신 덱"""
        return [game_state_manager.players[self._get_owner_id(caster_card)]]

    def _get_target_opponent_field(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 상대 필드 전체"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        opponent = game_state_manager.players[opponent_id]
        return opponent.field.get_cards()

    def _get_target_all_opponent_followers_damaged(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """대상 - 피해를 입은 상대 추종자 전체"""
        opponent_id = game_state_manager.opponent_id[self._get_owner_id(caster_card)]
        opponent = game_state_manager.players[opponent_id]
        opponent_followers = [c for c in opponent.field.get_cards() if c.get_type() == CardType.FOLLOWER]
        return [c for c in opponent_followers if c.current_defense < c.max_defense]

    def list_target(self, target_type: TargetType, caster_id: str,
                       game_state_manager: 'GameStateManager', effect_data: Effect = None):
        """타겟 타입을 해석하고 타겟 리스트를 반환합니다."""
        self.current_effect = effect_data
        caster_card = game_state_manager.get_entity_by_id(caster_id)
        if not caster_card:
            self._log_error(f"list_target - caster card with id {caster_id} not found.")
            return []
        # 통합 핸들러 호출을 사용합니다(내부에서 문자열에서 enum으로의 변환이 처리됩니다).
        return self._invoke_target_handler(target_type, caster_card, game_state_manager)


    def _process_stat_buff(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 스탯 버프"""
        value = effect_data.value
        attack, defense = value
        target.current_attack += attack
        target.current_defense += defense
        target.max_defense += defense
        self._log_info(f"[LOG] 처리 내용: 스텟 버프, 타겟: {target.get_display_name()}, 증가량: {value}")

    def _process_draw(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리 - 카드 드로우"""
        value = effect_data.value
        target_id = target.player_id
        condition_val = effect_data.get('condition')
        if condition_val and isinstance(condition_val, str):
            condition = lambda x: card_data.evaluate_condition(x, condition_val)
        else:
            condition = (lambda x: True)
        deck = game_state_manager.get_cards_in_zone(target_id, Zone.DECK, condition)

        if isinstance(value, list):
            count = len(value)
        else:
            try:
                count = int(value)
            except (ValueError, TypeError):
                count = 1

        for _ in range(count):
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

        print(f"[LOG] 처리 내용: 카드 드로우, 타겟: {target_id}, 드로우 장수: {count}")

    def _process_heal(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 체력 회복"""
        value = effect_data.value
        target.heal_damage(value)
        print(f"[LOG] 처리 내용: 체력 회복, 타겟: {target.get_display_name()}, 회복량: {value}")

    def _process_add_card_to_hand(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리 - 패에 카드 추가"""
        value = effect_data.value
        target_id = target.player_id

        # TargetType 인 경우 동적으로 대상을 평가합니다.
        if isinstance(value, TargetType):
            if value == TargetType.OPPONENT_DECK_RANDOM:
                opponent_id = "player2" if target_id == "player1" else "player1"
                opponent_deck = game_state_manager.get_cards_in_zone(opponent_id, Zone.DECK)
                count = min(5, len(opponent_deck))
                if count > 0:
                    chosen_cards = random.sample(opponent_deck, count)
                    value = [c.card_data for c in chosen_cards]
                else:
                    return

        if isinstance(value, card_data.CardData):
            card = game_state_manager.create_card_instance(value, target_id)
            if len(game_state_manager.get_cards_in_zone(target_id, Zone.HAND)) < 9:
                game_state_manager.add_card(card, Zone.HAND, target_id)
            else:
                game_state_manager.add_card(card, Zone.GRAVEYARD, target_id)
            print(f"[LOG] 처리 내용: 패에 카드 추가, 타겟: {target_id}, 추가 카드: {card.get_display_name()}")
            
            # 후속 조치 효과가 정의되어 있다면 실행합니다.
            post_action = getattr(effect_data, "post_action", None)
            if post_action:
                handler = self.process_handlers.get(post_action.process)
                if handler:
                    handler(post_action, card, game_state_manager)

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
                
                # 후속 조치 효과가 정의되어 있다면 실행합니다.
                post_action = getattr(effect_data, "post_action", None)
                if post_action:
                    handler = self.process_handlers.get(post_action.process)
                    if handler:
                        handler(post_action, card, game_state_manager)

    def _process_summon(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리 - 필드에 카드 소환"""
        value = effect_data.value
        target_id = target.player_id

        if isinstance(value, card_data.CardData):
            card = game_state_manager.create_card_instance(value, target_id)
            if len(game_state_manager.get_cards_in_zone(target_id, Zone.FIELD)) < 5:
                game_state_manager.add_card(card, Zone.FIELD, target_id)
            print(f"[LOG] 처리 내용: 필드에 카드 소환, 타겟: {target_id}, 소환 카드: {card.get_display_name()}")

            # 후속 조치 효과가 정의되어 있다면 실행합니다.
            post_action = getattr(effect_data, "post_action", None)
            if post_action:
                handler = self.process_handlers.get(post_action.process)
                if handler:
                    handler(post_action, card, game_state_manager)

        elif isinstance(value, list):
            value_copy = list(value)
            while value_copy:
                data = value_copy.pop()
                card = game_state_manager.create_card_instance(data, target_id)
                if len(game_state_manager.get_cards_in_zone(target_id, Zone.FIELD)) < 5:
                    game_state_manager.add_card(card, Zone.FIELD, target_id)
                print(f"[LOG] 처리 내용: 필드에 카드 소환, 타겟: {target_id}, 소환 카드: {card.get_display_name()}")

                # 후속 조치 효과가 정의되어 있다면 실행합니다.
                post_action = getattr(effect_data, "post_action", None)
                if post_action:
                    handler = self.process_handlers.get(post_action.process)
                    if handler:
                        handler(post_action, card, game_state_manager)

    def _process_summon_copy(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 복사본 소환"""
        caster_id = getattr(effect_data, "caster_id", "")
        caster_card = game_state_manager.get_entity_by_id(caster_id)

        owner_id = ""
        original_card_data = None

        if isinstance(target, Player):
            owner_id = target.player_id
            original_card_data = effect_data.value
        elif isinstance(target, Card):
            owner_id = target.owner_id
            original_card_data = target.card_data
        else:
            owner_id = self._get_owner_id(caster_card)
            if isinstance(caster_card, Card):
                original_card_data = caster_card.card_data

        if not original_card_data or not isinstance(original_card_data, card_data.CardData):
            if hasattr(effect_data, "value") and isinstance(effect_data.value, card_data.CardData):
                original_card_data = effect_data.value
            else:
                print("[WARNING] summon_copy - 원본 카드를 찾을 수 없습니다.")
                return

        if not owner_id:
            owner_id = self._get_owner_id(caster_card) or "player1"

        card = game_state_manager.create_card_instance(original_card_data, owner_id)
        if len(game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)) < 5:
            game_state_manager.add_card(card, Zone.FIELD, owner_id)

        print(f"[LOG] 처리 내용: 복사본 소환, 타겟: {owner_id}, 소환 카드: {card.get_display_name()}")

        # 후속 조치 효과가 정의되어 있다면 실행합니다.
        post_action = getattr(effect_data, "post_action", None)
        if post_action:
            handler = self.process_handlers.get(post_action.process)
            if handler:
                handler(post_action, card, game_state_manager)

    def _process_deal_damage(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 피해 입히기"""
        value = effect_data.value

        try:
            val = int(value)
        except (ValueError, TypeError):
            val = 0

        if target.has_keyword(EffectType.BARRIER):
            print(f"[LOG] {target.get_display_name()} 배리어로 데미지 0 받음.")
            val = 0
            target.effects = [effect for effect in target.effects if effect.type != EffectType.BARRIER]

        elif hasattr(target, "is_super_evolved") and target.is_super_evolved and game_state_manager.current_turn_player_id == target.owner_id:
            print(f"[LOG] {target.get_display_name()} 초진화 효과로 데미지 0 받음.")
            val = 0

        if target.take_damage(val):
            if target.get_type() == CardType.LEADER:
                # 게임 종료 처리를 수행합니다.
                pass
            else:
                target_id = target.card_id
                game_state_manager.move_card(target_id, Zone.FIELD, Zone.GRAVEYARD)
                self.event_manager.publish(DestroyedOnFieldEvent(target_id))
        print(f"[LOG] 처리 내용: 피해 입히기, 타겟: {target.get_display_name()}, 피해량: {value}")

    def _resolve_split_damage(self, effect_data: Effect, target_list: List[Any], game_state_manager: 'GameStateManager'):
        import copy
        try:
            remaining_damage = int(effect_data.value)
        except (ValueError, TypeError):
            remaining_damage = 0

        target_followers = [t for t in target_list if isinstance(t, Card) and t.get_type() == CardType.FOLLOWER]
        target_leaders = [t for t in target_list if isinstance(t, Player)]

        def sort_by_field_order(card):
            player = game_state_manager.players[card.owner_id]
            field_cards = player.field.get_cards()
            try:
                return field_cards.index(card)
            except ValueError:
                return 999
        target_followers.sort(key=sort_by_field_order)

        for follower in target_followers:
            if remaining_damage <= 0:
                break
            if follower.current_defense <= 0:
                continue
            damage_to_deal = min(remaining_damage, follower.current_defense)
            temp_effect = copy.deepcopy(effect_data)
            temp_effect.value = damage_to_deal
            self._process_deal_damage(temp_effect, follower, game_state_manager)
            remaining_damage -= damage_to_deal

        if remaining_damage > 0 and target_leaders:
            for leader in target_leaders:
                temp_effect = copy.deepcopy(effect_data)
                temp_effect.value = remaining_damage
                self._process_deal_damage(temp_effect, leader, game_state_manager)

    def _process_destroy(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 파괴"""
        if not hasattr(target, "card_id"):
            return
        if hasattr(target, "is_super_evolved") and target.is_super_evolved and game_state_manager.current_turn_player_id == target.owner_id:
            print(f"[LOG] 처리 내용: 파괴, 타겟: {target.get_display_name()}")
            print(f"[LOG] {target.get_display_name()} 초진화 효과로 파괴되지 않음.")
            return
        game_state_manager.move_card(target.card_id, Zone.FIELD, Zone.GRAVEYARD)
        self.event_manager.publish(DestroyedOnFieldEvent(target.card_id))
        print(f"[LOG] 처리 내용: 파괴, 타겟: {target.get_display_name()}")

    def _process_banish(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 소멸"""
        if not hasattr(target, "card_id"):
            return
        current_zone = getattr(target, "current_zone", Zone.FIELD)
        game_state_manager.move_card(target.card_id, current_zone, Zone.BANISHED)
        print(f"[LOG] 처리 내용 소멸, 타겟 {target.get_display_name()}.")

    def _process_select(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 선택. 선택된 아군 카드를 파괴 처리하거나 후속 조치를 실행합니다."""
        from src.common.enums import Zone, TargetType, ProcessType
        if not target or not hasattr(target, 'card_id'):
            return

        post_action = getattr(effect_data, "post_action", None)
        if post_action:
            proc_val = post_action.process if hasattr(post_action, "process") else post_action.get("process")
            handler = self.process_handlers.get(proc_val)
            if handler:
                # target이 손패에 있는 카드인 경우 (패 선택 후속 조치)
                if getattr(target, "current_zone", None) == Zone.HAND:
                    tgt_val = post_action.target if hasattr(post_action, "target") else post_action.get("target")
                    # post_action이 TargetType.SELF 를 지목하면 시전자 카드를 대상으로 후속 조치를 취합니다.
                    if tgt_val == TargetType.SELF:
                        caster_id = getattr(effect_data, "caster_id", None)
                        caster_card = game_state_manager.get_entity_by_id(caster_id) if caster_id else None
                        handler(post_action, caster_card or target, game_state_manager)
                    # 그 외 TRANSFORM, ADD_EFFECT 등의 카드 자체를 변형시키는 경우 target(선택된 카드)을 직접 전달합니다.
                    elif proc_val in (ProcessType.TRANSFORM, ProcessType.ADD_EFFECT):
                        handler(post_action, target, game_state_manager)
                    else:
                        post_action.value = target.card_data
                        owner = game_state_manager.players[target.owner_id]
                        handler(post_action, owner, game_state_manager)
                else:
                    # target이 필드에 있는 카드인 경우 (필드 선택 후속 조치)
                    handler(post_action, target, game_state_manager)
            return

        # 선택된 타겟 카드를 필드에서 묘지로 파괴 이동합니다.
        if target.is_super_evolved and game_state_manager.current_turn_player_id == target.owner_id:
            print(f"[LOG] 처리 내용: 선택 파괴 실패, 타겟 {target.get_display_name()}")
            print(f"[LOG] {target.get_display_name()} 초진화 효과로 파괴되지 않음.")
            return
        game_state_manager.move_card(target.card_id, Zone.FIELD, Zone.GRAVEYARD)
        self.event_manager.publish(DestroyedOnFieldEvent(target.card_id))
        print(f"[LOG] 처리 내용: 선택 파괴, 타겟 {target.get_display_name()}")

    def _process_recover_pp(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리 - PP 회복"""
        value = effect_data.value
        target.gain_pp(value)
        print(f"[LOG] 처리 내용: PP 회복, 타겟: {target.player_id}, 회복량: {value}")

    def _process_super_evolve(self, effect_data: Effect, target: Card, game_state_manager: 'GameStateManager'):
        """처리 - 초진화"""
        game_state_manager.super_evolve_card(target.card_id)
        self.event_manager.publish(FollowerSuperEvolvedEvent(target.card_id, spend_sep="False"))
        print(f"[LOG] 처리 내용: 초진화, 타겟: {target.get_display_name()}")

    def _process_evolve(self, effect_data: Effect, target: Card, game_state_manager: 'GameStateManager'):
        """처리 - 지정 카드를 진화시킵니다."""
        game_state_manager.evolve_card(target.card_id)
        from src.common.event import FollowerEvolvedEvent
        self.event_manager.publish(FollowerEvolvedEvent(target.card_id, spend_ep=False))
        print(f"[LOG] 처리 내용: 카드 진화, 타겟 {target.get_display_name()}")

    def _process_replace_deck(self, effect_data: Effect, target: Player, game_state_manager: 'GameStateManager'):
        """처리 - 덱 교체"""
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
        """처리 - 최대 체력 설정"""
        value = effect_data.value
        target.max_defense = value
        print(f"[LOG] 처리 내용: 최대 체력 설정, 타겟: {target.get_display_name()}, 설정값: {value}")

    def _process_add_keyword(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 키워드 부여"""
        value = effect_data.value
        if value is None:
            print(f"[LOG] 처리 내용: 키워드 부여 실패. 키워드가 존재하지 않습니다.")
            return

        if isinstance(value, list):
            for v in value:
                if isinstance(v, Effect):
                    target.effects.append(v)
                    print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name() if hasattr(target, 'get_display_name') else target}, 키워드: {v.type.value if hasattr(v, 'type') and hasattr(v.type, 'value') else v}")
                elif isinstance(v, EffectType):
                    new_eff = Effect(type=v)
                    target.effects.append(new_eff)
                    print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name() if hasattr(target, 'get_display_name') else target}, 키워드: {v.value}")
                elif isinstance(v, str):
                    try:
                        eff_type = EffectType[v.upper()]
                        new_eff = Effect(type=eff_type)
                        target.effects.append(new_eff)
                        print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name() if hasattr(target, 'get_display_name') else target}, 키워드: {eff_type.value}")
                    except KeyError:
                        print(f"[LOG] 처리 내용: 키워드 부여 경고. 알 수 없는 키워드 문자열 {v}")
        elif isinstance(value, Effect):
            target.effects.append(value)
            print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name() if hasattr(target, 'get_display_name') else target}, 키워드: {value.type.value if hasattr(value, 'type') and hasattr(value.type, 'value') else value}")
        elif isinstance(value, EffectType):
            new_eff = Effect(type=value)
            target.effects.append(new_eff)
            print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name() if hasattr(target, 'get_display_name') else target}, 키워드: {value.value}")
        elif isinstance(value, str):
            try:
                eff_type = EffectType[value.upper()]
                new_eff = Effect(type=eff_type)
                target.effects.append(new_eff)
                print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name() if hasattr(target, 'get_display_name') else target}, 키워드: {eff_type.value}")
            except KeyError:
                print(f"[LOG] 처리 내용: 키워드 부여 경고. 알 수 없는 키워드 문자열 {value}")

    def _process_remove_keyword(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 키워드 제거"""
        value = effect_data.value
        if value is None:
            target.effects = []
            val_str = "모든 능력"
        else:
            target.effects = [effect for effect in target.effects if not effect.type == value]
            val_str = value.value
        print(f"[LOG] 처리 내용 키워드 제거 타겟 {target.get_display_name()} 키워드 {val_str}.")


    def _process_return_to_deck(self, effect_data: Effect, target: Card, game_state_manager: 'GameStateManager'):
        """처리 - 덱으로 되돌리기"""
        game_state_manager.move_card(target.card_id, Zone.HAND, Zone.DECK)
        print(f"[LOG] 처리 내용: 덱으로 되돌리기, 타겟: {target.get_display_name()}")

    def _process_return_to_hand(self, effect_data: Effect, target: Card, game_state_manager: 'GameStateManager'):
        """처리 - 패로 되돌리기"""
        game_state_manager.move_card(target.card_id, Zone.FIELD, Zone.HAND)
        target.current_cost = target.card_data['cost']
        print(f"[LOG] 처리 내용: 패로 되돌리기, 타겟: {target.get_display_name()}")

    def _process_trigger_effect(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 다른 효과 발동"""
        value = effect_data.value
        if value == "random_unactivated":
            spell_effects = []
            for idx, effect in enumerate(target.effects):
                if effect.type == EffectType.SPELL:
                    spell_effects.append((idx, effect))
            if not spell_effects:
                return
            if not hasattr(target, "activated_abilities"):
                target.activated_abilities = set()
            unactivated = [(idx, eff) for idx, eff in spell_effects if idx not in target.activated_abilities]
            if unactivated:
                selected_idx, selected_eff = random.choice(unactivated)
                target.activated_abilities.add(selected_idx)
                self.resolve_effect(selected_eff, target.card_id, game_state_manager, None)
                print(f"[LOG] Slaus 효과 발동 - 인덱스 {selected_idx} 효과 실행.")
        else:
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

        # 설정된 조건이 있는 경우 시전자 카드가 이를 만족하는지 확인합니다.
        condition_str = effect_data.get("condition")
        if condition_str and isinstance(condition_str, str):
            from src.common import card_data as cd
            if not cd.evaluate_condition(caster_card, condition_str):
                print(f"[LOG] {caster_card.get_display_name()}의 조건 {condition_str} 미충족으로 효과 발동 실패.")
                return

        from copy import copy
        effect_data = copy(effect_data)
        effect_data.attributes = copy(effect_data.attributes)

        effect_data.update(caster_id=caster_id)

        # 변수 X의 값을 동적으로 해석하여 적용합니다.
        x_val = self._get_variable_value(caster_card, game_state_manager)
        self._resolve_effect_variables(effect_data, x_val)

        effect_type = getattr(effect_data, "type", None)

        # 대체(instead) 효과 체크 로직입니다.
        if isinstance(caster_card, Card) and effect_type in [EffectType.FANFARE, EffectType.SPELL]:
            raw_text = caster_card.card_data.get("raw_effects_text", "").lower()
            if "instead" in raw_text:
                # 콤보 대체 조건 검사
                has_combo = any(e.type == EffectType.COMBO for e in caster_card.effects)
                if has_combo:
                    import re
                    match = re.search(r"Combo\s*\((\d+)\)", caster_card.card_data.raw_effects_text, re.IGNORECASE)
                    req_combo = int(match.group(1)) if match else 3
                    player = game_state_manager.players[self._get_owner_id(caster_card)]
                    if player.combo_count >= req_combo:
                        print(f"[LOG] 콤보 조건 만족으로 인해 {effect_type.value if effect_type else 'None'} 효과 발동을 건너뛰고 콤보 효과로 대체합니다.")
                        return

                # 오의 대체 조건 검사
                has_sa = any(e.type == EffectType.SKYBOUND_ART for e in caster_card.effects)
                if has_sa:
                    sa_effects = [e for e in caster_card.effects if e.type == EffectType.SKYBOUND_ART]
                    if any(game_state_manager.turn_number + getattr(e, "skybound_art_evo_charge", 0) >= 10 for e in sa_effects):
                        print(f"[LOG] 오의 조건 만족으로 인해 {effect_type.value if effect_type else 'None'} 효과 발동을 건너뛰고 오의 효과로 대체합니다")
                        return

                # 해방오의 대체 조건 검사
                has_ssa = any(e.type == EffectType.SUPER_SKYBOUND_ART for e in caster_card.effects)
                if has_ssa:
                    ssa_effects = [e for e in caster_card.effects if e.type == EffectType.SUPER_SKYBOUND_ART]
                    if any(game_state_manager.turn_number + getattr(e, "skybound_art_evo_charge", 0) >= 15 for e in ssa_effects):
                        print(f"[LOG] 해방오의 조건 만족으로 인해 {effect_type.value if effect_type else 'None'} 효과 발동을 건너뛰고 해방오의 효과로 대체합니다")
                        return

        if effect_type == EffectType.COMBO:
            if isinstance(caster_card, Card):
                import re
                match = re.search(r"Combo\s*\((\d+)\)", caster_card.card_data.raw_effects_text, re.IGNORECASE)
                req_combo = int(match.group(1)) if match else 3
            else:
                req_combo = 3
            player = game_state_manager.players[self._get_owner_id(caster_card)]
            if player.combo_count < req_combo:
                print(f"[LOG] 콤보 카운트({player.combo_count})가 조건({req_combo})에 미달하여 효과 발동 실패.")
                return
            # value가 'X'인 경우, 다른 FANFARE나 SPELL 효과의 value 값을 복제하여 사용합니다.
            if effect_data.value == 'X':
                base_val = None
                if isinstance(caster_card, Card):
                    for e in caster_card.effects:
                        if e.type in [EffectType.FANFARE, EffectType.SPELL] and isinstance(e.value, int):
                            base_val = e.value
                            break
                if base_val is not None:
                    effect_data.value = base_val
                    print(f"[LOG] 콤보 효과의 수치 'X'를 기본 효과의 값인 {base_val}로 설정합니다.")
            print(f"[LOG] 콤보 {req_combo} 효과 발동.")

        elif effect_type == EffectType.SKYBOUND_ART:
            evo_charge = getattr(effect_data, "skybound_art_evo_charge", 0)
            total_charge = game_state_manager.turn_number + evo_charge
            if total_charge < 10:
                print(f"[LOG] 오의 게이지({total_charge}/10) 부족으로 효과 발동 실패.")
                return
            print(f"[LOG] 오의 효과 발동.")

        elif effect_type == EffectType.SUPER_SKYBOUND_ART:
            evo_charge = getattr(effect_data, "skybound_art_evo_charge", 0)
            total_charge = game_state_manager.turn_number + evo_charge
            if total_charge < 15:
                print(f"[LOG] 해방오의 게이지({total_charge}/15) 부족으로 효과 발동 실패.")
                return
            print(f"[LOG] 해방오의 효과 발동.")

        elif effect_type == EffectType.OVERFLOW:
            player = game_state_manager.players[self._get_owner_id(caster_card)]
            if not player.is_overflow:
                print(f"[LOG] 각성 조건 미충족으로 효과 발동 실패.")
                return
            print(f"[LOG] 각성 효과 발동.")

        elif effect_type == EffectType.RALLY:
            if isinstance(caster_card, Card):
                import re
                match = re.search(r"Rally\s*\((\d+)\)", caster_card.card_data.raw_effects_text, re.IGNORECASE)
                req_rally = int(match.group(1)) if match else 10
            else:
                req_rally = 10
            player = game_state_manager.players[self._get_owner_id(caster_card)]
            if player.rally_count < req_rally:
                print(f"[LOG] 연계 수치({player.rally_count})가 조건({req_rally})에 미달하여 효과 발동 실패.")
                return
            print(f"[LOG] 연계 {req_rally} 효과 발동.")

        if effect_type == EffectType.NECROMANCY:
            player = game_state_manager.players[self._get_owner_id(caster_card)]
            req_shadows = int(effect_data.value) if effect_data.value is not None else 0
            if player.graveyard.shadows_count >= req_shadows:
                player.graveyard.shadows_count -= req_shadows
                print(f"[LOG] 사령술 {req_shadows} 발동. 남은 그림자 수 {player.graveyard.shadows_count}.")
            else:
                print(f"[LOG] 그림자 수 부족으로 사령술 {req_shadows} 발동 실패. 현재 그림자 수 {player.graveyard.shadows_count}.")
                return

        if effect_type == EffectType.EARTH_RITE:
            player = game_state_manager.players[self._get_owner_id(caster_card)]
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
            effect_data.update(caster_id=caster_id)  # caster_id를 Effect 객체에 저장합니다.
            game_state_manager.is_awaiting_choice = True
            game_state_manager.pending_choice = effect_data
            game_state_manager.player_awaiting_choice = self._get_owner_id(caster_card)
            print(f"[LOG] {self._get_owner_id(caster_card)}의 선택 대기. 선택지: {effect_data.get('choices')}")
            return  # 여기서 처리를 중단하고 플레이어의 입력을 기다립니다.

        # 효과 처리 방식이 없거나 변수 정의인 경우 처리를 스킵하거나 후속 조치를 실행합니다.
        process_type = getattr(effect_data, "process", None)
        if not process_type or process_type == ProcessType.DEFINE_VARIABLE:
            # process가 없더라도 post_action이 있는 경우 시전자 카드를 대상으로 후속 조치를 직접 처리합니다.
            post_action = getattr(effect_data, "post_action", None)
            if post_action:
                proc_val = post_action.process if hasattr(post_action, "process") else post_action.get("process")
                handler = self.process_handlers.get(proc_val)
                if handler:
                    target = game_state_manager.get_entity_by_id(target_id) if target_id else caster_card
                    handler(post_action, target, game_state_manager)
            return

        handler = self.process_handlers.get(process_type)
        if not handler:
            print(f"[ERROR] 처리 타입 {process_type.value}에 대한 핸들러가 정의되지 않았습니다.")
            return

        print(f"[LOG] {caster_card.get_display_name()} (ID: {caster_id})의 키워드 {effect_type.value if effect_type else 'None'} 처리 시작")

        if target_id:
            target = game_state_manager.get_entity_by_id(target_id)
            handler(effect_data, target, game_state_manager)
            return

        target_type = effect_data.get('target')
        target_list = self.list_target(target_type, caster_id, game_state_manager, effect_data)

        if process_type == ProcessType.DEAL_DAMAGE and effect_data.get('is_split'):
            self._resolve_split_damage(effect_data, target_list, game_state_manager)
        else:
            for target in target_list:
                handler(effect_data, target, game_state_manager)

    def _process_reduce_cost(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 코스트 감소"""
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
        """처리 - 코스트 증가"""
        value = effect_data.value
        if hasattr(target, "current_cost"):
            try:
                val = int(value)
            except (ValueError, TypeError):
                val = 0
            target.current_cost = target.current_cost + val
            print(f"[LOG] 처리 내용 코스트 증가, 타겟 {target.get_display_name()}, 현재 코스트 {target.current_cost}.")

    def _process_set_cost(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 코스트 설정"""
        value = effect_data.value
        if hasattr(target, "current_cost"):
            try:
                val = int(value)
            except (ValueError, TypeError):
                val = 0
            target.current_cost = val
            print(f"[LOG] 처리 내용 코스트 설정, 타겟 {target.get_display_name()}, 현재 코스트 {target.current_cost}.")

    def _process_set_attack(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 공격력 설정"""
        value = effect_data.value
        if hasattr(target, "current_attack"):
            try:
                val = int(value)
            except (ValueError, TypeError):
                val = 0
            target.current_attack = val
            print(f"[LOG] 처리 내용 공격력 설정, 타겟 {target.get_display_name()}, 현재 공격력 {target.current_attack}.")

    def _process_advance_crest(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 문장 카운트 변경"""
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
        """처리 - 문장 파괴"""
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
        """처리 - EP 회복"""
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
        """처리 - 연계 회복"""
        if hasattr(target, "current_defense") and hasattr(target, "max_defense"):
            heal_amount = max(0, target.max_defense - target.current_defense)
            target.heal_damage(heal_amount)
            leader = game_state_manager.players[target.owner_id]
            leader.heal_damage(heal_amount)
            print(f"[LOG] 처리 내용 연계 회복, 타겟 {target.get_display_name()}, 회복량 {heal_amount}.")

    def _process_gain_shadow(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 묘지 그림자 증가"""
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
        """처리 - 사령 재생"""
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
        """처리 - 비술 마법진 획득"""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        sigil_data = card_data.CardData(
            card_id="Earth Sigil",
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
        """처리 - 변신"""
        if not isinstance(target, Card) or target.current_zone != Zone.FIELD:
            return

        new_card_data = effect_data.value
        owner_id = target.owner_id
        player = game_state_manager.players[owner_id]

        # TargetType 인 경우 동적으로 대상을 평가합니다.
        if isinstance(new_card_data, TargetType):
            if new_card_data == TargetType.OPPONENT_DECK_RANDOM:
                opponent_id = "player2" if owner_id == "player1" else "player1"
                opponent_deck = game_state_manager.get_cards_in_zone(opponent_id, Zone.DECK)
                if opponent_deck:
                    chosen_card = random.choice(opponent_deck)
                    new_card_data = chosen_card.card_data
                else:
                    print("[WARNING] Opponent deck is empty. Cannot transform.")
                    return
            elif new_card_data == TargetType.OWN_DECK_RANDOM_FOLLOWER:
                own_deck = game_state_manager.get_cards_in_zone(owner_id, Zone.DECK)
                followers = [c for c in own_deck if c.get_type() == CardType.FOLLOWER]
                if followers:
                    chosen_card = random.choice(followers)
                    new_card_data = chosen_card.card_data
                else:
                    print("[WARNING] Own deck has no followers. Cannot transform.")
                    return

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
        """처리 - 조건부 효과"""
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

    def _process_spellboost_hand(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 손패 주문 증폭"""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        caster_id = getattr(effect_data, "caster_id", None)
        times = 1
        if caster_id and game_state_manager.get_card_name(caster_id) == "William, Mysterian Student":
            times = 2
        elif effect_data.value is not None:
            try:
                times = int(effect_data.value)
            except (ValueError, TypeError):
                times = 1

        for _ in range(times):
            hand_cards = player.hand.get_cards()
            cards_with_sb = [c for c in hand_cards if c.has_keyword(EffectType.SPELLBOOST)]
            for card in cards_with_sb:
                card.spellboost_stacks += 1
                print(f"[LOG] 패의 {card.get_display_name()} 주문 증폭 스택 증가. 현재 스택 {card.spellboost_stacks}.")
                for effect in card.effects:
                    if effect.type == EffectType.SPELLBOOST:
                        self.resolve_effect(effect, card.card_id, game_state_manager, None)
    def _process_increase_skybound_art_gauge(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """처리 - 오의 및 해방오의 게이지 증가"""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        value = effect_data.value
        try:
            amount = int(value)
        except (ValueError, TypeError):
            amount = 1

        hand_cards = player.hand.get_cards()
        for card in hand_cards:
            for effect in card.effects:
                if effect.type in [EffectType.SKYBOUND_ART, EffectType.SUPER_SKYBOUND_ART]:
                    if hasattr(effect, "skybound_art_evo_charge"):
                        effect.skybound_art_evo_charge += amount
                        print(f"[LOG] {card.get_display_name()} 의 오의 진화 충전량 {amount} 증가 현재 충전량 {effect.skybound_art_evo_charge}")

    def _get_target_all_leaders_max_defense(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """체력이 가장 높은 리더들을 반환합니다."""
        players = list(game_state_manager.players.values())
        if not players:
            return []
        max_def = max(p.current_defense for p in players)
        return [p for p in players if p.current_defense == max_def]

    def _get_target_all_leaders_min_defense(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """체력이 가장 낮은 리더들을 반환합니다."""
        players = list(game_state_manager.players.values())
        if not players:
            return []
        min_def = min(p.current_defense for p in players)
        return [p for p in players if p.current_defense == min_def]

    def _get_target_another_ally_follower_random_unevolved(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """자신을 제외한 아군 진화 전 추종자 중 임의의 대상을 반환합니다."""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        candidates = [c for c in ally_cards if c.get_type() == CardType.FOLLOWER and c.card_id != caster_card.card_id and not c.is_evolved]
        if not candidates:
            return []
        return [random.choice(candidates)]

    def _get_target_ally_follower_random_super_evolved(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """아군 초진화 추종자 중 임의의 대상을 반환합니다."""
        owner_id = self._get_owner_id(caster_card)
        ally_cards = game_state_manager.get_cards_in_zone(owner_id, Zone.FIELD)
        candidates = [c for c in ally_cards if c.get_type() == CardType.FOLLOWER and c.is_super_evolved]
        if not candidates:
            return []
        return [random.choice(candidates)]

    def _get_target_summoned_followers(self, caster_card: Card, game_state_manager: 'GameStateManager') -> List[Any]:
        """방금 소환된 아군 추종자들을 반환합니다."""
        owner_id = self._get_owner_id(caster_card)
        return [c for c in game_state_manager.recently_summoned_cards if c.owner_id == owner_id]

    def _process_gain_max_pp(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """최대 PP를 증가시키는 처리를 담당합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        try:
            val = int(effect_data.value)
        except (ValueError, TypeError):
            val = 1

        player.max_pp = min(player.max_pp + val, player.MAX_PP)
        print(f"[LOG] 처리 내용 최대 PP 증가, 타겟 {player.player_id}, 증가량 {val}.")

    def _process_advance_countdown(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """마법진의 카운트다운을 진행시키는 처리를 담당합니다."""
        if not isinstance(target, Card) or target.countdown_value is None:
            return

        try:
            val = int(effect_data.value)
        except (ValueError, TypeError):
            val = 1

        target.countdown_value = max(0, target.countdown_value - val)
        print(f"[LOG] 처리 내용 카운트다운 진행, 타겟 {target.get_display_name()}, 진행 값 {val}, 남은 카운트다운 {target.countdown_value}.")

        if target.countdown_value == 0:
            game_state_manager.move_card(target.card_id, Zone.FIELD, Zone.GRAVEYARD)
            self.event_manager.publish(DestroyedOnFieldEvent(target.card_id))

    def _process_increase_combo(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """콤보 카운트를 강제로 증가시키는 처리를 담당합니다."""
        player = target
        if hasattr(target, "owner_id"):
            player = game_state_manager.players[target.owner_id]
        elif hasattr(target, "player_id"):
            player = target

        try:
            val = int(effect_data.value)
        except (ValueError, TypeError):
            val = 1

        player.combo_count += val
        print(f"[LOG] 처리 내용 콤보 카운트 증가, 타겟 {player.player_id}, 증가량 {val}, 현재 콤보 {player.combo_count}.")

    def _process_multi_attack(self, effect_data: Effect, target: Any, game_state_manager: 'GameStateManager'):
        """추종자에게 다중 공격 가능 횟수를 설정하는 처리를 담당합니다."""
        if not isinstance(target, Card):
            return

        try:
            val = int(effect_data.value)
        except (ValueError, TypeError):
            val = 2

        target.max_attack_count = val
        print(f"[LOG] 처리 내용 다중 공격 부여, 타겟 {target.get_display_name()}, 최대 공격 횟수 {val}.")