from enums import Zone
from main_game_logic import Game  # 상대 경로 임포트

# --- 게임 실행 예시 ---
if __name__ == "__main__":
    game = Game("player1", "player2")

    # 몇 턴 진행 예시
    current_player = "player1"
    for turn in range(1, 4):
        game.start_turn(current_player)

        # 현재 플레이어의 패 확인
        player_hand = game.game_state_manager.get_cards_in_zone(current_player, Zone.HAND)
        print(f"현재 {current_player}의 패: {[c.card_data['name'] for c in player_hand]}")
        print(f"현재 {current_player}의 PP: {game.game_state_manager.get_player_pp(current_player)}/{game.game_state_manager.get_player_max_pp(current_player)}")
        print(f"현재 {current_player}의 묘지 크기: {game.game_state_manager.get_graveyard_size(current_player)}")
        print(f"현재 {current_player}의 대지의 인장 스택: {game.game_state_manager.get_earth_sigil_stacks(current_player)}")


        # 카드 플레이 예시
        if player_hand:
            # 수호자 플레이 시도
            ward_card = next((c for c in player_hand if c.card_data['name'] == "수호자"), None)
            if ward_card and game.game_state_manager.get_player_pp(current_player) >= ward_card.current_cost:
                game.play_card(current_player, ward_card.card_id)

            # 마법진 플레이 시도
            amulet_card = next((c for c in player_hand if c.card_data['name'] == "카운트다운 마법진"), None)
            if amulet_card and game.game_state_manager.get_player_pp(current_player) >= amulet_card.current_cost:
                game.play_card(current_player, amulet_card.card_id)
                # 마법진 카운트다운은 다음 턴 시작 시 감소

            # 주문 증폭 마법사 플레이 시도
            spellboost_follower = next((c for c in player_hand if c.card_data['name'] == "주문증폭 마법사"), None)
            if spellboost_follower and game.game_state_manager.get_player_pp(current_player) >= spellboost_follower.current_cost:
                game.play_card(current_player, spellboost_follower.card_id)

            # 주문 증폭 효과를 보기 위해 다른 주문을 플레이 (예: 복수의 불꽃)
            spell_card = next((c for c in player_hand if c.card_data['name'] == "복수의 불꽃"), None)
            if spell_card and game.game_state_manager.get_player_pp(current_player) >= spell_card.current_cost:
                # 타겟은 임의의 상대방 필드 추종자 (여기서는 첫 번째 추종자)
                opponent_field_cards = game.game_state_manager.get_cards_in_zone(game._get_opponent_id(current_player), Zone.FIELD)
                target_follower_id = opponent_field_cards[0].card_id if opponent_field_cards else None
                if target_follower_id:
                     game.play_card(current_player, spell_card.card_id, [target_follower_id])

            # 대지의 술사 플레이 시도 (대지의 인장 쌓기)
            earthrite_follower = next((c for c in player_hand if c.card_data['name'] == "대지의 술사"), None)
            if earthrite_follower and game.game_state_manager.get_player_pp(current_player) >= earthrite_follower.current_cost:
                game.play_card(current_player, earthrite_follower.card_id)
                game.game_state_manager.add_earth_sigil(current_player, 1) # 대지의 술사 플레이 시 인장 1개 획득 가정


            # 질주/돌진 추종자 플레이 시도 및 공격
            storm_rush_follower = next((c for c in player_hand if c.card_data['name'] in ["질주하는 전사", "돌진하는 기사"]), None)
            if storm_rush_follower and game.game_state_manager.get_player_pp(current_player) >= storm_rush_follower.current_cost:
                game.play_card(current_player, storm_rush_follower.card_id)
                # 플레이 후 즉시 공격 시도
                opponent_field_cards = game.game_state_manager.get_cards_in_zone(game._get_opponent_id(current_player), Zone.FIELD)
                target_follower = next((c for c in opponent_field_cards if not c.has_keyword("수호")), None) # 수호 무시하지 않는 한 수호자 없어야 함

                if storm_rush_follower and target_follower and game.rule_engine.validate_attack(storm_rush_follower, target_follower, current_player):
                    game.attack_follower(storm_rush_follower.card_id, target_follower.card_id, current_player)
                elif storm_rush_follower:
                    print(f"DEBUG: {storm_rush_follower.card_data['name']}은(는) 공격할 대상이 없거나 규칙 위반.")

            # 사령술사 플레이 시도
            necromancer = next((c for c in player_hand if c.card_data['name'] == "네크로맨서"), None)
            if necromancer and game.game_state_manager.get_player_pp(current_player) >= necromancer.current_cost:
                # 묘지에 4장 이상 있어야 사령술 발동
                if game.game_state_manager.get_graveyard_size(current_player) >= 4:
                    game.play_card(current_player, necromancer.card_id)

            # 묘지에 카드 넣기 위한 임의의 동작 (유언 효과 테스트용)
            if turn == 1 and current_player == "player1":
                # 첫 턴에 강제로 카드 하나 묘지로 보내기 (테스트용)
                if game.game_state_manager.get_cards_in_zone(current_player, Zone.DECK):
                    card_for_graveyard = game.game_state_manager.get_cards_in_zone(current_player, Zone.DECK)[0]
                    game.game_state_manager.move_card(card_for_graveyard, Zone.DECK, Zone.GRAVEYARD)
                    print(f"DEBUG: {card_for_graveyard.card_data['name']} (테스트용) 묘지로 이동됨.")


        game.end_turn(current_player)
        current_player = game._get_opponent_id(current_player)