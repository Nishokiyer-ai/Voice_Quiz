# Voice-Based Quiz Generator

This project is an interactive voice-based quiz generator that uses LLM APIs (Groq/OpenAI), speech recognition, and text-to-speech to create and conduct quizzes from generated questions.

## Features
- Generates multiple-choice quiz questions using LLM APIs
- Conducts quizzes with voice feedback (TTS)
- Accepts answers via UI (radio buttons)
- Provides immediate feedback and explanations
- Supports navigation (Next, Previous, Submit)

## Requirements
- Python 3.8+
- [Groq API Key](https://console.groq.com/keys) (or OpenAI API Key if using OpenAI)
- Windows OS (for pyttsx3 TTS)

## Installation
1. **Clone the repository or copy the project files.**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   If you don't have a `requirements.txt`, install manually:
   ```bash
   pip install streamlit openai python-dotenv pyttsx3 SpeechRecognition
   ```
3. **Set up your `.env` file:**
   - Create a file named `.env` in the project root.
   - Add your Groq API key:
     ```
     groq_api_key=YOUR_GROQ_API_KEY
     ```

## Running the App
1. **Activate your Python environment (if using venv):**
   ```bash
   .venv\Scripts\activate
   ```
2. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```
3. **Open the provided local URL in your browser.**

## Usage
- Click the `Start 5-Question Quiz` button.
- Listen to the question (TTS will read it aloud).
- Select your answer and click `Submit`.
- Use `Next` and `Previous` to navigate.
- At the end, see your results.

## Troubleshooting
- If TTS (voice) does not work, ensure your system audio is enabled and pyttsx3 is installed.
- If you see `Error: Could not parse question.`, try restarting the quiz.
- For API errors, check your `.env` key and internet connection.

## Customization
- To change the number of questions, edit `NUM_QUESTIONS` in `app.py`.
- To use OpenAI instead of Groq, update the API key and endpoint in `working.py`.

---

**Enjoy your interactive voice-based quiz experience!**
