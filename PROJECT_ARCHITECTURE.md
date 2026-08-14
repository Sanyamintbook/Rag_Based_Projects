# SCIENCE RAG PROJECT - Architecture & Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                      │
│  (Student/Teacher UIs - Streamlit, HTML)                   │
└────────┬──────────────────────────────────────────────────┘
         │
    ┌────┴──────────────────────────────────────────┐
    │         API Gateway & Load Balancing           │
    └────┬──────────────────────────────────────────┘
         │
    ┌────┴────────────────────────────────────────────────────────────┐
    │                    Microservices Layer                          │
    ├──────────────────┬──────────────────┬──────────────────────────┤
    │ Plagiarism API   │ RAG Tutor API    │ Listening API      │     │
    │ (Port 8002)      │ (Port 8001)      │ (Port 8003)        │     │
    │                  │                  │                    │     │
    │ • AI Detection   │ • FAISS Search   │ • Whisper ASR      │     │
    │ • Copy Check     │ • LLM Inference  │ • Evaluation       │     │
    │ • Paraphrase     │ • Embeddings     │                    │     │
    │ • Originality    │                  │ Writing API        │     │
    │                  │                  │ (Port 8005)        │     │
    │ Teacher UI       │ RAG UI           │ • Grading          │     │
    │ (Port 8502)      │ (Port 8501)      │ • Feedback         │     │
    │                  │                  │                    │     │
    │                  │                  │ Speaking API       │     │
    │                  │                  │ (Port 8004)        │     │
    │                  │                  │ • Kokoro TTS       │     │
    └──────────────┬───┴────────────────┬─┴──────────────────────────┘
                   │                    │
    ┌──────────────┴────────────────────┴─────────────┐
    │          Inference & ML Layer                   │
    ├───────────────────────────────────────────────┤
    │ • Ollama LLM (Qwen 2.5 7B)                    │
    │   - Running on 45.194.3.86:11434              │
    │ • Embeddings (nomic-embed-text)               │
    │ • Kokoro TTS Models (ONNX)                    │
    │ • Whisper Speech Recognition                  │
    │ • Google Gemini API                           │
    └───────┬───────────────────────────┬───────────┘
            │                           │
    ┌───────┴──────────────┬────────────┴──────┐
    │   Data & Storage     │  Vector Search    │
    ├──────────────────────┼───────────────────┤
    │ • Submissions/       │ • FAISS Indexes   │
    │ • Reports (JSON)     │   - 10th Science  │
    │ • Assignment Data    │   - NCERT Content │
    │ • User Profiles      │   - Global Index  │
    │ • Logs               │                   │
    └──────────────────────┴───────────────────┘
```

## Component Interaction Diagram

```
Student Flow:
┌─────────┐
│ Student │
└────┬────┘
     │
     ├──> [Submit Assignment] ──> Plagiarism API ──> Detectors
     │                                    │
     │                                    └──> Report Builder ──> JSON Report
     │
     ├──> [Ask Question] ──> RAG API ──> FAISS Search ──> Ollama LLM ──> Answer
     │
     ├──> [Listening Practice] ──> Listening API ──> Whisper ──> Evaluator
     │
     └──> [Speaking] ──> Speaking API ──> Kokoro TTS ──> Audio Output


Teacher Flow:
┌─────────┐
│ Teacher │
└────┬────┘
     │
     └──> [Dashboard] ──> Teacher UI (Port 8502)
              │
              ├──> View Submissions
              ├──> Run Plagiarism Analysis
              ├──> Review Reports
              └──> View Student Analytics


Admin Flow:
┌────────┐
│ Admin  │
└────┬───┘
     │
     └──> [Admin Dashboard] ──> Streamlit (Port 8501)
              │
              ├──> System Health Monitoring
              ├──> Service Status
              ├──> Performance Metrics
              ├──> Analytics & Reports
              └──> Gemini AI Insights
