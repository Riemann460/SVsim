from enums import Zone, CardType, EffectType, TargetType
from main_game_logic import Game  # 상대 경로 임포트
from player import Player

# --- 게임 실행 예시 ---
if __name__ == "__main__":
    game = Game("player1", "player2")
    current_player = "player1"
    for turn_num in range(1, 21):  # 20턴까지 진행 예시
        while True:
            print("\n--- 현재 게임 상태 ---")
            print(
                f"현재 {current_player}의 PP: {game.game_state_manager.players[current_player].current_pp}/{game.game_state_manager.players[current_player].max_pp}")

            # 필드 상태 출력
            print("\n--- 현재 필드 ---")
            opponent_id = game.opponent_id[current_player]
            print(f"{opponent_id}의 필드:")
            opponent_field_cards = game.game_state_manager.get_cards_in_zone(opponent_id, Zone.FIELD)
            if opponent_field_cards:
                for i, card in enumerate(opponent_field_cards):
                    print(
                        f"  {i + 1}. [{card.card_id}] {card.card_data['name']} (공: {card.current_attack}, 체: {card.current_defense}, 타입: {card.get_type().value})" +
                        (
                            f", 남은 카운트다운: {card.countdown_value}" if card.get_type() == CardType.AMULET and card.has_keyword(
                                '카운트다운') else "") +
                        (
                            f", 키워드: {', '.join(effect['type'].value for effect in card.card_data.effects)}" if card.card_data.effects else ""))
            else:
                print("  비어있습니다.")

            print(f"{current_player}의 필드:")
            player_field_cards = game.game_state_manager.get_cards_in_zone(current_player, Zone.FIELD)
            if player_field_cards:
                for i, card in enumerate(player_field_cards):
                    print(
                        f"  {i + 1}. [{card.card_id}] {card.card_data['name']} (공: {card.current_attack}, 체: {card.current_defense}, 타입: {card.get_type().value})" +
                        (
                            f", 남은 카운트다운: {card.countdown_value}" if card.get_type() == CardType.AMULET and card.has_keyword(
                                '카운트다운') else "") +
                        (
                            f", 키워드: {', '.join(effect['type'].value for effect in card.card_data.effects)}" if card.card_data.effects else "") +
                        (f" (공격 가능)" if not card.is_summoned and not card.is_engaged else " (공격 불가)"))
            else:
                print("  비어있습니다.")

            print("\n--- 행동 선택 ---")
            print("1. 패에서 카드 내기")
            print("2. 필드 조작 (추종자 공격/진화/초진화, 마법진 활성화)")
            print("3. 턴 종료")

            choice = input("선택: ")

            if choice == '1':  # 패에서 카드 내기
                player_hand = game.game_state_manager.get_cards_in_zone(current_player, Zone.HAND)
                playable_cards = [card for card in player_hand if game.rule_engine.validate_play_card(card.card_id, current_player)]
                if not playable_cards:
                    print("패에 카드가 없습니다.")
                    continue

                print("\n--- 현재 사용 가능 패 ---")
                for i, card in enumerate(playable_cards):
                    print(f"{i + 1}. [{card.card_id}] {card.card_data['name']} (코스트: {card.current_cost}, 타입: {card.get_type()})")
                print(f"{len(playable_cards) + 1}. 뒤로 가기")

                card_choice = input("낼 카드 번호를 선택하세요: ")
                if not card_choice.isdigit():
                    print("잘못된 입력입니다. 숫자를 입력하세요.")
                    continue

                card_idx = int(card_choice) - 1
                if card_idx == len(playable_cards):  # 뒤로 가기
                    continue
                elif 0 <= card_idx < len(playable_cards):
                    selected_card = playable_cards[card_idx]
                    game.play_card(current_player, selected_card.card_id)
                else:
                    print("유효하지 않은 카드 번호입니다.")

            elif choice == '2':  # 필드 조작
                if not player_field_cards:
                    print("필드에 조작할 추종자/마법진이 없습니다.")
                    continue

                # --- 1. 조작할 카드 선택 ---
                print("\n--- 조작할 카드 선택 ---")
                for i, card in enumerate(player_field_cards):
                    status = []
                    if card.card_data.get('card_type') == CardType.FOLLOWER:
                        if not card.can_attack(TargetType.OPPONENT_LEADER):
                            if not card.can_attack(TargetType.OPPONENT_FOLLOWER_CHOICE):
                                status.append("공격 불가")
                            else: status.append("리더 공격 불가")
                    status_str = f" ({', '.join(status)})" if status else ""
                    print(f"{i + 1}. [{card.card_id}] {card.card_data.get('name')} " +
                          f"(공: {card.current_attack}, 체: {card.current_defense})" +
                          status_str)
                print(f"{len(player_field_cards) + 1}. 뒤로 가기")

                card_choice = input("조작할 카드 번호를 선택하세요: ")

                if not card_choice.isdigit():
                    print("잘못된 입력입니다. 숫자를 입력하세요.")
                    continue

                card_idx = int(card_choice) - 1
                if card_idx == len(player_field_cards):  # 뒤로 가기 선택
                    continue

                if not (0 <= card_idx < len(player_field_cards)):
                    print("유효하지 않은 카드 번호입니다.")
                    continue

                selected_card = player_field_cards[card_idx]

                # --- 2. 선택한 카드로 수행 가능한 행동 목록 생성 ---
                available_actions = []
                card_type = selected_card.get_type()

                # 행동 1: 공격 가능 여부 확인
                if card_type == CardType.FOLLOWER and selected_card.can_attack(TargetType.OPPONENT_FOLLOWER_CHOICE):
                    available_actions.append("추종자 공격")

                # 행동 2: 진화 가능 여부 확인
                if card_type == CardType.FOLLOWER and not selected_card.is_evolved and game.can_evolve(current_player):
                    available_actions.append("추종자 진화")

                # 행동 3: 마법진 활성화 가능 여부 확인
                if card_type == CardType.AMULET and selected_card.has_keyword(EffectType.ACTIVATE):
                    available_actions.append("마법진 활성화")

                if not available_actions:
                    print("선택한 카드로는 현재 할 수 있는 행동이 없습니다.")

                    continue

                # --- 3. 가능한 행동 목록 표시 및 선택 ---
                print(f"[{game.game_state_manager.get_card_name(selected_card.card_id)}]으로 할 행동 선택 ---")
                for i, action in enumerate(available_actions):
                    print(f"{i + 1}. {action}")
                print(f"{len(available_actions) + 1}. 취소")

                action_choice_input = input("선택: ")

                if not action_choice_input.isdigit():
                    print("잘못된 입력입니다. 숫자를 입력하세요.")
                    continue

                action_idx = int(action_choice_input) - 1

                if action_idx == len(available_actions):  # 취소 선택
                    continue

                if not (0 <= action_idx < len(available_actions)):
                    print("유효하지 않은 행동 번호입니다.")
                    continue

                chosen_action = available_actions[action_idx]

                # --- 4. 선택한 행동 실행 ---
                if chosen_action == "추종자 공격":
                    # 기존의 '공격 대상 선택' 로직 재사용
                    print("\n--- 공격 대상 선택 ---")
                    opponent_targets_id = [c.card_id for c in opponent_field_cards if c.get_type() == CardType.FOLLOWER] + [opponent_id]
                    possible_targets_id = [target_id for target_id in opponent_targets_id if game.rule_engine.validate_attack(selected_card.card_id, target_id)]

                    # 공격 대상 목록 표시
                    if not possible_targets_id:
                        print("공격할 수 있는 대상이 없습니다.")
                        continue

                    for i, target_id in enumerate(possible_targets_id):
                        target = game.game_state_manager.get_entity_by_id(target_id)
                        if isinstance(target, Player):  # '상대 리더'인 경우
                            print(f"{i + 1}. {target_id} (체력: {target.current_defense})")
                        else:  # 추종자인 경우
                            print(
                                f"{i + 1}. [{target_id}] {target.get_display_name()} (공: {target.current_attack}, 체: {target.current_defense})")
                    print(f"{len(possible_targets_id) + 1}. 취소")

                    target_choice = input("대상 번호를 선택하세요: ")

                    if not target_choice.isdigit(): continue

                    target_idx = int(target_choice) - 1

                    if 0 <= target_idx < len(possible_targets_id):
                        selected_target_id = possible_targets_id[target_idx]
                        selected_target = game.game_state_manager.get_entity_by_id(selected_target_id)
                        if isinstance(selected_target, Player):
                            game.attack_leader(selected_card.card_id)
                        else:
                            game.attack_follower(selected_card.card_id, selected_target.card_id)
                    else:
                        print("공격을 취소합니다.")

                elif chosen_action == "추종자 진화":
                    game.evolve_follower(selected_card.card_id, current_player)
                    print(f"[{selected_card.card_data.get('name')}]을(를) 진화시켰습니다!")

                elif chosen_action == "마법진 활성화":
                    game.activate_amulet(selected_card.card_id, current_player)
                    print(f"[{selected_card.card_data.get('name')}]을(를) 활성화했습니다!")

            elif choice == '3':  # 턴 종료
                print(f"{current_player} 턴 종료.")
                game.end_turn(current_player)
                break  # 턴 종료, 다음 플레이어로 넘어감
            else:
                print("유효하지 않은 선택입니다. 다시 선택해주세요.")

        # 턴 플레이어 전환
        current_player = game.opponent_id[current_player]

    print("\n--- 게임 종료 예시 ---")