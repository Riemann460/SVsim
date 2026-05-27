# 역할 정의. 게임 내 덱을 구성하고 포맷 및 직업별 카드 필터링과 유효성 검사를 제공하는 독립형 GUI 프로그램입니다.

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

from src.common import card_data
from src.common.enums import ClassType, CardType

def filter_cards_by_rules(format_type, class_type, all_cards):
    """지정된 포맷 및 직업 규칙에 부합하는 카드를 필터링하여 반환합니다."""
    filtered = []
    allowed_packs = []
    
    if format_type == "Rotation":
        # 로테이션은 기본 팩인 100 팩과 최신 6개 팩인 102부터 107 팩을 허용합니다.
        allowed_packs = ["100", "102", "103", "104", "105", "106", "107"]
    elif format_type == "Unlimited":
        # 언리미티드는 100부터 107 팩까지의 모든 카드를 허용합니다.
        allowed_packs = ["100", "101", "102", "103", "104", "105", "106", "107"]

    for card in all_cards.values():
        card_id_str = str(card.card_id)
        pack_id = card_id_str[:3]
        
        # 900 팩 등의 토큰 카드는 덱 빌딩 목록에서 완전히 제외합니다.
        if pack_id == "900":
            continue
            
        if pack_id not in allowed_packs:
            continue
            
        # 선택한 직업에 해당하거나 중립인 카드만 노출합니다.
        if card.class_type == class_type or card.class_type == ClassType.NEUTRAL:
            filtered.append(card)
            
    # 마친가지로 코스트 순서대로 정렬하여 반환합니다.
    filtered.sort(key=lambda x: x.cost)
    return filtered

def validate_deck_rules(deck_cards):
    """현재 덱이 섀도우버스 표준 규칙인 40장 수량 및 동일 카드 최대 3장 제한을 충족하는지 검사합니다."""
    if not deck_cards:
        return False
    
    total_count = sum(deck_cards.values())
    if total_count != 40:
        return False
        
    for card_id, count in deck_cards.items():
        if count <= 0:
            return False
        if count > 3:
            return False
            
    return True


