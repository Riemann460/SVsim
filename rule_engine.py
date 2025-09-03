from card import Card
from enums import Zone, CardType, EffectType
from game_state_manager import GameStateManager
from effect import Effect


class RuleEngine:
    """게임 규칙 상 행동의 유효성을 검사"""
    def __init__(self, game_state_manager: 'GameStateManager'):
        self.game_state_manager = game_state_manager

    def can_target_follower(self, attacker_card_id: str, target_card_id: str) -> bool:
        """추종자를 공격 대상으로 선택할 수 있는지 확인 (수호, 잠복, 위압, 오라)"""
        attacker_card = self.game_state_manager.get_entity_by_id(attacker_card_id)
        target_card = self.game_state_manager.get_entity_by_id(target_card_id)

        # 자신의 추종자는 공격 대상으로 선택 불가
        if attacker_card.owner_id == target_card.owner_id:
            print(f"[LOG] {attacker_card.get_display_name()} (ID: {attacker_card_id})는 자신의 추종자 {target_card.get_display_name()} (ID: {target_card_id})를 공격할 수 없습니다.")
            return False

        # 위압: 이 추종자는 공격의 대상이 될 수 없다.
        if target_card.has_keyword(EffectType.INTIMIDATE):
            print(f"[LOG] {target_card.get_display_name()}은(는) '위압'으로 공격 대상이 될 수 없습니다.")
            return False

        # 잠복: 이 추종자는 공격하기 전까지 공격이나 능력의 대상이 될 수 없다.
        if target_card.has_keyword(EffectType.AMBUSH):
            print(f"[LOG] {target_card.get_display_name()} (ID: {target_card_id})은(는) '잠복중'으로 공격 대상이 될 수 없습니다.")
            return False

        # 수호: 상대는 수호가 없는 추종자를 공격할 수 없다.
        # 자신의 전장에 수호 추종자가 있고, 대상 추종자가 수호가 아닐 때
        opponent_field = self.game_state_manager.get_cards_in_zone(target_card.owner_id, Zone.FIELD)
        has_ward_on_field = any(f.has_keyword(EffectType.WARD) for f in opponent_field)
        if has_ward_on_field and not target_card.has_keyword(EffectType.WARD):
            print(f"[LOG] '수호' 추종자가 필드에 있으므로 {target_card.get_display_name()} (ID: {target_card_id})을(를) 공격할 수 없습니다.")
            return False

        print(f"[LOG] {attacker_card.get_display_name()} (ID: {attacker_card_id})가 {target_card.get_display_name()} (ID: {target_card_id})를 공격할 수 있습니다.")
        return True  # 기본적으로 공격 가능

    def validate_play_card(self, card_id: str, player_id: str, use_extra_pp: bool) -> bool:
        """카드 플레이의 유효성 검사 (PP, 필드 제한 등)"""
        card = self.game_state_manager.get_entity_by_id(card_id, Zone.HAND)
        player = self.game_state_manager.get_entity_by_id(player_id)

        current_pp = player.current_pp
        field_count = player.field.size()

        # PP 부족
        if current_pp + (1 if use_extra_pp else 0) < card.current_cost:
            print(f"[LOG] {player_id}의 PP ({current_pp}) 부족으로 {card.get_display_name()} (ID: {card_id}) 플레이 불가. 필요 PP: {card.current_cost}")
            return False

        # 필드 제한 (추종자/마법진)
        if (card.get_type() in [CardType.FOLLOWER, CardType.AMULET]) and field_count >= 5:
            print(f"[LOG] {player_id}의 필드 ({field_count}개) 가득 차서 {card.get_display_name()} (ID: {card_id}) 플레이 불가.")
            return False

        print(f"[LOG] {player_id}가 {card.get_display_name()} (ID: {card_id})를 플레이할 수 있습니다.")
        return True

    def validate_activate_amulet(self, card_id: str, player_id: str) -> bool:
        """마법진 활성화의 유효성 검사 (PP, 대상 제한 등)"""
        card = self.game_state_manager.get_entity_by_id(card_id, Zone.FIELD)
        player = self.game_state_manager.get_entity_by_id(player_id)
        activate_effect: Effect = self.game_state_manager.get_card_effects(card_id, EffectType.ACTIVATE)[0]
        
        # 이번 턴에 활성화 했다면 불가능
        if card.is_activated:
            print(f"[LOG] {card.get_display_name()} (ID: {card_id})는 이번 턴에 이미 활성화되었습니다.")
            return False

        # 활성화에 코스트가 있고 PP 부족하면 불가능
        if 'cost' in activate_effect.attributes.keys():
            current_pp = player.current_pp
            # PP 부족
            if current_pp < activate_effect.cost:
                print(f"[LOG] {player_id}의 PP ({current_pp}) 부족으로 {card.get_display_name()} (ID: {card_id}) 활성화 불가. 필요 PP: {activate_effect.cost}")
                return False
        print(f"[LOG] {player_id}가 {card.get_display_name()} (ID: {card_id})를 활성화할 수 있습니다.")
        return True

    def validate_attack(self, attacker_id: str, target_id: str) -> bool:
        """공격 유효성 검사"""
        attacker = self.game_state_manager.get_entity_by_id(attacker_id)
        target = self.game_state_manager.get_entity_by_id(target_id)

        if not attacker or not target:
            print(f"[ERROR] validate_attack - 공격자 (ID: {attacker_id}) 또는 대상 (ID: {target_id})을(를) 찾을 수 없습니다.")
            return False
        # 공격자가 공격 가능한 상태가 아닐 경우 (이미 공격함, 소환됨(돌진, 질주, 진화 예외))
        if not attacker.can_attack(target.get_type()):
            print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id})는 {target.get_display_name()} (ID: {target_id})을(를) 공격할 수 없는 상태입니다.")
            return False

        # 타겟팅 규칙 검증
        if target.get_type() == CardType.FOLLOWER:
            return self.can_target_follower(attacker_id, target_id)
        elif target.get_type() == CardType.LEADER:  # 리더 공격
            # 상대의 전장에 수호 추종자 확인
            opponent_field = self.game_state_manager.get_cards_in_zone(target.player_id, Zone.FIELD)
            has_ward_on_field = any(f.has_keyword(EffectType.WARD) for f in opponent_field)
            if has_ward_on_field:
                print(f"[LOG] 상대 필드에 수호 추종자가 있어 리더 ({target.player_id})를 공격할 수 없습니다.")
                return False
            print(f"[LOG] {attacker.get_display_name()} (ID: {attacker_id})가 리더 ({target.player_id})를 공격할 수 있습니다.")
            return True
        print(f"[ERROR] validate_attack - 알 수 없는 타겟 타입: {target.get_type().value}")
        return False  # 알 수 없는 타겟 타입