from enum import Enum


class CardType(Enum):
    """카드 카테고리 정의"""
    FOLLOWER = "추종자"
    SPELL = "주문"
    AMULET = "마법진"
    LEADER = "리더"


class EventType(Enum):
    """게임 내에서 발생하는 이벤트 타입 정의"""
    AMULET_ACTIVATED = "마법진_활성화됨"  # 활성화 효과 발동
    CARD_PLAYED = "카드_플레이됨"  # 출격 능력 발동
    DESTROYED_ON_FIELD = "필드_카드_파괴됨"  # 유언 능력 발동
    TURN_START = "턴_시작"  # 카운트다운 처리
    COMBAT_INITIATED = "교전_시작됨"  # 쌍방 교전시 능력 발동
    ATTACK_DECLARED = "공격_선언됨"  # 공격자 공격시 능력 발동
    SPELL_CAST = "주문_사용됨"  # 주문 효과 발동
    FOLLOWER_EVOLVED = "추종자_진화됨"  # 진화시 능력 발동
    FOLLOWER_SUPER_EVOLVED = "추종자_초진화됨"  # 초진화시 능력 발동
    DAMAGE_DEALT_BY_COMBAT = "데미지_입힘"  # 흡혈 능력 발동
    TURN_END = "턴_종료"  # 턴 종료시 발동
    FOLLOWER_ENTER_FIELD = "추종자_전장_소환됨"  # 추종자 소환시 능력 발동
#    PP_GAINED = "PP_획득됨"
#    HEALED = "회복됨"
#    PP_SPENT = "PP_소모됨"
#    GAME_START = "게임_시작"
#    EXTRA_PP_USED = "엑스트라_PP_사용됨"
#    CARD_DRAWN = "카드_드로우됨"
#    CARD_MOVED_TO_GRAVEYARD = "카드_묘지로_이동됨"


class ClassType(Enum):
    """클래스(직업) 정의"""
    NEUTRAL = "Neutral"
    FORESTCRAFT = "Forestcraft"
    SWORDCRAFT = "Swordcraft"
    RUNECRAFT = "Runecraft"
    DRAGONCRAFT = "Dragoncraft"
    ABYSSCRAFT = "Abysscraft"
    HAVENCRAFT = "Havencraft"
    PORTALCRAFT = "Portalcraft"


class Zone(Enum):
    """게임 영역 정의"""
    DECK = "덱"
    HAND = "패"
    FIELD = "전장"
    GRAVEYARD = "묘지"
    BANISHED = "소멸"


class GamePhase(Enum):
    """턴 단계 정의"""
    START_PHASE = "시작_단계"
    MAIN_PHASE = "메인_단계"
    END_PHASE = "종료_단계"


class EffectType(Enum):
    """카드의 키워드 종류를 정의"""
    CHOOSE = "모드 선택"
    SPELLBOOST = "주문 증폭"
    AURA = "오라"
    CLASH = "교전시"
    STRIKE = "공격시"
    FANFARE = "출격"
    LAST_WORDS = "유언"
    ON_EVOLVE = "진화시"
    EVOLVED = "진화하면"
    ON_SUPER_EVOLVE = "초진화시"
    ON_MY_TURN_END = "내 턴 종료시"
    ON_OPPONENTS_TURN_END = "상대방 턴 종료시"
    ON_FOLLOWER_ENTER_FIELD = "추종자가 전장에 소환되었을 때"
    SUPER_EVOLVED = "초진화하면"
    ACTIVATE = "활성화"
    WARD = "수호"
    RUSH = "돌진"
    STORM = "질주"
    ENHANCE = "증강"
    SPELL = "주문 효과"
    COUNTDOWN = "카운트다운"
    BARRIER = "배리어"
    DRAIN = "흡혈"
    INTIMIDATE = "위압"
    AMBUSH = "잠복"
    BANE = "필살"


class ProcessType(Enum):
    """효과의 처리 방식을 정의"""
    CHOOSE = "모드 선택"
    STAT_BUFF = "스탯 버프"
    DRAW = "카드 드로우"
    HEAL = "체력 회복"
    ADD_CARD_TO_HAND = "패에 카드 추가"
    SUMMON = "필드에 소환"
    DEAL_DAMAGE = "피해 입히기"
    DESTROY = "파괴"
    BANISH = "소멸"
    RECOVER_PP = "PP 회복"
    SUPER_EVOLVE = "초진화"
    REPLACE_DECK = "덱 교체"
    SET_MAX_HEALTH = "최대 체력 설정"
    SET_DEFENSE = "체력 설정"
    ADD_EFFECT = "키워드 부여"
    REMOVE_KEYWORD = "키워드 제거"
    RETURN_TO_DECK = "카드를 덱으로 되돌림"
    RETURN_TO_HAND = "카드를 패로 되돌림"
    TRIGGER_EFFECT = "다른 효과 발동"


class TargetType(Enum):
    """효과가 적용되는 대상을 정의"""
    SELF = "자기 자신"
    OWN_LEADER = "자기 리더"
    OPPONENT_LEADER = "상대 리더"
    ANOTHER_ALLY_FOLLOWER_CHOICE = "자신 제외 아군 추종자 단일 선택"
    ALLY_FOLLOWER_CHOICE = "아군 추종자 단일 선택"
    OPPONENT_FOLLOWER_CHOICE = "상대 추종자 단일 선택"
    OPPONENT_FOLLOWER_CHOICE2 = "상대 추종자 중 둘 선택"
    ALL_OTHER_ALLY_FOLLOWERS = "나머지 아군 추종자 전체"
    ALL_ALLY_FOLLOWERS = "아군 추종자 전체"
    ALL_OPPONENT_FOLLOWERS = "상대 추종자 전체"
    OPPONENT_FOLLOWER_RANDOM = "상대 추종자 중 랜덤"
    OWN_HAND_CHOICE = "자기 패 단일 선택"
    OPPONENT_FOLLOWER_MAX_ATTACK_RANDOM = "상대 추종자 중 가장 공격력이 높은 추종자 중 랜덤"
    ALLY_FOLLOWER_CHOICE_UNEVOLVED = "진화하지 않은 아군 추종자 단일 선택"


class TribeType(Enum):
    """카드의 종족(타입)을 정의"""
    EARTH_SIGIL = "Earth_Sigil"
    LUMINOUS = "Luminous"
    LEVIN = "Levin"
    MYSTERIA = "Mysteria"
    ANATHEMA = "Anathema"
    OFFICER = "Officer"
    GOLEM = "Golem"
    SHIKIGAMI = "Shikigami"
    MARINE = "Marine"
    DEPARTED = "Departed"
    PUPPETRY = "Puppetry"
    ARTIFACT = "Artifact"