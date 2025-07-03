from card import Card
from enums import Zone, CardType, EffectType, TargetType
from main_game_logic import Game  # 상대 경로 임포트
from player import Player


def print_field_card(index: int, card_id: str, game: Game):
    card_name, card_type, card_attack, card_defense, countdown_value, effect_types = game.game_state_manager.get_card_info_field(card_id)
    print(
        f"  {index}. [{card_id}] {card_name} (공: {card_attack}, 체: {card_defense}, 타입: {card_type.value})" +
        (f", 남은 카운트다운: {countdown_value}"
         if card_type == CardType.AMULET and any(effect_type == EffectType.COUNTDOWN for effect_type in effect_types)
         else "") +
        (f", 키워드: {', '.join(effect_type.value for effect_type in effect_types)}"
         if effect_types else ""))

# --- 게임 실행 예시 ---
if __name__ == "__main__":
    game = Game("player1", "player2")
    current_player = "player1"
    opponent_id = game.opponent_id[current_player]

    for turn_num in range(1, 21):  # 20턴까지 진행 예시

        while True:
            # 게임 상태 정보 조회
            current_pp, max_pp = game.game_state_manager.get_pp_info(current_player)
            player_field_card_ids = game.game_state_manager.get_card_ids_in_zone(current_player, Zone.FIELD)
            opponent_field_card_ids = game.game_state_manager.get_card_ids_in_zone(opponent_id, Zone.FIELD)

            # 게임 상태 출력
            print("\n--- 현재 게임 상태 ---")
            print(
                f"현재 {current_player}의 PP: {current_pp}/{max_pp}")
            print(f"\n{opponent_id}의 필드:")
            if opponent_field_card_ids:
                for i, card_id in enumerate(opponent_field_card_ids):
                    print_field_card(i+1, card_id, game)
            else:
                print("  비어있습니다.")

            print(f"{current_player}의 필드:")
            if player_field_card_ids:
                for i, card_id in enumerate(player_field_card_ids):
                    print_field_card(i+1, card_id, game)
            else:
                print("  비어있습니다.")

            print("\n--- 행동 선택 ---")
            print("1. 패에서 카드 내기")
            print("2. 필드 조작 (추종자 공격/진화/초진화, 마법진 활성화)")
            print("3. 턴 종료")

            choice = input("선택: ")

            if choice == '1':  # 패에서 카드 내기
                player_hand_id = game.game_state_manager.get_card_ids_in_zone(current_player, Zone.HAND)
                playable_cards_id = [card_id for card_id in player_hand_id if game.rule_engine.validate_play_card(card_id, current_player)]
                if not playable_cards_id:
                    print("패에 카드가 없습니다.")
                    continue

                print("\n--- 현재 사용 가능 패 ---")
                enhanced_costs_on_hand = []
                for i, card_id in enumerate(playable_cards_id):
                    card_name, card_type, card_cost = game.game_state_manager.get_card_info_hand(card_id)
                    # 증강 키워드 체크
                    # card_cost = card.current_cost
                    card_cost_info = f"{card_cost}"
                    enhance_effects = [effect for effect in game.game_state_manager.get_card_effects(card_id, EffectType.ENHANCE)]
                    enhance_costs = [effect['enhance_cost'] for effect in enhance_effects if effect['enhance_cost'] <= current_pp]
                    if enhance_costs:
                        card_cost = max(enhance_costs)
                        card_cost_info = f"{card_cost}(증강됨)"
                        enhanced_costs_on_hand.append(card_cost)
                    else:
                        enhanced_costs_on_hand.append(0)
                    print(f"{i + 1}. [{card_id}] {card_name} (코스트: {card_cost_info}, 타입: {card_type.value})")
                print(f"{len(playable_cards_id) + 1}. 뒤로 가기")

                card_choice = input("낼 카드 번호를 선택하세요: ")
                if not card_choice.isdigit():
                    print("잘못된 입력입니다. 숫자를 입력하세요.")
                    continue

                card_idx = int(card_choice) - 1
                if card_idx == len(playable_cards_id):  # 뒤로 가기
                    continue
                elif 0 <= card_idx < len(playable_cards_id):
                    selected_card_id = playable_cards_id[card_idx]
                    game.play_card(current_player, selected_card_id, enhanced_costs_on_hand[card_idx])
                else:
                    print("유효하지 않은 카드 번호입니다.")

            elif choice == '2':  # 필드 조작
                if not player_field_card_ids:
                    print("필드에 조작할 추종자/마법진이 없습니다.")
                    continue

                # --- 1. 조작할 카드 선택 ---
                print("\n--- 조작할 카드 선택 ---")
                for i, card_id in enumerate(player_field_card_ids):
                    card_name, card_type, can_attack_leader, can_attack_follower, attack, defense, is_evolved, is_super_evolved = game.game_state_manager.get_card_attack_info_field(card_id)
                    # 공격 상태 체크
                    attack_status = ""
                    if card_type == CardType.FOLLOWER:
                        if not can_attack_follower:
                            if not can_attack_leader:
                                attack_status = " (공격 불가)"
                            else: attack_status = " (리더 공격 불가)"
                    # 진화 상태 체크
                    evolve_status = "(진화함)" if is_evolved else ""
                    if is_super_evolved:
                        evolve_status = "(초진화함)"
                    print(f"{i + 1}. [{card_id}] {card_name} (공: {attack}, 체: {defense})" + attack_status + evolve_status)
                print(f"{len(player_field_card_ids) + 1}. 뒤로 가기")

                card_choice = input("조작할 카드 번호를 선택하세요: ")

                if not card_choice.isdigit():
                    print("잘못된 입력입니다. 숫자를 입력하세요.")
                    continue

                card_idx = int(card_choice) - 1
                if card_idx == len(player_field_card_ids):  # 뒤로 가기 선택
                    continue

                if not (0 <= card_idx < len(player_field_card_ids)):
                    print("유효하지 않은 카드 번호입니다.")
                    continue

                selected_card_id = player_field_card_ids[card_idx]

                # --- 2. 선택한 카드로 수행 가능한 행동 목록 생성 ---
                available_actions = []
                card_name, card_type, can_attack_leader, can_attack_follower, _, _, is_evolved, _ = game.game_state_manager.get_card_attack_info_field(selected_card_id)

                # 행동 1: 공격 가능 여부 확인
                if card_type == CardType.FOLLOWER and can_attack_follower:
                    available_actions.append("추종자 공격")

                # 행동 2: 진화 가능 여부 확인
                if card_type == CardType.FOLLOWER and not is_evolved and game.game_state_manager.can_evolve(current_player):
                    available_actions.append("추종자 진화")

                # 행동 3: 초진화 가능 여부 확인
                if card_type == CardType.FOLLOWER and not is_evolved and game.game_state_manager.can_super_evolve(current_player):
                    available_actions.append("추종자 초진화")

                # 행동 4: 마법진 활성화 가능 여부 확인
                if card_type == CardType.AMULET and game.game_state_manager.has_keyword(card_id, EffectType.ACTIVATE):
                    available_actions.append("마법진 활성화")

                if not available_actions:
                    print("선택한 카드로는 현재 할 수 있는 행동이 없습니다.")
                    continue

                # --- 3. 가능한 행동 목록 표시 및 선택 ---
                print(f"[{card_name}]으로 할 행동 선택 ---")
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
                    opponent_targets_id = [card_id for card_id in opponent_field_card_ids if game.game_state_manager.get_type(card_id) == CardType.FOLLOWER] + [opponent_id]
                    possible_targets_id = [target_id for target_id in opponent_targets_id if game.rule_engine.validate_attack(selected_card_id, target_id)]

                    # 공격 대상 목록 표시
                    if not possible_targets_id:
                        print("공격할 수 있는 대상이 없습니다.")
                        continue

                    for i, target_id in enumerate(possible_targets_id):
                        card_type = game.game_state_manager.get_type(target_id)
                        if card_type == CardType.LEADER:  # '상대 리더'인 경우
                            print(f"{i + 1}. {target_id} (체력: {defense})")
                        else:  # 추종자인 경우
                            card_name, _, _, _, attack, defense, _, _ = game.game_state_manager.get_card_attack_info_field(target_id)
                            print(
                                f"{i + 1}. [{target_id}] {card_name} (공: {attack}, 체: {defense})")
                    print(f"{len(possible_targets_id) + 1}. 취소")

                    target_choice = input("대상 번호를 선택하세요: ")

                    if not target_choice.isdigit(): continue

                    target_idx = int(target_choice) - 1

                    if 0 <= target_idx < len(possible_targets_id):
                        selected_target_id = possible_targets_id[target_idx]
                        target_type = game.game_state_manager.get_type(selected_target_id)
                        if target_type == CardType.LEADER:
                            game.attack_leader(selected_card_id)
                        else:
                            game.attack_follower(selected_card_id, selected_target_id)
                    else:
                        print("공격을 취소합니다.")

                elif chosen_action == "추종자 진화":
                    game.evolve_follower(selected_card_id, current_player)
                    print(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 진화시켰습니다!")

                elif chosen_action == "추종자 초진화":
                    game.super_evolve_follower(selected_card_id, current_player)
                    print(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 초진화시켰습니다!")

                elif chosen_action == "마법진 활성화":
                    game.activate_amulet(selected_card_id, current_player)
                    print(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 활성화했습니다!")

            elif choice == '3':  # 턴 종료
                print(f"{current_player} 턴 종료.")
                game.end_turn(current_player)
                break  # 턴 종료, 다음 플레이어로 넘어감
            else:
                print("유효하지 않은 선택입니다. 다시 선택해주세요.")

        # 턴 플레이어 전환
        current_player = game.opponent_id[current_player]
        opponent_id = game.opponent_id[current_player]

    print("\n--- 게임 종료 예시 ---")