"""
Listening Assessment API
===========================================================
This module is fully independent. It uses Ollama (qwen2.5:3b) and its own local FAISS index.
"""
import os, io, json, random, re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_ollama import OllamaEmbeddings, OllamaLLM
import soundfile as sf

app = FastAPI(title="Listening Assessment API (Ollama)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

from gtts import gTTS

print("Initializing Ollama LLM...")
llm = OllamaLLM(model="qwen2.5:7b", format="json", base_url="http://45.194.3.86:11434")

class TopicRequest(BaseModel):
    topic: str

CURRENT_ASSESSMENT = {"audio_bytes": None, "questions": [], "answer_key": []}

def extract_json(text):
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        json_str = text[start:end+1]
        try: return json.loads(json_str)
        except: pass
    return None

@app.post("/generate_assessment")
def generate_assessment(request: TopicRequest):
    topic = request.topic.strip()
    if not topic or topic.lower() == "random": topic = random.choice(["Key Concepts", "Important Definitions", "Main Ideas"])
    
    prompt = f"""
    You are an expert teacher. Generate a VERY SHORT conversational script between two people about the topic '{topic}'.
    Then, generate 5 Multiple Choice Questions based ONLY on the script.
    Return ONLY a valid JSON object with this exact structure (Do not add any other text):
    {{
      "script": "The spoken conversation...",
      "questions": [
        {{ "id": 1, "question": "What is...?", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "B" }}
      ]
    }}
    """
    try:
        response_text = llm.invoke(prompt)
        result = extract_json(response_text)
        if not result or "script" not in result or "questions" not in result: raise ValueError("JSON parse failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama generation failed: {e}")
    
    try:
        tts = gTTS(text=result["script"], lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        CURRENT_ASSESSMENT["audio_bytes"] = audio_fp.read()
    except Exception as e: raise HTTPException(status_code=500, detail=f"Audio generation failed: {e}")

    CURRENT_ASSESSMENT["questions"] = []
    CURRENT_ASSESSMENT["answer_key"] = []
    for q in result["questions"]:
        CURRENT_ASSESSMENT["questions"].append({"id": q.get("id", 1), "question": q.get("question", ""), "options": q.get("options", {})})
        CURRENT_ASSESSMENT["answer_key"].append({"id": q.get("id", 1), "correct_answer": q.get("correct_answer", "A")})
    return {"status": "success", "topic": topic, "questions": CURRENT_ASSESSMENT["questions"]}

@app.get("/audio")
def get_audio():
    if not CURRENT_ASSESSMENT["audio_bytes"]: raise HTTPException(status_code=404, detail="No audio available.")
    return StreamingResponse(io.BytesIO(CURRENT_ASSESSMENT["audio_bytes"]), media_type="audio/mpeg")

@app.get("/answer_key")
def get_answer_key():
    return {"answer_key": CURRENT_ASSESSMENT["answer_key"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8003, reload=True)
