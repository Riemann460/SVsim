import uuid
from typing import List, Dict, Any


class Card:
    """게임 내 개별 카드 인스턴스"""
    def __init__(self, card_data: Dict[str, Any], owner_id: str):
        self.card_id = str(uuid.uuid4()) # 고유 ID
        self.card_data = card_data # CardData에서 로드된 정적 데이터
        self.owner_id = owner_id
        self.current_cost = card_data.get("cost", 0) # 현재 코스트 (주문 증폭 등에 의해 변경될 수 있음)
        self.current_attack = card_data.get("attack", 0) # 현재 공격력
        self.current_defense = card_data.get("defense", 0) # 현재 체력
        self.is_evolved = False # 진화 여부
        self.is_engaged = False # 참여 여부 (공격 완료 또는 수호 능력 사용)
        self.current_zone = None # 현재 카드 위치 (Zone Enum)
        self.keywords = self._parse_keywords(card_data.get("keywords", [])) # 키워드 능력 인스턴스

        # 키워드별 추가 상태
        self.countdown_value = card_data.get("countdown", None) # 카운트다운 마법진용
        self.spellboost_stacks = 0 # 주문 증폭용
        self.has_storm_this_turn = False # 질주/돌진 추종자가 이번 턴에 공격했는지 여부
        self.has_stealth = '잠복' in [k['name'] for k in self.keywords] # 잠복 상태

    def _parse_keywords(self, keyword_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """키워드 데이터를 파싱하여 내부적으로 사용 가능한 형태로 변환"""
        # 여기서는 단순히 딕셔너리 리스트로 저장하지만, 실제로는 KeywordAbility 클래스 인스턴스가 될 수 있음
        return keyword_data

    def take_damage(self, amount: int):
        """추종자가 피해를 입음"""
        self.current_defense -= amount
        print(f"DEBUG: {self.card_data['name']}이(가) {amount} 피해를 입음. 남은 체력: {self.current_defense}")
        if self.current_defense <= 0:
            return True # 파괴됨
        return False

    def can_attack(self, target_type: str = "follower"):
        """추종자가 공격할 수 있는지 확인"""
        # 진화한 턴, 질주, 돌진이 아닌 이상 소환된 턴에 공격 불가
        if self.is_evolved or '질주' in [k['name'] for k in self.keywords] or '돌진' in [k['name'] for k in self.keywords]:
            return True
        # 일반 추종자는 다음 턴부터 공격 가능
        # 이 로직은 턴 시작 시 engaged 상태를 리셋하는 것과 연관됨
        return not self.is_engaged and not self.has_storm_this_turn

    def has_keyword(self, keyword_name: str) -> bool:
        """특정 키워드 능력을 가지고 있는지 확인"""
        return any(k['name'] == keyword_name for k in self.keywords)