from huggingface_hub import hf_hub_download
import os
import sys
import shutil

print("Downloading Kokoro ONNX model files...")
try:
    os.makedirs("kokoro_models", exist_ok=True)
    
    # Download ONNX model
    hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-ONNX", 
        filename="onnx/model.onnx", 
        local_dir="kokoro_models"
    )
    # Move to root of kokoro_models for simplicity
    if os.path.exists("kokoro_models/onnx/model.onnx"):
        shutil.move("kokoro_models/onnx/model.onnx", "kokoro_models/model.onnx")
    
    # Download voices
    hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-ONNX", 
        filename="voices/af_bella.bin", 
        local_dir="kokoro_models"
    )
    if os.path.exists("kokoro_models/voices/af_bella.bin"):
        shutil.move("kokoro_models/voices/af_bella.bin", "kokoro_models/voices.bin")

    print("Download complete!")
except Exception as e:
    print(f"Error downloading: {e}")
    sys.exit(1)
