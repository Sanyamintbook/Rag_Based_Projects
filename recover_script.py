import json
import os

transcript_path = r"C:\Users\Sanyami Jain\.gemini\antigravity\brain\1b6a51d8-ca49-400e-b32d-7dd7ceecb7a3\.system_generated\logs\transcript.jsonl"

targets = [
    r"rag_app\api.py",
    r"rag_app\app.py",
    r"listening_app\ui.py",
    r"speaking_app\ui.py",
    r"plagiarism_app\plagiarism_api.py",
    r"plagiarism_app\teacher_ui.py",
    r"plagiarism_app\detectors\ai_detector.py",
    r"plagiarism_app\detectors\copy_detector.py",
    r"plagiarism_app\detectors\originality_scorer.py"
]

recovered_code = {t: None for t in targets}

print("Parsing transcript to recover code...")
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line.strip())
            if "tool_calls" in data:
                for tool in data["tool_calls"]:
                    if tool["name"] == "write_to_file":
                        args = tool.get("args", {})
                        target_file = args.get("TargetFile", "")
                        code_content = args.get("CodeContent", "")
                        
                        for t in targets:
                            if target_file.endswith(t):
                                recovered_code[t] = code_content
                                
                    elif tool["name"] == "multi_replace_file_content":
                        # We might miss multi_replace edits, but usually we wrote the file via write_to_file first.
                        # For the sake of this simple recovery, we just grab the last full write_to_file.
                        pass
        except Exception as e:
            pass

# Write the recovered files to disk
for t, code in recovered_code.items():
    if code:
        full_path = os.path.join(r"C:\Users\Sanyami Jain\Documents\SCIENCE_RAG_PROJECT-main", t)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as out:
            out.write(code)
        print(f"Recovered: {t}")
    else:
        print(f"Could not find code for: {t}")
