from typing import List, Any
from enums import CardType, EffectType, TargetType# 상대 경로 임포트

class CardData:
    """카드의 정적 데이터를 정의합니다."""
    def __init__(self, card_id: str, name: str, cost: int, card_type: CardType, attack: int = 0, defense: int = 0, effects: List = None):
        self.card_id = card_id
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.attack = attack  # 추종자 전용
        self.defense = defense  # 추종자 전용
        self.effects = effects if effects is not None else {}  # { 'type': EffectType, 'target': TargetType, 'value':... }
        # [1, 2, 3]

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """
        객체의 속성을 딕셔너리처럼 대괄호([])를 이용해 접근할 수 있게 합니다.
        예: card['cost']
        """
        # 만약 키가 존재하지 않을 때 KeyError 대신 AttributeError를 발생시키고 싶지 않다면
        # hasattr로 확인하는 로직을 추가할 수 있습니다.
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"CardData에 '{key}' 속성이 없습니다.")

# 예시 카드 데이터베이스 (실제로는 JSON 등 외부 파일에서 로드)
CARD_DATABASE = {
    "Indomitable Fighter": CardData("Indomitable Fighter", "불굴의 파이터", 2, CardType.FOLLOWER, 2, 2, effects=[
        {'type': EffectType.ENHANCE, 'target': TargetType.SELF, 'value': '4코스트, +3/+3을 얻는다.'}
    ]),
    "Leah, Bellringer Angel": CardData("Leah, Bellringer Angel", "종소리의 천사 리아", 2, CardType.FOLLOWER, 0, 2, effects=[
        {'type': EffectType.WARD},
        {'type': EffectType.LAST_WORDS, 'target': TargetType.OWN_LEADER, 'value': '덱에서 카드 1장을 뽑는다.'},
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.OWN_LEADER, 'value': '덱에서 카드 1장을 뽑는다.'}
    ]),
    "Quake Goliath": CardData("Quake Goliath", "격진의 골리앗", 4, CardType.FOLLOWER, 4, 5, effects=[
        {'type': EffectType.WARD}
    ]),
    "Detective's Lens": CardData("Detective's Lens", "탐정의 돋보기", 2, CardType.AMULET, effects=[
        {'type': EffectType.ACTIVATE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'value': '이 마법진을 파괴하고, 그 추종자는 수호 능력을 잃는다.'}
    ]),
    "Arriet, Luxminstrel": CardData("Arriet, Luxminstrel", "빛의 연주자 앙리에트", 3, CardType.FOLLOWER, 3, 3, effects=[
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.OWN_LEADER, 'value': '체력을 2 회복시킨다.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'target': TargetType.OWN_LEADER, 'value': '체력을 4 회복시킨다.'}
    ]),
    "Caravan Mammoth": CardData("Caravan Mammoth", "캐러밴 맘모스", 7, CardType.FOLLOWER, 10, 10, effects=[]),
    "Adventurers' Guild": CardData("Adventurers' Guild", "모험가 길드", 2, CardType.AMULET, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'value': '덱에서 추종자 카드 1장을 뽑는다.'},
        {'type': EffectType.ACTIVATE, 'target': TargetType.ALLY_FOLLOWER_CHOICE, 'value': '이 마법진을 파괴하고, 그 추종자는 돌진 능력을 얻는다.'}
    ]),
    "Ruby, Greedy Cherub": CardData("Ruby, Greedy Cherub", "욕심쟁이 지천사 루비", 2, CardType.FOLLOWER, 2, 2, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_HAND_CHOICE, 'value': '덱으로 되돌리고, 카드 1장을 뽑는다.'}
    ]),
    "Vigilant Detective": CardData("Vigilant Detective", "관찰하는 탐정", 3, CardType.FOLLOWER, 3, 3, effects=[
        {'type': EffectType.LAST_WORDS, 'target': TargetType.OWN_LEADER, 'value': '탐정의 돋보기 1장을 패에 넣는다.'}
    ]),
    "Goblin Foray": CardData("Goblin Foray", "고블린의 습격", 5, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.ALLY_FIELD, 'value': '고블린 5장을 내 전장에 소환한다.'}
    ]),
    "Goblin": CardData("Goblin", "고블린", 1, CardType.FOLLOWER, 1, 2, effects=[]),
    "Apollo, Heaven's Envoy": CardData("Apollo, Heaven's Envoy", "세찬 광명 아폴론", 3, CardType.FOLLOWER, 1, 2, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'value': '피해 1을 준다.'},
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'value': '출격 능력을 다시 발동시킨다.'}
    ]),
    "Seraphic Tidings": CardData("Seraphic Tidings", "치천사의 복음", 3, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.OWN_LEADER, 'value': '덱에서 카드 2장을 뽑는다.'}
    ]),
    "Phildau, Lionheart Ward": CardData("Phildau, Lionheart Ward", "낙랑의 천궁 필도어", 2, CardType.FOLLOWER, 2, 2, effects=[
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'value': '그 추종자를 파괴한다.'}
    ]),
    "Divine Thunder": CardData("Divine Thunder", "신의 뇌정", 4, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.OPPONENT_FOLLOWER_MAX_ATTACK_RANDOM, 'value': '공격력이 가장 높은 추종자 중 무작위로 1장을 파괴한다.'},
        {'type': EffectType.SPELL, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'value': '피해 1을 준다.'}
    ]),
    "Olivia, Heroic Dark Angel": CardData("Olivia, Heroic Dark Angel", "기백의 타천사 올리비에", 7, CardType.FOLLOWER, 4, 4, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'value': '카드를 2장 뽑는다.'},
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'value': '체력을 2 회복시킨다.'}, # 리더 체력 회복은 OWN_LEADER가 더 명확
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'value': 'PP를 2 회복시킨다.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'target': TargetType.ALLY_FOLLOWER_UNEVOLVED, 'value': '진화하지 않은 다른 아군 추종자 하나를 초진화시킨다.'}
    ]),
    "Ruler of Cocytus": CardData("Ruler of Cocytus", "종막의 죄 사탄", 10, CardType.FOLLOWER, 10, 10, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'value': '덱을 아포칼립스 덱으로 교체한다.'}
    ]),
    "Silent Rider": CardData("Silent Rider", "침묵의 마왕", 6, CardType.FOLLOWER, 10, 10, effects=[
        {'type': EffectType.STORM}
    ]),
    "Servant of Cocytus": CardData("Servant of Cocytus", "사탄의 하수인", 1, CardType.FOLLOWER, 13, 13, effects=[]),
    "Demon of Purgatory": CardData("Demon of Purgatory", "변옥의 악귀", 5, CardType.FOLLOWER, 9, 6, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE2, 'value': '2장을 선택하여 각각 피해 6을 준다.'},
        {'type': EffectType.FANFARE, 'target': TargetType.OPPONENT_LEADER, 'value': '피해 6을 준다.'},
    ]),
    "Astaroth's Reckoning": CardData("Astaroth's Reckoning", "아스타로트의 선고", 10, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.OPPONENT_LEADER, 'value': '체력 최대치를 1로 만든다.'}
    ])
}
