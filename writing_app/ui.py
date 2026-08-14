import streamlit as st
import requests

st.set_page_config(page_title="Writing Assistant", layout="wide")
st.title("📝 AI Writing Assistant")

API_URL = "http://127.0.0.1:8005"

st.write("Write an essay or short story below, and AI will provide feedback on your grammar, structure, and vocabulary.")

essay = st.text_area("Your Essay:", height=300, placeholder="Start typing here...")

if st.button("Get AI Feedback"):
    if essay:
        with st.spinner("Analyzing your writing..."):
            try:
                res = requests.post(f"{API_URL}/analyze", json={"text": essay})
                if res.status_code == 200:
                    feedback = res.json()["feedback"]
                    st.success("Analysis Complete!")
                    st.write("### AI Feedback")
                    st.write(feedback)
                else:
                    st.error("Error from AI service.")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
    else:
        st.warning("Please enter some text first.")
