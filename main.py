# 역할 정의. 게임을 실행하고 전체 흐름 및 플레이어 조작 루프를 데모하는 메인 엔트리 스크립트입니다.

from src.models.card import Card
from src.common.enums import Zone, CardType, EffectType, TargetType
from src.engine.main_game_logic import Game
from src.models.player import Player
from src.common import card_data
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox


def load_deck_file(filename, deck_dir="decks"):
    """선택한 덱 파일을 로드하여 CardData 객체 목록으로 변환합니다."""
    if not filename or filename == "기본 예시 덱":
        return None
    filepath = os.path.join(deck_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    cards_list = []
    for item in data.get("cards", []):
        card_id = item.get("card_id")
        count = item.get("count", 1)
        c_data = card_data.get_card_data_by_id(card_id)
        if c_data:
            for _ in range(count):
                cards_list.append(c_data)
    return cards_list


def select_decks_gui():
    """Tkinter를 사용하여 플레이어별 덱을 선택하는 다이얼로그를 띄웁니다."""
    deck_dir = "decks"
    deck_files = []
    if os.path.exists(deck_dir):
        deck_files = [f for f in os.listdir(deck_dir) if f.endswith(".json")]

    # 덱이 아예 없는 경우 콤보박스에 표시할 텍스트입니다.
    choices = deck_files if deck_files else ["기본 예시 덱"]

    root = tk.Tk()
    root.title("SVsim 덱 선택")
    root.geometry("400x250")
    
    # 다크 테마 느낌으로 스타일을 통일합니다.
    bg_dark = "#1e1e2e"
    bg_panel = "#313244"
    fg_light = "#cdd6f4"
    accent_blue = "#89b4fa"
    
    root.configure(bg=bg_dark)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=bg_dark)
    style.configure("TLabel", background=bg_dark, foreground=fg_light, font=("맑은 고딕", 10))
    style.configure("Header.TLabel", background=bg_dark, foreground=accent_blue, font=("맑은 고딕", 12, "bold"))
    style.configure("TCombobox", fieldbackground=bg_panel, background=bg_dark, foreground=fg_light)

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    ttk.Label(frame, text="플레이어 1 덱 선택", style="Header.TLabel").pack(anchor=tk.W, pady=5)
    p1_var = tk.StringVar(value=choices[0])
    p1_combo = ttk.Combobox(frame, textvariable=p1_var, values=choices, state="readonly", width=30)
    p1_combo.pack(fill=tk.X, pady=5)

    ttk.Label(frame, text="플레이어 2 덱 선택", style="Header.TLabel").pack(anchor=tk.W, pady=5)
    p2_var = tk.StringVar(value=choices[0])
    p2_combo = ttk.Combobox(frame, textvariable=p2_var, values=choices, state="readonly", width=30)
    p2_combo.pack(fill=tk.X, pady=5)

    def load_deck_file_with_gui(filename):
        """다이얼로그에서 예외가 발생하면 경고 메시지를 띄우고 기본 덱으로 작동시킵니다."""
        try:
            return load_deck_file(filename, deck_dir)
        except Exception as e:
            messagebox.showwarning("덱 로드 실패", f"덱 파일 로드 실패로 기본 덱을 사용합니다. {str(e)}")
            return None

    result = {"p1": None, "p2": None}

    def start_game():
        """선택한 덱 정보로 게임을 시작합니다."""
        result["p1"] = load_deck_file_with_gui(p1_var.get())
        result["p2"] = load_deck_file_with_gui(p2_var.get())
        root.destroy()

    def start_fallback():
        """기본 덱 설정을 적용하여 시작합니다."""
        result["p1"] = None
        result["p2"] = None
        root.destroy()

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill=tk.X, pady=20)

    start_btn = tk.Button(btn_frame, text="게임 시작", command=start_game, bg=accent_blue, fg=bg_dark, font=("맑은 고딕", 10, "bold"), relief=tk.FLAT, padx=10)
    start_btn.pack(side=tk.LEFT, padx=5)

    fallback_btn = tk.Button(btn_frame, text="기본 덱으로 시작", command=start_fallback, bg=bg_panel, fg=fg_light, font=("맑은 고딕", 10), relief=tk.FLAT, padx=10)
    fallback_btn.pack(side=tk.RIGHT, padx=5)

    root.mainloop()
    return result["p1"], result["p2"]


