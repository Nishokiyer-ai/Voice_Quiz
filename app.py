import streamlit as st
from working import generate_question_and_check_answer, speak
import json
import uuid

st.title("🎤 Voice-Based Quiz Generator")

NUM_QUESTIONS = 5

# --- SESSION STATE INIT ---
if 'quiz_session_id' not in st.session_state:
    st.session_state.quiz_session_id = str(uuid.uuid4())
if 'questions' not in st.session_state:
    st.session_state.questions = []
    st.session_state.user_choice = []
    st.session_state.submitted = []
    st.session_state.current_q = 0
    st.session_state.finished = False
    st.session_state.prev_questions = set()
    st.session_state.correct = 0
    st.session_state.incorrect = 0
    st.session_state.show_history = False

# --- START QUIZ ---
if st.button(f"Start {NUM_QUESTIONS}-Question Quiz") or (not st.session_state.questions and not st.session_state.finished):
    st.session_state.quiz_session_id = str(uuid.uuid4())
    st.session_state.questions = []
    st.session_state.user_choice = []
    st.session_state.submitted = []
    st.session_state.current_q = 0
    st.session_state.finished = False
    st.session_state.prev_questions = set()
    st.session_state.correct = 0
    st.session_state.incorrect = 0
    st.session_state.show_history = False
    # Generate the first unique question
    while True:
        quiz_json = generate_question_and_check_answer()
        try:
            quiz = json.loads(quiz_json)
        except Exception:
            quiz = {"question": "Error: Could not parse question.", "options": [], "answer": "", "explanation": ""}
        q_text = quiz.get('question', '').strip()
        if q_text and q_text not in st.session_state.prev_questions:
            st.session_state.prev_questions.add(q_text)
            break
    st.session_state.questions.append(quiz)
    st.session_state.user_choice.append(None)
    st.session_state.submitted.append(False)

