from card import Card
from enums import Zone, CardType, EffectType, TargetType
from main_game_logic import Game
from player import Player


# --- 게임 실행 예시 ---
if __name__ == "__main__":
    game = Game("player1", "player2")
    current_player = "player1"
    opponent_id = game.opponent_id[current_player]

    for turn_num in range(1, 21):  # 20턴까지 진행 예시

        while True:
            # '선택 대기' 상태이면 선택부터 처리
            game.process_player_choice()

            # 게임 상태 출력
            current_pp, max_pp, player_field_card_ids, opponent_field_card_ids = game.get_start_turn_ifo(current_player)

            # 플레이어 행동 선택
            choices = {
                "패에서 카드 내기": 0,
                "필드 조작 (추종자 공격/진화/초진화, 마법진 활성화)": 1,
                "턴 종료": 2
            }
            choice = int(game.gui.get_user_choice("--- 행동 선택 ---", choices))

            # 선택 행동 처리
            if choice == 0:  # 패에서 카드 내기
                # 엑스트라 PP 사용 여부 확인
                use_extra_pp = False
                if game.has_extra_pp(current_player):
                    extra_pp_choices = {"사용": 0, "미사용": 1}
                    use_extra_pp = int(game.gui.get_user_choice("엑스트라 PP를 사용하시겠습니까?", extra_pp_choices)) == 0

                # 사용 가능한 카드 확인
                hand_cards_id, is_validate = game.get_playable_cards_id(current_player, use_extra_pp)
                if not hand_cards_id or not any(is_validate):
                    game.gui.get_user_choice("패에 사용 가능한 카드가 없습니다.", {"확인": None})
                    continue
                playable_cards_id = [card_id for i, card_id in enumerate(hand_cards_id) if is_validate[i]]

                # 증강 코스트 확인
                enhanced_costs = []
                for i, card_id in enumerate(hand_cards_id):
                    if is_validate[i]:
                        card_name, card_type, card_cost = game.game_state_manager.get_card_info_hand(card_id)
                        enhance_effects = [effect for effect in game.game_state_manager.get_card_effects(card_id, EffectType.ENHANCE)]
                        enhance_costs_for_card = [effect.enhance_cost for effect in enhance_effects if effect.enhance_cost <= current_pp + (1 if use_extra_pp else 0)]
                        if enhance_costs_for_card:
                            enhanced_costs.append(max(enhance_costs_for_card))
                        else:
                            enhanced_costs.append(0) # 기본 코스트 (증강되지 않음)

                # 사용할 카드 선택
                card_choices = {f"{game.game_state_manager.get_card_name(card_id)} (ID: {card_id})": card_id for card_id in playable_cards_id}
                card_choices["뒤로 가기"] = None
                selected_card_id = str(game.gui.get_user_choice("--- 현재 플레이어의 패 ---", card_choices))

                if selected_card_id == "None":
                    print("다시 선택해주세요.")
                    continue
                
                enhanced_cost = enhanced_costs[playable_cards_id.index(selected_card_id)]
                game.play_card(current_player, selected_card_id, enhanced_cost, use_extra_pp)

            elif choice == 1:  # 필드 조작
                if not player_field_card_ids:
                    game.gui.get_user_choice("필드에 조작할 추종자/마법진이 없습니다.", {"확인": None})
                    continue

                # 필드 카드 출력
                card_choices = {f"{game.game_state_manager.get_card_name(card_id)} (ID: {card_id})": card_id for card_id in player_field_card_ids}
                card_choices["뒤로 가기"] = None
                selected_card_id = str(game.gui.get_user_choice("--- 조작할 카드 선택 ---", card_choices))

                if selected_card_id == "None":
                    print("다시 선택해주세요.")
                    continue

                # 선택한 카드의 가능한 조작 목록 생성
                available_actions, card_name = game.get_available_actions(selected_card_id, current_player)
                if not available_actions:
                    game.gui.get_user_choice("선택한 카드로는 현재 할 수 있는 행동이 없습니다.", {"확인": None})
                    continue

                # 가능한 조작 목록 출력
                action_choices = {action: action for action in available_actions}
                action_choices["취소"] = None
                chosen_action = str(game.gui.get_user_choice(f"[{card_name}]으로 할 행동 선택 ---", action_choices))

                if chosen_action == "None":
                    print("다시 선택해주세요.")
                    continue

                # 선택한 조작 실행
                if chosen_action == "추종자 공격":
                    print("\n--- 공격 대상 선택 ---")
                    opponent_targets_id = [card_id for card_id in opponent_field_card_ids if game.game_state_manager.get_type(card_id) == CardType.FOLLOWER] + [opponent_id]
                    possible_targets_id = [target_id for target_id in opponent_targets_id if game.rule_engine.validate_attack(selected_card_id, target_id)]
                    if not possible_targets_id:
                        game.gui.get_user_choice("공격할 수 있는 대상이 없습니다.", {"확인": None})
                        continue

                    # 공격 대상 목록 출력
                    target_choices = {f"{game.game_state_manager.get_card_name(target_id)} (ID: {target_id})": target_id for target_id in possible_targets_id}
                    target_choices["취소"] = None
                    selected_target_id = str(game.gui.get_user_choice("--- 공격 대상 선택 ---", target_choices))

                    if selected_target_id is None:
                        print("다시 선택해주세요.")
                        continue

                    # 공격 처리
                    target_type = game.game_state_manager.get_type(selected_target_id)
                    if target_type == CardType.LEADER:
                        game.attack_leader(selected_card_id)
                    else:
                        game.attack_follower(selected_card_id, selected_target_id)

                elif chosen_action == "추종자 진화":
                    game.evolve_follower(selected_card_id, current_player)
                    game.gui.get_user_choice(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 진화시켰습니다!", {"확인": None})

                elif chosen_action == "추종자 초진화":
                    game.super_evolve_follower(selected_card_id, current_player)
                    game.gui.get_user_choice(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 초진화시켰습니다!", {"확인": None})

                elif chosen_action == "마법진 활성화":
                    game.activate_amulet(selected_card_id, current_player)
                    game.gui.get_user_choice(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 활성화했습니다!", {"확인": None})

            elif choice == 2:  # 턴 종료
                game.gui.get_user_choice(f"{current_player} 턴 종료.", {"확인": None})
                game.end_turn(current_player)
                break  # 턴 종료, 다음 플레이어로 넘어감
            else:
                game.gui.get_user_choice("유효하지 않은 선택입니다. 다시 선택해주세요.", {"확인": None})

        # 턴 플레이어 전환
        current_player = game.opponent_id[current_player]
        opponent_id = game.opponent_id[current_player]

    game.gui.get_user_choice("--- 게임 종료 예시 ---", {"확인": None})