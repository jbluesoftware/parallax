import re
import customtkinter as ctk

from app.ui.theme import CORNER_RADIUS, FONTS, SPACING


class ChatFeed(ctk.CTkFrame):
    def __init__(self, parent, theme, **kwargs):
        super().__init__(parent, fg_color=theme["bg_primary"], corner_radius=0, **kwargs)
        self.theme = theme

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=CORNER_RADIUS["lg"],
            border_width=1,
            border_color=self.theme["border"],
            height=400,
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def update_theme(self, theme):
        self.theme = theme
        self.configure(fg_color=self.theme["bg_primary"])
        self.scrollable_frame.configure(fg_color=self.theme["bg_secondary"], border_color=self.theme["border"])
        self._update_widget_theme(self)

    def _update_widget_theme(self, widget):
        for child in widget.winfo_children():
            if hasattr(child, "configure"):
                try:
                    child.configure(fg_color=self.theme["bg_secondary"], text_color=self.theme["text_primary"])
                except Exception:
                    pass
            self._update_widget_theme(child)

    def add_user_message(self, prompt_text: str) -> None:
        self._add_message("You", prompt_text, self.theme["user_bg"], align="e")

    def add_assistant_message(self, assistant_text: str) -> None:
        self._add_message("Assistant", assistant_text, self.theme["assistant_bg"], align="w")

    def add_system_message(self, system_text: str) -> None:
        self._add_message("System", system_text, self.theme["system_bg"], align="w", muted=True)

    def _add_message(self, sender: str, message_text: str, bg_color: str, align: str = "w", muted: bool = False) -> None:
        bubble_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=bg_color,
            corner_radius=CORNER_RADIUS["md"],
            border_width=1,
            border_color=self.theme["border"],
            width=760,
        )
        bubble_frame.grid(sticky="ew", padx=SPACING["sm"], pady=(SPACING["sm"], 0))
        bubble_frame.grid_columnconfigure(0, weight=1)

        title_color = self.theme["text_secondary"] if muted else self.theme["accent"]
        title_label = ctk.CTkLabel(
            bubble_frame,
            text=sender,
            text_color=title_color,
            font=(FONTS["family"], FONTS["size_body"], FONTS["weight_bold"]),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=SPACING["md"], pady=(SPACING["md"], 0))

        row_index = 1
        for segment_type, content in self._split_markdown(message_text):
            if segment_type == "text":
                text_label = ctk.CTkLabel(
                    bubble_frame,
                    text=content,
                    text_color=self.theme["text_primary"],
                    wraplength=760,
                    justify="left",
                    font=(FONTS["family"], FONTS["size_body"]),
                )
                text_label.grid(row=row_index, column=0, sticky="w", padx=SPACING["md"], pady=(SPACING["sm"], 0))
                row_index += 1
            else:
                self._build_code_block(bubble_frame, content)
                row_index += 2

        self.scrollable_frame.after(20, lambda: self.scrollable_frame.yview_moveto(1.0))

    def _split_markdown(self, raw_text: str):
        if not raw_text:
            return [("text", "")]

        pattern = re.compile(r"```([\w+-]*)\n([\s\S]*?)```", re.MULTILINE)
        parts = []
        last_end = 0
        for match in pattern.finditer(raw_text):
            if match.start() > last_end:
                text_segment = raw_text[last_end:match.start()].strip()
                if text_segment:
                    parts.append(("text", text_segment))
            code_segment = match.group(2).rstrip()
            parts.append(("code", code_segment))
            last_end = match.end()

        remainder = raw_text[last_end:].strip()
        if remainder:
            parts.append(("text", remainder))

        if not parts:
            parts.append(("text", raw_text.strip()))

        return parts

    def _build_code_block(self, container, code_text: str) -> None:
        code_card = ctk.CTkFrame(
            container,
            fg_color=self.theme["code_bg"],
            corner_radius=CORNER_RADIUS["md"],
            border_width=1,
            border_color=self.theme["border"],
        )
        code_card.grid(sticky="ew", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]))
        code_card.grid_columnconfigure(0, weight=1)

        copy_button = ctk.CTkButton(
            code_card,
            text="Copy code",
            width=100,
            corner_radius=CORNER_RADIUS["sm"],
            fg_color=self.theme["bg_secondary"],
            hover_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            command=lambda text=code_text: self._copy_code(text),
        )
        copy_button.grid(row=0, column=0, sticky="e", padx=SPACING["md"], pady=(SPACING["md"], 0))

        code_widget = ctk.CTkTextbox(
            code_card,
            width=1,
            height=8,
            fg_color=self.theme["code_bg"],
            text_color=self.theme["code_fg"],
            corner_radius=CORNER_RADIUS["sm"],
            border_width=0,
            font=(FONTS["family_mono"], FONTS["size_body"]),
        )
        code_widget.grid(row=1, column=0, sticky="nsew", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["md"]))
        code_widget.insert("0.0", code_text)
        code_widget.configure(state="disabled")

    def _copy_code(self, code_text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(code_text)
        self.update()

    def clear(self) -> None:
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
