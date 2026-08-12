import customtkinter as ctk

from app.ui.main_window import App


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
