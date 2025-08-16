

# 📘 Pingdoc AI

Pingdoc AI is an **AI-powered educational assistant** that helps learners interact with PDF books in a smarter way. The chatbot can **read PDF books**, **answer user questions**, **conduct quizzes**, and provide a **personalized learning experience**.

---

## 🚀 Features

* 📂 **Upload PDF Books** – Extracts and processes book content.
* 🤖 **AI Chatbot** – Answers questions contextually from the PDF.
* 📝 **Quiz Generator** – Conducts quizzes automatically based on book content.
* 🎯 **Personalized Learning** – Provides adaptive learning experiences based on user interactions.
* 🔍 **Efficient Search** – Uses vector similarity search for fast and accurate results.

---

## 🛠️ Tech Stack

* **Frontend**: Bootstrap (Responsive UI)
* **Backend**: Python with Django
* **Database**: PostgreSQL
* **Vector DB**: FAISS (for semantic search and RAG)
* **AI/ML**: Open-source LLMs for Q/A, quiz generation, and learning recommendations

---

## ⚙️ Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/pingdoc-ai.git
   cd pingdoc-ai
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database**

   * Create a database (e.g., `pingdoc_ai`)
   * Update `settings.py` with your DB credentials

5. **Make migrations**

   ```bash
   python manage.py makemigrations
   ```

6. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Run the server**

   ```bash
   python manage.py runserver
   ```

7. **Access the app**
   Open your browser and visit: `http://127.0.0.1:8000/`

---

## 📊 Workflow

1. Upload a PDF book.
2. The system processes the content and stores embeddings in **FAISS DB**.
3. Ask questions → chatbot retrieves relevant context and answers.
4. Generate quizzes → AI creates personalized Q/A based on the content.
5. Track learning progress → system adapts quizzes & suggestions accordingly.

---



## 📌 Future Enhancements

* 🌐 Web scraping support for external learning material
* 📈 Advanced analytics on learning progress
* 🎙️ Voice-based Q/A chatbot
* 🧑‍🏫 Tutor mode with step-by-step explanations

---


