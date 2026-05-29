# 역할 정의. 시나리오 빌더의 기본 리소스 설정 동작을 검증하는 테스트 클래스입니다.

import unittest
from tests.scenario_helper import GameScenarioBuilder
from src.common.enums import Zone

class TestScenarioBuilderCore(unittest.TestCase):
    """시나리오 빌더의 코어 리소스 설정을 테스트하는 클래스입니다."""

    def test_resource_setup(self):
        """체력, PP, EP, SEP, 엑스트라 PP, 콤보, 연계, 묘지 카운트 설정을 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_health("player1", 12)
        builder.set_pp("player1", 4, 7)
        builder.set_ep("player1", 1, 2)
        builder.set_sep("player1", 2, 2)
        builder.set_extra_pp("player1", 1, 1)
        builder.set_combo("player1", 3)
        builder.set_rally("player1", 6)
        builder.set_graveyard("player1", 8)
        builder.set_active_player("player2")

        game = builder.build()
        self.assertIsNotNone(game)

        p1 = game.game_state_manager.players["player1"]
        p2 = game.game_state_manager.players["player2"]

        # 플레이어 리더 체력을 검증합니다.
        self.assertEqual(p1.current_defense, 12)
        self.assertEqual(p1.max_defense, 12)

        # PP 설정을 검증합니다.
        self.assertEqual(p1.current_pp, 4)
        self.assertEqual(p1.max_pp, 7)

        # EP/SEP 설정을 검증합니다.
        self.assertEqual(p1.current_ep, 1)
        self.assertEqual(p1.max_ep, 2)
        self.assertEqual(p1.current_sep, 2)
        self.assertEqual(p1.max_sep, 2)

        # 엑스트라 PP 설정을 검증합니다.
        self.assertEqual(p1.extra_pp, 1)
        self.assertEqual(p1.max_extra_pp, 1)

        # 콤보 및 연계 설정을 검증합니다.
        self.assertEqual(p1.combo_count, 3)
        self.assertEqual(p1.rally_count, 6)

        # 묘지 카운트 설정을 검증합니다.
        self.assertEqual(p1.graveyard.shadows_count, 8)

        # 활성 플레이어(선턴)를 검증합니다.
        self.assertEqual(game.game_state_manager.current_turn_player_id, "player2")

    def test_card_placement(self):
        """손패, 필드, 덱, 묘지에 ID와 이름으로 카드를 배치하는 것을 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        
        # 1. 이름으로 카드를 배치합니다.
        card1 = builder.add_to_hand("player1", "Indomitable Fighter")
        card2 = builder.add_to_field("player1", "Leah, Bellringer Angel")
        card3 = builder.add_to_deck("player2", "Leah, Bellringer Angel")
        card4 = builder.add_to_graveyard("player2", "Indomitable Fighter")
        
        # 2. ID로 카드를 배치합니다.
        card_id_sample = card1.card_data.card_id
        card5 = builder.add_to_hand("player2", card_id_sample)

        game = builder.build()
        p1 = game.game_state_manager.players["player1"]
        p2 = game.game_state_manager.players["player2"]

        # 손패를 검증합니다.
        self.assertEqual(len(p1.hand.get_cards()), 1)
        self.assertEqual(p1.hand.get_cards()[0].card_data.name, "Indomitable Fighter")

        # 필드를 검증합니다.
        self.assertEqual(len(p1.field.get_cards()), 1)
        self.assertEqual(p1.field.get_cards()[0].card_data.name, "Leah, Bellringer Angel")

        # 덱을 검증합니다.
        self.assertEqual(len(p2.deck.get_cards()), 1)
        self.assertEqual(p2.deck.get_cards()[0].card_data.name, "Leah, Bellringer Angel")

        # 묘지를 검증합니다.
        self.assertEqual(len(p2.graveyard.get_cards()), 1)
        self.assertEqual(p2.graveyard.get_cards()[0].card_data.name, "Indomitable Fighter")

        # ID 기반 손패 추가를 검증합니다.
        self.assertEqual(len(p2.hand.get_cards()), 1)
        self.assertEqual(p2.hand.get_cards()[0].card_data.name, "Indomitable Fighter")

    def test_scenario_simulation(self):
        """출격 효과와 공격 및 진화를 포함한 전투 시나리오를 시뮬레이션하고 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_pp("player1", 5, 5)
        builder.set_ep("player1", 1, 2)
        
        # player1의 패와 player2의 필드에 카드를 추가합니다.
        p1_card = builder.add_to_hand("player1", "Indomitable Fighter")
        p2_card = builder.add_to_field("player2", "Leah, Bellringer Angel")
        
        game = builder.build()
        
        # player1이 Indomitable Fighter를 플레이합니다 (비용 2).
        played = game.play_card("player1", p1_card.card_id)
        self.assertTrue(played)
        self.assertEqual(p1_card.current_zone, Zone.FIELD)
        
        # player1이 Indomitable Fighter를 진화시킵니다.
        game.evolve_follower(p1_card.card_id, "player1")
        self.assertTrue(p1_card.is_evolved)
        
        # player1이 player2의 Leah, Bellringer Angel을 공격합니다.
        # Leah, Bellringer Angel은 수호(Ward)를 가집니다.
        game.attack_follower(p1_card.card_id, p2_card.card_id)
        
        # Leah, Bellringer Angel이 파괴되어 묘지로 갔는지 검증합니다.
        self.assertEqual(p2_card.current_zone, Zone.GRAVEYARD)

    def test_direct_effect_resolution(self):
        """특정 카드의 개별 효과를 직접 지정하여 상황별로 디버깅하는 시나리오를 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        
        # 1. 필드에 비술 마법진(Magic Sediment)을 배치합니다.
        sigil1 = builder.add_to_field("player1", "Magic Sediment")
        sigil2 = builder.add_to_field("player1", "Magic Sediment")
        
        # 2. 플레이어1의 최대 PP를 7로 설정하여 각성 상태를 활성화합니다.
        builder.set_pp("player1", 0, 7)
        
        game = builder.build()
        gsm = game.game_state_manager
        p1 = gsm.players["player1"]
        
        # 각성(Overflow) 상태 활성화 여부를 확인합니다.
        self.assertTrue(p1.is_overflow)
        
        # 3. 흙의 비술(EARTH_RITE) 효과를 직접 정의합니다.
        from src.common.effect import Effect
        from src.common.enums import EffectType, ProcessType, TargetType
        
        rite_effect = Effect(
            type=EffectType.EARTH_RITE,
            process=ProcessType.DRAW,
            target=TargetType.OWN_LEADER,
            value=1
        )
        
        # 4. 효과를 직접 resolve_effect로 실행하여 첫 번째 마법진이 소모되는지 검증합니다.
        game.effect_processor.resolve_effect(rite_effect, sigil1.card_id, gsm, None)
        
        # 첫 번째 마법진은 묘지로 이동하고 두 번째는 필드에 유지합니다.
        self.assertEqual(sigil1.current_zone, Zone.GRAVEYARD)
        self.assertEqual(sigil2.current_zone, Zone.FIELD)

    def test_comment_format_check(self):
        """테스트 및 헬퍼 파일들의 주석 및 docstring 형식을 검증합니다."""
        import ast
        import tokenize
        import io
        import os

        # 검사 대상 파일 경로 목록입니다.
        target_files = [
            "tests/scenario_helper.py",
            "tests/test_scenario_builder.py",
            "src/models/card.py",
            "src/models/crest.py",
            "src/models/deck.py",
            "src/models/field.py",
            "src/models/graveyard.py",
            "src/models/hand.py",
            "src/models/player.py",
            "src/common/card_data.py",
            "src/common/effect.py",
            "src/common/enums.py",
            "src/common/event.py",
            "src/common/listener.py",
            "src/engine/effect_processor.py",
            "src/engine/event_manager.py",
            "src/engine/game_state_manager.py",
            "src/engine/main_game_logic.py",
            "src/engine/rule_engine.py",
            "ui/gui.py",
            "main.py",
            "card_data_pipeline/1_data_acquisition/add_korean_names.py",
            "card_data_pipeline/1_data_acquisition/analyze_effects.py",
            "card_data_pipeline/1_data_acquisition/card_data_crawl.py",
            "card_data_pipeline/1_data_acquisition/check_parsing_rate.py",
            "card_data_pipeline/1_data_acquisition/convert_database.py",
            "card_data_pipeline/1_data_acquisition/parse_script.py",
            "card_data_pipeline/2_manual_data_refinement/manual_editor.py"
        ]

        errors = []

        for filepath in target_files:
            if not os.path.exists(filepath):
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # AST 기반의 docstring 콜론 및 마침표를 검사합니다.
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{filepath} 구문 에러 - {e}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # docstring 내부 콜론을 검사합니다.
                        if ":" in docstring:
                            errors.append(f"{filepath} docstring 콜론 포함 - {docstring[:30]}")
                        # docstring 문장 마침표를 검사합니다.
                        lines = [l.strip() for l in docstring.split("\n") if l.strip()]
                        for line in lines:
                            # 대시 시작 항목이나 단순 단어 외의 문장은 온점으로 끝나야 합니다.
                            if line and not line.endswith(".") and not line.startswith("-") and len(line.split()) > 1:
                                errors.append(f"{filepath} docstring 마침표 누락 - {line}")

            # tokenize 기반의 한 줄 주석 콜론 및 마침표를 검사합니다.
            tokens = tokenize.generate_tokens(io.StringIO(content).readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    comment_text = token.string[1:].strip()
                    if not comment_text:
                        continue
                    # 주석 내부 콜론을 검사합니다.
                    if ":" in comment_text:
                        errors.append(f"{filepath} 주석 콜론 포함 - {token.string}")
                    # 주석 문장 마침표를 검사합니다 (단어가 2개 이상이고 문장 형태일 때).
                    words = comment_text.split()
                    if len(words) > 1 and not comment_text.endswith("."):
                        # 영어 태그 혹은 단순 표시용 주석 등 예외 사항을 필터링합니다.
                        if not comment_text.startswith("TODO") and not comment_text.startswith("FIXME"):
                            errors.append(f"{filepath} 주석 마침표 누락 - {token.string}")

        # 에러 발생 시 단언 실패로 처리합니다.
        if errors:
            print("\n--- 주석 규칙 위반 목록 ---")
            for err in errors:
                print(err)
            self.fail(f"총 {len(errors)}개의 주석 규칙 위반이 발견되었습니다.")

    def test_combo_mechanism(self):
        """콤보 효과 발동 및 대체 흐름을 테스트합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_pp("player1", 10, 10)

        # 콤보 검증용 추종자 배치.
        sagebrush = builder.add_to_hand("player1", "10111150")
        target_f1 = builder.add_to_field("player2", "Leah, Bellringer Angel")
        target_f2 = builder.add_to_field("player2", "Leah, Bellringer Angel")

        game = builder.build()

        # 1. 콤보가 아닐 때 (첫 카드 플레이).
        # 팬페어만 발동하여 타겟 중 1명에게만 피해를 주어야 합니다.
        game.play_card("player1", sagebrush.card_id)

        # 콤보 미달성으로 1명만 파괴되고 1명은 살아야 합니다.
        dead_count = sum(1 for f in [target_f1, target_f2] if f.current_zone == Zone.GRAVEYARD)
        self.assertEqual(dead_count, 1)

        # 2. 콤보가 3일 때 (콤보 달성).
        # 콤보 효과(3명 무작위 피해)가 대신 발동하여 두 타겟 모두 파괴되어야 합니다.
        builder2 = GameScenarioBuilder("player1", "player2")
        builder2.set_pp("player1", 10, 10)
        builder2.set_combo("player1", 2)

        sagebrush2 = builder2.add_to_hand("player1", "10111150")
        target2_f1 = builder2.add_to_field("player2", "Leah, Bellringer Angel")
        target2_f2 = builder2.add_to_field("player2", "Leah, Bellringer Angel")

        game2 = builder2.build()
        game2.play_card("player1", sagebrush2.card_id)

        # 콤보 달성으로 2명 모두 파괴되어 묘지로 가야 합니다.
        dead_count2 = sum(1 for f in [target2_f1, target2_f2] if f.current_zone == Zone.GRAVEYARD)
        self.assertEqual(dead_count2, 2)

    def test_spellboost_mechanism(self):
        """패의 주문 증폭 및 코스트 감소 효과를 테스트합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_pp("player1", 5, 5)

        # 주문 증폭용 카드 배치.
        blaze = builder.add_to_hand("player1", "10032120")
        spell = builder.add_to_hand("player1", "10012310")

        game = builder.build()

        # 초기 코스트 검증.
        self.assertEqual(blaze.current_cost, 10)

        # 주문 시전.
        game.play_card("player1", spell.card_id)

        # 주문 시전 후 패에 있는 Blaze Destroyer의 비용이 1 감소하여 9가 되어야 합니다.
        self.assertEqual(blaze.current_cost, 9)

    def test_skybound_art_mechanism(self):
        """오의 및 해방오의 카운터 감소를 테스트합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_pp("player1", 5, 5)
        builder.set_ep("player1", 1, 1)

        seofon = builder.add_to_hand("player1", "10424120")
        my_follower = builder.add_to_field("player1", "Indomitable Fighter")

        game = builder.build()

        # 초기 해방오의 게이지 확인.
        ssa_effect = [e for e in seofon.effects if e.type.name == "SUPER_SKYBOUND_ART"][0]
        self.assertEqual(ssa_effect.skybound_art_gauge, 15)

        # 아군 추종자 진화.
        game.evolve_follower(my_follower.card_id, "player1")

        # 게이지가 1 줄어야 합니다.
        self.assertEqual(ssa_effect.skybound_art_gauge, 14)

    def test_gain_max_pp_mechanism(self):
        """최대 PP 증가 메커니즘을 테스트합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_pp("player1", 3, 3)

        game = builder.build()
        gsm = game.game_state_manager

        # 최대 PP 1 증가 효과를 해결합니다.
        from src.common.effect import Effect
        from src.common.enums import EffectType, ProcessType, TargetType
        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.GAIN_MAX_PP,
            target=TargetType.OWN_LEADER,
            value=1
        )
        game.effect_processor.resolve_effect(effect, "player1", gsm, None)

        p1 = gsm.players["player1"]
        self.assertEqual(p1.max_pp, 4)

    def test_advance_countdown_mechanism(self):
        """마법진 카운트다운 가속 진행 메커니즘을 테스트합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        # 카운트다운이 2인 마법진을 배치합니다.
        amulet = builder.add_to_field("player1", "10031320")  # Truth Summons.
        amulet.countdown_value = 2

        game = builder.build()
        gsm = game.game_state_manager

        # 카운트다운을 2만큼 감소시키는 효과를 해결합니다.
        from src.common.effect import Effect
        from src.common.enums import EffectType, ProcessType, TargetType
        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.ADVANCE_COUNTDOWN,
            target=TargetType.SELF,
            value=2
        )
        game.effect_processor.resolve_effect(effect, amulet.card_id, gsm, None)

        # 마법진의 카운트다운이 0이 되어 묘지로 가야 합니다.
        self.assertEqual(amulet.countdown_value, 0)
        self.assertEqual(amulet.current_zone, Zone.GRAVEYARD)

    def test_increase_combo_mechanism(self):
        """콤보 강제 증가 메커니즘을 테스트합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_combo("player1", 1)

        game = builder.build()
        gsm = game.game_state_manager

        # 콤보를 2만큼 추가로 증가시키는 효과를 해결합니다.
        from src.common.effect import Effect
        from src.common.enums import EffectType, ProcessType, TargetType
        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.INCREASE_COMBO,
            target=TargetType.OWN_LEADER,
            value=2
        )
        game.effect_processor.resolve_effect(effect, "player1", gsm, None)

        p1 = gsm.players["player1"]
        self.assertEqual(p1.combo_count, 3)

    def test_multi_attack_mechanism(self):
        """다중 공격 상태 및 2회 공격의 정상 작동 여부를 테스트합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_pp("player1", 5, 5)
        # 내 필드의 추종자와 상대 필드의 샌드백 추종자들을 준비합니다.
        attacker = builder.add_to_field("player1", "Indomitable Fighter")
        # 질주 상태로 턴 공격 가능하도록 설정합니다.
        from src.common.effect import Effect
        from src.common.enums import EffectType
        attacker.effects.append(Effect(type=EffectType.STORM))

        target1 = builder.add_to_field("player2", "Leah, Bellringer Angel")
        target2 = builder.add_to_field("player2", "Leah, Bellringer Angel")

        game = builder.build()
        gsm = game.game_state_manager

        # 공격자에게 2회 다중 공격 프로세스를 해결합니다.
        from src.common.enums import ProcessType, TargetType
        effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.MULTI_ATTACK,
            target=TargetType.SELF,
            value=2
        )
        game.effect_processor.resolve_effect(effect, attacker.card_id, gsm, None)

        # 첫 번째 공격을 시도합니다.
        res1 = game.attack_follower(attacker.card_id, target1.card_id)
        self.assertTrue(res1)
        self.assertEqual(target1.current_zone, Zone.GRAVEYARD)
        # 아직 1회 공격을 완료하여 남은 횟수가 있으므로 is_engaged가 False여야 합니다.
        self.assertFalse(attacker.is_engaged)

        # 두 번째 공격을 시도합니다.
        res2 = game.attack_follower(attacker.card_id, target2.card_id)
        self.assertTrue(res2)
        self.assertEqual(target2.current_zone, Zone.GRAVEYARD)

        # 2회 공격을 모두 소진했으므로 이제 is_engaged가 True가 되어야 합니다.
        self.assertTrue(attacker.is_engaged)

    def test_wasteland_of_destruction_and_world_of_games(self):
        """파괴의 황야를 플레이하여 대유희 세계를 선택하고 파괴하는 연동 과정을 시뮬레이션합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_pp("player1", 5, 5)
        
        # 패에 파괴의 황야를 추가하고 필드에 대유희 세계를 배치합니다.
        wasteland = builder.add_to_hand("player1", "Wasteland of Destruction")
        world_of_games = builder.add_to_field("player1", "World of Games")
        
        game = builder.build()
        
        # GUI 선택 Mock을 설정하여 대유희 세계의 card_id가 선택되도록 보정합니다.
        game.gui.get_user_choice.return_value = world_of_games.card_id
        
        # 파괴의 황야를 플레이하여 전장의 아군인 대유희 세계를 선택하여 파괴하도록 유도합니다.
        game.play_card("player1", wasteland.card_id)
        
        # 대유희 세계가 파괴되어 묘지로 가고, 파괴의 황야가 필드에 배치되었는지 검증합니다.
        self.assertEqual(world_of_games.current_zone, Zone.GRAVEYARD)
        self.assertEqual(wasteland.current_zone, Zone.FIELD)

    def test_ghost_banish_on_leave_field_and_turn_end(self):
        """유령 카드가 필드를 벗어날 때 및 턴 종료 시 소멸하는지 검증합니다."""
        # 1. 턴 종료 시 소멸하는지 검증합니다.
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_active_player("player1")
        ghost = builder.add_to_field("player1", "90051130")
        
        game = builder.build()
        
        # 턴 종료를 처리합니다.
        game.end_turn("player1")
        
        # 유령 카드가 소멸 영역으로 가야 합니다.
        self.assertEqual(ghost.current_zone, Zone.BANISHED)
        
        # 2. 필드를 벗어날 때 소멸 영역으로 가는지 검증합니다.
        builder2 = GameScenarioBuilder("player1", "player2")
        builder2.set_pp("player1", 5, 5)
        
        ghost2 = builder2.add_to_field("player1", "90051130")
        game2 = builder2.build()
        
        # 직접 파괴 효과를 트리거합니다.
        from src.common.effect import Effect
        from src.common.enums import EffectType, ProcessType, TargetType
        destroy_effect = Effect(
            type=EffectType.SPELL,
            process=ProcessType.DESTROY,
            target=TargetType.SELF
        )
        game2.effect_processor.resolve_effect(destroy_effect, ghost2.card_id, game2.game_state_manager, None)
        game2.process_events()
        
        # 파괴되면서 필드를 벗어났으나 소멸 영역으로 가야 합니다.
        self.assertEqual(ghost2.current_zone, Zone.BANISHED)

    def test_fuzz_crash_snapshot_scenario(self):
        """퍼징 시뮬레이션 중 무결의 시계 플레이 시 발생한 지연 바인딩 AttributeError 크래시 스냅샷 시나리오를 재현하여 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_active_player("player1")
        builder.set_pp("player1", 4, 6)
        builder.set_health("player1", 13)
        builder.set_health("player2", 18)
        builder.set_pp("player2", 5, 5)

        # 플레이어1 손패 구성.
        builder.add_to_hand("player1", "Lyanthoth, Eld Tome")
        builder.add_to_hand("player1", "Missionary of Recruitment")
        builder.add_to_hand("player1", "Missionary of Recruitment")
        builder.add_to_hand("player1", "Greatness Ascended")
        builder.add_to_hand("player1", "Troue, Heroic Visionary")
        timepiece = builder.add_to_hand("player1", "Timepiece of Perfection")

        # 플레이어2 손패 구성.
        builder.add_to_hand("player2", "Belial, Archangel of Cunning")
        builder.add_to_hand("player2", "Harmony of Youth")
        builder.add_to_hand("player2", "Ephemeral Demon Princess")
        builder.add_to_hand("player2", "Ginsetsu & Yuzuki, Twin Calamities")
        builder.add_to_hand("player2", "Belial, Archangel of Cunning")

        # 플레이어1 필드 구성.
        builder.add_to_field("player1", "Temple of Repose")
        builder.add_to_field("player1", "Altaro Superfan")

        # 플레이어2 필드 구성.
        builder.add_to_field("player2", "Altaro Superfan")
        builder.add_to_field("player2", "Bat")

        game = builder.build()

        # player1이 Timepiece of Perfection을 남은 PP 4를 소모하여 플레이합니다.
        # 지연 바인딩 버그가 해결되었다면 AttributeError 없이 정상적으로 플레이되고 True를 리턴해야 합니다.
        played = game.play_card("player1", timepiece.card_id, enhanced_cost=4)
        self.assertTrue(played)
        self.assertEqual(timepiece.current_zone, Zone.FIELD)
        self.assertEqual(game.game_state_manager.players["player1"].current_pp, 0)

    def test_malice_of_the_mistbloom_effect(self):
        """무권화의 격분 주문을 플레이했을 때 손패의 무작위 카드가 덱으로 되돌아가고 세 장을 드로우하는지 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_active_player("player1")
        builder.set_pp("player1", 3, 3)
        malice = builder.add_to_hand("player1", "10561310")
        target_card = builder.add_to_hand("player1", "Indomitable Fighter")
        for _ in range(5):
            builder.add_to_deck("player1", "Leah, Bellringer Angel")
        
        game = builder.build()
        played = game.play_card("player1", malice.card_id)
        self.assertTrue(played)
        self.assertEqual(len(game.game_state_manager.players["player1"].hand.get_cards()), 3)
        self.assertEqual(target_card.current_zone, Zone.DECK)

    def test_slaus_random_ability_activation(self):
        """슬로스 추종자가 턴 시작 시 아직 활성화되지 않은 효과를 무작위로 하나씩 정상 발동하는지 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_active_player("player1")
        builder.set_pp("player1", 0, 3)
        slaus = builder.add_to_field("player1", "10574110")
        builder.add_to_hand("player1", "Indomitable Fighter")
        
        game = builder.build()
        game._start_turn("player1")
        self.assertEqual(len(slaus.activated_abilities), 1)

    def test_depths_of_the_eld_crystals(self):
        """천정의 심연 주문을 플레이했을 때 무작위 X, Y, Z 배분 및 융합 연산이 정상 작동하는지 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_active_player("player1")
        builder.set_pp("player1", 6, 6)
        depths = builder.add_to_hand("player1", "90034330")
        
        game = builder.build()
        player1 = game.game_state_manager.players["player1"]
        player1.faith = 5
        played = game.play_card("player1", depths.card_id)
        self.assertTrue(played)
        self.assertEqual(depths.x_val + depths.y_val + depths.z_val, 5)

    def test_noble_shikigami_enters_field(self):
        """식신 귀인이 전장에 소환될 때 이번 턴 파괴된 식신 추종자들의 누적 스탯만큼 버프를 얻는지 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_active_player("player1")
        builder.set_pp("player1", 10, 10)
        shikigami = builder.add_to_hand("player1", "90034120")
        destroyed_shikigami = builder.add_to_field("player1", "Noble Shikigami")
        
        game = builder.build()
        game.game_state_manager.move_card(destroyed_shikigami.card_id, Zone.FIELD, Zone.GRAVEYARD)
        from src.common.event import DestroyedOnFieldEvent
        game.event_manager.publish(DestroyedOnFieldEvent(card_id=destroyed_shikigami.card_id))
        game.process_events()
        
        played = game.play_card("player1", shikigami.card_id)
        self.assertTrue(played)
        self.assertEqual(shikigami.current_attack, 2)
        self.assertEqual(shikigami.current_defense, 2)

    def test_gear_of_remembrance_transform(self):
        """패스트 코어 카드가 필드에 플레이될 때 포티파이어 아티팩트로 정상 변신하는지 검증합니다."""
        builder = GameScenarioBuilder("player1", "player2")
        builder.set_active_player("player1")
        builder.set_pp("player1", 1, 1)
        # 패스트 코어(90071220)를 패에 추가합니다.
        gear = builder.add_to_hand("player1", "90071220")

        game = builder.build()
        # 카드를 플레이하여 변신 효과가 작동하도록 유도합니다.
        played = game.play_card("player1", gear.card_id)
        self.assertTrue(played)
        # 필드의 카드가 포티파이어 아티팩트(Fortifier Artifact)로 변신했는지 확인합니다.
        field_cards = game.game_state_manager.get_cards_in_zone("player1", Zone.FIELD)
        self.assertEqual(len(field_cards), 1)
        self.assertEqual(field_cards[0].card_data.name, "Fortifier Artifact")

