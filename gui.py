import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_state_manager import GameStateManager
    from card import Card
    from enums import CardType

class GameGUI:
    def __init__(self, game_state_manager: 'GameStateManager'):
        """GameGUI 클래스의 생성자입니다."""
        self.root = tk.Tk()
        self.root.title("Shadowverse Game Viewer")
        self.root.geometry("1200x800")
        self.game_state_manager = game_state_manager

        # Main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill="both", expand=True)

        # Player frames
        self.player_frames = {}
        # Player 2 (Opponent) at the top
        self.player_frames['player2'] = ttk.Frame(main_frame, relief="sunken", borderwidth=2)
        self.player_frames['player2'].pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        # Turn info in the middle
        self.turn_label = ttk.Label(main_frame, text="Turn Info", anchor="center", font=("Helvetica", 14, "bold"))
        self.turn_label.pack(side="top", fill="x", pady=10)

        # Choice frame for user interactions
        self.choice_frame = ttk.Frame(main_frame, relief="groove", borderwidth=2, padding="5")
        self.choice_frame.pack(side="top", fill="x", pady=5)
        self.choice_frame.pack_forget() # Hide initially

        self.choice_label = ttk.Label(self.choice_frame, text="", font=("Helvetica", 12))
        self.choice_label.pack(pady=5)

        self.choice_buttons_frame = ttk.Frame(self.choice_frame)
        self.choice_buttons_frame.pack(pady=5)

        # Player 1 (Current) at the bottom
        self.player_frames['player1'] = ttk.Frame(main_frame, relief="sunken", borderwidth=2)
        self.player_frames['player1'].pack(side="bottom", fill="both", expand=True, padx=5, pady=5)

        # Create UI elements for each player
        self.stat_labels = {}
        self.field_frames = {}
        self.hand_frames = {}

        for player_id, frame in self.player_frames.items():
            # Container for stats and hand
            left_container = ttk.Frame(frame)
            left_container.pack(side="left", fill="y", padx=10, pady=10)

            # Stats
            stats_container = ttk.LabelFrame(left_container, text=f"{player_id} Stats", padding="5")
            stats_container.pack(side="top", fill="x", pady=5)
            self.stat_labels[player_id] = ttk.Label(stats_container, text="Stats", justify="left")
            self.stat_labels[player_id].pack()

            # Hand
            hand_container = ttk.LabelFrame(left_container, text="Hand", padding="5")
            hand_container.pack(side="bottom", fill="both", expand=True, pady=5)
            self.hand_frames[player_id] = hand_container

            # Field
            field_container = ttk.LabelFrame(frame, text="Field", padding="10")
            field_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)
            self.field_frames[player_id] = field_container

        self.update()

    def update(self):
        """GUI의 모든 위젯을 최신 게임 상태로 업데이트합니다."""
        self._update_widgets()
        self.root.update()

    def _update_widgets(self):
        """내부 위젯들을 업데이트하는 헬퍼 메서드입니다."""
        # Update turn info
        current_player = self.game_state_manager.current_turn_player_id
        turn_num = self.game_state_manager.turn_number
        self.turn_label.config(text=f"Turn: {turn_num} - Current Player: {current_player}")

        # Update player info
        for player_id, player in self.game_state_manager.players.items():
            # Update stats
            stats_text = (
                f"HP: {player.current_defense}/{player.max_defense}\n"
                f"PP: {player.current_pp}/{player.max_pp}\n"
                f"EP: {player.current_ep}/{player.max_ep}\n"
                f"SEP: {player.current_sep}/{player.max_sep}\n"
                f"Deck: {player.deck.size()}\n"
                f"Grave: {player.graveyard.size()}"
            )
            self.stat_labels[player_id].config(text=stats_text)

            # Update field
            self._update_zone_frame(self.field_frames[player_id], player.field.get_cards(), is_field=True)

            # Update hand
            self._update_zone_frame(self.hand_frames[player_id], player.hand.get_cards(), is_field=False)

        self.root.update_idletasks()

    def _update_zone_frame(self, frame, cards: list['Card'], is_field: bool):
        """특정 영역(패 또는 필드)의 카드 표시를 업데이트합니다."""
        from enums import CardType
        for widget in frame.winfo_children():
            widget.destroy()

        for card in cards:
            card_frame = ttk.Frame(frame, borderwidth=2, relief="solid", padding=5)
            card_frame.pack(side="left", padx=5, pady=5, anchor="n")

            name_color = "black"
            if card.is_super_evolved:
                name_color = "purple"
            elif card.is_evolved:
                name_color = "blue"

            name_label = ttk.Label(card_frame, text=f"{card.get_display_name()} (ID: {card.card_id})", font=("Helvetica", 10, "bold"), foreground=name_color)
            name_label.pack()

            cost_label = ttk.Label(card_frame, text=f"Cost: {card.current_cost}")
            cost_label.pack()

            if card.get_type() == CardType.FOLLOWER:
                stats_label = ttk.Label(card_frame, text=f"{card.current_attack} / {card.current_defense}")
                stats_label.pack()
                if is_field and not card.can_attack(CardType.LEADER) and not card.can_attack(CardType.FOLLOWER):
                     stats_label.config(foreground="red")
            
            if card.get_type() == CardType.AMULET and card.countdown_value is not None:
                countdown_label = ttk.Label(card_frame, text=f"Countdown: {card.countdown_value}")
                countdown_label.pack()

            keywords = [eff.type.value for eff in card.effects]
            if keywords:
                keyword_label = ttk.Label(card_frame, text=", ".join(keywords)[:12], wraplength=100)
                keyword_label.pack()

    def get_mulligan_choices(self, player_id: str, hand_cards: list['Card']) -> list[str]:
        """플레이어에게 멀리건 선택 창을 표시하고 선택된 카드 ID 리스트를 반환합니다."""
        self.mulligan_selected_card_ids = []
        self.mulligan_vars = {}

        # Create a new top-level window for mulligan
        self.mulligan_window = tk.Toplevel(self.root)
        self.mulligan_window.title(f"{player_id}의 멀리건 선택")
        self.mulligan_window.transient(self.root)  # Make it a transient window
        self.mulligan_window.grab_set()  # Make it modal

        prompt_label = ttk.Label(self.mulligan_window, text="멀리건할 카드를 선택하세요 (체크된 카드가 교체됩니다):", font=("Helvetica", 12))
        prompt_label.pack(pady=10)

        cards_frame = ttk.Frame(self.mulligan_window)
        cards_frame.pack(pady=10)

        for card in hand_cards:
            var = tk.BooleanVar()
            self.mulligan_vars[card.card_id] = var
            card_text = f"{card.get_display_name()} (ID: {card.card_id}) (코스트: {card.current_cost})";
            chk = ttk.Checkbutton(cards_frame, text=card_text, variable=var)
            chk.pack(anchor="w", padx=5, pady=2)

        confirm_button = ttk.Button(self.mulligan_window, text="멀리건 확인", command=self._confirm_mulligan_choices)
        confirm_button.pack(pady=10)

        self.root.wait_window(self.mulligan_window)  # Block until the window is closed
        return self.mulligan_selected_card_ids

    def _confirm_mulligan_choices(self):
        """멀리건 선택을 확정하고 선택된 카드 ID를 저장합니다."""
        for card_id, var in self.mulligan_vars.items():
            if var.get():
                self.mulligan_selected_card_ids.append(card_id)
        self.mulligan_window.destroy()

    def get_user_choice(self, prompt: str, choices: dict[str, any]) -> any:
        """사용자에게 선택지를 제시하고 선택된 값을 반환합니다."""
        self.user_choice_var = tk.StringVar()
        self.choice_label.config(text=prompt)

        # Clear previous buttons
        for widget in self.choice_buttons_frame.winfo_children():
            widget.destroy()

        # Create new buttons
        for text, value in choices.items():
            button = ttk.Button(self.choice_buttons_frame, text=text, command=lambda v=value: self._set_user_choice(v))
            button.pack(side="left", padx=5)
        
        self.choice_frame.pack(side="top", fill="x", pady=5)  # Show the choice frame
        self.root.wait_variable(self.user_choice_var)  # Block until choice is made
        self.choice_frame.pack_forget()  # Hide after choice
        return self.user_choice_var.get()

    def _set_user_choice(self, choice):
        """사용자 선택 변수 값을 설정하고 대기를 종료합니다."""
        self.user_choice_var.set(choice)
