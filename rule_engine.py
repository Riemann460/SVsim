from card import Card
from enums import Zone, CardType
from game_state_manager import GameStateManager


class RuleEngine:
    """게임 규칙을 시행하고 행동의 유효성을 검사"""
    def __init__(self, game_state_manager: 'GameStateManager'):
        self.game_state_manager = game_state_manager

    def can_target_follower(self, attacker_card: Card, target_card: Card, player_id: str) -> bool:
        """추종자를 공격 대상으로 선택할 수 있는지 확인 (수호, 잠복, 위압, 오라)"""
        # 자신의 추종자는 공격 대상으로 선택 불가 (일반적인 규칙)
        if attacker_card.owner_id == target_card.owner_id:
            return False

        # 위압: 이 추종자는 공격의 대상이 될 수 없다.
        if target_card.has_keyword("위압"):
            print(f"DEBUG: {target_card.card_data['name']}은(는) '위압'으로 공격 대상이 될 수 없음.")
            return False

        # 수호: 상대는 수호가 없는 추종자를 공격할 수 없다.
        # 자신의 전장에 수호 추종자가 있고, 대상 추종자가 수호가 아닐 때
        opponent_field = self.game_state_manager.get_cards_in_zone(player_id, Zone.FIELD)
        has_ward_on_field = any(f.has_keyword("수호") for f in opponent_field)
        if has_ward_on_field and not target_card.has_keyword("수호"):
            print(f"DEBUG: '수호' 추종자가 필드에 있으므로 {target_card.card_data['name']}을(를) 공격할 수 없음.")
            return False

        return True # 기본적으로 공격 가능

    def can_target_with_ability(self, ability_caster: Card, target_card: Card, target_player_id: str) -> bool:
        """능력의 대상으로 추종자를 선택할 수 있는지 확인 (오라, 잠복)"""
        # 오라: 이 추종자는 상대방 능력의 대상으로 선택될 수 없다.
        if target_card.has_keyword("오라"):
            print(f"DEBUG: {target_card.card_data['name']}은(는) '오라'로 능력 대상이 될 수 없음.")
            return False

        # 잠복: 상대방의 능력 대상으로 선택되지 않는다.
        if target_card.has_keyword("잠복") and target_card.has_stealth: # 잠복 상태일 때만
            print(f"DEBUG: {target_card.card_data['name']}은(는) '잠복'으로 능력 대상이 될 수 없음.")
            return False
        return True

    def validate_play_card(self, card: Card, player_id: str) -> bool:
        """카드 플레이의 유효성 검사 (PP, 필드 제한 등)"""
        current_pp = self.game_state_manager.get_player_pp(player_id)
        field_count = len(self.game_state_manager.get_cards_in_zone(player_id, Zone.FIELD))

        # PP 부족
        if current_pp < card.current_cost:
            print(f"DEBUG: PP 부족. 현재 PP: {current_pp}, 카드 코스트: {card.current_cost}")
            return False

        # 필드 제한 (추종자/마법진)
        if (card.card_data['type'] == CardType.FOLLOWER.value or card.card_data['type'] == CardType.AMULET.value) and field_count >= 5:
            print(f"DEBUG: 전장 가득 참. 현재 전장: {field_count}, 최대: 5")
            return False

        return True

    def validate_attack(self, attacker: Card, target: Card, player_id: str) -> bool:
        """공격 유효성 검사"""
        if attacker.owner_id != player_id: # 자신의 카드가 아니면 공격 불가
            return False
        if attacker.is_engaged: # 이미 공격했으면 공격 불가
            return False
        if attacker.card_data['type'] != CardType.FOLLOWER.value: # 추종자만 공격 가능
            return False

        # 질주/돌진 추종자가 소환된 턴에 공격할 수 없는 경우 (잠복 해제)
        if attacker.has_keyword("잠복") and attacker.has_stealth:
            print(f"DEBUG: 잠복 추종자 {attacker.card_data['name']}이(가) 공격하여 잠복 해제됨.")
            attacker.has_stealth = False # 공격 시 잠복 해제

        # 타겟팅 규칙 검증
        if target.card_data['type'] == CardType.FOLLOWER.value:
            return self.can_target_follower(attacker, target, player_id)
        elif target.card_data['type'] == "리더": # 리더 공격
            return True # 리더 공격은 보통 항상 가능하지만, 수호에 의해 제한될 수 있음
        return False # 알 수 없는 타겟 타입