# --- MAIN QUIZ LOGIC ---
def render_quiz_view():
    if st.session_state.questions and not st.session_state.finished and not st.session_state.show_history:
        qidx = st.session_state.current_q
        # Generate a new unique question if needed
        if qidx >= len(st.session_state.questions):
            tries = 0
            while tries < 10:
                quiz_json = generate_question_and_check_answer()
                try:
                    quiz = json.loads(quiz_json)
                except Exception:
                    quiz = {"question": "Error: Could not parse question.", "options": [], "answer": "", "explanation": ""}
                q_text = quiz.get('question', '').strip()
                if q_text and q_text not in st.session_state.prev_questions:
                    st.session_state.prev_questions.add(q_text)
                    break
                tries += 1
            st.session_state.questions.append(quiz)
            st.session_state.user_choice.append(None)
            st.session_state.submitted.append(False)
        quiz = st.session_state.questions[qidx]
        options = quiz.get("options", [])
        submitted = st.session_state.submitted[qidx]
        user_choice = st.session_state.user_choice[qidx]
        session_id = st.session_state.quiz_session_id

        st.markdown(f"<h4>Question {qidx+1}/{NUM_QUESTIONS}:</h4>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:18px; margin-bottom:10px;'>{quiz.get('question', '')}</div>", unsafe_allow_html=True)
        st.write(":blue[Choose your answer:]")
        if not isinstance(options, list) or len(options) == 0:
            st.warning("No options available for this question. Please restart the quiz or try the next question.")
            options = ["Option 1 (N/A)", "Option 2 (N/A)"]
        if not submitted:
            user_choice = st.radio("", options, key=f"quiz_options_{session_id}_{qidx}", index=options.index(user_choice) if user_choice in options else 0)
            st.session_state.user_choice[qidx] = user_choice
        else:
            st.radio("", options, key=f"quiz_options_{session_id}_{qidx}_disabled", index=options.index(user_choice) if user_choice in options else 0, disabled=True)

        # --- VALIDATION ---
        if submitted:
            correct_answer = quiz.get("answer", "")
            user_answer = st.session_state.user_choice[qidx]
            explanation = quiz.get('explanation', '')
            if user_answer == correct_answer:
                st.markdown(f"<span style='color:green;font-weight:bold;'>Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:red;font-weight:bold;'>Incorrect.</span>", unsafe_allow_html=True)
            st.markdown(f"<b>Your answer:</b> {user_answer}<br><b>Correct answer:</b> {correct_answer}<br><b>Explanation:</b> <span style='color:#333;'>{explanation}</span>", unsafe_allow_html=True)

        # --- RECTANGLE BOX FOR RULES ONLY (rendered only once) ---
        rules_html = """
            <div style='text-align:left; margin:10px 0;'><b>Rules of quiz</b><br>
            1. Click submit to validate your answer.<br>
            2. Click next to navigate to next question.<br>
            3. Click history to view all your answers after finishing the quiz.</div>
        """
        st.markdown(f"""
            <div style='border:2px solid #4F8BF9; border-radius:10px; padding:20px; margin:20px 0; background-color:#f7fafd;'>
                {rules_html}
            </div>
        """, unsafe_allow_html=True)

        # --- BUTTONS ---
        can_submit = not submitted and st.session_state.user_choice[qidx] is not None
        can_next = submitted and st.session_state.current_q < NUM_QUESTIONS - 1
        can_prev = st.session_state.current_q > 0
        can_history = all(st.session_state.submitted) and len(st.session_state.submitted) == NUM_QUESTIONS
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            prev_btn = st.button("Previous", key=f"main_prev_btn_{session_id}_{qidx}", disabled=not can_prev)
        with col2:
            submit_btn = st.button("Submit", key=f"main_submit_btn_{session_id}_{qidx}", disabled=not can_submit)
        with col3:
            next_btn = st.button("Next", key=f"main_next_btn_{session_id}_{qidx}", disabled=not can_next)
        with col4:
            history_btn = st.button("History", key=f"main_history_btn_{session_id}", disabled=not can_history)
            if history_btn and can_history:
                st.session_state.show_history = True
                st.experimental_rerun()

        # --- SUBMIT LOGIC ---
        if submit_btn and can_submit and not submitted:
            st.session_state.submitted[qidx] = True
            correct_answer = quiz.get("answer", "")
            explanation = quiz.get('explanation', '')
            if st.session_state.user_choice[qidx] == correct_answer:
                st.session_state.correct += 1
                speak("Correct! " + explanation)
            else:
                st.session_state.incorrect += 1
                speak(f"Incorrect. The correct answer is: {correct_answer}. {explanation}")
            st.experimental_rerun()

        # --- NEXT LOGIC ---
        if next_btn and submitted:
            if st.session_state.current_q < NUM_QUESTIONS - 1:
                st.session_state.current_q += 1
            st.experimental_rerun()

        # --- PREVIOUS LOGIC ---
        if prev_btn and st.session_state.current_q > 0:
            st.session_state.current_q -= 1
            st.experimental_rerun()

def render_history_view():
    if st.session_state.show_history:
        session_id = st.session_state.quiz_session_id
        st.write("### Question & Answer History:")
        all_correct = st.session_state.correct == NUM_QUESTIONS
        for idx, quiz in enumerate(st.session_state.questions):
            user_ans = st.session_state.user_choice[idx]
            correct_ans = quiz['answer']
            result = "✅" if user_ans == correct_ans else "❌"
            st.markdown(f"""
                <div style='border:2px solid #4F8BF9; border-radius:10px; padding:20px; margin:20px 0; background-color:#f7fafd;'>
                    <b>Q{idx+1}:</b> {quiz['question']}<br>
                    <b>Your answer:</b> {user_ans} {result}<br>
                    <b>Correct answer:</b> {correct_ans}<br>
                    <b>Explanation:</b> <span style='color:#333;'>{quiz['explanation']}</span>
                </div>
            """, unsafe_allow_html=True)
        if all_correct:
            st.success("🎉 All the best! You got all answers correct!")
        else:
            st.warning("Better luck next time!")
        st.markdown("<h3 style='color: #4F8BF9;'>Thank you for participating in the quiz!</h3>", unsafe_allow_html=True)
        if st.button("Thank You", key=f"thank_you_btn_{session_id}"):
            st.session_state.questions = []
            st.session_state.user_choice = []
            st.session_state.submitted = []
            st.session_state.correct = 0
            st.session_state.incorrect = 0
            st.session_state.current_q = 0
            st.session_state.finished = False
            st.session_state.prev_questions = set()
            st.session_state.show_history = False
            st.session_state.quiz_session_id = str(uuid.uuid4())
            st.experimental_rerun()

# Main quiz rendering logic
if st.session_state.get("show_history", False):
    render_history_view()
else:
    render_quiz_view()