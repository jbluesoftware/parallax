import customtkinter as ctk
from app.ui.theme import CORNER_RADIUS, FONTS, SPACING


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, theme, **kwargs):
        super().__init__(
            parent,
            fg_color=theme["bg_secondary"],
            corner_radius=CORNER_RADIUS["lg"],
            border_width=1,
            border_color=theme["border"],
            **kwargs,
        )
        self.theme = theme
        self._build_ui()

    def _build_ui(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="Navigation",
            text_color=self.theme["text_primary"],
            font=(FONTS["family"], FONTS["size_body"], FONTS["weight_bold"]),
            anchor="w",
        )
        title.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        self.chat_button = ctk.CTkButton(
            self,
            text="Chat",
            corner_radius=CORNER_RADIUS["md"],
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color=self.theme["button_fg"],
            width=180,
            command=lambda: None,
        )
        self.chat_button.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        self.commands_button = ctk.CTkButton(
            self,
            text="Commands",
            corner_radius=CORNER_RADIUS["md"],
            fg_color=self.theme["bg_tertiary"],
            hover_color=self.theme["bg_secondary"],
            text_color=self.theme["text_primary"],
            width=180,
            command=lambda: None,
        )
        self.commands_button.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

    def update_theme(self, theme) -> None:
        self.theme = theme
        self.configure(fg_color=self.theme["bg_secondary"], border_color=self.theme["border"])
        self.chat_button.configure(fg_color=self.theme["accent"], hover_color=self.theme["accent_hover"], text_color=self.theme["button_fg"])
        self.commands_button.configure(fg_color=self.theme["bg_tertiary"], hover_color=self.theme["bg_secondary"], text_color=self.theme["text_primary"])
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                child.configure(text_color=self.theme["text_primary"])
