"""A Tkinter FAQ chatbot powered by NLTK and TF-IDF similarity matching."""

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk
from typing import List, Optional, Tuple

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_FILE = Path(__file__).with_name("faq_data.json")
GREETING_WORDS = {"hi", "hello", "hey"}
GREETING_RESPONSE = "Hello! How can I help with your programming or technology question today?"
NO_MATCH_RESPONSE = (
    "I don't have a confident answer for that yet. Please try rephrasing it "
    "or ask a question about programming or technology."
)


def ensure_nltk_data() -> None:
    """Download the NLTK resources used by the chatbot when they are missing."""
    resources = {
        "tokenizers/punkt": "punkt",
        # Newer NLTK releases keep sentence-tokenizer tables in this package.
        "tokenizers/punkt_tab": "punkt_tab",
        "corpora/stopwords": "stopwords",
        "corpora/wordnet": "wordnet",
    }
    for resource_path, download_name in resources.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(download_name, quiet=True)


class FAQEngine:
    """Load FAQs and return answers using preprocessed TF-IDF cosine similarity."""

    def __init__(self, data_path: Path, threshold: float = 0.30) -> None:
        """Load the FAQ data and fit a TF-IDF model for its questions."""
        ensure_nltk_data()
        self.threshold = threshold
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))
        self.faqs = self._load_faqs(data_path)
        self.vectorizer = TfidfVectorizer()
        processed_questions = [self.preprocess(item["question"]) for item in self.faqs]
        self.question_vectors = self.vectorizer.fit_transform(processed_questions)

    @staticmethod
    def _load_faqs(data_path: Path) -> List[dict]:
        """Read and validate the JSON FAQ knowledge base."""
        with data_path.open(encoding="utf-8") as file:
            faqs = json.load(file)

        if not isinstance(faqs, list) or not faqs:
            raise ValueError("FAQ data must be a non-empty JSON array.")
        if not all(isinstance(item, dict) and {"question", "answer"} <= item.keys() for item in faqs):
            raise ValueError("Each FAQ must contain 'question' and 'answer' fields.")
        return faqs

    def preprocess(self, text: str) -> str:
        """Tokenize, lowercase, remove stopwords, and lemmatize text with NLTK."""
        tokens = word_tokenize(text.lower())
        cleaned_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token.isalnum() and token not in self.stop_words
        ]
        return " ".join(cleaned_tokens)

    def get_response(self, user_message: str) -> Tuple[str, Optional[float]]:
        """Return a greeting, the best FAQ response, or a no-match response."""
        normalized_message = user_message.strip().lower()
        if normalized_message in GREETING_WORDS:
            return GREETING_RESPONSE, None

        processed_message = self.preprocess(user_message)
        if not processed_message:
            return NO_MATCH_RESPONSE, 0.0

        user_vector = self.vectorizer.transform([processed_message])
        scores = cosine_similarity(user_vector, self.question_vectors).flatten()
        best_index = scores.argmax()
        best_score = float(scores[best_index])

        if best_score < self.threshold:
            return NO_MATCH_RESPONSE, best_score
        return self.faqs[best_index]["answer"], best_score


class FAQChatbotGUI:
    """Tkinter chat interface that delegates question matching to ``FAQEngine``."""

    def __init__(self, root: tk.Tk, engine: FAQEngine) -> None:
        self.root = root
        self.engine = engine
        root.title("FAQ Chatbot")
        root.geometry("720x520")
        root.minsize(520, 380)

        container = ttk.Frame(root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self.chat_history = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 10)
        )
        self.chat_history.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.chat_history.tag_configure("user", foreground="#1d4ed8", font=("Segoe UI", 10, "bold"))
        self.chat_history.tag_configure("bot", foreground="#047857", font=("Segoe UI", 10, "bold"))

        self.message_entry = ttk.Entry(container)
        self.message_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.message_entry.bind("<Return>", self.send_message)
        ttk.Button(container, text="Send", command=self.send_message).grid(row=1, column=1, sticky="ew")
        ttk.Button(container, text="Clear Chat", command=self.clear_chat).grid(
            row=2, column=1, sticky="e", pady=(8, 0)
        )

        self._append_message("Bot", "Welcome! Ask me a programming or technology question.", "bot")
        self.message_entry.focus_set()

    def _append_message(self, sender: str, message: str, tag: str) -> None:
        """Add a labeled message to the read-only conversation history."""
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender}: ", tag)
        self.chat_history.insert(tk.END, f"{message}\n\n")
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def send_message(self, _event: object = None) -> str:
        """Send the entry text to the engine and show its response."""
        message = self.message_entry.get().strip()
        if not message:
            return "break"
        self._append_message("You", message, "user")
        self.message_entry.delete(0, tk.END)
        response, _score = self.engine.get_response(message)
        self._append_message("Bot", response, "bot")
        return "break"

    def clear_chat(self) -> None:
        """Remove all messages and restore the chatbot's welcome message."""
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.delete("1.0", tk.END)
        self.chat_history.configure(state=tk.DISABLED)
        self._append_message("Bot", "Chat cleared. What would you like to know?", "bot")


def main() -> None:
    """Create the FAQ engine and launch the desktop application."""
    try:
        engine = FAQEngine(DATA_FILE)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("FAQ Chatbot Error", f"Unable to start the chatbot:\n{error}")
        root.destroy()
        return

    root = tk.Tk()
    FAQChatbotGUI(root, engine)
    root.mainloop()


if __name__ == "__main__":
    main()