class DeckBuilderGUI:
    """Tkinter를 기반으로 한 덱 빌더 사용자 인터페이스 클래스입니다."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SVsim 덱 빌더")
        self.root.geometry("1000x700")
        
        # 데이터베이스 폴더를 안전하게 로드합니다.
        card_data.load_card_databases('card_database/3_parsed_database/card_database_parsed.json')
        self.all_cards = {**card_data.BASIC_CARD_DATABASE, **card_data.LEGENDS_RISE_CARD_DATABASE}
        
        # 덱에 추가된 카드들을 딕셔너리로 저장합니다.
        self.current_deck = {}
        
        # UI 스타일 구성을 초기화합니다.
        self._setup_style()
        self._create_widgets()
        self._update_card_list()
        
    def _setup_style(self):
        """다크 테마 및 컴포넌트 스타일을 선언합니다."""
        self.bg_dark = "#1e1e2e"
        self.bg_panel = "#313244"
        self.fg_light = "#cdd6f4"
        self.accent_blue = "#89b4fa"
        self.accent_green = "#a6e3a1"
        self.accent_red = "#f38ba8"
        
        self.root.configure(bg=self.bg_dark)
        
        # 스타일러를 구성합니다.
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 전반적인 다크 테마 설정을 프레임 등에 적용합니다.
        self.style.configure("TFrame", background=self.bg_dark)
        self.style.configure("TLabel", background=self.bg_dark, foreground=self.fg_light, font=("맑은 고딕", 10))
        self.style.configure("Header.TLabel", background=self.bg_dark, foreground=self.accent_blue, font=("맑은 고딕", 14, "bold"))
        self.style.configure("SubHeader.TLabel", background=self.bg_dark, foreground=self.fg_light, font=("맑은 고딕", 11, "bold"))
        
        # 콤보박스 색상을 오버라이드합니다.
        self.style.configure("TCombobox", fieldbackground=self.bg_panel, background=self.bg_dark, foreground=self.fg_light)
        
    def _create_widgets(self):
        """UI 구성 요소를 생성하여 배치합니다."""
        # 전체 레이아웃을 3분할 프레임으로 구성합니다.
        # 1. 상단 컨트롤 패널
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(top_frame, text="SVsim DECK BUILDER", style="Header.TLabel").pack(side=tk.LEFT, padx=5)
        
        # 포맷 필터
        ttk.Label(top_frame, text="포맷 ").pack(side=tk.LEFT, padx=10)
        self.format_var = tk.StringVar(value="Rotation")
        self.format_combo = ttk.Combobox(top_frame, textvariable=self.format_var, values=["Rotation", "Unlimited"], width=12, state="readonly")
        self.format_combo.pack(side=tk.LEFT, padx=5)
        self.format_combo.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())
        
        # 클래스 필터
        ttk.Label(top_frame, text="직업 ").pack(side=tk.LEFT, padx=10)
        self.class_var = tk.StringVar(value="FORESTCRAFT")
        class_list = [c.name for c in ClassType if c != ClassType.NEUTRAL]
        self.class_combo = ttk.Combobox(top_frame, textvariable=self.class_var, values=class_list, width=15, state="readonly")
        self.class_combo.pack(side=tk.LEFT, padx=5)
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())
        
        # 검색 필터
        ttk.Label(top_frame, text="검색 ").pack(side=tk.LEFT, padx=15)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var, bg=self.bg_panel, fg=self.fg_light, insertbackground=self.fg_light, width=18, font=("맑은 고딕", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self._update_card_list())
        
        # 2. 메인 패널 (좌측 카드 목록, 우측 덱 상태 목록)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # 좌측 패널
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(left_panel, text="선택 가능한 카드 목록", style="SubHeader.TLabel").pack(anchor=tk.W, pady=5)
        
        # 카드 목록을 담을 스크롤 프레임을 캔버스로 작성합니다.
        self.card_canvas = tk.Canvas(left_panel, bg=self.bg_dark, highlightthickness=0)
        self.card_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.card_canvas.yview)
        self.card_scroll_frame = ttk.Frame(self.card_canvas)
        
        self.card_scroll_frame.bind(
            "<Configure>",
            lambda e: self.card_canvas.configure(scrollregion=self.card_canvas.bbox("all"))
        )
        
        self.card_canvas.create_window((0, 0), window=self.card_scroll_frame, anchor="nw")
        self.card_canvas.configure(yscrollcommand=self.card_scrollbar.set)
        
        self.card_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.card_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 우측 패널
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, width=320, padx=5)
        
        ttk.Label(right_panel, text="현재 덱 구성 상황", style="SubHeader.TLabel").pack(anchor=tk.W, pady=5)
        
        # 덱 목록 리스트 박스 영역입니다.
        self.deck_list_frame = ttk.Frame(right_panel)
        self.deck_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.deck_canvas = tk.Canvas(self.deck_list_frame, bg=self.bg_dark, highlightthickness=0)
        self.deck_scrollbar = ttk.Scrollbar(self.deck_list_frame, orient="vertical", command=self.deck_canvas.yview)
        self.deck_scroll_frame = ttk.Frame(self.deck_canvas)
        
        self.deck_scroll_frame.bind(
            "<Configure>",
            lambda e: self.deck_canvas.configure(scrollregion=self.deck_canvas.bbox("all"))
        )
        
        self.deck_canvas.create_window((0, 0), window=self.deck_scroll_frame, anchor="nw")
        self.deck_canvas.configure(yscrollcommand=self.deck_scrollbar.set)
        
        self.deck_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.deck_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 3. 하단 제어 패널
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(bottom_frame, text="덱 이름 ").pack(side=tk.LEFT, padx=5)
        self.deck_name_entry = tk.Entry(bottom_frame, bg=self.bg_panel, fg=self.fg_light, insertbackground=self.fg_light, width=20, font=("맑은 고딕", 10))
        self.deck_name_entry.pack(side=tk.LEFT, padx=5)
        self.deck_name_entry.insert(0, "MyDeck")
        
        self.count_label = ttk.Label(bottom_frame, text="총 매수: 0 / 40 장", font=("맑은 고딕", 11, "bold"))
        self.count_label.pack(side=tk.LEFT, padx=25)
        
        save_btn = tk.Button(bottom_frame, text="덱 저장", command=self._save_deck, bg=self.accent_blue, fg=self.bg_dark, font=("맑은 고딕", 10, "bold"), relief=tk.FLAT, padx=12, pady=5)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        load_btn = tk.Button(bottom_frame, text="덱 불러오기", command=self._load_deck_dialog, bg=self.bg_panel, fg=self.fg_light, font=("맑은 고딕", 10), relief=tk.FLAT, padx=10, pady=5)
        load_btn.pack(side=tk.RIGHT, padx=5)
        
    def _on_filter_changed(self):
        """필터 조건 변경 시 현재 덱을 비우고 카드 리스트를 갱신합니다."""
        self.current_deck.clear()
        self._update_card_list()
        self._update_deck_list()
        
    def _update_card_list(self):
        """조건에 맞춰 카드 목록을 화면에 다시 갱신합니다."""
        # 기존 위젯들을 파괴합니다.
        for widget in self.card_scroll_frame.winfo_children():
            widget.destroy()
            
        f_type = self.format_var.get()
        c_name = self.class_var.get()
        c_type = ClassType[c_name]
        
        # 비즈니스 필터 규칙을 사용하여 카드 풀을 걸러냅니다.
        cards = filter_cards_by_rules(f_type, c_type, self.all_cards)
        
        # 검색어로 2차 필터링을 수행합니다.
        search_query = self.search_var.get().strip().lower()
        if search_query:
            cards = [c for c in cards if search_query in c.name.lower() or search_query in c.name_ko.lower()]
            
        for idx, card in enumerate(cards):
            card_frame = tk.Frame(self.card_scroll_frame, bg=self.bg_panel, bd=1, relief=tk.RIDGE)
            card_frame.pack(fill=tk.X, padx=10, pady=4, ipadx=5, ipady=3)
            
            # 한글 이름 우선 노출합니다.
            display_name = card.name_ko if card.name_ko else card.name
            card_class = "중립" if card.class_type == ClassType.NEUTRAL else card.class_type.value
            
            info_text = f"[{card_class}]  {display_name}  (비용: {card.cost})"
            
            # 추종자 스탯 표시 처리입니다.
            if card.card_type == CardType.FOLLOWER:
                info_text += f"   [{card.attack}/{card.defense}]"
            else:
                card_type_ko = "마법진" if card.card_type == CardType.AMULET else "주문"
                info_text += f"   ({card_type_ko})"
                
            label = tk.Label(card_frame, text=info_text, bg=self.bg_panel, fg=self.fg_light, font=("맑은 고딕", 9), anchor="w")
            label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # 카드 추가 버튼입니다.
            add_button = tk.Button(
                card_frame,
                text="+",
                command=lambda cid=card.card_id: self._add_to_deck(cid),
                bg=self.bg_dark,
                fg=self.accent_blue,
                font=("맑은 고딕", 9, "bold"),
                relief=tk.FLAT,
                width=3
            )
            add_button.pack(side=tk.RIGHT, padx=5)
            
    def _add_to_deck(self, card_id):
        """현재 덱에 해당 카드 번호를 추가합니다."""
        current_count = self.current_deck.get(card_id, 0)
        total_in_deck = sum(self.current_deck.values())
        
        if total_in_deck >= 40:
            messagebox.showwarning("오류", "덱에 더 이상 카드를 추가할 수 없습니다. 최대 40장입니다.")
            return
            
        if current_count >= 3:
            messagebox.showwarning("오류", "동일한 카드는 덱에 최대 3장까지만 넣을 수 있습니다.")
            return
            
        self.current_deck[card_id] = current_count + 1
        self._update_deck_list()
        
    def _remove_from_deck(self, card_id):
        """현재 덱에서 카드를 한 장 제거합니다."""
        if card_id in self.current_deck:
            self.current_deck[card_id] -= 1
            if self.current_deck[card_id] <= 0:
                del self.current_deck[card_id]
        self._update_deck_list()
        
    def _update_deck_list(self):
        """덱 목록 화면을 새로 갱신합니다."""
        for widget in self.deck_scroll_frame.winfo_children():
            widget.destroy()
            
        total_count = sum(self.current_deck.values())
        self.count_label.config(text=f"총 매수: {total_count} / 40 장")
        if total_count == 40:
            self.count_label.config(foreground=self.accent_green)
        else:
            self.count_label.config(foreground=self.fg_light)
            
        # 덱에 포함된 카드들을 가져와 그리드 구성합니다.
        for card_id, count in sorted(self.current_deck.items(), key=lambda item: self.all_cards[item[0]].cost if item[0] in self.all_cards else 99):
            card = self.all_cards.get(card_id)
            if not card:
                continue
                
            item_frame = tk.Frame(self.deck_scroll_frame, bg=self.bg_panel, bd=1, relief=tk.FLAT)
            item_frame.pack(fill=tk.X, padx=5, pady=2, ipady=2)
            
            display_name = card.name_ko if card.name_ko else card.name
            desc = f"({card.cost}) {display_name}  x {count}"
            
            label = tk.Label(item_frame, text=desc, bg=self.bg_panel, fg=self.fg_light, font=("맑은 고딕", 9), anchor="w")
            label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            del_button = tk.Button(
                item_frame,
                text="-",
                command=lambda cid=card_id: self._remove_from_deck(cid),
                bg=self.bg_dark,
                fg=self.accent_red,
                font=("맑은 고딕", 8),
                relief=tk.FLAT,
                width=2
            )
            del_button.pack(side=tk.RIGHT, padx=5)
            
    def _save_deck(self):
        """현재 구성한 덱을 규칙 유효성 검사 후 JSON 파일로 저장합니다."""
        # 덱 상태의 정합성을 검증합니다.
        if not validate_deck_rules(self.current_deck):
            total_count = sum(self.current_deck.values())
            messagebox.showerror("저장 실패", f"덱은 반드시 40장이어야 저장이 가능합니다. 현재 {total_count}장입니다.")
            return
            
        deck_name = self.deck_name_entry.get().strip()
        if not deck_name:
            messagebox.showerror("저장 실패", "올바른 덱 이름을 입력해주세요.")
            return
            
        # decks 폴더를 생성합니다.
        os.makedirs("decks", exist_ok=True)
        file_path = os.path.join("decks", f"{deck_name}.json")
        
        # 덱 데이터를 구조화합니다.
        deck_data_to_save = {
            "deck_name": deck_name,
            "format": self.format_var.get(),
            "class_type": self.class_var.get(),
            "cards": [{"card_id": cid, "count": count} for cid, count in self.current_deck.items()]
        }
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(deck_data_to_save, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("저장 완료", f"덱 '{deck_name}'이(가) 성공적으로 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("저장 실패", f"파일 작성 중 에러가 발생하였습니다.\n{str(e)}")
            
    def _load_deck_dialog(self):
        """decks 디렉터리에서 저장된 덱 파일을 불러옵니다."""
        if not os.path.exists("decks"):
            messagebox.showinfo("정보", "저장된 덱 파일이 존재하지 않습니다.")
            return
            
        deck_files = [f for f in os.listdir("decks") if f.endswith(".json")]
        if not deck_files:
            messagebox.showinfo("정보", "저장된 덱 파일이 존재하지 않습니다.")
            return
            
        # 불러오기 전용 다이얼로그 창을 띄웁니다.
        load_win = tk.Toplevel(self.root)
        load_win.title("덱 불러오기")
        load_win.geometry("300x250")
        load_win.configure(bg=self.bg_dark)
        
        ttk.Label(load_win, text="불러올 덱을 선택하세요", font=("맑은 고딕", 10, "bold")).pack(pady=10)
        
        selected_file = tk.StringVar(value=deck_files[0])
        combo = ttk.Combobox(load_win, textvariable=selected_file, values=deck_files, state="readonly", width=25)
        combo.pack(pady=15)
        
        def do_load():
            filename = selected_file.get()
            filepath = os.path.join("decks", filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                self.format_var.set(data.get("format", "Rotation"))
                self.class_var.set(data.get("class_type", "FORESTCRAFT"))
                self.deck_name_entry.delete(0, tk.END)
                self.deck_name_entry.insert(0, data.get("deck_name", "LoadedDeck"))
                
                # 덱 딕셔너리를 복구합니다.
                self.current_deck.clear()
                for c_info in data.get("cards", []):
                    self.current_deck[c_info["card_id"]] = c_info["count"]
                    
                self._update_card_list()
                self._update_deck_list()
                load_win.destroy()
                messagebox.showinfo("로딩 성공", f"덱 '{filename}'을(를) 불러왔습니다.")
            except Exception as e:
                messagebox.showerror("로딩 실패", f"덱을 로드하는 중 에러가 발생하였습니다.\n{str(e)}")
                
        tk.Button(load_win, text="불러오기", command=do_load, bg=self.accent_blue, fg=self.bg_dark, font=("맑은 고딕", 9, "bold"), relief=tk.FLAT, padx=10, pady=3).pack(pady=10)


if __name__ == "__main__":
    main_root = tk.Tk()
    app = DeckBuilderGUI(main_root)
    main_root.mainloop()
