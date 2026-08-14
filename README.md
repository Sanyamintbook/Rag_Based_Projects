# Rag_Based_Projects - SCIENCE RAG PROJECT

A comprehensive educational platform combining **Retrieval-Augmented Generation (RAG)**, **Plagiarism Detection**, and **Multi-Modal Learning Tools** for student assessment and tutoring.

## 🎯 Project Overview

This project is an integrated education platform designed for:
- **Plagiarism Detection** - Multi-method detection system for academic integrity
- **RAG-Based AI Tutoring** - Intelligent tutoring system using FAISS vector search and LLM
- **Speech Processing** - Listening, speaking, and writing evaluation
- **Dashboard & Analytics** - Comprehensive monitoring and reporting system

---

## 📁 Project Structure

```
SCIENCE_RAG_PROJECT/
├── dashboard/                    # Main admin dashboard
│   └── app.py                   # Streamlit dashboard
├── plagiarism_app/              # Plagiarism detection system
│   ├── plagiarism_api.py        # FastAPI backend
│   ├── student_ui.py            # Student submission UI
│   ├── teacher_ui.py            # Teacher review UI
│   ├── report_builder.py        # Report generation
│   └── detectors/               # Detection modules
│       ├── ai_detector.py       # AI-generated content detection
│       ├── copy_checker.py      # Duplicate detection
│       ├── paraphrase.py        # Paraphrase detection
│       ├── originality.py       # Originality scoring
│       ├── ollama_client.py     # Ollama LLM integration
│       └── text_extractor.py    # Text extraction from files
├── rag_app/                     # RAG tutoring system
│   ├── api.py                   # FastAPI backend
│   ├── app.py                   # Main application
│   └── rag_ui.py                # UI interface
├── listening_app/               # Speech-to-text evaluation
│   ├── api.py                   # FastAPI backend
│   ├── ui.py                    # Streamlit UI
│   └── backend/
│       ├── whisper_service.py   # Whisper speech recognition
│       └── evaluator.py         # Answer evaluation
├── speaking_app/                # Text-to-speech generation
│   ├── api.py                   # FastAPI backend
│   └── index.html               # Web interface
├── writing_app/                 # Writing evaluation
│   ├── api.py                   # FastAPI backend
│   └── ui.py                    # Streamlit UI
├── global_plagiarism/           # Advanced plagiarism detection
│   ├── preprocessing/           # Text preprocessing
│   ├── embeddings/              # Embedding generation
│   ├── llm/                     # LLM integration
│   ├── utils/                   # Utility functions
│   ├── vector_store/            # FAISS index management
│   ├── verification/            # Result verification
│   ├── sources/                 # Reference source management
│   ├── storage/                 # Data storage
│   ├── data/                    # Data files
│   └── tests/                   # Test suite
├── Gemini/                      # Google Gemini integration
│   ├── faiss_index/             # Vector index
│   └── ncert_opac/              # NCERT content
├── kokoro_models/               # Text-to-speech models
│   ├── model.onnx               # ONNX TTS model
│   ├── voices/                  # Voice profiles
│   └── onnx/                    # ONNX resources
├── faiss_index/                 # RAG vector indexes
│   └── 10th_science_book/       # Science textbook embeddings
├── data/                        # Application data
│   ├── assignments/             # Assignment files
│   └── submissions/             # Student submissions
├── reports/                     # Generated reports
├── submissions/                 # Submitted files
├── logs/                        # Application logs
├── start.py                     # Main service launcher
└── requirements.txt             # Python dependencies
```

---

## 🚀 Key Features

### 1. **Plagiarism Detection System**
- **AI Content Detection** - Identifies AI-generated content
- **Copy Detection** - Finds duplicate submissions
- **Paraphrase Detection** - Detects rephrased plagiarism
- **Originality Scoring** - Calculates originality percentage
- **Vector-Based Search** - FAISS-powered similarity detection
- **Teacher Dashboard** - Review and manage student submissions
- **Student Portal** - Submit assignments and view feedback

### 2. **RAG-Based AI Tutor**
- **FAISS Vector Search** - Fast similarity search over textbook content
- **Ollama LLM Integration** - Local LLM for privacy-preserving AI
- **Question Answering** - Answer student questions using textbook context
- **10th Grade Science** - Specialized for Indian NCERT curriculum
- **Context-Aware Responses** - Generates answers with textbook references

