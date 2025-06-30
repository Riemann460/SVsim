from enum import Enum

class CardType(Enum):
    """카드 카테고리 정의"""
    FOLLOWER = "추종자"
    SPELL = "주문"
    AMULET = "마법진"

class EventType(Enum):
    """게임 내에서 발생하는 이벤트 타입 정의"""
    CARD_PLAYED = "카드_플레이됨"
    FOLLOWER_DESTROYED = "추종자_파괴됨"
    TURN_START = "턴_시작"
    COMBAT_INITIATED = "교전_시작됨"
    ATTACK_DECLARED = "공격_선언됨"
    SPELL_CAST = "주문_사용됨"
    FOLLOWER_EVOLVED = "추종자_진화됨"
    DAMAGE_DEALT = "데미지_입힘"
    PP_GAINED = "PP_획득됨" # 각성 조건 확인용
    # 추가적인 이벤트 타입
    GAME_START = "게임_시작"
    TURN_END = "턴_종료"
    EXTRA_PP_USED = "엑스트라_PP_사용됨"
    CARD_DRAWN = "카드_드로우됨"
    CARD_MOVED_TO_GRAVEYARD = "카드_묘지로_이동됨" # 사령술, 유언 등

class Zone(Enum):
    """게임 영역 정의"""
    DECK = "덱"
    HAND = "패"
    FIELD = "전장"
    GRAVEYARD = "묘지"
    BANISHED = "추방"

class GamePhase(Enum):
    """턴 단계 정의"""
    START_PHASE = "시작_단계"
    MAIN_PHASE = "메인_단계"
    END_PHASE = "종료_단계"