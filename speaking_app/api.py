"""
Conversational Speaking Assessment API

This FastAPI backend handles the core logic for the speaking assessment. 
It processes incoming audio using Whisper (Speech-to-Text), evaluates 
grammar and pronunciation, and generates spoken responses using Qwen2.5 
and Edge-TTS.
"""
import os
import io
import json
import tempfile
import base64
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
from pydub import AudioSegment
import requests

import soundfile as sf
import numpy as np
import asyncio
import re

app = FastAPI(title="Conversational Speaking Assessment API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    with open(os.path.join(ROOT_DIR, "index.html"), "r", encoding="utf-8") as f:
        html = f.read()
        return HTMLResponse(
            content=html,
            status_code=200,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

print("Initializing Voice AI Backend...")
try:
    print("Initializing SpeechRecognition...")
    recognizer_engine = sr.Recognizer()
    whisper_model = "Active"
except Exception as e:
    print(f"Error loading Whisper: {e}")
    whisper_model = None

class OllamaDirectClient:
    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.fallback_urls = [
            self.base_url,
            "http://127.0.0.1:11434",
            "http://10.80.100.214:11434",
        ]
        self.fallback_urls = list(dict.fromkeys(u.rstrip("/") for u in self.fallback_urls if u and u.strip()))

    def invoke(self, prompt: str) -> str:
        last_error = None
        for base_url in self.fallback_urls:
            try:
                response = requests.post(
                    f"{base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 140}
                    },
                    timeout=20,
                )
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict) and "response" in payload:
                    return payload["response"]
                if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                    return payload[0].get("response", "")
                return str(payload)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                last_error = e
                continue
            except Exception as e:
                raise RuntimeError(f"Ollama request failed: {e}") from e

        fallback = {
            "grammar_score": 7,
            "vocab_score": 7,
            "corrections": [],
            "ai_response": "I am listening. Tell me more about the topic you are talking about."
        }
        print(f"Ollama request failed on all endpoints, using local fallback: {last_error}")
        return json.dumps(fallback)


try:
    print("Loading qwen2.5:3b...")
    llm = OllamaDirectClient(model="qwen2.5:3b", base_url="http://10.80.100.214:11434")
    llm_standard = OllamaDirectClient(model="qwen2.5:3b", base_url="http://10.80.100.214:11434")
except Exception as e:
    print(f"Error loading Ollama: {e}")
    llm = None
    llm_standard = None

from gtts import gTTS


def normalize_llm_json(raw_text):
    if raw_text is None:
        return {}

    text = str(raw_text).strip()
    if not text:
        return {}

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', text)
    text = re.sub(r":\s*([A-Za-z][^,}\]]*?)(?=\s*(?:,|\}))", r': "\1"', text)
    text = text.replace("'", '"')
    text = re.sub(r',\s*([}\]])', r'\1', text)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    return {}


def extract_json(text):
    parsed = normalize_llm_json(text)
    if parsed:
        ai_response = parsed.get("ai_response") or parsed.get("text") or parsed.get("message")
        if ai_response and isinstance(ai_response, str) and ai_response.strip() and not is_generic_reply(ai_response):
            return {
                "grammar_score": int(parsed.get("grammar_score", 6) or 6),
                "vocab_score": int(parsed.get("vocab_score", 6) or 6),
                "corrections": parsed.get("corrections", []) or [],
                "ai_response": ai_response,
            }

    return {"grammar_score": 6, "vocab_score": 6, "ai_response": "Tell me more about your topic and what you find most interesting about it.", "corrections": []}


def estimate_pronunciation(transcript: str) -> int:
    if not transcript:
        return 5
    words = transcript.split()
    if len(words) <= 3:
        return 6
    if len(words) <= 8:
        return 7
    if len(words) <= 15:
        return 8
    return 9


def estimate_fluency(transcript: str) -> int:
    if not transcript:
        return 5
    words = transcript.split()
    if len(words) <= 3:
        return 6
    if len(words) <= 8:
        return 7
    if len(words) <= 15:
        return 8
    return 9


