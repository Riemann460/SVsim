# 역할 정의. 게임의 종류, 타입, 영역, 페이즈, 효과, 처리 방식, 대상 및 종족을 구분하기 위한 열거형 상수 집합입니다.

from enum import Enum


class CardType(Enum):
    """카드 카테고리를 정의합니다."""
    FOLLOWER = "추종자"
    SPELL = "주문"
    AMULET = "마법진"
    LEADER = "리더"


class EventType(Enum):
    """게임 내에서 발생하는 이벤트 타입을 정의합니다."""
    CARD_ENGAGED = "카드_활성화됨"  # 활성화 효과 발동을 의미합니다.
    CARD_PLAYED = "카드_플레이됨"  # 출격 능력 발동을 의미합니다.
    DESTROYED_ON_FIELD = "필드_카드_파괴됨"  # 유언 능력 발동을 의미합니다.
    TURN_START = "턴_시작"  # 카운트다운 처리를 의미합니다.
    COMBAT_INITIATED = "교전_시작됨"  # 쌍방 교전시 능력 발동을 의미합니다.
    ATTACK_DECLARED = "공격_선언됨"  # 공격자 공격시 능력 발동을 의미합니다.
    SPELL_CAST = "주문_사용됨"  # 주문 효과 발동을 의미합니다.
    FOLLOWER_EVOLVED = "추종자_진화됨"  # 진화시 능력 발동을 의미합니다.
    FOLLOWER_SUPER_EVOLVED = "추종자_초진화됨"  # 초진화시 능력 발동을 의미합니다.
    DAMAGE_DEALT_BY_COMBAT = "데미지_입힘"  # 흡혈 능력 발동을 의미합니다.
    TURN_END = "턴_종료"  # 턴 종료시 발동을 의미합니다.
    FOLLOWER_ENTER_FIELD = "추종자_전장_소환됨"  # 추종자 소환시 능력 발동을 의미합니다.
    CARD_DISCARDED = "카드_버려짐"  # 카드 버려짐을 의미합니다.
    FUSE_DECLARED = "융합_선언됨"  # 융합 발동을 의미합니다.

    # 미구현 이벤트를 정의합니다.
    PP_GAINED = "PP_획득됨"
    HEALED = "회복됨"
    PP_SPENT = "PP_소모됨"
    GAME_START = "게임_시작"
    EXTRA_PP_USED = "엑스트라_PP_사용됨"
    CARD_DRAWN = "카드_드로우됨"
    CARD_MOVED_TO_GRAVEYARD = "카드_묘지로_이동됨"


class ClassType(Enum):
    """클래스(직업)를 정의합니다."""
    NEUTRAL = "Neutral"
    FORESTCRAFT = "Forestcraft"
    SWORDCRAFT = "Swordcraft"
    RUNECRAFT = "Runecraft"
    DRAGONCRAFT = "Dragoncraft"
    ABYSSCRAFT = "Abysscraft"
    HAVENCRAFT = "Havencraft"
    PORTALCRAFT = "Portalcraft"


class Zone(Enum):
    """게임 영역을 정의합니다."""
    DECK = "덱"
    HAND = "패"
    FIELD = "전장"
    GRAVEYARD = "묘지"
    BANISHED = "소멸"


class GamePhase(Enum):
    """턴 단계를 정의합니다."""
    START_PHASE = "시작_단계"
    MAIN_PHASE = "메인_단계"
    END_PHASE = "종료_단계"


class EffectType(Enum):
    """카드의 키워드 종류를 정의합니다."""
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
    ENGAGE = "활성화"
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
    COMBO = "콤보"
    EARTH_RITE = "흙의 비술"
    EARTH_SIGIL = "비술 마법진"
    NECROMANCY = "사령술"
    REANIMATE = "사령 재생"
    OVERFLOW = "각성"
    RALLY = "연계"
    SKYBOUND_ART = "오의"
    SUPER_SKYBOUND_ART = "해방오의"
    INVOKE = "직접소환"


class ProcessType(Enum):
    """효과의 처리 방식을 정의합니다."""
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
    GAIN_CREST = "문장 획득"
    FUSE = "융합"
    DISCARD = "버리기"
    REDUCE_COST = "코스트 감소"
    INCREASE_COST = "코스트 증가"
    SET_COST = "코스트 설정"
    SET_ATTACK = "공격력 설정"
    ADVANCE_CREST = "문장 카운트 증가"
    DESTROY_CREST = "문장 파괴"
    RECOVER_EP = "EP 회복"
    HEAL_LINKED = "연계 회복"
    GAIN_EARTH_SIGIL = "비술 마법진 획득"
    SPELLBOOST_HAND = "패 주문 증폭"
    CONDITIONAL_EFFECT = "조건부 효과"
    GAIN_SHADOW = "묘지 수 증가"
    TRANSFORM = "변신"
    REANIMATE = "사령 재생"

    # 미구현 프로세스들을 정의합니다.
    INCREASE_COMBO = "콤보 증가"
    ADVANCE_COUNTDOWN = "카운트다운 진행"
    DEFINE_VARIABLE = "변수 정의"
    MULTI_ATTACK = "다중 공격"
    GAIN_MAX_PP = "최대 PP 증가"
    IMMUNITY = "면역"
    SELECT = "선택"



class TargetType(Enum):
    """효과가 적용되는 대상을 정의합니다."""
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
    ALL_FOLLOWERS = "모든 추종자 전체"
    ANOTHER_ALLY_FOLLOWER_RANDOM = "자신 제외 아군 추종자 중 랜덤"
    ALL_OPPONENTS = "상대 전체"
    VARIABLE = "변수"
    OWN_DECK = "자신 덱"
    OPPONENT_FIELD = "상대 필드"
    ALL_OPPONENT_FOLLOWERS_DAMAGED = "피해를 입은 상대 추종자 전체"

    # 미구현 타겟들을 정의합니다.
    ALL_LEADERS_MAX_DEFENSE = "가장 체력이 높은 리더 전체"
    ALL_FOLLOWERS_MAX_DEFENSE = "가장 체력이 높은 추종자 전체"
    ANOTHER_ALLY_FOLLOWER_RANDOM_UNEVOLVED_NO_ATTACK = "자신 제외 공격하지 않은 진화전 아군 추종자 중 랜덤"
    ALLY_FOLLOWER_RANDOM_SUPER_EVOLVED = "아군 초진화 추종자 중 랜덤"
    ALL_LEADERS_MIN_DEFENSE = "가장 체력이 낮은 리더 전체"
    ALL_FOLLOWERS_MIN_DEFENSE = "가장 체력이 낮은 추종자 전체"
    ALL_NON_ENCROACHER_FOLLOWERS = "Encroacher가 아닌 추종자 전체"
    ANOTHER_ALLY_FOLLOWER_RANDOM_UNEVOLVED = "자신 제외 아군 진화전 추종자 중 랜덤"


class TribeType(Enum):
    """카드의 종족(타입)을 정의합니다."""
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