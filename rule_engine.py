from card import Card
from enums import Zone, CardType, EffectType
from game_state_manager import GameStateManager


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
            return False

        # 위압: 이 추종자는 공격의 대상이 될 수 없다.
        if target_card.has_keyword(EffectType.INTIMIDATE):
            print(f"DEBUG: {target_card.card_data['name']}은(는) '위압'으로 공격 대상이 될 수 없음.")
            return False

        # 잠복: 이 추종자는 공격하기 전까지 공격이나 능력의 대상이 될 수 없다.
        if target_card.has_keyword(EffectType.AMBUSH):
            print(f"DEBUG: {target_card.card_data['name']}은(는) '잠복중'으로 공격 대상이 될 수 없음.")
            return False

        # 수호: 상대는 수호가 없는 추종자를 공격할 수 없다.
        # 자신의 전장에 수호 추종자가 있고, 대상 추종자가 수호가 아닐 때
        opponent_field = self.game_state_manager.get_cards_in_zone(target_card.owner_id, Zone.FIELD)
        has_ward_on_field = any(f.has_keyword(EffectType.WARD) for f in opponent_field)
        if has_ward_on_field and not target_card.has_keyword(EffectType.WARD):
            print(f"DEBUG: '수호' 추종자가 필드에 있으므로 {target_card.card_data['name']}을(를) 공격할 수 없음.")
            return False

        return True  # 기본적으로 공격 가능

    def validate_play_card(self, card_id: str, player_id: str) -> bool:
        """카드 플레이의 유효성 검사 (PP, 필드 제한 등)"""
        card = self.game_state_manager.get_entity_by_id(card_id, Zone.HAND)
        player = self.game_state_manager.get_entity_by_id(player_id)

        current_pp = player.current_pp
        field_count = player.field.size()

        # PP 부족
        if current_pp < card.current_cost:
            # print(f"DEBUG: PP 부족. 현재 PP: {current_pp}, 카드 코스트: {card.current_cost}")
            return False

        # 필드 제한 (추종자/마법진)
        if (card.get_type() in [CardType.FOLLOWER, CardType.AMULET]) and field_count >= 5:
            # print(f"DEBUG: 전장 가득 참. 현재 전장: {field_count}, 최대: 5")
            return False

        return True

    def validate_attack(self, attacker_id: str, target_id: str) -> bool:
        """공격 유효성 검사"""
        attacker = self.game_state_manager.get_entity_by_id(attacker_id)
        target = self.game_state_manager.get_entity_by_id(target_id)

        if not attacker or not target:
            print("ERROR: validate_attack - attacker or target not found.")
            return False
        # 공격자가 공격 가능한 상태가 아닐 경우 (이미 공격함, 소환됨(돌진, 질주, 진화 예외))
        if not attacker.can_attack(target.get_type()):
            return False

        # 타겟팅 규칙 검증
        if target.get_type() == CardType.FOLLOWER:
            return self.can_target_follower(attacker_id, target_id)
        elif target.get_type() == CardType.LEADER:  # 리더 공격
            # 상대의 전장에 수호 추종자 확인
            opponent_field = self.game_state_manager.get_cards_in_zone(target.player_id, Zone.FIELD)
            has_ward_on_field = any(f.has_keyword(EffectType.WARD) for f in opponent_field)
            return not has_ward_on_field
        return False  # 알 수 없는 타겟 타입
