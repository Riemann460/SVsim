import unittest
from unittest.mock import MagicMock, patch

from src.common.enums import Zone, CardType, ClassType, TribeType, ProcessType, EventType, EffectType, TargetType
from src.engine.main_game_logic import Game
from src.common.card_data import CardData
from src.common.effect import Effect
from src.models.card import Card

class TestUnimplementedEnums(unittest.TestCase):
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

    def test_combo_and_rally(self):
        """콤보 카운트의 증가/초기화와 연계 카운트의 증가를 검증합니다."""
        # 1. Player 객체에 combo_count와 rally_count 속성이 있는지 확인
        self.assertTrue(hasattr(self.p1, "combo_count"))
        self.assertTrue(hasattr(self.p1, "rally_count"))

        # 2. 카드 플레이 시 콤보 카운트 증가 확인
        card_data_sample = CardData("tc_combo", "Test Card", 1, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        card1 = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card1, Zone.HAND, "player1")

        self.game.play_card("player1", card1.card_id)
        self.assertEqual(self.p1.combo_count, 1)

        # 3. 턴 종료 시 콤보 카운터 리셋 확인
        self.game.end_turn("player1")
        self.assertEqual(self.p1.combo_count, 0)

        # 4. 추종자 필드 진입 시 연계 카운트 증가 확인
        follower_data = CardData("tc_rally", "Test Follower", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 2, 2, [], [])
        follower = self.gsm.create_card_instance(follower_data, "player1")
        
        initial_rally = self.p1.rally_count
        self.gsm.add_card(follower, Zone.FIELD, "player1")
        self.assertEqual(self.p1.rally_count, initial_rally + 1)

    def test_necromancy_and_reanimate(self):
        """사령술 묘지 카운트 관리와 사령 재생(Reanimate) 메커니즘을 검증합니다."""
        # 1. Graveyard에 shadows_count 속성이 있는지 확인
        self.assertTrue(hasattr(self.p1.graveyard, "shadows_count"))

        # 2. 카드가 묘지로 갈 때 shadows_count가 증가하는지 확인
        card_data_sample = CardData("tc_shadow", "Test Card", 1, CardType.SPELL, ClassType.NEUTRAL, [], [])
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.GRAVEYARD, "player1")
        self.assertEqual(self.p1.graveyard.shadows_count, 1)

        # 3. ProcessType.GAIN_SHADOW 핸들러 검증
        gain_effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.GAIN_SHADOW,
            target=TargetType.OWN_LEADER,
            value=3
        )
        self.game.effect_processor.resolve_effect(gain_effect, card.card_id, self.gsm, None)
        self.assertEqual(self.p1.graveyard.shadows_count, 4)

        # 4. REANIMATE 프로세스 검증
        # 묘지에 비용 1, 3, 4 짜리 추종자를 넣어둔다.
        f1 = self.gsm.create_card_instance(CardData("f1", "F1", 1, CardType.FOLLOWER, ClassType.NEUTRAL, 1, 1, [], []), "player1")
        f3 = self.gsm.create_card_instance(CardData("f3", "F3", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, [], []), "player1")
        f4 = self.gsm.create_card_instance(CardData("f4", "F4", 4, CardType.FOLLOWER, ClassType.NEUTRAL, 4, 4, [], []), "player1")
        self.gsm.add_card(f1, Zone.GRAVEYARD, "player1")
        self.gsm.add_card(f3, Zone.GRAVEYARD, "player1")
        self.gsm.add_card(f4, Zone.GRAVEYARD, "player1")

        # REANIMATE 3 효과 실행: 묘지에 있는 비용 3 이하 최고비용 추종자(f3)가 전장에 소환되어야 함.
        reanimate_effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.REANIMATE,
            target=TargetType.OWN_LEADER,
            value=3
        )
        self.game.effect_processor.resolve_effect(reanimate_effect, card.card_id, self.gsm, None)

        # f3가 필드에 존재하는지 확인
        self.assertEqual(f3.current_zone, Zone.FIELD)
        self.assertEqual(len(self.p1.field.get_cards()), 1)

    def test_earth_rite_and_overflow(self):
        """흙의 비술 마법진 파괴와 각성(Overflow) 메커니즘을 검증합니다."""
        # 1. 각성(Overflow) 프로퍼티 및 상태 검증
        self.p1.max_pp = 6
        self.assertFalse(self.p1.is_overflow)
        self.p1.max_pp = 7
        self.assertTrue(self.p1.is_overflow)

        # 2. 흙의 비술(EARTH_RITE) 발동 시 먼저 소환된 EARTH_SIGIL 마법진 1장 파괴 검증
        sigil1 = self.gsm.create_card_instance(CardData("s1", "Sigil 1", 1, CardType.AMULET, ClassType.RUNECRAFT, [], [], tribes=[TribeType.EARTH_SIGIL]), "player1")
        sigil2 = self.gsm.create_card_instance(CardData("s2", "Sigil 2", 1, CardType.AMULET, ClassType.RUNECRAFT, [], [], tribes=[TribeType.EARTH_SIGIL]), "player1")
        self.gsm.add_card(sigil1, Zone.FIELD, "player1")
        self.gsm.add_card(sigil2, Zone.FIELD, "player1")

        # 흙의 비술 효과 발동 (GAIN_EARTH_SIGIL 이나 직접적인 비술 발동)
        # 흙의 비술은 ProcessType.EARTH_RITE(비술 발동) 혹은 효과 내 처리로 동작할 것이다.
        # enums.py에 Earth Rite는 EffectType.EARTH_RITE 로 정의되어 있고, 프로세스엔 GAIN_EARTH_SIGIL이 있다.
        # EffectProcessor에 EARTH_RITE 효과 발동 로직(Sigil 파괴 연계)을 구현해야 한다.
        # 가짜 카드로 흙의 비술 효과를 resolve 해보자.
        # EffectType = EARTH_RITE 인 효과가 발동하면 필드의 EARTH_SIGIL 1개를 파괴(소모)한다.
        # 이를 트리거하기 위한 흙의 비술 효과 resolving 테스트
        rite_effect = Effect(
            type=EffectType.EARTH_RITE,
            process=ProcessType.DRAW, # 후속 프로세스
            target=TargetType.OWN_LEADER,
            value=1
        )
        # sigil1이 sigil2보다 먼저 들어왔으므로 sigil1이 파괴되어 묘지로 가야 한다.
        # (graveyard 크기가 기존 shadows_count 증가에 의해 어떻게 되었는지 확인)
        # resolve_effect_rite를 구현하거나, resolve_effect 내에 Earth Rite 전처리(Sigil 파괴)를 결합한다.
        self.game.effect_processor.resolve_effect(rite_effect, sigil1.card_id, self.gsm, None)

        self.assertEqual(sigil1.current_zone, Zone.GRAVEYARD)
        self.assertEqual(sigil2.current_zone, Zone.FIELD)

    def test_skybound_art_and_invoke(self):
        """오의 게이지 차감과 직접소환(Invoke) 검증 테스트입니다."""
        # 1. 오의(SKYBOUND_ART) 카드 패 추가 및 진화 시 게이지 감소 검증
        sa_effect = Effect(
            type=EffectType.SKYBOUND_ART,
            process=ProcessType.DEAL_DAMAGE,
            target=TargetType.OPPONENT_LEADER,
            value=5
        )
        sa_effect.skybound_art_gauge = 10  # 오의 기본 게이지 설정
        card_data_sa = CardData("sa_card", "Skybound Art Card", 5, CardType.SPELL, ClassType.NEUTRAL, 0, 0, [], [sa_effect])
        sa_card = self.gsm.create_card_instance(card_data_sa, "player1")
        self.gsm.add_card(sa_card, Zone.HAND, "player1")

        # 아군 추종자 진화
        follower = self.gsm.create_card_instance(CardData("f_evo", "Follower", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, [], []), "player1")
        self.gsm.add_card(follower, Zone.FIELD, "player1")
        self.p1.current_ep = 1

        self.game.evolve_follower(follower.card_id, "player1")
        # 오의 게이지가 10에서 9로 줄어야 함
        self.assertEqual(sa_card.effects[0].skybound_art_gauge, 9)

    def test_invoke_on_turn_start(self):
        """덱에 있는 직접소환(INVOKE) 카드가 조건을 만족하여 턴 시작 시 자동 소환되는지 검증합니다."""
        # 직접소환 카드 설계
        invoke_effect = Effect(
            type=EffectType.INVOKE,
            process=ProcessType.SUMMON,
            target=TargetType.OWN_LEADER,
            value=None
        )
        # 조건: 콤보가 3 이상일 때 직접소환되거나, 턴 종료시 등
        # invoke 카드가 덱에 존재함
        card_data_invoke = CardData("invoke_card", "Invoke Card", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, [], [invoke_effect])
        invoke_card = self.gsm.create_card_instance(card_data_invoke, "player1")
        self.gsm.add_card(self.gsm.create_card_instance(CardData("dummy_draw", "Dummy Draw", 1, CardType.SPELL, ClassType.NEUTRAL, 0, 0, [], []), "player1"), Zone.DECK, "player1")
        self.gsm.add_card(invoke_card, Zone.DECK, "player1")

        # 직접소환 조건을 임의로 체크하기 위해 game._check_invoke() 와 같은 메서드를 호출하거나,
        # 턴 시작/종료 연동 검사
        # 예를 들어 직접소환 조건: 묘지 shadows_count가 5 이상일 때 직접소환되는 카드라고 가정.
        # invoke_effect 에 조건식 등록
        invoke_effect.condition = lambda game: game.game_state_manager.players["player1"].graveyard.shadows_count >= 5

        self.p1.graveyard.shadows_count = 5

        # 턴 시작 호출
        self.game._start_turn("player1")

        # 덱에 있던 invoke_card가 필드(Zone.FIELD)에 나와 있는지 확인
        self.assertEqual(invoke_card.current_zone, Zone.FIELD)

    def test_transform_and_conditional_effect(self):
        """변신(Transform)과 조건부 효과(Conditional Effect)를 검증합니다."""
        # 1. 변신 검증
        target_follower = self.gsm.create_card_instance(CardData("tf_target", "Target Follower", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, [], []), "player1")
        self.gsm.add_card(target_follower, Zone.FIELD, "player1")

        # 변신시킬 새 카드 데이터
        new_card_data = CardData("tf_new", "Golem", 2, CardType.FOLLOWER, ClassType.RUNECRAFT, 3, 3, [TribeType.GOLEM], [])
        
        transform_effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.TRANSFORM,
            target=TargetType.SELF,
            value=new_card_data
        )

        self.game.effect_processor.resolve_effect(transform_effect, target_follower.card_id, self.gsm, None)

        # Golem이 필드에 존재하고, 기존 target_follower는 필드에서 사라졌으며 묘지로 가지 않았어야 함 (변신이므로 퇴장 이벤트 우회)
        field_cards = self.p1.field.get_cards()
        self.assertEqual(len(field_cards), 1)
        self.assertEqual(field_cards[0].get_display_name(), "Golem")
        self.assertNotIn(target_follower.card_id, [c.card_id for c in field_cards])
        self.assertEqual(self.p1.graveyard.size(), 0) # 묘지로 가지 않음

        # 2. 조건부 효과 검증
        # 조건: 연계가 5 이상일 때 드로우 2장, 미만일 때 드로우 1장
        cond_effect = Effect(
            type=EffectType.FANFARE,
            process=ProcessType.CONDITIONAL_EFFECT,
            target=TargetType.OWN_LEADER,
            value={
                "condition": lambda game_state: game_state.players["player1"].rally_count >= 5,
                "if_true": Effect(type=EffectType.FANFARE, process=ProcessType.DRAW, target=TargetType.OWN_LEADER, value=2),
                "if_false": Effect(type=EffectType.FANFARE, process=ProcessType.DRAW, target=TargetType.OWN_LEADER, value=1)
            }
        )
        card_dummy = self.gsm.create_card_instance(CardData("dummy", "Dummy", 1, CardType.SPELL, ClassType.NEUTRAL, [], []), "player1")
        self.gsm.add_card(card_dummy, Zone.HAND, "player1")

        # 덱에 드로우할 카드들 3장 넣어둔다
        for i in range(3):
            self.gsm.add_card(self.gsm.create_card_instance(CardData(f"draw{i}", "Draw Card", 1, CardType.SPELL, ClassType.NEUTRAL, [], []), "player1"), Zone.DECK, "player1")

        # rally_count가 3일 때 (5 미만)
        self.p1.rally_count = 3
        self.game.effect_processor.resolve_effect(cond_effect, card_dummy.card_id, self.gsm, None)
        self.assertEqual(len(self.p1.hand.get_cards()), 2) # dummy + 1장 드로우 = 2

        # rally_count가 6일 때 (5 이상)
        self.p1.rally_count = 6
        self.game.effect_processor.resolve_effect(cond_effect, card_dummy.card_id, self.gsm, None)
        self.assertEqual(len(self.p1.hand.get_cards()), 4) # 기존 2장 + 2장 드로우 = 4