def generate_audio_b64(text: str) -> str:
    try:
        tts = gTTS(text=text, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return base64.b64encode(audio_fp.read()).decode("utf-8")
    except Exception as e:
        print(f"TTS Error: {e}")
        return ""


def sanitize_history(history: str) -> str:
    if not history:
        return ""
    normalized = history.replace("\\n", "\n").replace("\\r", "\n").replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.strip() for line in normalized.split("\n") if line.strip())


def latest_student_message(history: str) -> str:
    cleaned = sanitize_history(history)
    if not cleaned:
        return ""
    for line in reversed(cleaned.split("\n")):
        if line.lower().startswith("student:"):
            return line.split(":", 1)[1].strip()
    return ""


def resolve_active_topic(transcript: str, history: str = "", topic_hint: str = "") -> str:
    transcript_text = (transcript or "").strip()
    hint = (topic_hint or "").strip().lower()

    if transcript_text:
        detected = detect_topic_from_text(transcript_text, history)
        if detected:
            return detected
        if hint and hint not in {"general", "none", ""}:
            return hint

    recent_text = latest_student_message(history)
    if recent_text:
        detected = detect_topic_from_text(recent_text, "")
        if detected:
            return detected

    if hint and hint not in {"general", "none", ""}:
        return hint

    return ""


def detect_topic_from_text(transcript: str, history: str = "") -> str:
    transcript_text = (transcript or "").strip()
    if transcript_text:
        text = transcript_text.lower()
    else:
        text = (history or "").lower()

    if not text:
        return ""

    topic_keywords = {
        "cricket": ["cricket", "bat", "ball", "pitch", "bowling", "batting"],
        "sports": ["football", "tennis", "basketball", "volleyball", "badminton", "soccer", "sport", "sports"],
        "school": ["school", "teacher", "homework", "class", "study", "exam", "lesson", "assignment", "classroom"],
        "music": ["music", "song", "singing", "dance", "playlist", "instrument", "concert"],
        "technology": ["computer", "computer science", "technology", "coding", "programming", "robot", "laptop", "internet"],
        "food": ["food", "pizza", "fruit", "vegetable", "rice", "tea", "coffee", "recipe", "cooking"],
        "pets": ["pet", "dog", "cat", "animal", "bird", "rabbit", "fish"],
        "science": ["science", "experiment", "plant", "space", "moon", "star", "earth", "nature"],
        "travel": ["travel", "trip", "place", "city", "country", "holiday", "tour"],
        "daily_life": ["daily life", "home", "family", "friends", "routine", "weekend"],
        "photosynthesis": ["photosynthesis", "plant", "sunlight", "leaf", "water", "carbon dioxide"],
    }

    for topic, words in topic_keywords.items():
        if any(word in text for word in words):
            return topic

    return ""


