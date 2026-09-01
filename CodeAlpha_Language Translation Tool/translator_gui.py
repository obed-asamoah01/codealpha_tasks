"""CodeAlpha Language Translator desktop application.

Run after installing requirements with: python translator_gui.py
"""

from __future__ import annotations

import os
import tempfile
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Any

from deep_translator import GoogleTranslator
from gtts import gTTS
from playsound import playsound


APP_TITLE = "CodeAlpha Language Translator"
AUTO_DETECT = "Auto Detect"
DEFAULT_FONT = ("Segoe UI", 10)


class LanguageTranslatorApp:
    """Tkinter interface and asynchronous translation/TTS operations."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("760x650")
        self.root.minsize(620, 520)

        self.source_var = tk.StringVar(value=AUTO_DETECT)
        self.target_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Loading supported languages...")
        self.languages: dict[str, str] = {}
        self.busy = False

        self._configure_style()
        self._build_ui()
        self._load_languages_async()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TFrame", padding=0)
        style.configure("TLabelframe", padding=12)
        style.configure("TLabelframe.Label", font=("Segoe UI Semibold", 10))
        style.configure("TButton", font=DEFAULT_FONT, padding=(10, 6))
        style.configure("TLabel", font=DEFAULT_FONT)

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)
        container.rowconfigure(5, weight=1)

        title = ttk.Label(
            container,
            text="Language Translation Tool",
            font=("Segoe UI Semibold", 18),
        )
        title.grid(row=0, column=0, sticky="w")
        ttk.Label(
            container,
            text="Translate text with Google Translate.",
            foreground="#5d6470",
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        input_frame = ttk.LabelFrame(container, text="Text to translate")
        input_frame.grid(row=2, column=0, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        self.input_text = scrolledtext.ScrolledText(
            input_frame, wrap=tk.WORD, height=8, font=DEFAULT_FONT,
            relief=tk.FLAT, padx=8, pady=8,
        )
        self.input_text.grid(row=0, column=0, sticky="nsew")

        controls = ttk.Frame(container)
        controls.grid(row=3, column=0, sticky="ew", pady=14)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        ttk.Label(controls, text="Source Language").grid(
            row=0, column=0, sticky="w"
        )
        self.source_combo = ttk.Combobox(
            controls, textvariable=self.source_var, state="disabled",
            font=DEFAULT_FONT,
        )
        self.source_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        self.swap_button = ttk.Button(
            controls, text="⇄  Swap", command=self.swap_languages, state="disabled"
        )
        self.swap_button.grid(row=1, column=2, padx=12, pady=(4, 0))

        ttk.Label(controls, text="Target Language").grid(
            row=0, column=3, sticky="w"
        )
        self.target_combo = ttk.Combobox(
            controls, textvariable=self.target_var, state="disabled",
            font=DEFAULT_FONT,
        )
        self.target_combo.grid(row=1, column=3, sticky="ew", pady=(4, 0))

        self.translate_button = ttk.Button(
            container, text="Translate", command=self.translate, state="disabled"
        )
        self.translate_button.grid(row=4, column=0, pady=(0, 14))

        output_frame = ttk.LabelFrame(container, text="Translation")
        output_frame.grid(row=5, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, height=8, font=DEFAULT_FONT,
            relief=tk.FLAT, padx=8, pady=8, state=tk.DISABLED,
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        footer = ttk.Frame(container)
        footer.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status_var, foreground="#5d6470").grid(
            row=0, column=0, sticky="w"
        )
        self.copy_button = ttk.Button(footer, text="Copy", command=self.copy_translation)
        self.copy_button.grid(row=0, column=1, padx=(10, 0))
        self.speak_button = ttk.Button(
            footer, text="Speak", command=self.speak_translation, state="disabled"
        )
        self.speak_button.grid(row=0, column=2, padx=(8, 0))

    def _load_languages_async(self) -> None:
        threading.Thread(target=self._load_languages, daemon=True).start()

    def _load_languages(self) -> None:
        try:
            languages = GoogleTranslator().get_supported_languages(as_dict=True)
            self.root.after(0, self._set_languages, languages)
        except Exception as error:  # Network library may raise varying exception types.
            self.root.after(0, self._language_load_error, str(error))

    def _set_languages(self, languages: dict[str, str]) -> None:
        self.languages = languages
        names = sorted(languages, key=str.casefold)
        self.source_combo.configure(values=[AUTO_DETECT, *names], state="readonly")
        self.target_combo.configure(values=names, state="readonly")
        self.target_var.set("English" if "English" in languages else names[0])
        self.translate_button.configure(state=tk.NORMAL)
        self.swap_button.configure(state=tk.NORMAL)
        self.status_var.set("Ready")

    def _language_load_error(self, details: str) -> None:
        self.status_var.set("Could not load languages")
        messagebox.showerror(
            "Language loading failed",
            "Supported languages could not be loaded. Check your internet connection.\n\n"
            f"Details: {details}",
        )

    def _set_busy(self, busy: bool, status: str) -> None:
        self.busy = busy
        self.status_var.set(status)
        state = tk.DISABLED if busy else tk.NORMAL
        self.translate_button.configure(state=state)
        self.swap_button.configure(state=state)
        self.speak_button.configure(
            state=tk.DISABLED if busy or not self._get_output().strip() else tk.NORMAL
        )

    def _get_output(self) -> str:
        return self.output_text.get("1.0", tk.END).strip()

    def _set_output(self, text: str) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.configure(state=tk.DISABLED)

    def _language_code(self, language_name: str) -> str:
        return "auto" if language_name == AUTO_DETECT else self.languages[language_name]

    def translate(self) -> None:
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Nothing to translate", "Enter some text before translating.")
            return
        if self.busy:
            return
        source = self.source_var.get()
        target = self.target_var.get()
        self._set_busy(True, "Translating...")
        threading.Thread(
            target=self._translate_worker, args=(text, source, target), daemon=True
        ).start()

    def _translate_worker(self, text: str, source: str, target: str) -> None:
        try:
            translator = GoogleTranslator(
                source=self._language_code(source), target=self._language_code(target)
            )
            translated = translator.translate(text)
            self.root.after(0, self._translation_complete, translated)
        except Exception as error:
            self.root.after(0, self._operation_error, "Translation failed", str(error))

    def _translation_complete(self, translated: str) -> None:
        self._set_output(translated)
        self._set_busy(False, "Translation complete")

    def swap_languages(self) -> None:
        source = self.source_var.get()
        target = self.target_var.get()
        if source == AUTO_DETECT:
            messagebox.showinfo(
                "Choose a source language",
                "Swap is unavailable while Source Language is set to Auto Detect. "
                "Select the original language first, then swap.",
            )
            return
        self.source_var.set(target)
        self.target_var.set(source)
        original, translated = self.input_text.get("1.0", tk.END).strip(), self._get_output()
        if translated:
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", translated)
            self._set_output(original)
        self.status_var.set("Languages swapped")

    def copy_translation(self) -> None:
        translated = self._get_output()
        if not translated:
            messagebox.showinfo("Nothing to copy", "Translate text before copying it.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(translated)
        self.root.update()
        self.status_var.set("Translation copied to clipboard")

    def speak_translation(self) -> None:
        text = self._get_output()
        if not text or self.busy:
            return
        language = self._language_code(self.target_var.get())
        self._set_busy(True, "Generating speech...")
        threading.Thread(target=self._speak_worker, args=(text, language), daemon=True).start()

    def _speak_worker(self, text: str, language: str) -> None:
        path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                path = temp_file.name
            gTTS(text=text, lang=language).save(path)
            self.root.after(0, self.status_var.set, "Playing translation...")
            playsound(path)
            self.root.after(0, self._speech_complete)
        except Exception as error:
            self.root.after(0, self._operation_error, "Speech failed", str(error))
        finally:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def _speech_complete(self) -> None:
        self._set_busy(False, "Speech complete")

    def _operation_error(self, title: str, details: str) -> None:
        self._set_busy(False, "Ready")
        messagebox.showerror(title, f"{title}. Please check your connection and try again.\n\nDetails: {details}")


def main() -> None:
    root = tk.Tk()
    LanguageTranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
