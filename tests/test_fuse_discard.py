import unittest
from unittest.mock import MagicMock, patch

from src.common.enums import Zone, CardType, ClassType, TribeType, ProcessType, EventType, EffectType, TargetType
from src.engine.main_game_logic import Game
from src.models.card import Card
from src.common.card_data import CardData
from src.common.effect import Effect

class TestFuseDiscard(unittest.TestCase):
    def setUp(self):
        from src.common import card_data
        try:
            card_data.load_card_databases()
        except FileNotFoundError:
            # Fallback path if run from subdirectory
            card_data.load_card_databases('../card_database/3_parsed_database/card_database_parsed.json')

        # Game GUI 팝업이 뜨는 것을 막기 위해 GameGUI를 mock 처리합니다.
        self.gui_patcher = patch('src.engine.main_game_logic.GameGUI')
        self.mock_gui_class = self.gui_patcher.start()
        
        # GUI 인스턴스의 헬퍼 함수들도 모킹합니다.
        self.mock_gui = MagicMock()
        self.mock_gui_class.return_value = self.mock_gui
        
        # 게임 초기화
        self.game = Game("player1", "player2")
        self.gsm = self.game.game_state_manager
        
        # 테스트 전용 플레이어1 셋업
        self.p1 = self.gsm.players["player1"]
        # 패와 덱을 비웁니다.
        self.p1.hand._cards = []
        self.p1.deck._cards = []

    def tearDown(self):
        self.gui_patcher.stop()

    def test_discard_single_card(self):
        """패에서 카드 한 장을 버렸을 때 정상적으로 묘지로 가고 이벤트가 발생하는지 검사합니다."""
        # 1. 패에 임의의 카드 추가
        card_data_sample = CardData(
            card_id="test_card_1",
            name="Test Card",
            cost=1,
            card_type=CardType.FOLLOWER,
            class_type=ClassType.FORESTCRAFT,
            tribes=[],
            effects=[]
        )
        card = self.gsm.create_card_instance(card_data_sample, "player1")
        self.gsm.add_card(card, Zone.HAND, "player1")

        # 버리기 전 묘지 확인
        self.assertEqual(len(self.p1.hand.get_cards()), 1)
        self.assertEqual(self.p1.graveyard.size(), 0)

        # 이벤트 구독 확인을 위한 mock 리스너 등록
        event_received = []
        def on_discard(event):
            event_received.append(event)

        from src.common.listener import Listener
        discard_listener = Listener("test_discard", EventType.CARD_DISCARDED, on_discard)
        self.game.event_manager.subscribe(discard_listener)

        # 2. 카드 버리기 실행
        self.game.discard_card("player1", card.card_id)

        # 3. 검증
        self.assertEqual(len(self.p1.hand.get_cards()), 0)
        self.assertEqual(self.p1.graveyard.size(), 1)
        self.assertEqual(self.p1.graveyard.get_cards()[0].card_id, card.card_id)
        self.assertEqual(len(event_received), 1)
        self.assertEqual(event_received[0].card_id, card.card_id)
        self.assertEqual(event_received[0].player_id, "player1")

        # 리스너 해제
        self.game.event_manager.unsubscribe(EventType.CARD_DISCARDED, "test_discard")

    def test_discard_cards_manually(self):
        """플레이어가 수동으로 카드를 선택하여 버리는 동작을 검사합니다."""
        card_data_sample1 = CardData("c1", "Card 1", 1, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        card_data_sample2 = CardData("c2", "Card 2", 2, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        
        c1 = self.gsm.create_card_instance(card_data_sample1, "player1")
        c2 = self.gsm.create_card_instance(card_data_sample2, "player1")
        self.gsm.add_card(c1, Zone.HAND, "player1")
        self.gsm.add_card(c2, Zone.HAND, "player1")

        # GUI에서 c1을 선택한 것으로 모킹
        self.mock_gui.get_discard_choices.return_value = [c1.card_id]

        self.game.discard_cards_manually("player1", 1)

        # 검증: c1은 묘지로 가고 c2는 여전히 패에 남아있어야 함
        self.assertEqual(len(self.p1.hand.get_cards()), 1)
        self.assertEqual(self.p1.hand.get_cards()[0].card_id, c2.card_id)
        self.assertEqual(self.p1.graveyard.size(), 1)
        self.assertEqual(self.p1.graveyard.get_cards()[0].card_id, c1.card_id)
        self.mock_gui.get_discard_choices.assert_called_once_with("player1", [c1, c2], 1)

    def test_process_discard_random_player_target(self):
        """_process_discard 핸들러가 Player 대상으로 호출되었을 때 무작위 카드를 버리는지 검사합니다."""
        card_data_sample1 = CardData("c1", "Card 1", 1, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        card_data_sample2 = CardData("c2", "Card 2", 2, CardType.SPELL, ClassType.FORESTCRAFT, [], [])
        
        c1 = self.gsm.create_card_instance(card_data_sample1, "player1")
        c2 = self.gsm.create_card_instance(card_data_sample2, "player1")
        self.gsm.add_card(c1, Zone.HAND, "player1")
        self.gsm.add_card(c2, Zone.HAND, "player1")

        # Effect 객체 (ProcessType.DISCARD, value=1)
        discard_effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.DISCARD,
            target=TargetType.OWN_LEADER,
            value=1
        )

        # EffectProcessor의 버리기 동작 수행
        self.game.effect_processor.resolve_effect(discard_effect, c1.card_id, self.gsm, None)

        # 검증: 패에서 한 장이 줄어들고 묘지에 한 장이 생겨야 함
        self.assertEqual(len(self.p1.hand.get_cards()), 1)
        self.assertEqual(self.p1.graveyard.size(), 1)

    def test_fuse_cards_success_and_failure(self):
        """융합 조건에 맞는 카드는 성공하고, 맞지 않는 카드는 실패하는지 검사합니다."""
        # 베이스 카드 (Forestcraft 융합 가능)
        base_data = CardData("base", "Forest Queen", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, [], [])
        base_data.fuse_condition = "Forestcraft cards"
        
        # 재료 카드 1 (Forestcraft) -> 성공해야 함
        mat_success_data = CardData("mat_ok", "Elven Archer", 1, CardType.FOLLOWER, ClassType.FORESTCRAFT, [], [])
        # 재료 카드 2 (Neutral) -> 실패해야 함
        mat_fail_data = CardData("mat_fail", "Goblin", 1, CardType.FOLLOWER, ClassType.NEUTRAL, [], [])

        base_card = self.gsm.create_card_instance(base_data, "player1")
        mat_ok = self.gsm.create_card_instance(mat_success_data, "player1")
        mat_fail = self.gsm.create_card_instance(mat_fail_data, "player1")

        self.gsm.add_card(base_card, Zone.HAND, "player1")
        self.gsm.add_card(mat_ok, Zone.HAND, "player1")
        self.gsm.add_card(mat_fail, Zone.HAND, "player1")

        # 실패 테스트: 맞지 않는 조건의 카드 융합
        res = self.game.fuse_cards("player1", base_card.card_id, [mat_fail.card_id])
        self.assertFalse(res)
        self.assertEqual(len(self.p1.hand.get_cards()), 3) # 모두 패에 남아있어야 함

        # 성공 테스트: 맞는 조건의 카드 융합
        # 이벤트 구독 확인
        fuse_events = []
        def on_fuse(event):
            fuse_events.append(event)
        from src.common.listener import Listener
        fuse_listener = Listener("test_fuse", EventType.FUSE_DECLARED, on_fuse)
        self.game.event_manager.subscribe(fuse_listener)

        res = self.game.fuse_cards("player1", base_card.card_id, [mat_ok.card_id])
        self.assertTrue(res)
        
        # 검증: 재료 카드는 패에서 사라져야 함
        self.assertEqual(len(self.p1.hand.get_cards()), 2) # base, mat_fail 만 남음
        # base_card.fused_cards 에 mat_ok ID가 들어가 있어야 함
        self.assertTrue(hasattr(base_card, "fused_cards"))
        self.assertIn(mat_ok.card_id, base_card.fused_cards)
        # 융합된 카드의 Zone은 None이 되어야 함
        self.assertIsNone(mat_ok.current_zone)

        # 이벤트 발생 검증
        self.assertEqual(len(fuse_events), 1)
        self.assertEqual(fuse_events[0].card_id, base_card.card_id)
        self.assertEqual(fuse_events[0].material_card_ids, [mat_ok.card_id])

        self.game.event_manager.unsubscribe(EventType.FUSE_DECLARED, "test_fuse")

    def test_process_fuse_trigger(self):
        """_process_fuse 핸들러를 통한 융합이 정상적으로 작동하는지 검사합니다."""
        base_data = CardData("base", "Forest Queen", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, [], [])
        base_data.fuse_condition = "Forestcraft cards"
        
        mat_data = CardData("mat", "Elven Archer", 1, CardType.FOLLOWER, ClassType.FORESTCRAFT, [], [])

        base_card = self.gsm.create_card_instance(base_data, "player1")
        mat_card = self.gsm.create_card_instance(mat_data, "player1")

        self.gsm.add_card(base_card, Zone.HAND, "player1")
        self.gsm.add_card(mat_card, Zone.HAND, "player1")

        # GUI에서 융합할 재료로 mat_card를 선택한 것으로 모킹
        self.mock_gui.get_fuse_choices.return_value = [mat_card.card_id]

        fuse_effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.FUSE,
            target=TargetType.SELF,
            value=None
        )

        # 융합 해결 실행
        self.game.effect_processor.resolve_effect(fuse_effect, base_card.card_id, self.gsm, base_card.card_id)

        # 검증: 융합이 수행되어 재료가 사라지고 base_card에 융합되어 있어야 함
        self.assertEqual(len(self.p1.hand.get_cards()), 1)
        self.assertIn(mat_card.card_id, base_card.fused_cards)
        self.mock_gui.get_fuse_choices.assert_called_once()

if __name__ == '__main__':
    unittest.main()