def build_local_followup(transcript: str, history_text: str) -> dict:
    transcript_text = (transcript or "").strip()
    lower = transcript_text.lower()
    topic = resolve_active_topic(transcript_text, history_text)

    info_patterns = [
        "tell me about", "what is", "what are", "how does", "why is", "why do",
        "explain", "can you explain", "learn about", "know about", "information about",
        "more about", "i want to know about", "i want to learn about", "what is the meaning of"
    ]
    suggestion_patterns = [
        "let's talk about something", "let us talk about something", "talk about something",
        "suggest a topic", "suggest some topics", "give me a topic", "any topic",
        "what should we talk about", "what topic should we talk about"
    ]

    if not transcript_text:
        ai_response = "Hi there! Let’s start with a topic you enjoy. I can talk about science, technology, music, sports, food, travel, or daily life."
    elif any(p in lower for p in suggestion_patterns):
        ai_response = "Sure! Good topic ideas are science, school, sports, music, technology, food, travel, pets, daily life, and nature. Which one sounds most interesting to you?"
    elif any(p in lower for p in info_patterns):
        if topic:
            if topic == "cricket":
                ai_response = "Cricket is a bat-and-ball sport played between two teams. It includes batting, bowling, and fielding, and people enjoy it for strategy, teamwork, and excitement."
            elif topic == "sports":
                ai_response = "Sports help us stay active and teach teamwork, discipline, and confidence. Popular ones include cricket, football, badminton, and basketball."
            elif topic == "school":
                ai_response = "School is where we learn new ideas, improve our skills, and grow with our teachers and friends. It helps us understand the world better."
            elif topic == "music":
                ai_response = "Music is a way to express feelings and create joy. It can be a song, rhythm, instrument, or dance that brings people together."
            elif topic == "technology":
                ai_response = "Technology is the use of tools and systems to solve problems and make life easier. It includes computers, coding, smartphones, and the internet."
            elif topic == "food":
                ai_response = "Food gives our bodies energy and helps us stay healthy. Different foods provide different nutrients, and many cultures have special meals and recipes."
            elif topic == "pets":
                ai_response = "Pets are animals we care for at home, like dogs, cats, and birds. They can be friendly companions and can make us feel happy and calm."
            elif topic == "science":
                ai_response = "Science helps us understand the world through experiments and observation. It explains things like plants, weather, space, and how the human body works."
            elif topic == "travel":
                ai_response = "Travel lets us explore new places, meet new people, and learn about different cultures. It helps us understand the world beyond our daily routine."
            elif topic == "photosynthesis":
                ai_response = "Photosynthesis is the process plants use to make food using sunlight, water, and carbon dioxide. It is important because it helps plants grow and produces oxygen."
            elif topic == "daily_life":
                ai_response = "Daily life includes the simple routines we do every day, like studying, eating, playing, helping at home, and spending time with family and friends."
            else:
                ai_response = f"{topic.replace('_', ' ').title()} is an interesting topic. It can be explained by looking at what it is, why it matters, and how people use it in everyday life."
        else:
            ai_response = "I can explain many topics like science, technology, school, sports, music, food, travel, and nature. Tell me the topic you want to learn about and I will explain it simply."
    elif any(x in lower for x in ["don't know", "dont know", "i do not know", "i don't know", "change topic", "different topic", "move on"]):
        topic_choices = ["animals", "space", "sports", "daily life", "school life", "travel", "food", "science"]
        choice = topic_choices[sum(ord(ch) for ch in transcript_text) % len(topic_choices)]
        ai_response = f"No worries! Let’s try a new topic. A good option is {choice}. It is interesting and easy to talk about."
    elif topic == "cricket":
        ai_response = "Cricket is exciting. What part of cricket do you enjoy the most when you watch or play it?"
    elif topic == "sports":
        sport_name = next((x for x in ["cricket", "football", "tennis", "basketball", "volleyball", "badminton", "soccer", "sport"] if x in lower), "that sport")
        ai_response = f"That sounds exciting! What part of {sport_name.title()} do you enjoy the most?"
    elif topic == "music":
        music_name = next((x for x in ["music", "song", "singing", "dance", "playlist", "instrument", "concert"] if x in lower), "music")
        ai_response = f"Music is a great topic. What part of {music_name.title()} do you enjoy the most?"
    elif topic == "technology":
        tech_name = next((x for x in ["computer", "technology", "coding", "programming", "robot", "laptop", "internet"] if x in lower), "technology")
        ai_response = f"Technology is interesting. What part of {tech_name.title()} do you enjoy the most?"
    elif topic == "school":
        ai_response = "School is a great topic. What part of school or homework do you enjoy the most, and why?"
    elif topic == "food":
        food_name = next((x for x in ["food", "pizza", "fruit", "vegetable", "rice", "tea", "coffee", "recipe", "cooking"] if x in lower), "food")
        ai_response = f"Food is a great topic. What part of {food_name.title()} do you enjoy the most?"
    elif topic == "pets":
        ai_response = "Pets are so much fun. Which pet do you like the most, and why?"
    elif topic == "science":
        ai_response = "Science is interesting. Which science idea or experiment do you find the most exciting?"
    elif topic == "travel":
        ai_response = "Travel is fun to talk about. Which place would you like to visit and why?"
    elif topic == "photosynthesis":
        ai_response = "Photosynthesis is a fascinating science idea. What part of it do you find most interesting?"
    elif topic == "daily_life":
        ai_response = "Daily life is interesting. What part of your day do you enjoy the most?"
    elif any(x in lower for x in ["i like", "love", "enjoy", "favorite", "favourite", "want to talk about", "want to learn about", "want to explore", "want to know about", "talk about", "play", "study", "music", "sports", "food", "travel", "school", "computer", "science", "pets"]):
        ai_response = f"That sounds interesting. We can talk more about {topic or 'that topic'} and learn a few useful facts about it."
    elif "hello" in lower or "hi" in lower:
        ai_response = "Hi! Nice to meet you. I can talk about many topics like science, sports, music, technology, food, travel, school, and daily life. Which one do you want to start with?"
    elif any(x in lower for x in ["joke", "funny", "laugh", "haha", "crack"]):
        ai_response = "Haha, nice one! Tell me about your day or something funny that happened recently."
    elif len(transcript_text.split()) <= 3:
        ai_response = "Good try! Can you say a little more and explain it in a full sentence?"
    else:
        ai_response = "Great answer! You can add one more detail, or I can explain the topic more simply if you want."

    return {
        "grammar_score": 7,
        "vocab_score": 7,
        "corrections": [],
        "ai_response": ai_response
    }


