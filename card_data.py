from typing import List, Any
from enums import CardType, EffectType, TargetType, ProcessType# 상대 경로 임포트

class CardData:
    """카드의 정적 데이터를 정의합니다."""
    def __init__(self, card_id: str, name: str, cost: int, card_type: CardType, attack: int = 0, defense: int = 0, effects: List = None):
        self.card_id = card_id  # 영문명
        self.name = name  # 한글명
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
        {'type': EffectType.ENHANCE, 'target': TargetType.SELF, 'enhance_cost': 4, 'process': ProcessType.STAT_BUFF, 'value': (3, 3)}
    ]),
    "Leah, Bellringer Angel": CardData("Leah, Bellringer Angel", "종소리의 천사 리아", 2, CardType.FOLLOWER, 0, 2, effects=[
        {'type': EffectType.WARD},
        {'type': EffectType.LAST_WORDS, 'target': TargetType.OWN_LEADER, 'process': ProcessType.DRAW, 'value': 1},
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.DRAW, 'value': 1}
    ]),
    "Quake Goliath": CardData("Quake Goliath", "격진의 골리앗", 4, CardType.FOLLOWER, 4, 5, effects=[
        {'type': EffectType.WARD}
    ]),
    "Detective's Lens": CardData("Detective's Lens", "탐정의 돋보기", 2, CardType.AMULET, effects=[
        {'type': EffectType.ACTIVATE, 'target': TargetType.SELF, 'process': ProcessType.DESTROY},
        {'type': EffectType.ACTIVATE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'process': ProcessType.REMOVE_KEYWORD, 'value': EffectType.WARD}
    ]),
    "Arriet, Luxminstrel": CardData("Arriet, Luxminstrel", "빛의 연주자 앙리에트", 3, CardType.FOLLOWER, 3, 3, effects=[
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.HEAL, 'value': 2},
        {'type': EffectType.ON_SUPER_EVOLVE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.HEAL, 'value': 4}
    ]),
    "Caravan Mammoth": CardData("Caravan Mammoth", "캐러밴 맘모스", 7, CardType.FOLLOWER, 10, 10, effects=[]),
    "Adventurers' Guild": CardData("Adventurers' Guild", "모험가 길드", 2, CardType.AMULET, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.DRAW, 'value': 1, 'codition': lambda x: x.card_type == CardType.FOLLOWER},
        {'type': EffectType.ACTIVATE, 'target': TargetType.ALLY_FOLLOWER_CHOICE, 'process': ProcessType.ADD_KEYWORD, 'value': {'type': EffectType.RUSH}}
    ]),
    "Ruby, Greedy Cherub": CardData("Ruby, Greedy Cherub", "욕심쟁이 지천사 루비", 2, CardType.FOLLOWER, 2, 2, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_HAND_CHOICE, 'process': ProcessType.RETURN_TO_DECK},
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.DRAW, 'value': 1}
    ]),
    "Vigilant Detective": CardData("Vigilant Detective", "관찰하는 탐정", 3, CardType.FOLLOWER, 3, 3, effects=[
        # value에 카드 이름을 문자열로 전달하여, 어떤 카드를 만들지 명시
        {'type': EffectType.LAST_WORDS, 'target': TargetType.OWN_LEADER, 'process': ProcessType.ADD_CARD_TO_HAND, 'value': "Detective's Lens"}
    ]),
    "Goblin Foray": CardData("Goblin Foray", "고블린의 습격", 5, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.OWN_LEADER, 'process': ProcessType.SUMMON, 'value': "Goblin"},
        {'type': EffectType.SPELL, 'target': TargetType.OWN_LEADER, 'process': ProcessType.SUMMON, 'value': "Goblin"},
        {'type': EffectType.SPELL, 'target': TargetType.OWN_LEADER, 'process': ProcessType.SUMMON, 'value': "Goblin"},
        {'type': EffectType.SPELL, 'target': TargetType.OWN_LEADER, 'process': ProcessType.SUMMON, 'value': "Goblin"},
        {'type': EffectType.SPELL, 'target': TargetType.OWN_LEADER, 'process': ProcessType.SUMMON, 'value': "Goblin"}
    ]),
    "Goblin": CardData("Goblin", "고블린", 1, CardType.FOLLOWER, 1, 2, effects=[]),
    "Apollo, Heaven's Envoy": CardData("Apollo, Heaven's Envoy", "세찬 광명 아폴론", 3, CardType.FOLLOWER, 1, 2, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'process': ProcessType.DEAL_DAMAGE, 'value': 1},
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'process': ProcessType.TRIGGER_EFFECT, 'value': EffectType.FANFARE}
    ]),
    "Seraphic Tidings": CardData("Seraphic Tidings", "치천사의 복음", 3, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.OWN_LEADER, 'process': ProcessType.DRAW, 'value': 2}
    ]),
    "Phildau, Lionheart Ward": CardData("Phildau, Lionheart Ward", "낙랑의 천궁 필도어", 2, CardType.FOLLOWER, 2, 2, effects=[
        {'type': EffectType.ON_EVOLVE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE, 'process': ProcessType.DESTROY}
    ]),
    "Divine Thunder": CardData("Divine Thunder", "신의 뇌정", 4, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.OPPONENT_FOLLOWER_MAX_ATTACK_RANDOM, 'process': ProcessType.DESTROY},
        {'type': EffectType.SPELL, 'target': TargetType.ALL_OPPONENT_FOLLOWERS, 'process': ProcessType.DEAL_DAMAGE, 'value': 1}
    ]),
    "Olivia, Heroic Dark Angel": CardData("Olivia, Heroic Dark Angel", "기백의 타천사 올리비에", 7, CardType.FOLLOWER, 4, 4, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.DRAW, 'value': 2},
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.HEAL, 'value': 2},
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.RECOVER_PP, 'value': 2},
        {'type': EffectType.ON_SUPER_EVOLVE, 'target': TargetType.ALLY_FOLLOWER_CHOICE_UNEVOLVED, 'process': ProcessType.EVOLVE_SUPER}
    ]),
    "Ruler of Cocytus": CardData("Ruler of Cocytus", "종막의 죄 사탄", 10, CardType.FOLLOWER, 10, 10, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OWN_LEADER, 'process': ProcessType.REPLACE_DECK, 'value': ["Silent Rider"*3, "Servant of Cocytus"*3, "Demon of Purgatory"*3, "Astaroth's Reckoning"]}
    ]),
    "Silent Rider": CardData("Silent Rider", "침묵의 마왕", 6, CardType.FOLLOWER, 10, 10, effects=[
        {'type': EffectType.STORM}
    ]),
    "Servant of Cocytus": CardData("Servant of Cocytus", "사탄의 하수인", 1, CardType.FOLLOWER, 13, 13, effects=[]),
    "Demon of Purgatory": CardData("Demon of Purgatory", "변옥의 악귀", 5, CardType.FOLLOWER, 9, 6, effects=[
        {'type': EffectType.FANFARE, 'target': TargetType.OPPONENT_FOLLOWER_CHOICE2, 'process': ProcessType.DEAL_DAMAGE, 'value': 6},
        {'type': EffectType.FANFARE, 'target': TargetType.OPPONENT_LEADER, 'process': ProcessType.DEAL_DAMAGE, 'value': 6},
    ]),
    "Astaroth's Reckoning": CardData("Astaroth's Reckoning", "아스타로트의 선고", 10, CardType.SPELL, effects=[
        {'type': EffectType.SPELL, 'target': TargetType.OPPONENT_LEADER, 'process': ProcessType.SET_MAX_HEALTH, 'value': 1}
    ])
}
