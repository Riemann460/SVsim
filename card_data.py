from typing import List, Dict, Any
from enums import CardType# 상대 경로 임포트

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

# 예시 카드 데이터베이스 (실제로는 JSON 등 외부 파일에서 로드)
CARD_DATABASE = {
    "Indomitable Fighter": CardData("Indomitable Fighter", "불굴의 파이터", 2, CardType.FOLLOWER, 2, 2, "증강 4: 이 추종자는 +3/+3"),
    "Leah, Bellringer Angel": CardData("Leah, Bellringer Angel", "종소리의 천사 리아", 2, CardType.FOLLOWER, 0, 2, "수호, 유언: 내 덱에서 1장을 뽑는다, 진화시: 내 덱에서 1장을 뽑는다"),
    "Quake Goliath": CardData("Quake Goliath", "격진의 골리앗", 4, CardType.FOLLOWER, 4, 5, "수호"),
    "Detective's Lens": CardData("Detective's Lens", "탐정의 돋보기", 2, CardType.AMULET, "활성화: 이 마법진을 파괴. 상대방 전장에서 추종자 1장을 선택한다. 그 추종자는 수호를 잃는다"),
    "Arriet, Luxminstrel": CardData("Arriet, Luxminstrel", "빛의 연주자 앙리에트", 3, CardType.FOLLOWER, 3, 3, "진화시: 내 리더를 2회복, 초진화시: 2 회복 대신 4회복"),
    "Caravan Mammoth": CardData("Caravan Mammoth", "캐러밴 맘모스", 7, CardType.FOLLOWER, 10, 10),
    "Adventurers' Guild": CardData("Adventurers' Guild", "모험가 길드", 2, CardType.AMULET, "출격: 내 덱에서 추종자 1장을 뽑는다, 활성화: 이 마법진을 파괴. 내 전장에서 추종자 1장을 선택한다. 그 추종자는 돌진을 갖는다"),
    "Ruby, Greedy Cherub": CardData("Ruby, Greedy Cherub", "욕심쟁이 지천사 루비", 2, CardType.FOLLOWER, 2, 2, "출격: 내 페에서 1장을 선택한다. 그 카드를 덱으로 되돌린다. 내 덱에서 1장을 뽑는다"),
    "Vigilant Detective": CardData("Vigilant Detective", "관찰하는 탐정", 3, CardType.FOLLOWER, 3, 3, "유언: 탐정의 돋보기 1장을 내 패에 넣는다"),
    "Goblin Foray": CardData("Goblin Foray", "고블린의 습격", 5, CardType.SPELL, "고블린 5장을 내 전장에 소환"),
    "Goblin": CardData("Goblin", "고블린", 1, CardType.FOLLOWER, 1, 2),
    "Apollo, Heaven's Envoy": CardData("Apollo, Heaven's Envoy", "세찬 광명 아폴론", 3, CardType.FOLLOWER, 1, 2, "출격: 상대방 전장의 추종자 모두에게 1 피해, 진화시: 출격과 같은 능력이 발동"),
    "Seraphic Tidings": CardData("Seraphic Tidings", "치천사의 복음", 3, CardType.SPELL, "내 덱에서 2장을 뽑는다"),
    "Phildau, Lionheart Ward": CardData("Phildau, Lionheart Ward", "낙랑의 천궁 필도어", 2, CardType.FOLLOWER, 2, 2, "진화시: 상대방 전장에서 추종자 1장을 선택한다. 그 추종자를 파괴"),
    "Divine Thunder": CardData("Divine Thunder", "신의 뇌정", 4, CardType.SPELL, "상대방 전장의 공격력이 가장 높은 추종자 중 무작위로 1장을 파괴. 상대방 전장의 추종자 모두에게 1 피해"),
    "Olivia, Heroic Dark Angel": CardData("Olivia, Heroic Dark Angel", "기백의 타천사 올리비에", 7, CardType.FOLLOWER, 4, 4, "출격: 내 덱에서 2장을 뽑는다. 내 리더를 2회복. 내 PP를 2회복, 초진화시: 내 전장에서 진화전인 다른 추종자 1장을 선택한다. 그 추종자는 초진화한다"),
    "Ruler of Cocytus": CardData("Ruler of Cocytus", "종막의 죄 사탄", 10, CardType.FOLLOWER, 10, 10, "출격: 내 덱을 아포칼립스 덱으로 바꾼다."),
    "Silent Rider": CardData("Silent Rider", "침묵의 마왕", 6, CardType.FOLLOWER, 10, 10, "질주"),
    "Servant of Cocytus": CardData("Servant of Cocytus", "사탄의 하수인", 1, CardType.FOLLOWER, 13, 13),
    "Demon of Purgatory": CardData("Demon of Purgatory", "변옥의 악귀", 5, CardType.FOLLOWER, 9, 6, "출격: 상대방 전장에서 추종자 2장을 선택한다. 그 추종자와 상대방 리더에게 6 피해"),
    "Astaroth's Reckoning": CardData("Astaroth's Reckoning", "아스타로트의 선고", 10, CardType.SPELL, "상대방 리더의 체력 최대치를 1로 만든다.")
}