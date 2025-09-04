

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import pandas as pd
import copy

class CardEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Card Effect Manual Editor")
        self.root.geometry("1200x850") # Adjusted height for new buttons

        # File Paths
        self.source_file = '_card_database_parsed.json'
        self.output_file = '_card_database_manual.json'
        self.set_id = None # Will be set by switch_dataset

        # Setup card pack selection buttons first
        self.setup_set_selection_buttons()

        # Main Paned Window
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Data
        self.card_data = {}
        self.parsed_card_data = {} # To store original parsed data
        self.df = pd.DataFrame()

        # Left Pane: Card List
        self.left_pane = ttk.Frame(self.paned_window, width=600)
        self.paned_window.add(self.left_pane, weight=2)
        self.setup_left_pane()

        # Right Pane: Editor
        self.right_pane = ttk.Frame(self.paned_window, width=600)
        self.paned_window.add(self.right_pane, weight=3)
        self.setup_right_pane()
        
        # Initial data load
        self.switch_dataset('100')

    def setup_set_selection_buttons(self):
        set_frame = ttk.LabelFrame(self.root, text="Select Card Pack")
        set_frame.pack(fill=tk.X, padx=10, pady=5)

        packs = {
            "BASIC": "100",
            "LEGENDS RISE": "101",
            "INFINITY EVOLVED": "102",
            "TOKEN": "900"
        }

        for name, pack_id in packs.items():
            btn = ttk.Button(set_frame, text=f"{name} ({pack_id})", 
                             command=lambda p=pack_id: self.switch_dataset(p))
            btn.pack(side=tk.LEFT, padx=5, pady=5)

    def switch_dataset(self, set_id):
        if self.set_id == set_id:
            return # Don't reload if it's the same set

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
        # Frame for Treeview and Scrollbar
        tree_frame = ttk.Frame(self.left_pane)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for displaying cards
        cols = ("Card Name", "Class", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_card_select)

        # Status Label
        self.status_label = ttk.Label(self.left_pane, text="", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

    def setup_right_pane(self):
        # Frame for raw_effects_text
        raw_text_frame = ttk.LabelFrame(self.right_pane, text="Raw Effect Text")
        raw_text_frame.pack(fill=tk.X, padx=10, pady=5)
        self.raw_effects_label = ttk.Label(raw_text_frame, text="", wraplength=550, justify=tk.LEFT)
        self.raw_effects_label.pack(padx=5, pady=5)

        # Frame for auto-parsed effects
        parsed_effects_frame = ttk.LabelFrame(self.right_pane, text="Auto-parsed Effects (Read-only)")
        parsed_effects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.parsed_effects_text = scrolledtext.ScrolledText(parsed_effects_frame, wrap=tk.WORD, height=5, width=70)
        self.parsed_effects_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.parsed_effects_text.config(state=tk.DISABLED)

        # Frame for editable effects
        effects_frame = ttk.LabelFrame(self.right_pane, text="Effects (Edit JSON here)")
        effects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.effects_text = scrolledtext.ScrolledText(effects_frame, wrap=tk.WORD, height=10, width=70)
        self.effects_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for required listeners
        listeners_frame = ttk.LabelFrame(self.right_pane, text="Required Listeners (Edit JSON here)")
        listeners_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.listeners_text = scrolledtext.ScrolledText(listeners_frame, wrap=tk.WORD, height=5, width=70)
        self.listeners_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for controls
        control_frame = ttk.Frame(self.right_pane)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        self.status_var = tk.BooleanVar()
        self.status_check = ttk.Checkbutton(control_frame, text="Mark as Complete", variable=self.status_var, command=self.update_status)
        self.status_check.pack(side=tk.LEFT, padx=10)

        self.save_button = ttk.Button(control_frame, text="Save Changes", command=self.save_card_data)
        self.save_button.pack(side=tk.RIGHT, padx=10)

    def load_data(self):
        try:
            with open(self.set_id + self.source_file, 'r', encoding='utf-8') as f:
                self.parsed_card_data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"{self.set_id + self.source_file} not found.")
            self.parsed_card_data = {}
            self.card_data = {}
            return

        try:
            with open(self.set_id + self.output_file, 'r', encoding='utf-8') as f:
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
            records.append({
                'card_id': card_id,
                'Card Name': card_info.get('name', card_id),
                'Class': card_info.get('class_type', 'N/A'),
                'Status': card_info.get('_manual_review_status', 'Pending')
            })
        return pd.DataFrame(records)

    def populate_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if not self.df.empty:
            for index, row in self.df.iterrows():
                status = row['Status']
                tag = 'completed' if status == 'Completed' else 'pending'
                self.tree.insert("", "end", iid=index, values=(row["Card Name"], row["Class"], status), tags=(tag,))
            
            self.tree.tag_configure('completed', background='lightgreen')
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

        # Update right pane
        self.raw_effects_label.config(text=card_info_manual.get('raw_effects_text', ''))
        
        # Display parsed effects (read-only)
        parsed_effects_json = json.dumps(card_info_parsed.get('effects', []), indent=4, ensure_ascii=False)
        self.parsed_effects_text.config(state=tk.NORMAL)
        self.parsed_effects_text.delete('1.0', tk.END)
        self.parsed_effects_text.insert('1.0', parsed_effects_json)
        self.parsed_effects_text.config(state=tk.DISABLED)

        # Display editable effects
        effects_json = json.dumps(card_info_manual.get('effects', []), indent=4, ensure_ascii=False)
        self.effects_text.delete('1.0', tk.END)
        self.effects_text.insert('1.0', effects_json)

        listeners_json = json.dumps(card_info_manual.get('required_listeners', []), indent=4, ensure_ascii=False)
        self.listeners_text.delete('1.0', tk.END)
        self.listeners_text.insert('1.0', listeners_json)

        # Update checkbox
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

        # Validate and get edited effects
        try:
            edited_effects = json.loads(self.effects_text.get('1.0', tk.END))
            if not isinstance(edited_effects, list):
                raise ValueError("Effects must be a JSON list.")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Error", f"Invalid JSON format in Effects: {e}")
            return

        # Validate and get edited listeners
        try:
            edited_listeners = json.loads(self.listeners_text.get('1.0', tk.END))
            if not isinstance(edited_listeners, list):
                raise ValueError("Required Listeners must be a JSON list.")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Error", f"Invalid JSON format in Required Listeners: {e}")
            return

        # Update in-memory data
        self.card_data[card_id]['effects'] = edited_effects
        self.card_data[card_id]['required_listeners'] = edited_listeners
        
        # Save the entire database to the output file
        try:
            output_path = f"../../card_database/manual_database/{self.set_id}{self.output_file}"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.card_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"Changes for '{card_record['Card Name']}' saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def update_status(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_var.set(not self.status_var.get()) # Revert checkbox
            messagebox.showwarning("Warning", "Please select a card to update its status.")
            return

        selected_index = int(selected_items[0])
        
        new_status = "Completed" if self.status_var.get() else "Pending"
        
        # Update DataFrame
        self.df.loc[selected_index, 'Status'] = new_status
        
        # Update Treeview
        self.tree.item(selected_items[0], values=(self.df.loc[selected_index, "Card Name"], self.df.loc[selected_index, "Class"], new_status))
        self.tree.tag_configure('completed', background='lightgreen')
        self.tree.item(selected_items[0], tags=('completed' if new_status == 'Completed' else 'pending',))

        # Update main data object
        card_record = self.df.loc[selected_index]
        card_id = card_record['card_id']
        self.card_data[card_id]['_manual_review_status'] = new_status

        self.update_status_label()

    def update_status_label(self):
        total_cards = len(self.df)
        completed_cards = len(self.df[self.df['Status'] == 'Completed'])
        self.status_label.config(text=f"Progress: {completed_cards} / {total_cards} cards completed.")


if __name__ == "__main__":
    # Check if pandas is installed
    try:
        import pandas as pd
    except ImportError:
        print("Pandas is not installed. Please install it using: pip install pandas")
        exit()
        
    root = tk.Tk()
    app = CardEditorApp(root)
    root.mainloop()

tk.Tk()
    app = CardEditorApp(root)
    root.mainloop()