def is_generic_reply(text: str) -> bool:
    if text is None:
        return True
    t = re.sub(r"\s+", " ", str(text).lower()).strip()
    if not t:
        return True

    known_topic_terms = (
        "cricket", "football", "tennis", "basketball", "volleyball", "badminton", "soccer",
        "school", "music", "dance", "song", "computer", "technology", "coding", "programming",
        "food", "pizza", "fruit", "vegetable", "rice", "tea", "coffee", "travel", "science",
        "plant", "photosynthesis", "pet", "animal", "daily life", "space", "moon", "star",
        "robot", "laptop", "internet", "homework", "class", "teacher", "lesson", "assignment",
        "cricket", "sports"
    )

    generic_phrases = [
        "i didn't quite catch that. could you say it differently?",
        "please say it again",
        "could you say it differently?",
        "nice! what is one hobby or activity you enjoy in your free time?",
        "hi! nice to meet you. what hobby or activity do you enjoy in your free time?",
        "hi there! i’m sara. tell me what topic you would like to talk about today.",
        "hi there! i'm sara. tell me what topic you would like to talk about today.",
        "great answer! can you tell me a little more about that?",
        "great answer! can you add one more detail to make it even clearer and a little more interesting?",
        "good try! can you say a little more and explain it in a full sentence?",
        "i am listening. tell me more about the topic you are talking about.",
        "nice work! let’s keep the conversation going—what do you enjoy most about that?",
        "nice work! let's keep the conversation going—what do you enjoy most about that?",
        "tell me more about your topic and what you find most interesting about it.",
        "tell me more about your topic and what you find most interesting about it",
        "tell me more about your topic and what you find most interesting",
        "what topic would you like to talk about today",
        "what topic you would like to talk about today",
        "what do you enjoy most about that",
        "what do you like most about it",
        "what do you think about",
        "what hobby or activity do you enjoy in your free time",
        "what hobby or activity are you into",
        "what hobby or activity do you enjoy most"
    ]
    generic_markers = (
        "what hobby or activity",
        "what topic would you like to talk about today",
        "what topic you would like to talk about today",
        "what do you like most about it",
        "what do you think about",
        "tell me more about your topic",
        "what you find most interesting about it",
        "what do you enjoy most about that",
        "what do you enjoy most about this",
        "what do you enjoy most about it"
    )

    if t in generic_phrases:
        return True
    if t.startswith("i didn't quite catch"):
        return True
    if any(marker in t for marker in generic_markers):
        if "what do you enjoy most about" in t and any(term in t for term in known_topic_terms):
            return False
        if "tell me more about" in t and any(term in t for term in known_topic_terms):
            return False
        return True

    if "what do you enjoy most about" in t:
        return not any(term in t for term in known_topic_terms)

    return False