### 3. **Speech Processing**
- **Listening Evaluation** - Speech-to-text with answer evaluation
- **Speaking System** - Kokoro TTS for natural speech generation
- **Whisper Integration** - Accurate speech recognition
- **Performance Metrics** - Pronunciation and comprehension scoring

### 4. **Writing Evaluation**
- **Automated Grading** - Score writing assignments
- **Feedback Generation** - AI-powered feedback
- **Grammar & Style** - Analysis of writing quality
- **Plagiarism Check** - Integrated plagiarism detection

### 5. **Analytics Dashboard**
- **Real-time Monitoring** - Track all services
- **Performance Metrics** - View system health
- **Student Analytics** - Track progress and performance
- **Report Generation** - Export detailed reports
- **Gemini Integration** - AI-powered insights

---

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern async API framework
- **Streamlit** - Interactive dashboards and UIs
- **LangChain** - LLM orchestration framework
- **FAISS** - Vector similarity search
- **Ollama** - Local LLM inference
- **Pydantic** - Data validation

### Speech Processing
- **OpenAI Whisper** - Speech recognition
- **Kokoro TTS** - Text-to-speech synthesis
- **ONNX** - Model inference

### Data & Search
- **FAISS** - Vector database for RAG
- **Embeddings** - Ollama embeddings (`nomic-embed-text`)
- **LLM** - Ollama Qwen 2.5 7B model

### Integration
- **Google Gemini** - Advanced AI insights
- **External Ollama Server** - Remote LLM inference (45.194.3.86:11434)

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- pip package manager
- Git
- Ollama (for local LLM inference)

