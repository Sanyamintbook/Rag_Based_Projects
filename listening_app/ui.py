import streamlit as st
import requests
import json

st.set_page_config(page_title="Listening Assessment", layout="centered")
st.title("🎧 Listening Comprehension Assessment")

API_URL = "http://127.0.0.1:8003"

topic = st.text_input("Enter a science topic (e.g. Photosynthesis) or leave blank for a random topic:")

if st.button("Generate Assessment"):
    with st.spinner("Generating audio and questions using AI..."):
        try:
            res = requests.post(f"{API_URL}/generate_assessment", json={"topic": topic})
            if res.status_code == 200:
                st.session_state.assessment = res.json()
                st.session_state.submitted = False
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Failed to connect: {e}")

if "assessment" in st.session_state:
    data = st.session_state.assessment
    st.success(f"Assessment generated for topic: {data['topic']}")
    
    st.write("### 1. Listen to the Audio")
    st.audio(f"{API_URL}/audio", format="audio/mpeg")
    
    st.write("### 2. Answer the Questions")
    
    user_answers = {}
    for q in data["questions"]:
        st.write(f"**Q{q['id']}: {q['question']}**")
        options = []
        for key, value in q["options"].items():
            options.append(f"{key}: {value}")
        
        choice = st.radio(f"Select answer for Q{q['id']}", options, key=f"q_{q['id']}")
        user_answers[q['id']] = choice[0] # The letter
        
    if st.button("Submit Answers"):
        st.session_state.submitted = True
        try:
            ans_res = requests.get(f"{API_URL}/answer_key")
            if ans_res.status_code == 200:
                answer_key = ans_res.json()["answer_key"]
                
                score = 0
                st.write("### Results")
                for key_obj in answer_key:
                    q_id = key_obj["id"]
                    correct = key_obj["correct_answer"]
                    user_ans = user_answers.get(q_id, "")
                    
                    if user_ans == correct:
                        st.success(f"Q{q_id}: Correct! ({correct})")
                        score += 1
                    else:
                        st.error(f"Q{q_id}: Incorrect. You answered {user_ans}. Correct answer is {correct}.")
                        
                st.write(f"## Final Score: {score} / {len(answer_key)}")
        except Exception as e:
            st.error(f"Failed to fetch answer key: {e}")