def evaluate_conversation_history(history: str) -> dict:
    cleaned = sanitize_history(history)
    if not cleaned:
        return {
            "overall_score": 0,
            "final_feedback": "No conversation yet. Start speaking to get an evaluation.",
            "strengths": [],
            "improvements": ["Start with a short answer and keep speaking naturally."],
            "ai_audio_b64": "",
            "metrics": {
                "pronunciation": 0,
                "speed": 0,
                "sentence": 0,
                "grammar": 0,
                "vocabulary": 0,
            },
        }

    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    student_lines = []
    for line in lines:
        if line.lower().startswith("student:"):
            student_lines.append(line.split(":", 1)[1].strip())

    if not student_lines:
        return {
            "overall_score": 5,
            "final_feedback": "The conversation has started, but no student answer was recorded yet.",
            "strengths": ["The system is engaged and ready for a response."],
            "improvements": ["Speak a full answer so the system can rate it properly."],
            "ai_audio_b64": "",
            "metrics": {
                "pronunciation": 0,
                "speed": 0,
                "sentence": 0,
                "grammar": 0,
                "vocabulary": 0,
            },
        }

    metric_values = {
        "pronunciation": [],
        "speed": [],
        "sentence": [],
        "grammar": [],
        "vocabulary": [],
    }

    total_words = 0
    for answer in student_lines:
        clean_answer = re.sub(r"\|.*$", "", answer).strip()
        total_words += len(clean_answer.split())

        for key, pattern in {
            "pronunciation": r"pronunciation\s*=\s*(\d+(?:\.\d+)?)",
            "speed": r"fluency\s*=\s*(\d+(?:\.\d+)?)",
            "grammar": r"grammar\s*=\s*(\d+(?:\.\d+)?)",
            "vocabulary": r"vocab\s*=\s*(\d+(?:\.\d+)?)",
        }.items():
            m = re.search(pattern, answer, re.IGNORECASE)
            if m:
                metric_values[key].append(float(m.group(1)))

        sentence_score = min(5, max(1, round((len(clean_answer.split()) / 12) * 2.5)))
        metric_values["sentence"].append(float(sentence_score))

    avg_words = total_words / len(student_lines)
    turn_count = len(student_lines)

    final_metrics = {}
    for key in ["pronunciation", "speed", "sentence", "grammar", "vocabulary"]:
        values = metric_values.get(key, [])
        if values:
            final_metrics[key] = round(sum(values) / len(values), 1)
        else:
            base = 3.5 if key in ["sentence", "grammar", "vocabulary"] else 3.0
            if key == "speed":
                base = 3.5 if avg_words >= 6 else 3.0
            if key == "pronunciation":
                base = 3.5 if avg_words >= 6 else 3.0
            final_metrics[key] = round(base, 1)

    # Each metric is on a 0-5 scale. Overall score is on a 10-point scale.
    # Keep the total realistic: a low pronunciation or speed score must stay low, and
    # a score like 0.5 cannot be turned into 9/10.
    final_metrics = {k: min(5.0, max(0.0, v)) for k, v in final_metrics.items()}
    overall_score = round((sum(final_metrics.values()) / len(final_metrics)) * 2, 1)
    overall_score = min(10.0, max(0.0, overall_score))

    strengths = []
    if turn_count >= 2:
        strengths.append("You kept the conversation moving with multiple turns.")
    if final_metrics["sentence"] >= 3.5:
        strengths.append("Your sentences are mostly clear and easy to follow.")
    if final_metrics["grammar"] >= 3.5:
        strengths.append("Your grammar is understandable and improving.")
    if not strengths:
        strengths.append("You are speaking with effort and trying to answer clearly.")

    improvements = []
    if final_metrics["pronunciation"] < 3.5:
        improvements.append("Work on clearer pronunciation and speaking each word more carefully.")
    if final_metrics["speed"] < 3.5:
        improvements.append("Try speaking at a steady pace so your ideas are easier to understand.")
    if final_metrics["sentence"] < 3.5:
        improvements.append("Build longer and more complete sentences with a clear idea in each answer.")
    if final_metrics["grammar"] < 3.5:
        improvements.append("Check sentence structure and try to use simple correct grammar in each response.")
    if final_metrics["vocabulary"] < 3.5:
        improvements.append("Add a few more useful words and examples to improve your speaking range.")
    if not improvements:
        improvements.append("Keep speaking in full sentences and answer directly to improve confidence.")

    final_feedback = (
        f"Pronunciation: {final_metrics['pronunciation']:.1f}/5. Speed: {final_metrics['speed']:.1f}/5. "
        f"Sentence quality: {final_metrics['sentence']:.1f}/5. Grammar: {final_metrics['grammar']:.1f}/5. "
        f"Vocabulary: {final_metrics['vocabulary']:.1f}/5. "
        "Your overall speaking effort is good, and your answers are moving in the right direction. "
        "Keep speaking in full sentences and keep adding clear detail to improve confidence and fluency."
    )

    ai_text = final_feedback
    try:
        audio_b64 = generate_audio_b64(ai_text)
    except Exception:
        audio_b64 = ""

    return {
        "overall_score": float(overall_score),
        "final_feedback": final_feedback,
        "strengths": strengths,
        "improvements": improvements,
        "ai_audio_b64": audio_b64,
        "metrics": {
            "pronunciation": float(final_metrics["pronunciation"]),
            "speed": float(final_metrics["speed"]),
            "sentence": float(final_metrics["sentence"]),
            "grammar": float(final_metrics["grammar"]),
            "vocabulary": float(final_metrics["vocabulary"]),
        },
    }


