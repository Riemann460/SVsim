# 역할 정의. 카드 데이터베이스를 편리하게 수동 검토하고 편집할 수 있도록 지원하는 Tkinter UI 기반 수동 에디터 애플리케이션입니다.

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import pandas as pd
import copy

def is_fully_parsed(card_info: dict) -> bool:
    """자동 파싱 성공 여부를 확인합니다."""
    effects = card_info.get('effects', [])
    if not effects:
        return True
    for effect in effects:
        if not isinstance(effect, dict):
            continue
        if 'raw_effect_text' in effect or 'raw_action_text' in effect:
            return False
    return True


class CardEditorApp:
    """카드 데이터의 효과 JSON 및 리스너 정보를 시각적으로 편집하기 위한 에디터 앱 클래스입니다."""
    def __init__(self, root):
        self.root = root
        self.root.title("Card Effect Manual Editor")
        self.root.geometry("1200x850")  # 새로운 버튼들을 배치하기 위해 높이를 조절합니다.

        # 파일 경로들을 정의합니다.
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.parsed_dir = os.path.normpath(os.path.join(script_dir, "../../card_database/3_parsed_database"))
        self.manual_dir = os.path.normpath(os.path.join(script_dir, "../../card_database/4_manual_database"))
        
        self.source_file = '_card_database_parsed.json'
        self.output_file = '_card_database_manual.json'
        self.set_id = None  # switch_dataset 메서드에 의해 세트 ID가 결정됩니다.

        # 카드팩 선택 버튼들을 먼저 구성합니다.
        self.setup_set_selection_buttons()

        # 메인 분할창(PanedWindow)을 생성합니다.
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 관리할 데이터 구조입니다.
        self.card_data = {}
        self.parsed_card_data = {}  # 원본 파싱 데이터를 보관합니다.
        self.df = pd.DataFrame()

        # 왼쪽 패널 - 카드 목록 영역.
        self.left_pane = ttk.Frame(self.paned_window, width=600)
        self.paned_window.add(self.left_pane, weight=2)
        self.setup_left_pane()

        # 오른쪽 패널 - 에디터 영역.
        self.right_pane = ttk.Frame(self.paned_window, width=600)
        self.paned_window.add(self.right_pane, weight=3)
        self.setup_right_pane()
        
        # 초기 데이터를 로드합니다.
        self.switch_dataset('100')

    def setup_set_selection_buttons(self):
        set_frame = ttk.LabelFrame(self.root, text="Select Card Pack")
        set_frame.pack(fill=tk.X, padx=10, pady=5)

        packs = {
            "BASIC": "100",
            "LEGENDS RISE": "101",
            "INFINITY EVOLVED": "102",
            "HEIRS OF THE OMEN": "103",
            "SKYBOUND DRAGONS": "104",
            "BLOSSOMING FATE": "105",
            "APOCALYPSE PACT": "106",
            "ANATHEMA'S GAMBIT": "107",
            "TOKEN": "900"
        }

        for name, pack_id in packs.items():
            btn = ttk.Button(set_frame, text=f"{name} ({pack_id})", 
                             command=lambda p=pack_id: self.switch_dataset(p))
            btn.pack(side=tk.LEFT, padx=5, pady=5)

    def switch_dataset(self, set_id):
        if self.set_id == set_id:
            return  # 동일한 세트인 경우 다시 로드하지 않습니다.

        self.set_id = set_id
        self.root.title(f"Card Effect Manual Editor - Set {self.set_id}")

        self.clear_editor_panes()
        self.load_data()
        self.df = self.create_dataframe()
        self.populate_treeview()

    def clear_editor_panes(self):
        self.raw_effects_label.config(text="")
        
        self.parsed_effects_text.config(state=tk.NORMAL)
        self.parsed_effects_text.delete('1.0', tk.END)
        self.parsed_effects_text.config(state=tk.DISABLED)

        self.effects_text.delete('1.0', tk.END)
        self.listeners_text.delete('1.0', tk.END)
        self.status_var.set(False)

    def setup_left_pane(self):
        # Treeview와 Scrollbar를 담을 프레임입니다.
        tree_frame = ttk.Frame(self.left_pane)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # 카드를 보여주기 위한 Treeview입니다.
        cols = ("Card Name", "Class", "Parsing", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        # 스크롤바입니다.
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_card_select)

        # 상태 표시 레이블입니다.
        self.status_label = ttk.Label(self.left_pane, text="", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

    def setup_right_pane(self):
        # raw_effects_text를 표시할 프레임입니다.
        raw_text_frame = ttk.LabelFrame(self.right_pane, text="Raw Effect Text")
        raw_text_frame.pack(fill=tk.X, padx=10, pady=5)
        self.raw_effects_label = ttk.Label(raw_text_frame, text="", wraplength=550, justify=tk.LEFT)
        self.raw_effects_label.pack(padx=5, pady=5)

        # 자동 파싱된 효과를 표시할 프레임입니다.
        parsed_effects_frame = ttk.LabelFrame(self.right_pane, text="Auto-parsed Effects (Read-only)")
        parsed_effects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.parsed_effects_text = scrolledtext.ScrolledText(parsed_effects_frame, wrap=tk.WORD, height=5, width=70)
        self.parsed_effects_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.parsed_effects_text.config(state=tk.DISABLED)

        # 직접 편집 가능한 효과를 정의할 프레임입니다.
        effects_frame = ttk.LabelFrame(self.right_pane, text="Effects (Edit JSON here)")
        effects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.effects_text = scrolledtext.ScrolledText(effects_frame, wrap=tk.WORD, height=10, width=70)
        self.effects_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 필요한 이벤트 리스너를 정의할 프레임입니다.
        listeners_frame = ttk.LabelFrame(self.right_pane, text="Required Listeners (Edit JSON here)")
        listeners_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.listeners_text = scrolledtext.ScrolledText(listeners_frame, wrap=tk.WORD, height=5, width=70)
        self.listeners_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 제어용 컨트롤 프레임입니다.
        control_frame = ttk.Frame(self.right_pane)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        self.status_var = tk.BooleanVar()
        self.status_check = ttk.Checkbutton(control_frame, text="Mark as Complete", variable=self.status_var, command=self.update_status)
        self.status_check.pack(side=tk.LEFT, padx=10)

        self.save_button = ttk.Button(control_frame, text="Save Changes", command=self.save_card_data)
        self.save_button.pack(side=tk.RIGHT, padx=10)

    def load_data(self):
        import os
        parsed_path = os.path.join(self.parsed_dir, f"{self.set_id}{self.source_file}")
        try:
            with open(parsed_path, 'r', encoding='utf-8') as f:
                self.parsed_card_data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"{parsed_path} 파일을 찾을 수 없습니다.")
            self.parsed_card_data = {}
            self.card_data = {}
            return

        manual_path = os.path.join(self.manual_dir, f"{self.set_id}{self.output_file}")
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                manual_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            manual_data = {}

        db_content = copy.deepcopy(self.parsed_card_data)

        for card_id, card_info in manual_data.items():
            if card_id in db_content:
                if 'effects' in card_info:
                    db_content[card_id]['effects'] = card_info['effects']
                if 'required_listeners' in card_info:
                    db_content[card_id]['required_listeners'] = card_info['required_listeners']
                if '_manual_review_status' in card_info:
                    db_content[card_id]['_manual_review_status'] = card_info['_manual_review_status']

        self.card_data = db_content

    def create_dataframe(self):
        if not self.card_data:
            return pd.DataFrame()
        records = []
        for card_id, card_info in self.card_data.items():
            fully_parsed = is_fully_parsed(card_info)
            records.append({
                'card_id': card_id,
                'Card Name': card_info.get('name', card_id),
                'Class': card_info.get('class_type', 'N/A'),
                'Parsing': 'Parsed' if fully_parsed else 'Raw Text',
                'Status': card_info.get('_manual_review_status', 'Pending')
            })
        return pd.DataFrame(records)

    def populate_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if not self.df.empty:
            for index, row in self.df.iterrows():
                status = row['Status']
                parsing = row['Parsing']
                
                if status == 'Completed':
                    tag = 'completed'
                elif parsing == 'Parsed':
                    tag = 'auto_parsed'
                else:
                    tag = 'raw_text'
                self.tree.insert("", "end", iid=index, values=(row["Card Name"], row["Class"], parsing, status), tags=(tag,))
            
            self.tree.tag_configure('completed', background='#d4edda')
            self.tree.tag_configure('auto_parsed', background='#d1ecf1')
            self.tree.tag_configure('raw_text', background='#f8d7da')
        self.update_status_label()

    def on_card_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        selected_index = int(selected_items[0])
        card_record = self.df.loc[selected_index]
        card_id = card_record['card_id']
        
        card_info_manual = self.card_data[card_id]
        card_info_parsed = self.parsed_card_data.get(card_id, {})

        # 오른쪽 패널 정보를 업데이트합니다.
        self.raw_effects_label.config(text=card_info_manual.get('raw_effects_text', ''))
        
        # 파싱된 효과 목록을 보여줍니다 (읽기 전용).
        parsed_effects_json = json.dumps(card_info_parsed.get('effects', []), indent=4, ensure_ascii=False)
        self.parsed_effects_text.config(state=tk.NORMAL)
        self.parsed_effects_text.delete('1.0', tk.END)
        self.parsed_effects_text.insert('1.0', parsed_effects_json)
        self.parsed_effects_text.config(state=tk.DISABLED)

        # 편집 가능한 효과 목록을 보여줍니다.
        effects_json = json.dumps(card_info_manual.get('effects', []), indent=4, ensure_ascii=False)
        self.effects_text.delete('1.0', tk.END)
        self.effects_text.insert('1.0', effects_json)

        listeners_json = json.dumps(card_info_manual.get('required_listeners', []), indent=4, ensure_ascii=False)
        self.listeners_text.delete('1.0', tk.END)
        self.listeners_text.insert('1.0', listeners_json)

        # 체크박스 상태를 업데이트합니다.
        status = card_info_manual.get('_manual_review_status', 'Pending')
        self.status_var.set(status == 'Completed')

    def save_card_data(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a card to save.")
            return

        selected_index = int(selected_items[0])
        card_record = self.df.loc[selected_index]
        card_id = card_record['card_id']

        # 편집된 효과 JSON의 유효성을 검증합니다.
        try:
            edited_effects = json.loads(self.effects_text.get('1.0', tk.END))
            if not isinstance(edited_effects, list):
                raise ValueError("Effects must be a JSON list.")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Error", f"Invalid JSON format in Effects - {e}")
            return

        # 편집된 리스너 JSON의 유효성을 검증합니다.
        try:
            edited_listeners = json.loads(self.listeners_text.get('1.0', tk.END))
            if not isinstance(edited_listeners, list):
                raise ValueError("Required Listeners must be a JSON list.")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Error", f"Invalid JSON format in Required Listeners - {e}")
            return

        # 메모리 내 데이터를 업데이트합니다.
        self.card_data[card_id]['effects'] = edited_effects
        self.card_data[card_id]['required_listeners'] = edited_listeners
        
        # 전체 데이터베이스를 파일에 저장합니다.
        try:
            import os
            output_path = os.path.join(self.manual_dir, f"{self.set_id}{self.output_file}")
            os.makedirs(self.manual_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.card_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"Changes for '{card_record['Card Name']}' saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file - {e}")

    def update_status(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_var.set(not self.status_var.get())  # 체크박스 상태를 복구합니다.
            messagebox.showwarning("Warning", "Please select a card to update its status.")
            return

        selected_index = int(selected_items[0])
        
        new_status = "Completed" if self.status_var.get() else "Pending"
        
        # DataFrame을 업데이트합니다.
        self.df.loc[selected_index, 'Status'] = new_status
        
        # Treeview를 업데이트합니다.
        parsing = self.df.loc[selected_index, 'Parsing']
        self.tree.item(selected_items[0], values=(self.df.loc[selected_index, "Card Name"], self.df.loc[selected_index, "Class"], parsing, new_status))
        
        if new_status == 'Completed':
            tag = 'completed'
        elif parsing == 'Parsed':
            tag = 'auto_parsed'
        else:
            tag = 'raw_text'
        self.tree.item(selected_items[0], tags=(tag,))

        # 메인 데이터 객체를 업데이트합니다.
        card_record = self.df.loc[selected_index]
        card_id = card_record['card_id']
        self.card_data[card_id]['_manual_review_status'] = new_status

        self.update_status_label()

    def update_status_label(self):
        total_cards = len(self.df)
        completed_cards = len(self.df[self.df['Status'] == 'Completed'])
        raw_cards = len(self.df[(self.df['Status'] != 'Completed') & (self.df['Parsing'] == 'Raw Text')])
        auto_parsed_cards = len(self.df[(self.df['Status'] != 'Completed') & (self.df['Parsing'] == 'Parsed')])
        
        self.status_label.config(text=f"Total: {total_cards} | Completed: {completed_cards} | Needs Review (Raw): {raw_cards} | Auto-Parsed: {auto_parsed_cards}")


if __name__ == "__main__":
    # pandas 라이브러리가 설치되어 있는지 확인합니다.
    try:
        import pandas as pd
    except ImportError:
        print("Pandas is not installed. Please install it using: pip install pandas")
        exit()
        
    root = tk.Tk()
    app = CardEditorApp(root)
    root.mainloop()
