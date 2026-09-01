# CodeAlpha FAQ Chatbot
A desktop chatbot application that answers frequently asked questions using natural language processing and similarity matching, developed as part of the CodeAlpha Artificial Intelligence Internship.
Repository: (https://github.com/obed-asamoah01/CodeAlpha_FAQChatbot)



## Project Objective
The goal of this project is to build a functional FAQ Chatbot that can understand a user's question in natural language and respond with the most relevant answer from a predefined knowledge base. The project demonstrates core natural language processing techniques, including text preprocessing and similarity-based intent matching, applied within a simple, user-friendly desktop chat interface.



## Features
- Curated FAQ knowledge base of question-and-answer pairs on general programming and technology topics
- Text preprocessing pipeline (tokenization, lowercasing, stopword removal, lemmatization)
- Similarity-based question matching using TF-IDF vectorization and cosine similarity
- Returns the most relevant FAQ answer based on the user's input, regardless of exact phrasing
- Simple, interactive chat-style user interface
- Confidence threshold handling: informs the user when no sufficiently similar FAQ is found
- Scrollable conversation history within the chat window
- Lightweight desktop application; no browser or server required



## Technologies
| Category | Tool / Library |
|---|---|
| Language | Python 3 |
| GUI Framework | Tkinter (tkinter, ttk) |
| NLP Preprocessing | NLTK (tokenization, stopwords, lemmatization) |
| Similarity Matching | scikit-learn (TF-IDF Vectorizer, cosine similarity) |
| Data Storage | JSON (FAQ dataset) |



## How It Works
1. A predefined set of frequently asked questions and their answers is stored in a structured JSON file.
2. On startup, each stored question is preprocessed (tokenized, lowercased, stripped of stopwords and lemmatized) using NLTK.
3. The preprocessed questions are converted into TF-IDF vectors using scikit-learn.
4. When the user types a question into the chat interface, it undergoes the same preprocessing and is vectorized using the same TF-IDF model.
5. Cosine similarity is calculated between the user's question and every FAQ question in the knowledge base.
6. The FAQ with the highest similarity score above a defined confidence threshold is selected, and its answer is displayed as the chatbot's response.
7. If no FAQ meets the similarity threshold, the chatbot responds indicating it could not find a confident match.



## Installation
### Prerequisites
- Python 3.8 or higher

### Steps
1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd CodeAlpha_FAQChatbot
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download required NLTK data (only needed once):
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
   ```



## Usage
1. Run the application:
   ```bash
   python faq_chatbot_gui.py
   ```
2. Type a question into the input box at the bottom of the chat window.
3. Press Enter or click Send to submit the question.
4. The chatbot's best-matching answer appears in the conversation history above.
5. Continue the conversation by asking further questions.



## Screenshots
Chat Interface
[Chat interface](screenshots/chat_interface.png)

Sample Conversation
[Sample conversation](screenshots/sample_conversation.png)


## Limitations

- The chatbot can only answer questions covered by its predefined FAQ dataset; it does not generate new answers dynamically.
- Matching accuracy depends on the similarity threshold and the phrasing overlap between the user's question and the stored FAQs; significantly different phrasing may not be matched correctly.
- No conversational memory is implemented; each question is evaluated independently of prior messages.
- The FAQ dataset must be manually updated to expand the chatbot's knowledge; there is no self-learning mechanism.
- Performance and accuracy have not been benchmarked against large-scale or highly ambiguous FAQ sets.



## Author
Obed Asamoah
GitHub: https://github.com/obed-asamoah01



