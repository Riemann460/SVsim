import unittest
from unittest.mock import MagicMock, patch

from src.common.enums import Zone, CardType, ClassType, ProcessType, EffectType, TargetType
from src.engine.main_game_logic import Game
from src.common.card_data import CardData
from src.common.effect import Effect
from src.models.crest import Crest

class TestUnimplementedProcessors(unittest.TestCase):
    def setUp(self):
        from src.common import card_data
        try:
            card_data.load_card_databases()
        except FileNotFoundError:
            card_data.load_card_databases('../card_database/3_parsed_database/card_database_parsed.json')

        self.gui_patcher = patch('src.engine.main_game_logic.GameGUI')
        self.mock_gui_class = self.gui_patcher.start()
        self.mock_gui = MagicMock()
        self.mock_gui_class.return_value = self.mock_gui

        self.game = Game("player1", "player2")
        self.gsm = self.game.game_state_manager
        self.p1 = self.gsm.players["player1"]
        self.p1.hand._cards = []
        self.p1.deck._cards = []

    def tearDown(self):
        self.gui_patcher.stop()

    def test_reduce_cost_by_amount(self):
        """REDUCE_COST로 카드의 코스트가 특정 값만큼 감소하는지 검사합니다."""
        card_data_sample = CardData("tc1", "Test Card 1", 5, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.REDUCE_COST,
            target=TargetType.SELF,
            value=2
        )

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(card.current_cost, 3)

    def test_reduce_cost_below_zero(self):
        """REDUCE_COST로 코스트가 0 미만으로 내려가지 않는지 검사합니다."""
        card_data_sample = CardData("tc2", "Test Card 2", 3, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.REDUCE_COST,
            target=TargetType.SELF,
            value=5
        )

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(card.current_cost, 0)

    def test_reduce_cost_halve(self):
        """REDUCE_COST의 value가 'halve'일 때 코스트가 절반(올림)으로 감소하는지 검사합니다."""
        card_data_sample = CardData("tc3", "Test Card 3", 5, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.REDUCE_COST,
            target=TargetType.SELF,
            value="halve"
        )

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(card.current_cost, 3)  # 5의 절반은 2.5 이며 올림해서 3

    def test_increase_cost(self):
        """INCREASE_COST로 카드의 코스트가 특정 값만큼 증가하는지 검사합니다."""
        card_data_sample = CardData("tc4", "Test Card 4", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.INCREASE_COST,
            target=TargetType.SELF,
            value=3
        )

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(card.current_cost, 5)

    def test_set_cost(self):
        """SET_COST로 카드의 코스트가 지정된 값으로 고정되는지 검사합니다."""
        card_data_sample = CardData("tc5", "Test Card 5", 4, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.SET_COST,
            target=TargetType.SELF,
            value=1
        )

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(card.current_cost, 1)

    def test_set_attack(self):
        """SET_ATTACK으로 추종자의 공격력이 지정된 값으로 변경되는지 검사합니다."""
        card_data_sample = CardData("tc6", "Test Follower", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, 2, 3, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.FIELD, "player1")

        effect = Effect(
            type=EffectType.ON_EVOLVE,
            process=ProcessType.SET_ATTACK,
            target=TargetType.SELF,
            value=4
        )

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(card.current_attack, 4)

    def test_recover_ep(self):
        """RECOVER_EP로 플레이어의 EP가 증가하는지 검사합니다."""
        self.p1.current_ep = 0
        self.p1.max_ep = 2

        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.RECOVER_EP,
            target=TargetType.OWN_LEADER,
            value=1
        )

        # 임의의 카스터 아이디를 넘겨 resolve_effect 실행
        card_data_sample = CardData("dummy", "Dummy", 1, CardType.SPELL, ClassType.NEUTRAL, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(self.p1.current_ep, 1)

        # 최대 EP 초과 방지 검증
        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(self.p1.current_ep, 2)
        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        self.assertEqual(self.p1.current_ep, 2)

    def test_heal_linked(self):
        """HEAL_LINKED로 추종자 체력이 완전 회복되고, 그 양만큼 리더도 회복하는지 검사합니다."""
        card_data_sample = CardData("tc7", "Test Follower", 3, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 3, 5, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.FIELD, "player1")

        # 추종자 피해 상태 유도
        card.current_defense = 2
        # 리더 체력 15로 설정
        self.p1.current_defense = 15

        effect = Effect(
            type=EffectType.ON_MY_TURN_END,
            process=ProcessType.HEAL_LINKED,
            target=TargetType.SELF,
            value=None
        )

        self.game.effect_processor.resolve_effect(effect, card.card_id, self.gsm, None)
        
        # 추종자 체력 완전 회복 (5)
        self.assertEqual(card.current_defense, 5)
        # 리더 체력은 15 + (5 - 2) = 18로 회복
        self.assertEqual(self.p1.current_defense, 18)

    def test_advance_and_destroy_crest(self):
        """ADVANCE_CREST와 DESTROY_CREST로 문장의 카운트 조작 및 파괴가 정상 작동하는지 검사합니다."""
        # 1. 문장 획득 효과 실행
        gain_effect = Effect(
            type=EffectType.FANFARE,
            process=ProcessType.GAIN_CREST,
            target=TargetType.OWN_LEADER,
            value="Belial, Archangel of Cunning"
        )
        card_data_sample = CardData("dummy", "Dummy", 1, CardType.SPELL, ClassType.NEUTRAL, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        self.game.effect_processor.resolve_effect(gain_effect, card.card_id, self.gsm, None)

        self.assertEqual(len(self.p1.crests), 1)
        crest = self.p1.crests[0]
        self.assertEqual(crest.name, "Belial, Archangel of Cunning")
        self.assertEqual(crest.count, 0) # 기본 0으로 시작

        # 2. 문장 카운트 증가 효과 실행 (특정 문장 카운트 증가)
        advance_effect = Effect(
            type=EffectType.ON_EVOLVE,
            process=ProcessType.ADVANCE_CREST,
            target=TargetType.OWN_LEADER,
            value=["Belial, Archangel of Cunning", 2]
        )
        self.game.effect_processor.resolve_effect(advance_effect, card.card_id, self.gsm, None)
        self.assertEqual(crest.count, 2)

        # 3. 문장 카운트 지연 효과 실행 (전체 문장 딜레이, value=1, value2="-0")
        delay_effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.ADVANCE_CREST,
            target=TargetType.OWN_LEADER,
            value=1,
            value2="-0"
        )
        self.game.effect_processor.resolve_effect(delay_effect, card.card_id, self.gsm, None)
        self.assertEqual(crest.count, 1) # 2 - 1 = 1

        # 4. 문장 파괴 효과 실행
        destroy_effect = Effect(
            type=EffectType.FANFARE,
            process=ProcessType.DESTROY_CREST,
            target=TargetType.OWN_LEADER,
            value="Belial, Archangel of Cunning"
        )
        self.game.effect_processor.resolve_effect(destroy_effect, card.card_id, self.gsm, None)
        self.assertEqual(len(self.p1.crests), 0)