```

---

## Plagiarism Detection Pipeline

### Multi-Method Detection Approach

```
Student Submission
        │
        ├──> 1. Text Extraction (docx → text)
        │
        ├──> 2. AI Content Detection
        │    └─> LLM Analysis (Ollama)
        │
        ├──> 3. Copy Detection
        │    └─> String similarity matching
        │
        ├──> 4. Paraphrase Detection
        │    └─> Semantic similarity (embeddings)
        │
        ├──> 5. Originality Scoring
        │    └─> Combined score calculation
        │
        └──> 6. Report Generation
             └─> JSON report with detailed metrics
```

### Detection Algorithms

| Method | Algorithm | Approach |
|--------|-----------|----------|
| **AI Detection** | LLM Pattern Analysis | Uses Ollama LLM to identify AI writing patterns |
| **Copy Detection** | TF-IDF + Similarity | Text matching with similarity thresholds |
| **Paraphrase** | Embeddings + Cosine | Semantic similarity using embeddings |
| **Originality** | Weighted Combination | Combines all detection methods |
| **FAISS Vector** | Approximate Nearest Neighbor | Fast similarity search in vector space |

---

## RAG Tutoring System

### Architecture

```
Question Input
    │
    ├──> Pre-processing (lowercasing, tokenization)
    │
    ├──> Embedding Generation
    │    └─> Ollama nomic-embed-text model
    │
    ├──> FAISS Vector Search
    │    └─> Retrieve top-k similar textbook passages
    │
    ├──> Context Assembly
    │    └─> Combine retrieved passages with question
    │
    ├──> LLM Processing
    │    ├─> Model: Ollama Qwen 2.5 7B
    │    ├─> Prompt: System + Context + Question
    │    └─> Generation: Answer with citations
    │
    └──> Response Output
         └─> Student receives answer with source references
```

### Key Features

1. **Retrieval-Augmented Generation**
   - Uses FAISS for fast vector search
   - Context-aware prompt engineering
   - Multi-passage ranking

2. **Vector Index**
   - Pre-indexed 10th-grade science textbook
   - 768-dimensional embeddings
   - Cosine similarity matching

3. **LLM Integration**
   - Ollama (local inference)
   - Qwen 2.5 7B model
   - Context injection via system prompt

---

## Speech Processing Subsystems

### Listening System (Port 8003)

```
Audio Input
    │
    ├──> Speech Recognition (Whisper)
    │    └─> Convert audio to text
    │
    ├──> Answer Extraction
    │    └─> Parse student response
    │
    ├──> Evaluation
    │    ├─> Compare with expected answer
    │    ├─> Score comprehension
    │    └─> Generate feedback
    │
    └──> Result Output
         └─> Pronunciation & comprehension score
```

### Speaking System (Port 8004)

```
Text Input
    │
    ├──> Text Processing
    │    └─> Normalize and prepare text
    │
    ├──> TTS Synthesis (Kokoro)
    │    ├─> Model: ONNX format
    │    ├─> Voice Selection: Multiple profiles
    │    └─> Inference: Generate audio
    │
    └──> Audio Output
         └─> Natural-sounding speech