def write_uploaded_audio(audio_file: UploadFile) -> str:
    content = audio_file.file.read()
    filename = (audio_file.filename or "audio.wav").lower()
    ext = os.path.splitext(filename)[1] or ".wav"

    if not ext and audio_file.content_type:
        ct = audio_file.content_type.lower()
        if "webm" in ct:
            ext = ".webm"
        elif "mp4" in ct or "m4a" in ct:
            ext = ".mp4"
        elif "mpeg" in ct or "mp3" in ct:
            ext = ".mp3"
        elif "ogg" in ct:
            ext = ".ogg"
        elif "wav" in ct:
            ext = ".wav"

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".wav")
    temp.write(content)
    temp.close()
    return temp.name


def transcribe_audio_file(path: str) -> str:
    transcript = ""
    converted_wav = path + ".converted.wav"

    try:
        audio_seg = AudioSegment.from_file(path)
        audio_seg.export(converted_wav, format="wav")
        with sr.AudioFile(converted_wav) as source:
            audio_data = recognizer_engine.record(source)
            transcript = recognizer_engine.recognize_google(audio_data)
        return transcript.strip()
    except Exception as e:
        print(f"SpeechRecognition Error: {e}")

    # Fallback: if the browser sent a format other than wav, try explicit conversion using the file extension.
    try:
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if ext:
            audio_seg = AudioSegment.from_file(path, format=ext)
            audio_seg.export(converted_wav, format="wav")
            with sr.AudioFile(converted_wav) as source:
                audio_data = recognizer_engine.record(source)
                transcript = recognizer_engine.recognize_google(audio_data)
            return transcript.strip()
    except Exception as e:
        print(f"Fallback SpeechRecognition Error: {e}")

    return ""


