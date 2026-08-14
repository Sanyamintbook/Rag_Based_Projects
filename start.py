import subprocess
import os
import sys
import time
import atexit

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

# ── Service Definitions ──────────────────────────────────────────────────────
# Format: (Display Name, Command List, Working Directory)
SERVICES = [
    (
        "Listening Backend     (http://localhost:8003)",
        [PYTHON, "-m", "uvicorn", "api:app", "--port", "8003", "--log-level", "warning"],
        os.path.join(ROOT, "listening_app"),
    ),

    (
        "Writing Backend       (http://localhost:8005)",
        [PYTHON, "-m", "uvicorn", "api:app", "--port", "8005", "--log-level", "warning"],
        os.path.join(ROOT, "writing_app"),
    ),
    (
        "Plagiarism Backend    (http://localhost:8002)",
        [PYTHON, "-m", "uvicorn", "plagiarism_api:app", "--port", "8002", "--log-level", "warning"],
        os.path.join(ROOT, "plagiarism_app"),
    ),
    (
        "Global Dashboard      (http://localhost:8501)",
        [PYTHON, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
        os.path.join(ROOT, "dashboard"),
    ),
    (
        "Teacher Dashboard     (http://localhost:8502)",
        [PYTHON, "-m", "streamlit", "run", "teacher_ui.py", "--server.port", "8502", "--server.headless", "true"],
        os.path.join(ROOT, "plagiarism_app"),
    ),
    (
        "Listening UI          (http://localhost:8503)",
        [PYTHON, "-m", "streamlit", "run", "ui.py", "--server.port", "8503", "--server.headless", "true"],
        os.path.join(ROOT, "listening_app"),
    ),
    (
        "Speaking Native UI    (http://localhost:8004)",
        [PYTHON, "-m", "uvicorn", "api:app", "--port", "8004", "--log-level", "warning"],
        os.path.join(ROOT, "speaking_app"),
    ),
    (
        "Writing UI            (http://localhost:8505)",
        [PYTHON, "-m", "streamlit", "run", "ui.py", "--server.port", "8505", "--server.headless", "true"],
        os.path.join(ROOT, "writing_app"),
    ),
    (
        "RAG Backend           (http://localhost:8000)",
        [PYTHON, "-m", "uvicorn", "api:app", "--port", "8000", "--log-level", "warning"],
        os.path.join(ROOT, "rag_app"),
    ),
    (
        "RAG Tutor UI          (http://localhost:8506)",
        [PYTHON, "-m", "streamlit", "run", "rag_ui.py", "--server.port", "8506", "--server.headless", "true"],
        os.path.join(ROOT, "rag_app"),
    ),
    (
        "Plagiarism Student UI (http://localhost:8507)",
        [PYTHON, "-m", "streamlit", "run", "student_ui.py", "--server.port", "8507", "--server.headless", "true"],
        os.path.join(ROOT, "plagiarism_app"),
    ),
]

processes = []

def cleanup():
    print("\n[System] Shutting down all services...")
    for p in processes:
        try:
            p.terminate()
        except:
            pass
    print("[System] All services stopped.")

atexit.register(cleanup)

def main():
    print("="*60)
    print("STARTING VIDYA AI ARCHITECTURE")
    print("="*60)

    for name, cmd, cwd in SERVICES:
        if not os.path.exists(cwd):
            print(f"[Warning] Skipping {name}: Directory '{cwd}' not found.")
            continue
            
        print(f"Starting {name}...")
        try:
            p = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            processes.append(p)
        except Exception as e:
            print(f"[Error] Failed to start {name}: {e}")
            
    print("="*60)
    print("ALL SYSTEMS ONLINE!")
    print("Press CTRL+C in this terminal to shut down everything safely.")
    print("="*60)
    print("\nACCESS LINKS:")
    print("  Global Dashboard:      http://localhost:8501")
    print("  Teacher UI:            http://localhost:8502")
    print("  Listening UI:          http://localhost:8503")
    print("  Speaking UI:           http://localhost:8004")
    print("  Writing UI:            http://localhost:8505")
    print("  RAG Tutor UI:          http://localhost:8506")
    print("  Plagiarism Student UI: http://localhost:8507\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
