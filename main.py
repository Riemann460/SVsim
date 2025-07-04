from card import Card
from enums import Zone, CardType, EffectType, TargetType
from main_game_logic import Game  # 상대 경로 임포트
from player import Player


def print_field_card(index: int, card_id: str, game: Game):
    """필드의 카드 정보를 출력(이름/공/체/타입/카운트다운/키워드)"""
    card_name, card_type, card_attack, card_defense, countdown_value, effect_types = game.game_state_manager.get_card_info_field(card_id)
    print(
        f"  {index}. [{card_id}] {card_name} (공: {card_attack}, 체: {card_defense}, 타입: {card_type.value})" +
        (f", 남은 카운트다운: {countdown_value}"
         if card_type == CardType.AMULET and any(effect_type == EffectType.COUNTDOWN for effect_type in effect_types)
         else "") +
        (f", 키워드: {', '.join(effect_type.value for effect_type in effect_types)}"
         if effect_types else ""))


def print_hand_card(index: int, card_id: str, is_validate: bool, game: Game):
    """패의 카드 정보를 출력(이름/코스트(증강고려)/타입)"""
    card_name, card_type, card_cost = game.game_state_manager.get_card_info_hand(card_id)

    if not is_validate:
        print(f"-X [{card_id}] {card_name} (코스트: {card_cost}, 타입: {card_type.value}) (사용 불가)")
        return 0

    # 증강 키워드 체크
    card_cost_info = f"{card_cost}"
    enhance_effects = [effect for effect in game.game_state_manager.get_card_effects(card_id, EffectType.ENHANCE)]
    enhance_costs = [effect['enhance_cost'] for effect in enhance_effects if effect['enhance_cost'] <= current_pp]
    if enhance_costs:
        card_cost = max(enhance_costs)
        card_cost_info = f"{card_cost}(증강됨)"
        print(f"{index}. [{card_id}] {card_name} (코스트: {card_cost_info}, 타입: {card_type.value})")
        return card_cost

    print(f"{index}. [{card_id}] {card_name} (코스트: {card_cost_info}, 타입: {card_type.value})")
    return 0


def print_hand(hand_cards_id, is_validate):
    """패 전체의 카드 정보를 출력"""
    card_choice_index = 1
    enhanced_costs = []
    playable_cards_id = []
    for i, card_id in enumerate(hand_cards_id):
        enhanced_cost = print_hand_card(card_choice_index, card_id, is_validate[i], game)
        if is_validate[i]:
            card_choice_index += 1
            playable_cards_id.append(card_id)
            enhanced_costs.append(enhanced_cost)
    print(f"{card_choice_index}. 뒤로 가기")
    return playable_cards_id, enhanced_costs


def print_field_card_to_play(index, card_id):
    """필드에서 조작할 카드의 정보를 출력(이름/공/체/공격상태/진화상태)"""
    card_name, card_type, can_attack_leader, can_attack_follower, attack, defense, is_evolved, is_super_evolved = game.game_state_manager.get_card_attack_info_field(card_id)
    # 공격 상태 체크
    attack_status = ""
    if card_type == CardType.FOLLOWER and not can_attack_leader:
        attack_status = " (리더 공격 불가)" if can_attack_follower else " (공격 불가)"
    # 진화 상태 체크
    evolve_status = " (진화함)" if is_evolved else ""
    if is_super_evolved:
        evolve_status = " (초진화함)"
    print(f"{index}. [{card_id}] {card_name} (공: {attack}, 체: {defense})" + attack_status + evolve_status)


def input_and_check(index: int):
    """숫자를 입력받아 선택지 중 하나를 선택"""
    choice = input("번호를 선택하세요: ")
    if not choice.isdigit():
        print("잘못된 입력입니다. 숫자를 입력하세요.")
        return False, None

    chosen_idx = int(choice) - 1
    if chosen_idx == index:  # 뒤로 가기 선택
        return False, None
    elif 0 <= chosen_idx < index:
        return True, chosen_idx
    else:
        print("유효하지 않은 번호입니다.")
        return False, None


def get_available_actions(card_id: str, game: Game):
    """대상 필드 카드의 가능한 조작 목록을 출력"""
    card_name, card_type, can_attack_leader, can_attack_follower, _, _, is_evolved, _ = game.game_state_manager.get_card_attack_info_field(selected_card_id)
    available_actions = []

    if card_type == CardType.FOLLOWER and can_attack_follower:
        available_actions.append("추종자 공격")

    if card_type == CardType.FOLLOWER and not is_evolved and game.game_state_manager.can_evolve(current_player):
        available_actions.append("추종자 진화")

    if card_type == CardType.FOLLOWER and not is_evolved and game.game_state_manager.can_super_evolve(current_player):
        available_actions.append("추종자 초진화")

    if card_type == CardType.AMULET and game.game_state_manager.has_keyword(card_id, EffectType.ACTIVATE):
        available_actions.append("마법진 활성화")

    return available_actions, card_name


def print_target_card(param, target_id, game):
    """공격 대상 카드의 정보 출력(이름/공/체)"""
    card_type = game.game_state_manager.get_type(target_id)
    if card_type == CardType.LEADER:  # '상대 리더'인 경우
        defense = game.game_state_manager.get_player_defense(target_id)
        print(f"{i + 1}. {target_id} (체력: {defense})")
    else:  # 추종자인 경우
        card_name, _, _, _, attack, defense, _, _ = game.game_state_manager.get_card_attack_info_field(target_id)
        print(
            f"{i + 1}. [{target_id}] {card_name} (공: {attack}, 체: {defense})")


