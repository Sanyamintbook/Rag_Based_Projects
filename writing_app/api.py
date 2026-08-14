import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM

app = FastAPI(title="AI Writing Assessment API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Reuse the existing FAISS index from the listening app (the Science Textbook)
FAISS_INDEX_DIR = os.path.join(ROOT_DIR, "..", "listening_app", "faiss_index")

print("Initializing AI Writing Assessment Backend...")

try:
    print("Loading FAISS Textbook Index...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 4})
except Exception as e:
    print(f"Error loading FAISS: {e}")
    retriever = None

try:
    print("Loading Qwen2.5:3b (JSON mode)...")
    llm = OllamaLLM(model="qwen2.5:3b", format="json")
except Exception as e:
    print(f"Error loading Ollama: {e}")
    llm = None

class WritingAssessmentRequest(BaseModel):
    question: str
    student_answer: str
    class_level: Optional[str] = "class_10"
    subject: Optional[str] = "Science"
    max_marks: Optional[float] = 100.0
    expected_min_words: Optional[int] = 0
    expected_max_words: Optional[int] = 0
    expected_min_lines: Optional[int] = 0
    expected_max_lines: Optional[int] = 0

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except: pass
    return {"status": "error", "message": "Failed to parse JSON from AI"}

@app.post("/ai-writing-assessment")
async def ai_writing_assessment(request: WritingAssessmentRequest):
    if not llm or not retriever:
        raise HTTPException(status_code=500, detail="Backend models not loaded properly.")

    question = request.question.strip()
    student_answer = request.student_answer.strip()

    if not question:
        return {"status": "error", "message": "Question is required."}
    if not student_answer:
        return {"status": "error", "message": "Student answer is required."}

    word_count = len(student_answer.split())
    line_count = len([line for line in student_answer.splitlines() if line.strip()])

    # Retrieve context from our FAISS textbook database
    try:
        docs = retriever.invoke(question)
    except Exception as e:
        return {"status": "error", "message": f"Failed to connect to AI/Database: {str(e)}"}
    
    if not docs:
        context = "No relevant textbook context found."
    else:
        context = "\n\n".join([f"Source {i + 1}:\n{doc.page_content}" for i, doc in enumerate(docs)])

    # The user's incredible 100-mark prompt
    prompt = f"""
    You are an AI Writing Assessment Evaluator for Class 10 students.

    Evaluate the student's written answer using ONLY the textbook content provided.

    Question:
    {question}

    TEXTBOOK CONTEXT:
    {context}

    STUDENT ANSWER:
    {student_answer}

    SCORING RUBRIC:
    Grammar: 20 marks
    Spelling: 15 marks
    Structure: 15 marks
    Relevance to Question: 25 marks
    Content Accuracy from Textbook: 25 marks
    Total: 100 marks

    QUESTION METADATA:
    Class Level: {request.class_level}
    Subject: {request.subject}
    Maximum Marks: {request.max_marks}
    Expected Minimum Words: {request.expected_min_words}
    Expected Maximum Words: {request.expected_max_words}
    Expected Minimum Lines: {request.expected_min_lines}
    Expected Maximum Lines: {request.expected_max_lines}
    Student Word Count: {word_count}
    Student Line Count: {line_count}

    MARK DISPLAY RULE:
    The internal rubric is always out of 100 marks.
    The student's final displayed score must be calculated using the teacher-defined max_marks.
    Do not say the final answer is out of 100 if max_marks is provided.
    Use: actual_score = total_score / 100 * max_marks
    Example: If total_score is 80 and max_marks is 5, actual_score is 4/5.
    Rubric category scores like Grammar 20, Spelling 15, and Relevance 25 are only internal rubric scores.
    Final student marks must be shown using actual_score and max_marks.

    QUESTION-CONTEXT CONSISTENCY RULE:
    Evaluate only the CURRENT QUESTION and CURRENT STUDENT ANSWER given in this request.
    Do not use any previous question, previous answer, previous topic, or unrelated context.
    If the retrieved textbook context does not match the current question, do not invent feedback from another topic.
    Instead set:
    "context_match": false
    "needs_manual_review": true
    "feedback": "The retrieved textbook context does not clearly match the question. Manual review is recommended."
    The feedback, missing concepts, mistakes, and suggestions must always refer to the CURRENT QUESTION only.

    TEXTBOOK COPY DETECTION:
    Before final feedback, classify the student answer into one of these 3 cases:

    Case 1: Direct textbook copy
    1. Use this when the student answer matches the textbook wording almost exactly.
    2. Set "is_textbook_copy": true
    3. Set "copied_from_textbook": true
    4. Set "copy_status": "direct_textbook_copy"
    5. Keep content accuracy and relevance high if the copied text correctly answers the question.
    6. In originality_feedback, tell the student the answer is correct but should be written in their own words.
    7. Add short matched wording evidence in textbook_copy_evidence.

    Case 2: Paraphrased textbook answer
    1. Use this when the answer has the same textbook meaning but uses the student's own words.
    2. Set "is_textbook_copy": false
    3. Set "copied_from_textbook": false
    4. Set "copy_status": "paraphrased_textbook_answer"
    5. Score normally based on correctness, completeness, grammar, spelling, and structure.

    Case 3: Incorrect, unrelated, or not textbook-based answer
    1. Use this when the answer does not match the required textbook concept or is off-topic.
    2. Set "is_textbook_copy": false
    3. Set "copied_from_textbook": false
    4. Set "copy_status": "not_textbook_based_or_incorrect"
    5. Apply the relevance gate and content accuracy deductions.

    ANSWER TYPE DETECTION RULES:
    Detect the type of student answer.
    Use one of these values for "answer_type_detected":
    1. "complete_answer" = answer fully explains the asked concept.
    2. "partial_answer" = answer is related but incomplete.
    3. "vague_answer" = answer has very little meaning or only one/two words.
    4. "irrelevant_answer" = answer is meaningful but about a different topic.
    5. "garbage_input" = answer contains random, meaningless, joking, abusive, or non-academic text.
    6. "incorrect_answer" = answer is related to the question but scientifically incorrect.
    7. "mixed_correct_wrong_answer" = answer has some correct and some wrong points.
    8. "multilingual_answer" = answer is in Hindi, Hinglish, or another language but relevant.

    LENGTH EVALUATION RULE:
    Evaluate whether the student's answer length is suitable for the assigned maximum marks.

    If expected_min_words or expected_min_lines is provided and the answer is shorter than expected:
    1. Set "length_status": "too_short"
    2. Deduct marks from structure and content completeness.
    3. Mention that the answer is too short for the assigned marks.

    If expected_max_words or expected_max_lines is provided and the answer is too long with unnecessary or irrelevant content:
    1. Set "length_status": "too_long"
    2. Deduct marks from structure and clarity.

    If answer length is suitable:
    1. Set "length_status": "appropriate"

    Do not give marks only because the answer is long.
    A long wrong answer should still get low content accuracy.
    A short but correct answer can get good marks for low-mark questions.

    If answer_type_detected is "garbage_input":
    1. Set "is_relevant" to false
    2. Set "relevance_status": "irrelevant"
    3. Set "needs_manual_review" to true
    4. Set total_score between 0 and 5
    5. Do not give grammar, spelling, or structure marks
    6. Explain that the response is random, non-academic, or meaningless

    MIXED CORRECT/WRONG ANSWER RULE:
    If the student answer contains at least one correct concept related to the question, do NOT mark it as completely irrelevant.
    If the answer is related to the question but contains false scientific claims:
    1. Set "is_relevant": true
    2. Set "relevance_status": "partially_relevant"
    3. Set "answer_type_detected": "mixed_correct_wrong_answer" or "incorrect_answer"
    4. Give relevance marks for addressing the topic
    5. Deduct content accuracy marks for false claims
    6. Put false claims inside "mistakes"
    7. Do NOT set total_score to 0 unless the answer is completely unrelated or garbage input

    RELEVANCE VS ACCURACY RULE:
    Relevance means the answer is about the asked topic.
    Accuracy means the answer is scientifically correct.
    Do not confuse relevance with accuracy.
    An answer can be relevant but inaccurate.
    In that case:
    1. Relevance score should be medium or high
    2. Content accuracy score should be low
    3. Total score should not be zero

    IMPORTANT RELEVANCE GATE:
    Before scoring, check whether the student answer is relevant to the question.
    Compare the main concept asked in the question with the main concept discussed in the student answer.
    If the question asks about one concept but the answer discusses a different science concept, the answer is irrelevant.
    Example: If the question asks about malleability but the answer explains chemical reactions, mark it irrelevant.
    Do not award full relevance just because the answer contains some science words.
    If content_accuracy_score is 10 or below, relevance_score must not be full marks.

    If the student answer is completely unrelated to the question:
    1. Set "is_relevant": false
    2. Set "relevance_status": "irrelevant"
    3. Set "answer_type_detected": "irrelevant_answer"
    4. Set relevance_score to 0
    5. Set content_accuracy_score to 0
    6. Set grammar_score to 0, spelling_score to 0, and structure_score to 0
    7. total_score must be 0
    8. Explain clearly that the answer is off-topic

    If the answer is partially related:
    1. Set "is_relevant": true
    2. Set "relevance_status": "partially_relevant"
    3. Set "answer_type_detected": "partial_answer"
    4. Continue normal scoring but deduct marks for missing concepts

    If the answer directly answers the question:
    1. Set "is_relevant": true
    2. Set "relevance_status": "relevant"
    3. Set "answer_type_detected": "complete_answer"
    4. Continue full rubric scoring
        
    fixing force evidence:
    1.For every deduction you make, you MUST provide a specific reason.
    2.Do not deduct marks unless an actual error exists.
    3.If grammar is correct, grammar score must be full marks.
    4.If spelling is correct, spelling score must be full marks.
    5.Do not deduct grammar or spelling marks because of missing concepts.

    IMPORTANT:
    Missing concepts should only affect:
    1. Content Accuracy
    2. Relevance, if the missing concepts make the answer incomplete or weakly related

    Missing concepts must NOT affect:
    1. Grammar
    2. Spelling
    3. Structure

    Evaluation Rules:
    1. Judge whether the student answer correctly answers the question.
    2. Check if the answer matches the textbook context.
    3. Do not give high content accuracy if important textbook points are missing.
    4. Give simple student-friendly feedback.
    5. Mention missing concepts from the textbook.
    6. Show exact marks earned for every category.
    7. For every mark deduction, explain the student mistake in simple words.
    8. Use deduction_details for category-wise reasons.
    9. Return ONLY valid JSON.
    10. Do not use markdown.
    11. Do not add explanation outside JSON.

    JSON FORMAT:
    {{
    "rubric_total": 100,
    "max_marks": {request.max_marks},
    "actual_score": 0,
    "actual_deducted_marks": 0,
    "display_score": "",
    "word_count": {word_count},
    "line_count": {line_count},
    "length_status": "appropriate",
    "length_feedback": "",
    "context_match": true,
    "is_relevant": true,
    "relevance_status": "relevant",
    "answer_type_detected": "complete_answer",
    "is_textbook_copy": false,
    "copied_from_textbook": false,
    "copy_status": "paraphrased_textbook_answer",
    "textbook_copy_evidence": [],
    "originality_feedback": "",
    "needs_manual_review": false,
    
    "grammar_score": 0,
    "grammar_max_marks": 20,
    "grammar_deducted_marks": 0,
    "grammar_deduction_reasons": [],

    "spelling_score": 0,
    "spelling_max_marks": 15,
    "spelling_deducted_marks": 0,
    "spelling_deduction_reasons": [],

    "structure_score": 0,
    "structure_max_marks": 15,
    "structure_deducted_marks": 0,
    "structure_deduction_reasons": [],

    "relevance_score": 0,
    "relevance_max_marks": 25,
    "relevance_deducted_marks": 0,
    "relevance_deduction_reasons": [],

    "content_accuracy_score": 0,
    "content_accuracy_max_marks": 25,
    "content_accuracy_deducted_marks": 0,
    "content_accuracy_deduction_reasons": [],

    "total_score": 0,
    "total_max_marks": 100,
    "total_deducted_marks": 0,

    "score_breakdown": [
        {{
        "key": "grammar",
        "label": "Grammar",
        "score": 0,
        "max_marks": 20,
        "deducted_marks": 0,
        "deduction_reasons": []
        }}
    ],

    "deductions": [],
    "grade": "",
    "feedback": "",
    "missing_concepts": [],
    "mistakes": [],
    "suggestions": []

    }}
    """

    try:
        raw_response = llm.invoke(prompt)
        parsed_evaluation = extract_json(raw_response)
        
        # Do a quick safety check on the returned JSON
        if "actual_score" not in parsed_evaluation:
            # Recompute actual score if missing
            total = float(parsed_evaluation.get("total_score", 0))
            parsed_evaluation["actual_score"] = round((total / 100.0) * request.max_marks, 2)
            parsed_evaluation["display_score"] = f"{parsed_evaluation['actual_score']}/{request.max_marks}"
            
        return {
            "status": "success",
            "question": question,
            "student_answer": student_answer,
            "evaluation": parsed_evaluation
        }
    except Exception as e:
        return {"status": "error", "message": f"Evaluation failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8005, reload=True)