### 1. Clone the Repository
```bash
git clone https://github.com/Sanyamintbook/Rag_Based_Projects.git
cd Rag_Based_Projects
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create `.env` file in root directory:
```env
OLLAMA_BASE_URL=http://45.194.3.86:11434
GEMINI_API_KEY=your_gemini_key_here
```

### 5. Download Models
```bash
# Download required FAISS indexes and models
python download_kokoro.py
```

---

## 🏃 Running the Project

### Start All Services
```bash
python start.py
```

This will launch:

| Service | Port | Purpose |
|---------|------|---------|
| Listening Backend | 8003 | Speech-to-text API |
| Writing Backend | 8005 | Writing evaluation API |
| Plagiarism Backend | 8002 | Plagiarism detection API |
| Global Dashboard | 8501 | Main admin dashboard |
| Teacher Dashboard | 8502 | Teacher plagiarism review |
| Listening UI | 8503 | Student listening practice |
| Speaking API | 8004 | Text-to-speech API |
| Writing UI | 8505 | Writing assignment UI |

### Access Dashboards
- **Admin Dashboard**: http://localhost:8501
- **Teacher Plagiarism Review**: http://localhost:8502
- **Listening Practice**: http://localhost:8503
- **Writing Interface**: http://localhost:8505

### Stop All Services
```bash
# Windows
stop_all.bat
# macOS/Linux
bash stop_all.sh
```

---

## 📊 API Endpoints

### Plagiarism Detection API (Port 8002)
```
POST   /submit              - Student uploads assignment
POST   /run_analysis        - Teacher initiates plagiarism check
GET    /all_reports         - Get summary report table
GET    /report/{student}    - Get detailed student report
```

### RAG Tutor API (Port 8001)
```
POST   /ask                 - Ask a question to the AI tutor
GET    /health              - Health check
```

### Listening API (Port 8003)
```
POST   /transcribe          - Convert speech to text
POST   /evaluate            - Evaluate student answer
```

### Writing API (Port 8005)
```
POST   /evaluate            - Evaluate writing assignment
GET    /report/{student}    - Get writing evaluation report
```

### Speaking API (Port 8004)
```
POST   /synthesize          - Convert text to speech
GET    /voices              - List available voices
```

---

## 📚 Data Flow

### Plagiarism Detection Flow
1. Student uploads assignment → `/submit` endpoint
2. Teacher triggers analysis → `/run_analysis` endpoint
3. System runs multiple detectors:
   - AI content detection
   - Copy detection (text matching)
   - Paraphrase detection
   - FAISS vector similarity
4. Reports generated and stored in `reports/`
5. Results available on teacher dashboard

### RAG Tutoring Flow
1. Student asks question
2. FAISS retrieves similar textbook passages
3. LLM combines context with question
4. AI tutor generates answer with citations
5. Response returned with source references

---

## 🗂️ Key Directories

| Directory | Purpose |
|-----------|---------|
| `submissions/` | Stores student-submitted files |
| `reports/` | Generated plagiarism and evaluation reports |
| `faiss_index/` | Vector indexes for RAG system |
| `logs/` | Application and service logs |
| `data/assignments/` | Assignment definitions |
| `data/submissions/` | Processed submission data |
| `global_plagiarism/` | Advanced plagiarism detection system |
| `Gemini/` | Gemini AI integration |
| `kokoro_models/` | TTS model files |

---

## 🔍 Key Components

### Text Extraction (`detectors/text_extractor.py`)
- Extracts text from various file formats (DOCX, PDF, TXT)
- Preprocessing and normalization

### AI Detection (`detectors/ai_detector.py`)
- Detects AI-generated content using language patterns
- Integrates with Ollama LLM

### Copy Checker (`detectors/copy_checker.py`)
- String similarity matching
- Finds duplicate and near-duplicate submissions

### Paraphrase Detection (`detectors/paraphrase.py`)
- Semantic similarity analysis
- Detects reworded plagiarism

### Originality Scoring (`detectors/originality.py`)
- Calculates plagiarism percentage
- Combines multiple detection methods

### Report Builder (`report_builder.py`)
- Generates comprehensive plagiarism reports
- JSON and HTML format support

---

## 📈 Monitoring & Logs

### Service Logs
- **All Services**: `logs/all_services/`
- **Plagiarism**: `logs/plagiarism/`

### Health Monitoring
Check service status via:
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

---

## 🛠️ Troubleshooting

### Ollama Connection Issues
```
ERROR: Connection to Ollama failed at 45.194.3.86:11434
```
**Solution**: Ensure Ollama server is running and accessible

### FAISS Index Not Found
```
Warning: FAISS index not found. Running in standard LLM mode without vector embeddings.
```
**Solution**: Run `python download_kokoro.py` to download required indexes

### Port Already in Use
```
Address already in use
```
**Solution**: Kill the process using the port or use different port in `start.py`

---

## 📝 Configuration

### Models
- **LLM**: Ollama Qwen 2.5 7B
- **Embeddings**: Ollama nomic-embed-text
- **TTS**: Kokoro ONNX model
- **ASR**: OpenAI Whisper

### Vector Search
- **Index**: FAISS
- **Dimension**: 768 (nomic-embed-text)
- **Similarity Metric**: Cosine

---

## 👥 User Roles

1. **Students**
   - Submit assignments
   - Practice listening
   - Get writing feedback
   - Ask AI tutor questions

2. **Teachers**
   - Review submissions
   - Run plagiarism checks
   - Generate reports
   - View analytics

3. **Admins**
   - Monitor system health
   - Configure settings
   - Manage user accounts
   - View global analytics

---

## 📄 License

This project is part of the SCIENCE_RAG_PROJECT initiative.

---

## 👨‍💻 Author

**Sanyami Jain**  
GitHub: [@Sanyamintbook](https://github.com/Sanyamintbook)  
Repository: [Rag_Based_Projects](https://github.com/Sanyamintbook/Rag_Based_Projects)

---

## 📞 Support & Feedback

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review logs in `logs/` directory

---

## 🔄 Last Updated

**Date**: August 12, 2026  
**Latest Changes**: 
- Plagiarism detection API improvements
- RAG tutor initialization
- Dashboard analytics updates
- Speaking and listening app enhancements

---

## 🎓 Educational Focus

This system is optimized for:
- **10th Grade Science** (NCERT Curriculum)
- **Academic Integrity Assessment**
- **Multi-Modal Learning** (Text, Speech, Writing)
- **Student Performance Analytics**
- **Automated Tutoring and Feedback**

---

**Happy Learning! 🚀**
