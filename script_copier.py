import customtkinter as ctk
import os
from datetime import datetime
from tkinter import messagebox

from data_loader import create_example_groups_file, load_groups_from_file


APP_VERSION = "v0.0040"


class ScriptCopier(ctk.CTk):
    def __init__(self, scripts_file: str = "scripts.json"):
        super().__init__()

        self.scripts_file = scripts_file
        self.groups = {}

        self.configure_window()
        self.build_interface()
        self.load_scripts()

    def configure_window(self):
        self.title("Скрипты склада — быстрые ответы")
        self.geometry("940x680")
        self.resizable(True, True)

    def build_interface(self):
        self.build_header()
        self.build_group_controls()
        self.build_search_bar()
        self.build_scripts_area()
        self.build_preview_area()
        self.build_version_label()

    def build_header(self):
        self.title_label = ctk.CTkLabel(
            self,
            text="Быстрые скриптовые ответы для склада",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.title_label.pack(pady=20)

    def build_group_controls(self):
        self.group_frame = ctk.CTkFrame(self)
        self.group_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(
            self.group_frame,
            text="Группа:",
            font=ctk.CTkFont(size=15),
        ).pack(side="left", padx=(10, 5))

        self.group_var = ctk.StringVar(value="Загрузка...")
        self.group_menu = ctk.CTkOptionMenu(
            self.group_frame,
            variable=self.group_var,
            values=["Загрузка..."],
            command=self.on_group_change,
            width=320,
        )
        self.group_menu.pack(side="left", padx=5)

        self.refresh_btn = ctk.CTkButton(
            self.group_frame,
            text="↻ Обновить список",
            width=140,
            command=self.load_scripts,
        )
        self.refresh_btn.pack(side="right", padx=0)

    def build_search_bar(self):
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Поиск по названию скрипта...",
            textvariable=self.search_var,
            height=38,
        )
        self.search_entry.pack(fill="x", padx=25, pady=15)
        self.search_var.trace("w", lambda *args: self.show_scripts())

    def build_scripts_area(self):
        self.scripts_frame = ctk.CTkScrollableFrame(self)
        self.scripts_frame.pack(fill="both", expand=True, padx=25, pady=10)

    def build_preview_area(self):
        ctk.CTkLabel(
            self,
            text="Предпросмотр:",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=25, pady=(5, 0))

        self.preview_text = ctk.CTkTextbox(self, height=150)
        self.preview_text.pack(fill="x", padx=25, pady=(0, 25))

    def build_version_label(self):
        ctk.CTkLabel(
            self,
            height=5,
            text=APP_VERSION,
            font=ctk.CTkFont(size=10),
            text_color="#555555",
        ).place(relx=1.0, rely=1.0, x=-5, y=-5, anchor="se")

    def load_scripts(self):
        self.groups = self.read_groups_from_file()
        self.update_group_menu()
        self.show_scripts()

    def read_groups_from_file(self) -> dict:
        if not self.file_exists(self.scripts_file):
            example_groups = create_example_groups_file(self.scripts_file)
            messagebox.showinfo(
                "Пример создан",
                (
                    f"Файл {self.scripts_file} создан с примерами.\n"
                    "Отредактируйте его под себя и нажмите «Обновить список»."
                ),
            )
            return example_groups

        try:
            return load_groups_from_file(self.scripts_file)
        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось прочитать {self.scripts_file}\n\n{error}",
            )
            return {}

    @staticmethod
    def file_exists(path: str) -> bool:
        return os.path.exists(path)

    def update_group_menu(self):
        groups_list = list(self.groups.keys())

        if not groups_list:
            groups_list = ["Нет групп"]

        self.group_menu.configure(values=groups_list)
        if groups_list:
            self.group_var.set(groups_list[0])

    def on_group_change(self, choice):
        self.show_scripts()

    def show_scripts(self):
        self.clear_scripts_area()

        group_name = self.group_var.get()
        search_text = self.search_var.get().lower().strip()

        if group_name not in self.groups:
            self.render_message("Выберите группу или добавьте скрипты в JSON")
            return

        scripts = self.filter_scripts(self.groups[group_name], search_text)

        if not scripts:
            self.render_message("В группе пока нет скриптов")
            return

        self.render_script_buttons(scripts)

    def clear_scripts_area(self):
        for widget in self.scripts_frame.winfo_children():
            widget.destroy()

    def render_message(self, text: str):
        ctk.CTkLabel(
            self.scripts_frame,
            text=text,
            text_color="gray",
        ).pack(pady=30)

    def filter_scripts(self, scripts: list, search_text: str) -> list:
        if not search_text:
            return scripts

        return [
            script
            for script in scripts
            if search_text in script.get("name", "").lower()
        ]

    def render_script_buttons(self, scripts: list):
        for script in scripts:
            name = script.get("name", "Без названия")
            text = script.get("text", "")

            button = ctk.CTkButton(
                self.scripts_frame,
                text=name,
                anchor="w",
                height=45,
                font=ctk.CTkFont(size=14),
                command=lambda t=text, n=name: self.copy_to_clipboard(t, n),
            )
            button.pack(fill="x", pady=4, padx=10)

    def copy_to_clipboard(self, text: str, name: str):
        text = self.apply_template_replacements(text)

        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            self.update_preview(text)
            messagebox.showinfo("✓ Скопировано", f"Скрипт «{name}» скопирован в буфер обмена")
        except Exception as error:
            messagebox.showerror("Ошибка копирования", str(error))

    def apply_template_replacements(self, text: str) -> str:
        now = datetime.now()
        replacements = {
            "{{date}}": now.strftime("%d.%m.%y"),
            "{{date_full}}": now.strftime("%d.%m.%Y"),
            "{{time}}": now.strftime("%H:%M"),
            "[наименование]": " ",
            "[номер накладной]": " ",
            "[дата доставки]": " ",
        }

        for pattern, replacement in replacements.items():
            text = text.replace(pattern, replacement)

        return text

    def update_preview(self, text: str):
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", text)
