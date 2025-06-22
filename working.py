import openai
import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv

# Initialize TTS engine
engine = pyttsx3.init()

# Load environment variables from .env file
load_dotenv()

# Groq API setup

def speak(text):
    try:
        if engine._inLoop:
            engine.endLoop()
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        pass  # Prevent crash if run loop already started

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."

def generate_question():
    api_key = os.getenv("groq_api_key") or "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"
    client = openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "system", "content": "Generate a simple quiz question"}]
    )
    return response.choices[0].message.content

def generate_question_and_check_answer(user_answer=None):
    api_key = os.getenv("groq_api_key") or "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"
    client = openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    import json
    if user_answer is None:
        prompt = (
            "Generate a multiple-choice quiz question with 4 options. "
            "Provide the correct answer and a brief explanation in JSON format as: "
            '{"question": "<question>", "options": ["<option1>", "<option2>", "<option3>", "<option4>"], "answer": "<correct_option>", "explanation": "<explanation>"}'
            " Return only valid JSON. Do not include any text before or after the JSON. If you cannot comply, return a default valid JSON with a simple math question."
        )
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        import re
        import json
        # Try to extract JSON from the response
        match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
        if match:
            try:
                # Validate JSON
                json.loads(match.group(0))
                return match.group(0)
            except Exception:
                pass
        # If failed, try to parse the whole response as JSON
        try:
            return json.dumps(json.loads(response.choices[0].message.content))
        except Exception:
            # Return a default valid question if all else fails
            return '{"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4", "explanation": "2 + 2 equals 4."}'
    else:
        # Check the user's answer
        prompt = (
            f"The user answered: '{user_answer}'. "
            "Given the quiz question and correct answer, reply with 'Correct' or 'Incorrect' and a short explanation."
        )
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content

def run_quiz(num_questions=20):
    results = []
    for i in range(num_questions):
        quiz_json = generate_question_and_check_answer()
        import json
        try:
            quiz = json.loads(quiz_json)
        except Exception:
            quiz = {"question": "Error: Could not parse question.", "options": [], "answer": "", "explanation": ""}
        print(f"Q{i+1}: {quiz['question']}")
        print("Options:", quiz.get('options', []))
        # For demo, select the correct answer automatically
        user_answer = quiz.get('answer', '')
        feedback = generate_question_and_check_answer(user_answer)
        results.append({
            "question": quiz.get('question', ''),
            "answer": user_answer,
            "feedback": feedback
        })
    return results