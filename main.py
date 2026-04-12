import customtkinter as ctk
import json
import os

from datetime import datetime
from tkinter import messagebox

# Настройки внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ScriptCopier(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Скрипты склада — быстрые ответы")
        self.geometry("940x680")
        self.resizable(True, True)

        self.scripts_file = "scripts.json"
        self.groups = {}

        # === Интерфейс ===
        self.title_label = ctk.CTkLabel(self, 
            text="Быстрые скриптовые ответы для склада",
            font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=20)

        # Выбор группы
        self.group_frame = ctk.CTkFrame(self)
        self.group_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(self.group_frame, text="Группа:", 
                     font=ctk.CTkFont(size=15)).pack(side="left", padx=(10, 5))

        self.group_var = ctk.StringVar(value="Загрузка...")
        self.group_menu = ctk.CTkOptionMenu(self.group_frame, variable=self.group_var, values=["Загрузка..."], command=self.on_group_change, width=320)
        self.group_menu.pack(side="left", padx=5)

        self.refresh_btn = ctk.CTkButton(self.group_frame, text="↻ Обновить список", width=100, command=self.load_scripts)
        self.refresh_btn.pack(side="right", padx=0)

        # Поиск
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, 
            placeholder_text="Поиск по названию скрипта...",
            textvariable=self.search_var, height=38)
        self.search_entry.pack(fill="x", padx=25, pady=15)
        self.search_var.trace("w", lambda *args: self.show_scripts())

        # Список скриптов
        self.scripts_frame = ctk.CTkScrollableFrame(self)
        self.scripts_frame.pack(fill="both", expand=True, padx=25, pady=10)

        # Предпросмотр
        ctk.CTkLabel(self, text="Предпросмотр:", 
                     font=ctk.CTkFont(size=14)).pack(anchor="w", padx=25, pady=(5,0))
        self.preview_text = ctk.CTkTextbox(self, height=150)
        self.preview_text.pack(fill="x", padx=25, pady=(0, 25))

        # Версия приложения в правом нижнем углу
        version_label = ctk.CTkLabel(
            self,
            height=5,
            text="v0.0030",                   
            font=ctk.CTkFont(size=10),
            text_color="#555555",            
        )
        version_label.place(relx=1.0, rely=1.0, x=-5, y=-5, anchor="se")

        # Загружаем скрипты
        self.load_scripts()

    def load_scripts(self):
        """Загружает скрипты и обновляет интерфейс"""
        if os.path.exists(self.scripts_file):
            try:
                with open(self.scripts_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.groups = data.get("groups", {})
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось прочитать scripts.json\n\n{e}")
                self.groups = {}
        else:
            self.create_example_json()
            messagebox.showinfo("Пример создан", 
                f"Файл {self.scripts_file} создан с примерами.\n"
                "Отредактируйте его под себя и нажмите «Обновить список».")

        self.update_group_menu()
        self.show_scripts()

    def update_group_menu(self):
        groups_list = list(self.groups.keys())
        
        if not groups_list:
            groups_list = ["Нет групп"]

        # Обновляем значения
        self.group_menu.configure(values=groups_list)
        
        # Ставим первое значение
        if groups_list:
            self.group_var.set(groups_list[0])

    def on_group_change(self, choice):
        self.show_scripts()

    def show_scripts(self):
        # Очистка старых кнопок
        for widget in self.scripts_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().lower().strip()
        group_name = self.group_var.get()

        if group_name not in self.groups:
            ctk.CTkLabel(self.scripts_frame, 
                         text="Выберите группу или добавьте скрипты в JSON",
                         text_color="gray").pack(pady=30)
            return

        scripts = self.groups[group_name]

        if not scripts:
            ctk.CTkLabel(self.scripts_frame, text="В группе пока нет скриптов").pack(pady=20)
            return

        for script in scripts:
            name = script.get("name", "Без названия")
            text = script.get("text", "")

            if search_text and search_text not in name.lower():
                continue

            btn = ctk.CTkButton(
                self.scripts_frame,
                text=name,
                anchor="w",
                height=45,
                font=ctk.CTkFont(size=14),
                command=lambda t=text, n=name: self.copy_to_clipboard(t, n)
            )
            btn.pack(fill="x", pady=4, padx=10)

    def copy_to_clipboard(self, text: str, name: str):
        
        now = datetime.now()
        text = text.replace("{{date}}", now.strftime("%d.%m.%y"))      
        text = text.replace("{{date_full}}", now.strftime("%d.%m.%Y")) 
        text = text.replace("{{time}}", now.strftime("%H:%M"))    
        text = text.replace("[наименование]", " ")    
        text = text.replace("[номер накладной]", " ")
        text = text.replace("[дата доставки]", " ")
        
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()

            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", text)

            messagebox.showinfo("✓ Скопировано", f"Скрипт «{name}» скопирован в буфер обмена")
        except Exception as e:
            messagebox.showerror("Ошибка копирования", str(e))


if __name__ == "__main__":
    app = ScriptCopier()
    app.mainloop()