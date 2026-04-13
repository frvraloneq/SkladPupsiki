import customtkinter as ctk

from script_copier import ScriptCopier

# Настройки внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


if __name__ == "__main__":
    app = ScriptCopier()
    app.mainloop()
