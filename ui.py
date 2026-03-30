"""
Simple Tkinter-based UI for F1-Deck configuration
"""

import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from config import ConfigManager

log = logging.getLogger("f1-deck.ui")


class ConfigUI:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.root = tk.Tk()
        self.root.title("F1-Deck Configuration")
        self.root.geometry("800x600")

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Profile:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            main_frame, textvariable=self.profile_var, state="readonly"
        )
        self.profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)

        ttk.Button(main_frame, text="New Profile", command=self.new_profile).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(main_frame, text="Delete", command=self.delete_profile).grid(
            row=0, column=3
        )

        ttk.Separator(main_frame, orient="horizontal").grid(
            row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10
        )

        ttk.Label(main_frame, text="Mappings:", font=("Arial", 11)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )

        ttk.Button(main_frame, text="Add Mapping", command=self.add_mapping).grid(
            row=2, column=1, sticky=tk.W, pady=5
        )

        mappings_frame = ttk.Frame(main_frame)
        mappings_frame.grid(
            row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        main_frame.rowconfigure(3, weight=1)

        columns = ("#", "Trigger", "Control", "Action Type", "Action Details")
        self.mappings_tree = ttk.Treeview(
            mappings_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.mappings_tree.heading(col, text=col)
            self.mappings_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(
            mappings_frame, orient="vertical", command=self.mappings_tree.yview
        )
        self.mappings_tree.configure(yscrollcommand=scrollbar.set)

        self.mappings_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        mappings_frame.columnconfigure(0, weight=1)
        mappings_frame.rowconfigure(0, weight=1)

        ttk.Button(main_frame, text="Edit Selected", command=self.edit_mapping).grid(
            row=4, column=0, sticky=tk.W, pady=10
        )
        ttk.Button(
            main_frame, text="Delete Selected", command=self.delete_mapping
        ).grid(row=4, column=1, sticky=tk.W, pady=10)

        ttk.Button(main_frame, text="Save & Exit", command=self.save_and_exit).grid(
            row=4, column=3, sticky=tk.E, pady=10
        )

        self.refresh_profiles()
        self.refresh_mappings()

    def refresh_profiles(self):
        profiles = self.config_manager.config.get("profiles", [])
        self.profile_combo["values"] = [p["name"] for p in profiles]

        active_idx = self.config_manager.config.get("active_profile", 0)
        if active_idx < len(profiles):
            self.profile_var.set(profiles[active_idx]["name"])

    def refresh_mappings(self):
        for item in self.mappings_tree.get_children():
            self.mappings_tree.delete(item)

        profile = self.config_manager.get_active_profile()
        mappings = profile.get("mappings", [])

        for i, mapping in enumerate(mappings, 1):
            trigger = mapping.get("trigger", "")
            note = mapping.get("note", "")
            action = mapping.get("action", {})
            action_type = action.get("type", "")

            if trigger == "fader":
                details = f"Value: {note}"
            else:
                details = str(action)[:50]

            self.mappings_tree.insert(
                "", "end", values=(i, trigger, note, action_type, details)
            )

    def on_profile_change(self, event):
        idx = self.profile_combo.current()
        self.config_manager.set_active_profile(idx)
        self.refresh_mappings()

    def new_profile(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Profile")
        dialog.geometry("300x100")

        ttk.Label(dialog, text="Profile Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(pady=5)

        def create():
            name = name_var.get().strip()
            if name:
                self.config_manager.config.setdefault("profiles", []).append(
                    {"name": name, "mappings": []}
                )
                self.config_manager.save_config()
                self.refresh_profiles()
                dialog.destroy()

        ttk.Button(dialog, text="Create", command=create).pack(pady=5)

    def delete_profile(self):
        idx = self.profile_combo.current()
        profiles = self.config_manager.config.get("profiles", [])

        if len(profiles) <= 1:
            messagebox.showwarning("Cannot Delete", "Must have at least one profile")
            return

        if messagebox.askyesno(
            "Confirm Delete", f"Delete profile '{profiles[idx]['name']}'?"
        ):
            profiles.pop(idx)
            if self.config_manager.config.get("active_profile", 0) >= len(profiles):
                self.config_manager.config["active_profile"] = 0
            self.config_manager.save_config()
            self.refresh_profiles()
            self.refresh_mappings()

    def add_mapping(self):
        dialog = MappingDialog(self.root)
        dialog.wait_window()

        if dialog.result:
            self.config_manager.add_mapping(dialog.result)
            self.refresh_mappings()

    def edit_mapping(self):
        selected = self.mappings_tree.selection()
        if not selected:
            return

        idx = self.mappings_tree.index(selected[0])
        profile = self.config_manager.get_active_profile()

        if idx < len(profile.get("mappings", [])):
            mapping = profile["mappings"][idx]
            dialog = MappingDialog(self.root, mapping)
            dialog.wait_window()

            if dialog.result:
                profile["mappings"][idx] = dialog.result
                self.config_manager.save_config()
                self.refresh_mappings()

    def delete_mapping(self):
        selected = self.mappings_tree.selection()
        if not selected:
            return

        idx = self.mappings_tree.index(selected[0])

        if messagebox.askyesno("Confirm Delete", "Delete this mapping?"):
            self.config_manager.remove_mapping(idx)
            self.refresh_mappings()

    def save_and_exit(self):
        self.config_manager.save_config()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


class MappingDialog(tk.Toplevel):
    def __init__(self, parent, mapping=None):
        super().__init__(parent)
        self.result = None
        self.mapping = mapping or {}

        self.title("Edit Mapping")
        self.geometry("400x300")

        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Trigger Type:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.trigger_var = tk.StringVar(value=self.mapping.get("trigger", "pad"))
        ttk.Radiobutton(frame, text="Pad", variable=self.trigger_var, value="pad").grid(
            row=0, column=1, sticky=tk.W
        )
        ttk.Radiobutton(
            frame, text="Fader", variable=self.trigger_var, value="fader"
        ).grid(row=0, column=2, sticky=tk.W)

        ttk.Label(frame, text="Control:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.control_var = tk.StringVar(value=self.mapping.get("note", "pad_4_1"))
        control_combo = ttk.Combobox(frame, textvariable=self.control_var)

        pads = [f"pad_{r}_{c}" for r in range(1, 6) for c in range(1, 5)]
        faders = ["fader_1", "fader_2", "fader_3", "fader_4"]
        control_combo["values"] = pads + faders
        control_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Action Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.action_type_var = tk.StringVar(
            value=self.mapping.get("action", {}).get("type", "keyboard")
        )
        action_types = [
            "keyboard",
            "hotkey",
            "launch",
            "url",
            "script",
            "system",
            "text",
            "fader_callback",
        ]
        ttk.Combobox(
            frame,
            textvariable=self.action_type_var,
            values=action_types,
            state="readonly",
        ).grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Action Config (JSON):").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.action_text = tk.Text(frame, height=8, width=40)
        self.action_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))

        action_config = self.mapping.get("action", {})
        if action_config:
            import json

            self.action_text.insert("1.0", json.dumps(action_config, indent=2))

        ttk.Label(frame, text="Color (R,G,B):").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )
        self.color_var = tk.StringVar(value=str(self.mapping.get("color", [255, 0, 0])))
        ttk.Entry(frame, textvariable=self.color_var, width=20).grid(
            row=5, column=1, sticky=tk.W
        )

        ttk.Button(frame, text="Save", command=self.save).grid(
            row=6, column=2, sticky=tk.E, pady=10
        )

    def save(self):
        import json

        try:
            action_config = json.loads(self.action_text.get("1.0", tk.END))
        except json.JSONDecodeError:
            action_config = {"type": self.action_type_var.get()}

        try:
            color = eval(self.color_var.get())
            if not isinstance(color, (list, tuple)) or len(color) != 3:
                color = [255, 0, 0]
        except:
            color = [255, 0, 0]

        self.result = {
            "trigger": self.trigger_var.get(),
            "note": self.control_var.get(),
            "action": action_config,
            "color": color,
        }
        self.destroy()


def launch_ui():
    config_manager = ConfigManager()
    app = ConfigUI(config_manager)
    app.run()
