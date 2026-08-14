from fastapi import FastAPI, HTTPException  # <--- Added HTTPException here
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# =========================================================================
# 1. INITIALIZE THE FASTAPI APP
# =========================================================================
app = FastAPI(title="10th Grade Science AI Tutor")

class UserRequest(BaseModel):
    question: str

# =========================================================================
# 2. LOAD THE RAG PIPELINE
# =========================================================================
import os
from langchain_core.runnables import RunnablePassthrough

INDEX_DIR = "faiss_science_index"

print("Booting up the AI Engine...")
llm = OllamaLLM(model="qwen2.5:7b", base_url="http://45.194.3.86:11434")

system_prompt = (
    "You are a helpful 10th-grade science tutor.\n"
    "Answer the user's question clearly and accurately as if you are referencing their 10th-grade science textbook.\n"
    "Keep your answers concise, easy to understand, and educational.\n\n"
    "Textbook Context:\n{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

if os.path.exists(INDEX_DIR) and os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://45.194.3.86:11434")
    db = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
else:
    print("Warning: FAISS index not found. Running in standard LLM mode without vector embeddings.")
    # Fallback chain without retrieval
    rag_chain = (
        {"context": lambda x: "No textbook context available. Answer based on general science knowledge.", "input": lambda x: x["input"]} 
        | prompt 
        | llm 
        | (lambda output: {"answer": output})
    )

print("Engine Ready! Web server is live.")

# =========================================================================
# 3. CREATE THE API ENDPOINT (Now with Error Catching!)
# =========================================================================

@app.post("/ask")
def ask_tutor(request: UserRequest):
    try:
        # We TRY to do the normal process...
        response = rag_chain.invoke({"input": request.question})
        return {"answer": response["answer"]}
        
    except Exception as e:
        # IF IT FAILS, catch the exact error and print it to the web browser!
        print(f"CRASH REPORT: {str(e)}")
        raise HTTPException(status_code=500, detail=f"The AI Engine Crashed: {str(e)}")