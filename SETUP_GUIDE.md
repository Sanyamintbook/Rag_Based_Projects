# 🚀 Quick Setup Guide

Get the SCIENCE RAG PROJECT up and running in 5 minutes!

## Prerequisites

- ✅ Windows 10+ (or macOS/Linux with adjustments)
- ✅ Python 3.9+
- ✅ 8GB+ RAM
- ✅ Git installed
- ✅ Ollama running (or accessible at `45.194.3.86:11434`)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/Sanyamintbook/Rag_Based_Projects.git
cd Rag_Based_Projects
```

---

## Step 2: Create Virtual Environment

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Installation takes 5-10 minutes** depending on your internet speed.

---

## Step 4: Configure Environment (Optional)

Create `.env` file in project root:
```env
OLLAMA_BASE_URL=http://45.194.3.86:11434
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=False
```

---

## Step 5: Download Models

```bash
python download_kokoro.py
```

This downloads TTS models and FAISS indexes (~500MB).

---

## Step 6: Start All Services

### Windows
```bash
python start.py
```

### macOS/Linux
```bash
python start.py
```

**Wait 30-60 seconds for all services to start.**

---

## Step 7: Access the Applications

Open these URLs in your browser:

| Application | URL | Purpose |
|------------|-----|---------|
| 📊 Main Dashboard | http://localhost:8501 | Admin panel & analytics |
| 👨‍🏫 Teacher Dashboard | http://localhost:8502 | Plagiarism review |
| 👂 Listening Practice | http://localhost:8503 | Speech evaluation |
| ✍️ Writing Interface | http://localhost:8505 | Writing assignments |
| 🤖 RAG Tutor API | http://localhost:8001 | AI tutoring backend |

---

## ✅ Verification Checklist

Check if everything is working:

```bash
# Test Plagiarism API
curl http://localhost:8002/health

# Test RAG API
curl http://localhost:8001/health

# Test Listening API
curl http://localhost:8003/health
```

Should return `200 OK` for each.

---

## 🛑 Stop All Services

### Windows
```bash
stop_all.bat
```

### macOS/Linux
```bash
bash stop_all.sh
```

Or simply press `Ctrl+C` in the terminal.

---

## 📁 Project Structure at a Glance

```
Rag_Based_Projects/
├── dashboard/           # Admin dashboard
├── plagiarism_app/      # Plagiarism detection
├── rag_app/             # AI tutoring system
├── listening_app/       # Speech-to-text
├── speaking_app/        # Text-to-speech
├── writing_app/         # Writing evaluation
├── README.md            # Full documentation
├── PROJECT_ARCHITECTURE.md # System design
└── start.py             # Start all services
```

---

## 🎯 First Time Usage

### For Students:
1. Go to http://localhost:8503 (Listening Practice)
2. Record your answer to a question
3. Get instant feedback on your response

### For Teachers:
1. Go to http://localhost:8502 (Teacher Dashboard)
2. Upload student assignments
3. Click "Run Analysis" to detect plagiarism
4. Review detailed reports

### For Admins:
1. Go to http://localhost:8501 (Main Dashboard)
2. Monitor all services
3. View analytics and reports

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8501
netstat -ano | findstr :8501

# Kill the process (Windows)
taskkill /PID <PID> /F
```

### Ollama Connection Error
```
Error: Connection refused to 45.194.3.86:11434
```
**Solution**: 
- Check if Ollama is running
- Update `OLLAMA_BASE_URL` in `.env`
- Restart the service

### Module Not Found Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### FAISS Index Error
```bash
# Regenerate indexes
python download_kokoro.py
```

---

## 💡 Pro Tips

1. **Use Anaconda** (Optional but recommended)
   ```bash
   conda env create -f environment.yml
   conda activate rag-project
   ```

2. **Run in Background** (Windows)
   ```bash
   start python start.py
   ```

3. **Check Logs**
   ```bash
   tail -f logs/all_services/service.log
   ```

4. **Clear Cache** (If experiencing issues)
   ```bash
   rm -r __pycache__ .pytest_cache
   ```

---

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Review [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) for system design
- Check individual module READMEs in each app folder
- Explore API endpoints in code

---

## 🆘 Need Help?

1. **Check Logs**: Look in `logs/` directory
2. **Read Docs**: See `docs/` folder for detailed guides
3. **GitHub Issues**: Open an issue on GitHub
4. **Code Comments**: Read the source code for inline documentation

---

## ✨ What's Included

✅ AI-powered plagiarism detection  
✅ RAG-based tutoring system  
✅ Speech recognition & evaluation  
✅ Text-to-speech synthesis  
✅ Writing evaluation  
✅ Analytics dashboard  
✅ Teacher review interface  
✅ Student practice portal  

---

## 📊 System Requirements

| Component | Requirement |
|-----------|-------------|
| CPU | 4+ cores recommended |
| RAM | 8GB minimum, 16GB recommended |
| Disk | 10GB free space |
| Network | Stable internet for Ollama server |
| Python | 3.9+ |

---

## 🎓 Learn More

- **NCERT Curriculum**: Optimized for 10th-grade science
- **Multi-Modal**: Text, speech, and writing evaluation
- **Privacy-First**: Local LLM inference (no cloud dependency)
- **Scalable**: Easy to extend with new features

---

**You're all set! Happy learning! 🚀**

---

Last Updated: August 12, 2026