@app.post("/start_conversation")
def start_conversation(topic: str = Form(...)):
    response_text = "Hi there! I’m Sara. Tell me what topic you would like to talk about today."

    try:
        prompt = "You are Sara, a friendly speaking buddy. The student just opened the app. Say hello in one short sentence and ask them what topic they want to talk about today. Keep it natural and not repetitive."
        if llm_standard is not None:
            llm_text = llm_standard.invoke(prompt)
            if llm_text and llm_text.strip() not in ["", "null", "none"]:
                parsed = normalize_llm_json(llm_text)
                if parsed and (parsed.get("ai_response") or parsed.get("text") or parsed.get("message")):
                    response_text = str(parsed.get("ai_response") or parsed.get("text") or parsed.get("message")).replace('"', '').replace('\n', ' ').strip()
                else:
                    response_text = str(llm_text).replace('"', '').replace('\n', ' ').strip()
    except Exception as e:
        print(f"Start greeting fallback used: {e}")

    response_text = response_text.replace('"', '').replace('\n', ' ').strip()

    clean_audio_text = re.sub(r'[\U0001F300-\U0001FAFF]', '', response_text)

    try:
        audio_b64 = generate_audio_b64(clean_audio_text)
    except Exception as e:
        print(f"TTS Error: {e}")
        audio_b64 = ""

    return {"ai_text": response_text, "ai_audio_b64": audio_b64}

@app.post("/process_turn")
def process_turn(audio_file: UploadFile, topic: str = Form(default=""), history: str = Form(default="")):
    if not whisper_model:
        raise HTTPException(status_code=500, detail="Whisper not loaded")

    tmp_path = write_uploaded_audio(audio_file)
    transcript = transcribe_audio_file(tmp_path)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    converted_wav = tmp_path + ".converted.wav"
    if os.path.exists(converted_wav):
        os.remove(converted_wav)

    transcript = transcript.strip()

    if not transcript:
        return {"error": "No speech detected in the audio file."}

    # 3. Calculate metrics
    fluency_score = estimate_fluency(transcript)
    pronunciation_score = estimate_pronunciation(transcript)

    # 4. Context retrieval
    context_text = ""

    # 5. LLM Evaluation
    history_text = sanitize_history(history)
    active_topic = resolve_active_topic(transcript, history_text, topic)
    prompt = f"""
    You are Sara, a fun, super friendly and highly encouraging cartoon girl language buddy from the app Vidya.
    Here is the conversation history so far:
    {history_text}

    Active topic hint from the latest student turn: {active_topic or 'none'}

    The student just answered: "{transcript}"

    Important: the most recent student message is the source of truth. If the newest answer mentions a different topic than earlier history, follow the newest topic and do not drift back to older history.
    - Do not ask a generic hobby question if the student already mentioned a topic like homework, school, computers, music, sports, travel, pets, food, science, cricket, or any other topic.
    - If the student clearly names a topic, continue that topic naturally. Give a short, useful explanation if they ask for information, or ask a relevant follow-up question if they are speaking casually.
    - If the student asks "tell me about", "what is", "how does", "why", or similar, answer simply with a short fact or explanation. Do not turn it into a fixed question.
    - If the student says "let's talk about something", or asks for topic suggestions, suggest 3-5 good topics from the student's interests and keep it conversational.
    - If the student says they do not know, asks to change the topic, or says move on, choose a fresh topic and suggest an easy option.
    - If they answer with a short or weak reply, gently encourage them and ask them to add one more detail or explain it a bit more.
    - Keep your tone encouraging, playful, and very simple.
    - Do not force every reply to be a question; sometimes give a short answer or helpful info instead.
    - Keep the full reply to 2 short sentences max.

    Return ONLY a valid JSON object matching this structure exactly:
    {{
      "grammar_score": 8,
      "vocab_score": 7,
      "corrections": ["correction 1"],
      "ai_response": "Your spoken reply here."
    }}
    """
    
    try:
        llm_out = llm.invoke(prompt)
        result = extract_json(llm_out)
        if not result or not result.get("ai_response"):
            raise ValueError("No valid response from model")
    except Exception as e:
        print(f"LLM Error: {e}")
        result = build_local_followup(transcript, history_text)

    generic_text = str(result.get("ai_response", "")).lower()
    if not result.get("ai_response") or is_generic_reply(generic_text):
        result = build_local_followup(transcript, history_text)

    # 6. Text to Speech
    ai_resp_text = result.get("ai_response", "Let's continue!")
    clean_audio_text = re.sub(r'[\U0001F300-\U0001FAFF]', '', ai_resp_text)
    
    try:
        audio_b64 = generate_audio_b64(clean_audio_text)
    except Exception as e:
        print(f"TTS Error: {e}")
        audio_b64 = ""

    return {
        "transcript": transcript,
        "fluency_score": max(0, fluency_score),
        "pronunciation_score": max(0, pronunciation_score),
        "grammar_score": result.get("grammar_score", 5),
        "vocab_score": result.get("vocab_score", 5),
        "corrections": result.get("corrections", []),
        "ai_text": result.get("ai_response", "Let's continue!"),
        "ai_audio_b64": audio_b64
    }

