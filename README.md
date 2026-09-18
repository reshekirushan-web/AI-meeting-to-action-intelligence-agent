# 🎤 AI Meeting Assistant

An AI-powered meeting assistant that uses **Google Gemini** to analyze meeting audio, identify speakers, and extract important information such as tasks, commitments, promises, and deadlines.

## 🚀 Features

* 🎙️ Record or upload meeting audio
* 🤖 Analyze meeting audio using Google Gemini
* 📝 Generate meeting transcripts
* 👤 Identify speakers
* ✅ Detect tasks and commitments
* 📅 Extract deadlines
* 📋 Display results in a simple Streamlit interface

## 🛠️ Technologies Used

* **Python**
* **Streamlit** – Web application interface
* **Google Gemini API** – AI-powered audio analysis
* **Streamlit WebRTC** – Voice/audio recording
* **PyAV** – Audio and media processing

## 📂 Project Structure

```text
AI-Meeting-Assistant/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd AI-Meeting-Assistant
```

### 2. Install the required packages

```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API Key

Create an environment variable named:

```text
GEMINI_API_KEY
```

Or configure it through Streamlit secrets.

Example:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

**Do not upload your API key to GitHub.**

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔄 How It Works

```text
Meeting Audio
      ↓
Voice Recording / Upload
      ↓
Google Gemini API
      ↓
Audio & Conversation Analysis
      ↓
Speaker Identification
      ↓
Task & Commitment Detection
      ↓
Deadlines & Important Decisions
      ↓
Meeting Summary
```

## 📋 Example Output

| Speaker   | Task / Commitment        | Deadline |
| --------- | ------------------------ | -------- |
| Speaker 1 | Complete database module | Friday   |
| Speaker 2 | Prepare presentation     | Tomorrow |
| Speaker 1 | Send project report      | Monday   |

## 🎯 Use Cases

* Team meetings
* College project meetings
* Business meetings
* Online discussions
* Project management
* Meeting documentation

## 🔮 Future Improvements

* Real-time meeting transcription
* More accurate speaker identification
* Voice-based participant recognition
* Automatic meeting summaries
* Email/task reminders
* Export reports as PDF
* Calendar integration
* Multi-language support

## 👨‍💻 Project

This project is developed as an **AI-powered meeting assistant** using Google Gemini and Streamlit.

---

⭐ If you find this project useful, consider giving the repository a star!
