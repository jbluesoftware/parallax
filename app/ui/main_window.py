import threading

import customtkinter as ctk
from app.config import APP_HEIGHT, APP_TITLE, APP_WIDTH, MODEL_REFRESH_INTERVAL_SECONDS
from app.core.agent_client import OllamaClient
from app.core.agent_manager import OllamaServerManager
from app.core.scheduler import Scheduler
from app.ui.theme import CORNER_RADIUS, FONTS, SPACING, THEMES
from app.ui.widgets.chat_feed import ChatFeed
from app.ui.widgets.sidebar import Sidebar


class App:
    def __init__(self, root: ctk.CTk):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.minsize(820, 620)
        self.server = OllamaServerManager()
        self.client = OllamaClient()
        self.scheduler = Scheduler(self.root, interval_ms=MODEL_REFRESH_INTERVAL_SECONDS * 1000)

        self.theme_name = "light"
        self.theme = THEMES[self.theme_name]
        self.models = []

        self._build_ui()
        self._apply_theme()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._start_server_and_refresh_models()
        self.scheduler.start(self._refresh_model_list)

    def _build_ui(self) -> None:
        self.root.configure(fg_color=self.theme["bg_primary"])

        self.page_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.theme["bg_primary"],
            corner_radius=0,
            border_width=0,
        )
        self.page_frame.pack(fill="both", expand=True)

        self.sidebar = Sidebar(self.page_frame, theme=self.theme)
        self.sidebar.pack(side="left", fill="y", padx=(SPACING["md"], 0), pady=SPACING["md"])

        self.content_frame = ctk.CTkFrame(
            self.page_frame,
            fg_color=self.theme["bg_primary"],
            corner_radius=0,
            border_width=0,
        )
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(SPACING["md"], SPACING["md"]), pady=SPACING["md"])

        self.header_card = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.theme["bg_secondary"],
            corner_radius=CORNER_RADIUS["lg"],
            border_width=1,
            border_color=self.theme["border"],
        )
        self.header_card.pack(fill="x", pady=(0, SPACING["md"]))

        self.title_label = ctk.CTkLabel(
            self.header_card,
            text="Ollama LLM Chat",
            text_color=self.theme["text_primary"],
            font=(FONTS["family"], FONTS["size_h1"], FONTS["weight_bold"]),
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.theme_button = ctk.CTkButton(
            self.header_card,
            text="Switch to dark",
            corner_radius=CORNER_RADIUS["md"],
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color=self.theme["button_fg"],
            command=self._toggle_theme,
        )
        self.theme_button.grid(row=0, column=1, sticky="e")

        self.subtitle_label = ctk.CTkLabel(
            self.header_card,
            text="A refined chat experience for your Ollama models.",
            text_color=self.theme["text_secondary"],
            font=(FONTS["family"], FONTS["size_body"]),
        )
        self.subtitle_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(SPACING["sm"], 0))

        self.header_card.grid_columnconfigure(0, weight=1)
        self.header_card.grid_columnconfigure(1, weight=0)

        self.control_card = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.theme["bg_secondary"],
            corner_radius=CORNER_RADIUS["lg"],
            border_width=1,
            border_color=self.theme["border"],
        )
        self.control_card.pack(fill="x", pady=(0, SPACING["md"]))

        self.model_label = ctk.CTkLabel(
            self.control_card,
            text="Choose model",
            text_color=self.theme["text_primary"],
            font=(FONTS["family"], FONTS["size_body"], FONTS["weight_bold"]),
        )
        self.model_label.grid(row=0, column=0, sticky="w")

        self.model_var = ctk.StringVar()
        self.model_select = ctk.CTkComboBox(
            self.control_card,
            values=[],
            variable=self.model_var,
            fg_color=self.theme["bg_tertiary"],
            button_color=self.theme["bg_secondary"],
            button_hover_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            width=280,
            corner_radius=CORNER_RADIUS["md"],
        )
        self.model_select.grid(row=1, column=0, sticky="w", pady=(SPACING["sm"], 0))

        self.status_label = ctk.CTkLabel(
            self.control_card,
            text="Starting Ollama server and loading models...",
            text_color=self.theme["text_secondary"],
            font=(FONTS["family"], FONTS["size_caption"]),
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=(SPACING["lg"], 0))

        self.hint_label = ctk.CTkLabel(
            self.control_card,
            text="Type /help for command shortcuts. Prompts are sent to the selected model.",
            text_color=self.theme["text_secondary"],
            font=(FONTS["family"], FONTS["size_caption"]),
            anchor="e",
        )
        self.hint_label.grid(row=1, column=1, sticky="e", padx=(SPACING["lg"], 0), pady=(SPACING["sm"], 0))

        self.control_card.grid_columnconfigure(0, weight=1)
        self.control_card.grid_columnconfigure(1, weight=0)

        self.feed = ChatFeed(self.content_frame, self.theme)
        self.feed.pack(fill="both", expand=True)

        self.bottom_bar = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.theme["bg_secondary"],
            corner_radius=CORNER_RADIUS["lg"],
            border_width=1,
            border_color=self.theme["border"],
        )
        self.bottom_bar.pack(fill="x", pady=(SPACING["md"], 0))

        self.prompt_text = ctk.StringVar()
        self.prompt_entry = ctk.CTkEntry(
            self.bottom_bar,
            textvariable=self.prompt_text,
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            placeholder_text="Enter your prompt or command...",
            height=40,
            corner_radius=CORNER_RADIUS["md"],
        )
        self.prompt_entry.pack(side="left", fill="both", expand=True, padx=(0, SPACING["sm"]))
        self.prompt_entry.bind("<Return>", lambda event: self.on_send())

        self.send_button = ctk.CTkButton(
            self.bottom_bar,
            text="Send",
            corner_radius=CORNER_RADIUS["md"],
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color=self.theme["button_fg"],
            command=self.on_send,
            width=100,
        )
        self.send_button.pack(side="right")

    def _apply_theme(self) -> None:
        self.theme = THEMES[self.theme_name]
        ctk.set_appearance_mode("light" if self.theme_name == "light" else "dark")

        self.root.configure(fg_color=self.theme["bg_primary"])
        self.page_frame.configure(fg_color=self.theme["bg_primary"])
        self.content_frame.configure(fg_color=self.theme["bg_primary"])
        self.sidebar.update_theme(self.theme)
        self.header_card.configure(fg_color=self.theme["bg_secondary"], border_color=self.theme["border"])
        self.control_card.configure(fg_color=self.theme["bg_secondary"], border_color=self.theme["border"])
        self.bottom_bar.configure(fg_color=self.theme["bg_secondary"], border_color=self.theme["border"])

        self.title_label.configure(text_color=self.theme["text_primary"])
        self.subtitle_label.configure(text_color=self.theme["text_secondary"])
        self.model_label.configure(text_color=self.theme["text_primary"])
        self.status_label.configure(text_color=self.theme["text_secondary"])
        self.hint_label.configure(text_color=self.theme["text_secondary"])
        self.theme_button.configure(fg_color=self.theme["accent"], hover_color=self.theme["accent_hover"], text_color=self.theme["button_fg"])
        self.send_button.configure(fg_color=self.theme["accent"], hover_color=self.theme["accent_hover"], text_color=self.theme["button_fg"])
        self.prompt_entry.configure(fg_color=self.theme["bg_tertiary"], text_color=self.theme["text_primary"], placeholder_text_color=self.theme["text_secondary"])

        self.model_select.configure(fg_color=self.theme["bg_tertiary"], text_color=self.theme["text_primary"], button_color=self.theme["bg_secondary"], button_hover_color=self.theme["bg_tertiary"], dropdown_fg_color=self.theme["bg_secondary"], dropdown_text_color=self.theme["text_primary"], border_color=self.theme["border"], corner_radius=CORNER_RADIUS["md"])
        self.feed.update_theme(self.theme)
        self.theme_button.configure(text=self._theme_button_text())

    def _theme_button_text(self) -> str:
        if self.theme_name == "light":
            return "Switch to dark"
        if self.theme_name == "dark":
            return "Switch to light"
        return "Hacker mode"

    def _toggle_theme(self) -> None:
        if self.theme_name == "light":
            self.theme_name = "dark"
        else:
            self.theme_name = "light"
        self._apply_theme()
        self.feed.add_system_message(f"Theme switched to {self.theme_name} mode.")

    def _enter_hacker_mode(self) -> None:
        self.theme_name = "hacker"
        self._apply_theme()
        self.feed.add_system_message("Hacker theme engaged. Welcome to the terminal.")

    def _start_server_and_refresh_models(self) -> None:
        threading.Thread(target=self._initialize_service, daemon=True).start()

    def _initialize_service(self) -> None:
        try:
            self.server.start_server()
            self._refresh_model_list()
            self._set_status("Ollama server is running. Select a model and send a prompt.")
        except Exception as exc:
            self._set_status(f"Failed to start Ollama: {exc}")
            self.feed.add_system_message(str(exc))

    def _refresh_model_list(self) -> None:
        threading.Thread(target=self._refresh_model_list_worker, daemon=True).start()

    def _refresh_model_list_worker(self) -> None:
        try:
            models = self.server.get_available_models()
            if not models:
                self._set_status(
                    "No available Ollama models detected. Install a model with `ollama pull <model>` and restart the app."
                )
                return
            self.models = models
            self.root.after(0, self._update_model_dropdown)
            self._set_status(f"Loaded {len(models)} model(s).")
        except Exception as exc:
            self._set_status(f"Unable to refresh models: {exc}")

    def _update_model_dropdown(self) -> None:
        self.model_select.configure(values=self.models)
        if self.models and self.model_var.get() not in self.models:
            self.model_var.set(self.models[0])

    def _set_status(self, message: str) -> None:
        self.root.after(0, lambda: self.status_label.configure(text=message))

    def on_send(self) -> None:
        prompt = self.prompt_text.get().strip()
        if not prompt:
            return
        self.prompt_text.set("")
        self.feed.add_user_message(prompt)

        if prompt.startswith("/"):
            self._execute_command(prompt)
            return

        model = self.model_var.get()
        if not model:
            self.feed.add_system_message("Please select a model before sending a prompt.")
            return

        threading.Thread(target=self._send_prompt, args=(model, prompt), daemon=True).start()

    def _execute_command(self, command: str) -> None:
        normalized = command.strip().lower()
        if normalized == "/help":
            help_text = (
                "Available commands:\n"
                "/help - Show this help message\n"
                "/imin - Activate black-and-green hacker theme\n"
                "/clear - Clear the chat feed"
            )
            self.feed.add_system_message(help_text)
        elif normalized == "/imin":
            self._enter_hacker_mode()
        elif normalized == "/clear":
            self.feed.clear()
            self.feed.add_system_message("Chat cleared.")
        else:
            self.feed.add_system_message("Command not recognised, type `/help` for a list of commands")

    def _send_prompt(self, model: str, prompt: str) -> None:
        try:
            response_text = self.client.send_chat(model, prompt)
        except Exception as exc:
            response_text = f"Unable to contact Ollama: {exc}"
        self.root.after(0, lambda: self.feed.add_assistant_message(response_text))

    def on_close(self) -> None:
        try:
            self.scheduler.stop()
            self.server.stop_server()
        finally:
            self.root.destroy()