```

---

## Data Models

### Student Submission
```json
{
  "student_name": "John Doe",
  "assignment_id": "assignment_1",
  "file_path": "submissions/john_doe__essay.docx",
  "submission_date": "2026-08-12",
  "content": "extracted text..."
}
```

### Plagiarism Report
```json
{
  "student": "John Doe",
  "assignment": "assignment_1",
  "overall_plagiarism_score": 45.2,
  "ai_detection_score": 0.85,
  "copy_detection_score": 0.32,
  "paraphrase_detection_score": 0.18,
  "originality_score": 54.8,
  "details": {
    "detected_sources": [...],
    "flagged_sections": [...]
  },
  "generated_at": "2026-08-12T14:30:00Z"
}
```

### RAG Query
```json
{
  "question": "What is photosynthesis?",
  "retrieved_context": [
    "Passage 1: ...",
    "Passage 2: ..."
  ],
  "answer": "Photosynthesis is...",
  "sources": ["Chapter 3, Page 45", "Chapter 3, Page 47"]
}
```

---

## Performance Considerations

### Vector Search Optimization
- **FAISS Index Type**: Flat with IVF (Inverted File)
- **Dimension**: 768 (nomic-embed-text)
- **Top-K**: 3 (retrieve 3 most similar passages)
- **Search Time**: ~5-10ms per query

### LLM Inference
- **Model**: Ollama Qwen 2.5 7B (quantized)
- **Inference Time**: ~2-5 seconds per query
- **Batch Processing**: Sequential (no batching)
- **Server**: Remote (45.194.3.86:11434)

### Plagiarism Detection Speed
- **Text Extraction**: ~100-500ms (file dependent)
- **AI Detection**: ~3-5 seconds (LLM inference)
- **Copy Detection**: ~1-2 seconds
- **Total Pipeline**: ~10-15 seconds per submission

---

## Database & Storage

### File Storage Structure
```
submissions/
├── student1__assignment1.docx
├── student1__assignment2.docx
├── student2__assignment1.docx
└── ...

reports/
├── student1.json
├── student2.json
└── ...

faiss_index/
├── 10th_science_book/
│   ├── index.faiss
│   └── index.pkl
└── ...

logs/
├── plagiarism/
│   └── analysis_2026-08-12.log
└── all_services/
    └── service_2026-08-12.log
```

### Data Retention Policy
- **Submissions**: Stored indefinitely
- **Reports**: Archived after 1 year
- **Logs**: Rotated daily, kept for 30 days
- **Vector Indexes**: Periodically recomputed

---

## Error Handling & Recovery

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Ollama Connection Error | LLM server down | Check remote server status, restart service |
| FAISS Index Error | Corrupted index | Regenerate index, restart service |
| Memory Error | Large file processing | Implement chunking, increase heap size |
| Timeout Error | Long inference | Increase timeout, optimize prompt |
| File Format Error | Unsupported file type | Add format support or reject file |

### Logging
- **Service Logs**: `logs/all_services/`
- **Plagiarism Logs**: `logs/plagiarism/`
- **Level**: DEBUG, INFO, WARNING, ERROR
- **Rotation**: Daily rotation with 30-day retention

---

## Security Considerations

1. **Data Privacy**
   - Student submissions stored securely
   - Report access controlled by role
   - No data sent to external servers (except Ollama)

2. **API Security**
   - Input validation via Pydantic
   - File upload restrictions
   - Error message sanitization

3. **Model Security**
   - Local LLM inference (no cloud dependency)
   - FAISS index stored locally
   - No model weights exposed

---

## Deployment Guide

### Local Development
```bash
python start.py
```

### Docker Deployment (Future)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "start.py"]
```

### Environment Variables
```env
OLLAMA_BASE_URL=http://45.194.3.86:11434
GEMINI_API_KEY=your_api_key
DEBUG=False
LOG_LEVEL=INFO
```

---

## Monitoring & Observability

### Metrics to Track
- Service uptime/downtime
- API response times
- Error rates
- Model inference latency
- Storage usage
- User activity metrics

### Health Checks
```bash
curl http://localhost:8001/health  # RAG API
curl http://localhost:8002/health  # Plagiarism API
curl http://localhost:8003/health  # Listening API
```

---

## Future Enhancements

1. **Multi-language Support**
   - Add non-English plagiarism detection
   - Support for multiple textbooks

2. **Advanced Analytics**
   - Predictive student performance
   - Trend analysis across cohorts
   - AI-powered insights

3. **Scalability**
   - Distributed FAISS indexes
   - Caching layer (Redis)
   - Load balancing

4. **Feature Additions**
   - Peer review system
   - Collaborative learning
   - Video content support

---

**Last Updated**: August 12, 2026
**Version**: 1.0.0