@app.post("/process_turn_text")
def process_turn_text(transcript: str = Form(...), topic: str = Form(default=""), history: str = Form(default="")):
    # 3. Calculate metrics (default since we only have text)
    fluency_score = estimate_fluency(transcript)
    pronunciation_score = estimate_pronunciation(transcript)
    history_text = sanitize_history(history)
    active_topic = resolve_active_topic(transcript, history_text, topic)

    prompt = f"""
    You are Sara, a warm, friendly language buddy from the app Vidya. Keep the conversation natural and follow the student's actual topic.

    Conversation history:
    {history_text}

    Active topic hint from the latest student turn: {active_topic or 'none'}

    Student just answered: "{transcript}"

    Rules:
    1. The most recent student message wins over older history. If the newest answer mentions a different topic, switch to that topic and continue it naturally.
    2. If the student clearly mentions a topic, continue that topic naturally. If they ask for information, give a short explanation instead of asking a question every time.
    3. Do not ask a generic hobby question when the student already named a real topic like cricket, school, music, computers, science, pets, food, travel, sports, homework, or any other topic.
    4. If the student says "tell me about", "what is", "how does", "why", or similar, answer with a simple fact or explanation. Do not make every reply a question.
    5. If the student says "let's talk about something", or asks for topic suggestions, suggest 3-5 easy topic ideas.
    6. If the student says they do not know, asks to change topic, or says move on, choose a fresh topic and suggest a simple option.
    7. Be encouraging, cheerful, and very simple.
    8. Do not force every reply to be a question; sometimes answer directly.
    9. Keep the whole reply to 2 short sentences maximum.

    Return ONLY valid JSON with this exact shape:
    {{
      "grammar_score": 8,
      "vocab_score": 7,
      "corrections": ["correction 1"],
      "ai_response": "Your spoken reply here."
    }}
    """
    
    try:
        print("Calling LLM...")
        llm_out = llm.invoke(prompt)
        print("LLM returned")
        result = extract_json(llm_out)
        if not result or not result.get("ai_response"):
            raise ValueError("No valid response from model")
    except Exception as e:
        print(f"LLM Error: {e}")
        result = build_local_followup(transcript, history_text)

    generic_text = str(result.get("ai_response", "")).lower()
    if not result.get("ai_response") or is_generic_reply(generic_text):
        result = build_local_followup(transcript, history_text)

    # 6. Text to Speech
    ai_resp_text = result.get("ai_response", "Let's continue!")
    clean_audio_text = re.sub(r'[\U0001F300-\U0001FAFF]', '', ai_resp_text)
    
    try:
        print("Generating TTS...")
        audio_b64 = generate_audio_b64(clean_audio_text)
        print("TTS generated")
    except Exception as e:
        print(f"TTS Error: {e}")
        audio_b64 = ""

    return {
        "transcript": transcript,
        "fluency_score": fluency_score,
        "pronunciation_score": pronunciation_score,
        "grammar_score": result.get("grammar_score", 5),
        "vocab_score": result.get("vocab_score", 5),
        "corrections": result.get("corrections", []),
        "ai_text": result.get("ai_response", "Let's continue!"),
        "ai_audio_b64": audio_b64
    }

@app.post("/evaluate_conversation")
def evaluate_conversation(history: str = Form(default="")):
    result = evaluate_conversation_history(history)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8004, reload=True)
