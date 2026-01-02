import os
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from database import create_db_and_tables
from agents import app as agent_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Storage directories
UPLOADS_DIR = Path("uploads")  # Temporary uploads (cleared periodically)
PERSISTENT_DIR = Path("persistent_docs")  # Permanent documents (company policies, etc.)
CHROMA_DB_DIR = Path("chroma_db")  # Vector store (persists independently)

def cleanup_old_uploads(max_age_hours: int = 24):
    """Clean up temporary uploads older than max_age_hours."""
    if not UPLOADS_DIR.exists():
        return
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    removed_count = 0
    
    for file_path in UPLOADS_DIR.glob('*'):
        if file_path.is_file():
            file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age < cutoff_time:
                try:
                    file_path.unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
    
    if removed_count > 0:
        print(f"✅ Cleaned up {removed_count} old temporary files from uploads/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    
    # Create storage directories
    UPLOADS_DIR.mkdir(exist_ok=True)
    PERSISTENT_DIR.mkdir(exist_ok=True)
    CHROMA_DB_DIR.mkdir(exist_ok=True)
    
    # Clean up old temporary uploads on startup
    cleanup_old_uploads(max_age_hours=24)
    
    print(f"📁 Storage initialized:")
    print(f"   - Temp uploads: {UPLOADS_DIR.absolute()}")
    print(f"   - Persistent docs: {PERSISTENT_DIR.absolute()}")
    print(f"   - Vector store: {CHROMA_DB_DIR.absolute()}")
    
    yield
    # Shutdown

app = FastAPI(title="Multi-Agent AI Backend", lifespan=lifespan)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:7860", "http://127.0.0.1:7860"],  # React dev server and Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    file_path: str | None = None
    thread_id: str = "default"

class UploadRequest(BaseModel):
    persistent: bool = False  # If True, store in persistent_docs instead of uploads

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Process a user query through the Agentic Workflow.
    Optionally accepts a file_path for document QA.
    """
    inputs = {"messages": [HumanMessage(content=request.query)]}
    if request.file_path:
        inputs["file_path"] = request.file_path
    
    try:
        # Invoke the LangGraph workflow
        result = agent_app.invoke(inputs)
        final_message = result["messages"][-1].content
        return {"response": final_message}
    except StopIteration as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ StopIteration Error Details:\n{error_details}")
        raise HTTPException(status_code=500, detail="Model returned empty response. Try a different model or check API configuration.")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error Details:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), persistent: bool = False):
    """
    Upload a document for the Document Agent to process.
    Returns the absolute file path to be passed to the chat endpoint.
    
    Args:
        file: The file to upload
        persistent: If True, store in persistent_docs/ (for company policies, etc.)
                   If False, store in uploads/ (temporary, cleaned up after 24h)
    
    Supports: PDF, TXT, MD, DOCX files
    Max size: 10MB
    
    Note: Vectors are ALWAYS stored persistently in ChromaDB regardless of file location
    """
    # File validation
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md', 'docx'}
    
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type '.{file_ext}' not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Choose storage directory
        storage_dir = PERSISTENT_DIR if persistent else UPLOADS_DIR
        storage_type = "persistent" if persistent else "temporary"
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}.{file_ext}"
        file_path = storage_dir / file_name
        
        # Read and validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (10MB)"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Write file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        return {
            "message": f"File uploaded successfully ({storage_type})", 
            "file_path": str(file_path.absolute()),
            "document_id": f"{file_id}_{file_ext}",
            "file_size": f"{file_size / 1024:.2f}KB",
            "file_type": file_ext,
            "storage_type": storage_type,
            "note": "Vectors stored persistently in ChromaDB"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/storage/info")
async def get_storage_info():
    """Get information about storage usage."""
    def get_dir_size(path: Path) -> tuple[int, int]:
        """Returns (total_size_bytes, file_count)"""
        if not path.exists():
            return 0, 0
        total = 0
        count = 0
        for file in path.glob('**/*'):
            if file.is_file():
                total += file.stat().st_size
                count += 1
        return total, count
    
    uploads_size, uploads_count = get_dir_size(UPLOADS_DIR)
    persistent_size, persistent_count = get_dir_size(PERSISTENT_DIR)
    chroma_size, _ = get_dir_size(CHROMA_DB_DIR)
    
    return {
        "temporary_uploads": {
            "directory": str(UPLOADS_DIR.absolute()),
            "file_count": uploads_count,
            "size_mb": round(uploads_size / 1024 / 1024, 2),
            "cleanup_policy": "Files older than 24 hours are auto-deleted"
        },
        "persistent_documents": {
            "directory": str(PERSISTENT_DIR.absolute()),
            "file_count": persistent_count,
            "size_mb": round(persistent_size / 1024 / 1024, 2),
            "cleanup_policy": "Manual cleanup only"
        },
        "vector_store": {
            "directory": str(CHROMA_DB_DIR.absolute()),
            "size_mb": round(chroma_size / 1024 / 1024, 2),
            "note": "Vectors persist independently of source files"
        }
    }

@app.post("/storage/cleanup")
async def cleanup_storage(max_age_hours: int = 24):
    """Manually trigger cleanup of old temporary uploads."""
    if max_age_hours < 1 or max_age_hours > 168:  # 1 hour to 1 week
        raise HTTPException(status_code=400, detail="max_age_hours must be between 1 and 168")
    
    cleanup_old_uploads(max_age_hours)
    return {"message": f"Cleanup completed for files older than {max_age_hours} hours"}

# Serve React Frontend (for production/Docker)
frontend_path = Path("frontend/build")
if frontend_path.exists():
    # Mount static assets
    app.mount("/static", StaticFiles(directory=frontend_path / "static"), name="static")
    
    # Catch-all route for React Router
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Check if file exists in build directory
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
            
        # Fallback to index.html for React Router
        return FileResponse(frontend_path / "index.html")

# CLI entry point for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