# --- 게임 실행 예시 ---
if __name__ == "__main__":
    game = Game("player1", "player2")
    current_player = "player1"
    opponent_id = game.opponent_id[current_player]

    for turn_num in range(1, 21):  # 20턴까지 진행 예시

        while True:
            # 게임 상태 출력
            current_pp, max_pp, player_field_card_ids, opponent_field_card_ids = game.get_start_turn_ifo(current_player)
            print("\n--- 현재 게임 상태 ---")
            print(f"현재 {current_player}의 PP: {current_pp}/{max_pp}")
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

            # 플레이어 행동 선택
            print("\n--- 행동 선택 ---")
            print("1. 패에서 카드 내기")
            print("2. 필드 조작 (추종자 공격/진화/초진화, 마법진 활성화)")
            print("3. 턴 종료")

            input_validate, choice = input_and_check(3)
            if not input_validate:
                print("다시 선택해주세요.")
                continue

            # 선택 행동 처리
            if choice == 0:  # 패에서 카드 내기
                hand_cards_id, is_validate = game.get_playable_cards_id(current_player)

                if not hand_cards_id or not any(is_validate):
                    print("패에 사용 가능한 카드가 없습니다.")
                    continue

                # 플레이어 패 출력
                print("\n--- 현재 플레이어의 패 ---")
                playable_cards_id, enhanced_costs = print_hand(hand_cards_id, is_validate)

                # 사용할 카드 선택
                input_validate, card_idx = input_and_check(len(playable_cards_id))
                if not input_validate:
                    print("다시 선택해주세요.")
                    continue
                selected_card_id = playable_cards_id[card_idx]

                # 카드 사용
                game.play_card(current_player, selected_card_id, enhanced_costs[card_idx])

            elif choice == 1:  # 필드 조작
                if not player_field_card_ids:
                    print("필드에 조작할 추종자/마법진이 없습니다.")
                    continue

                # 필드 카드 출력
                print("\n--- 조작할 카드 선택 ---")
                for i, card_id in enumerate(player_field_card_ids):
                    print_field_card_to_play(i+1, card_id)
                print(f"{len(player_field_card_ids) + 1}. 뒤로 가기")

                # 조작할 카드 선택
                input_validate, card_idx = input_and_check(len(player_field_card_ids))
                if not input_validate:
                    print("다시 선택해주세요.")
                    continue
                selected_card_id = player_field_card_ids[card_idx]

                # 선택한 카드의 가능한 조작 목록 생성
                available_actions, card_name = get_available_actions(selected_card_id, game)
                if not available_actions:
                    print("선택한 카드로는 현재 할 수 있는 행동이 없습니다.")
                    continue

                # 가능한 조작 목록 출력
                print(f"[{card_name}]으로 할 행동 선택 ---")
                for i, action in enumerate(available_actions):
                    print(f"{i + 1}. {action}")
                print(f"{len(available_actions) + 1}. 취소")

                # 수행할 조작 선택
                input_validate, action_idx = input_and_check(len(available_actions))
                if not input_validate:
                    print("다시 선택해주세요.")
                    continue
                chosen_action = available_actions[action_idx]

                # 선택한 조작 실행
                if chosen_action == "추종자 공격":
                    print("\n--- 공격 대상 선택 ---")
                    opponent_targets_id = [card_id for card_id in opponent_field_card_ids if game.game_state_manager.get_type(card_id) == CardType.FOLLOWER] + [opponent_id]
                    possible_targets_id = [target_id for target_id in opponent_targets_id if game.rule_engine.validate_attack(selected_card_id, target_id)]
                    if not possible_targets_id:
                        print("공격할 수 있는 대상이 없습니다.")
                        continue

                    # 공격 대상 목록 출력
                    for i, target_id in enumerate(possible_targets_id):
                        print_target_card(i+1, target_id, game)
                    print(f"{len(possible_targets_id) + 1}. 취소")

                    # 공격 대상 선택
                    input_validate, target_idx = input_and_check(len(possible_targets_id))
                    if not input_validate:
                        print("다시 선택해주세요.")
                        continue
                    selected_target_id = possible_targets_id[target_idx]

                    # 공격 처리
                    target_type = game.game_state_manager.get_type(selected_target_id)
                    if target_type == CardType.LEADER:
                        game.attack_leader(selected_card_id)
                    else:
                        game.attack_follower(selected_card_id, selected_target_id)

                elif chosen_action == "추종자 진화":
                    game.evolve_follower(selected_card_id, current_player)
                    print(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 진화시켰습니다!")

                elif chosen_action == "추종자 초진화":
                    game.super_evolve_follower(selected_card_id, current_player)
                    print(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 초진화시켰습니다!")

                elif chosen_action == "마법진 활성화":
                    game.activate_amulet(selected_card_id, current_player)
                    print(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 활성화했습니다!")

            elif choice == 2:  # 턴 종료
                print(f"{current_player} 턴 종료.")
                game.end_turn(current_player)
                break  # 턴 종료, 다음 플레이어로 넘어감
            else:
                print("유효하지 않은 선택입니다. 다시 선택해주세요.")

        # 턴 플레이어 전환
        current_player = game.opponent_id[current_player]
        opponent_id = game.opponent_id[current_player]

    print("\n--- 게임 종료 예시 ---")