# 게임 실행 예시입니다.
if __name__ == "__main__":
    card_data.load_card_databases('card_database/3_parsed_database/card_database_parsed.json')
    p1_deck, p2_deck = select_decks_gui()
    game = Game("player1", "player2", p1_deck, p2_deck)
    current_player = "player1"
    opponent_id = game.opponent_id[current_player]

    for turn_num in range(1, 21):  # 20턴까지 진행하는 예시입니다.

        while True:
            # '선택 대기' 상태이면 선택부터 처리합니다.
            game.process_player_choice()

            # 게임 상태를 출력합니다.
            current_pp, max_pp, player_field_card_ids, opponent_field_card_ids = game.get_start_turn_ifo(current_player)

            # 플레이어 행동을 선택합니다.
            choices = {
                "패에서 카드 내기": 0,
                "필드 조작 (추종자 공격/진화/초진화, 마법진 활성화)": 1,
                "턴 종료": 2
            }
            choice = int(game.gui.get_user_choice("--- 행동 선택 ---", choices))

            # 선택된 행동을 처리합니다.
            if choice == 0:  # 패에서 카드를 내는 경우입니다.
                # 엑스트라 PP를 사용할지 여부를 확인합니다.
                use_extra_pp = False
                if game.has_extra_pp(current_player):
                    extra_pp_choices = {"사용": 0, "미사용": 1}
                    use_extra_pp = int(game.gui.get_user_choice("엑스트라 PP를 사용하시겠습니까?", extra_pp_choices)) == 0

                # 사용 가능한 카드가 존재하는지 확인합니다.
                hand_cards_id, is_validate = game.get_playable_cards_id(current_player, use_extra_pp)
                if not hand_cards_id or not any(is_validate):
                    game.gui.get_user_choice("패에 사용 가능한 카드가 없습니다.", {"확인": None})
                    continue
                playable_cards_id = [card_id for i, card_id in enumerate(hand_cards_id) if is_validate[i]]

                # 증강(Enhance) 코스트를 지불할 수 있는지 확인합니다.
                enhanced_costs = []
                for i, card_id in enumerate(hand_cards_id):
                    if is_validate[i]:
                        card_name, card_type, card_cost = game.game_state_manager.get_card_info_hand(card_id)
                        enhance_effects = [effect for effect in game.game_state_manager.get_card_effects(card_id, EffectType.ENHANCE)]
                        enhance_costs_for_card = [effect.enhance_cost for effect in enhance_effects if effect.enhance_cost <= current_pp + (1 if use_extra_pp else 0)]
                        if enhance_costs_for_card:
                            enhanced_costs.append(max(enhance_costs_for_card))
                        else:
                            enhanced_costs.append(0)  # 기본 코스트를 사용합니다(증강되지 않음).

                # 사용할 카드를 선택합니다.
                card_choices = {f"{game.game_state_manager.get_card_name(card_id)} (ID - {card_id})": card_id for card_id in playable_cards_id}
                card_choices["뒤로 가기"] = None
                selected_card_id = str(game.gui.get_user_choice("--- 현재 플레이어의 패 ---", card_choices))

                if selected_card_id == "None":
                    print("다시 선택해주세요.")
                    continue
                
                enhanced_cost = enhanced_costs[playable_cards_id.index(selected_card_id)]
                game.play_card(current_player, selected_card_id, enhanced_cost, use_extra_pp)

            elif choice == 1:  # 필드를 조작하는 경우입니다.
                if not player_field_card_ids:
                    game.gui.get_user_choice("필드에 조작할 추종자/마법진이 없습니다.", {"확인": None})
                    continue

                # 필드에 존재하는 카드들을 보여줍니다.
                card_choices = {f"{game.game_state_manager.get_card_name(card_id)} (ID - {card_id})": card_id for card_id in player_field_card_ids}
                card_choices["뒤로 가기"] = None
                selected_card_id = str(game.gui.get_user_choice("--- 조작할 카드 선택 ---", card_choices))

                if selected_card_id == "None":
                    print("다시 선택해주세요.")
                    continue

                # 선택한 카드로 수행 가능한 조작 목록을 생성합니다.
                available_actions, card_name = game.get_available_actions(selected_card_id, current_player)
                if not available_actions:
                    game.gui.get_user_choice("선택한 카드로는 현재 할 수 있는 행동이 없습니다.", {"확인": None})
                    continue

                # 가능한 조작 목록을 보여줍니다.
                action_choices = {action: action for action in available_actions}
                action_choices["취소"] = None
                chosen_action = str(game.gui.get_user_choice(f"[{card_name}]으로 할 행동 선택 ---", action_choices))

                if chosen_action == "None":
                    print("다시 선택해주세요.")
                    continue

                # 선택한 조작을 실행합니다.
                if chosen_action == "추종자 공격":
                    print("\n--- 공격 대상 선택 ---")
                    opponent_targets_id = [card_id for card_id in opponent_field_card_ids if game.game_state_manager.get_type(card_id) == CardType.FOLLOWER] + [opponent_id]
                    possible_targets_id = [target_id for target_id in opponent_targets_id if game.rule_engine.validate_attack(selected_card_id, target_id)]
                    if not possible_targets_id:
                        game.gui.get_user_choice("공격할 수 있는 대상이 없습니다.", {"확인": None})
                        continue

                    # 공격 대상 목록을 보여줍니다.
                    target_choices = {f"{game.game_state_manager.get_card_name(target_id)} (ID - {target_id})": target_id for target_id in possible_targets_id}
                    target_choices["취소"] = None
                    selected_target_id = str(game.gui.get_user_choice("--- 공격 대상 선택 ---", target_choices))

                    if selected_target_id is None:
                        print("다시 선택해주세요.")
                        continue

                    # 공격을 처리합니다.
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

                elif chosen_action == "카드 활성화(Engage)":
                    game.engage_card(selected_card_id, current_player)
                    game.gui.get_user_choice(f"[{game.game_state_manager.get_card_name(selected_card_id)}]을(를) 활성화했습니다!", {"확인": None})

            elif choice == 2:  # 턴을 종료하는 경우입니다.
                game.gui.get_user_choice(f"{current_player} 턴 종료.", {"확인": None})
                game.end_turn(current_player)
                break  # 턴 종료 후 다음 플레이어로 넘어갑니다.
            else:
                game.gui.get_user_choice("유효하지 않은 선택입니다. 다시 선택해주세요.", {"확인": None})

        # 턴 플레이어를 전환합니다.
        current_player = game.opponent_id[current_player]
        opponent_id = game.opponent_id[current_player]

    game.gui.get_user_choice("--- 게임 종료 예시 ---", {"확인": None})