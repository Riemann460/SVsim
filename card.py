import uuid
from typing import List, Dict, Any

from enums import TargetType, EffectType


class Card:
    """게임 내 개별 카드 인스턴스"""
    def __init__(self, card_data: Dict[str, Any], owner_id: str):
        self.card_id = str(uuid.uuid4()) # 고유 ID
        self.card_data = card_data  # CardData에서 로드된 정적 데이터
        self.owner_id = owner_id
        self.current_cost = card_data.get("cost", 0)  # 현재 코스트 (주문 증폭 등에 의해 변경될 수 있음)
        self.current_attack = card_data.get("attack", 0)  # 현재 공격력
        self.current_defense = card_data.get("defense", 0)  # 현재 체력
        self.max_defense = card_data.get("defense", 0)  # 최대 체력
        self.is_evolved = False  # 진화 여부
        self.is_engaged = False  # 공격 완료 여부
        self.is_summoned = True  # 현재 턴 소환 여부
        self.current_zone = None  # 현재 카드 위치 (Zone Enum)
        self.effects = card_data.get("effects", [])  # 카드 효과 인스턴스

        # 키워드별 추가 상태
        self.countdown_value = card_data.get("countdown", None)  # 카운트다운 마법진용
        self.spellboost_stacks = 0  # 주문 증폭용

    def take_damage(self, amount: int):
        """추종자가 피해를 입음"""
        self.current_defense -= amount
        print(f"DEBUG: {self.card_data['name']}이(가) {amount} 피해를 입음. 남은 체력: {self.current_defense}")
        if self.current_defense <= 0:
            return True  # 파괴됨
        return False

    def heal_damage(self, amount: int):
        """추종자가 회복됨"""
        self.current_defense = min(self.current_defense+amount, self.max_defense)
        # self.event_manager.publish(EventType.HEALED, {'player_id': self.player_id, 'amount': amount, 'current_hp': self.leader_hp})
        print(f"{self.card_data['name']}이(가) {amount} 체력을 회복했습니다. 현재 체력: {self.current_defense}")

    def can_attack(self, target_type: TargetType):
        """추종자가 공격할 수 있는지 확인"""
        # 공격한 턴에는 공격 불가
        if self.engaged:
            return False

        # 소환된 다음 턴 부터는 같은 턴에 공격하지 않았다면 제한없이 가능
        if not self.is_summoned:
            return True

        # 질주가 아닌 이상 소환된 턴에 리더 공격 불가
        if target_type == TargetType.OPPONENT_LEADER:
            return self.has_keyword(EffectType.STORM) and not self.is_engaged

        # 진화, 돌진, 질주가 아닌 이상 소환된 턴에 추종자 공격 불가
        return self.is_evolved or self.has_keyword(EffectType.RUSH) or self.has_keyword(EffectType.STORM)

    def has_keyword(self, keyword_name: EffectType) -> bool:
        """특정 키워드 능력을 가지고 있는지 확인"""
        return any(effect.get('type') == keyword_name for effect in self.effects)

    def get_type(self):
        """카드 타입을 반환"""
        return self.card_data['card_type']