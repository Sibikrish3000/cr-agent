"""
Ingest persistent documents into vector store.
Run this to make company policies searchable.
"""
from pathlib import Path
from vector_store import get_vector_store

def ingest_persistent_docs():
    """Ingest all documents from persistent_docs/ into vector store."""
    persistent_dir = Path("persistent_docs")
    
    if not persistent_dir.exists():
        print("❌ persistent_docs/ directory not found")
        return
    
    vector_store = get_vector_store()
    
    # Find all supported files
    supported_extensions = ['.txt', '.md']
    files = []
    for ext in supported_extensions:
        files.extend(persistent_dir.glob(f'*{ext}'))
    
    if not files:
        print("📂 No text files found in persistent_docs/")
        return
    
    print(f"\n📚 Found {len(files)} document(s) to ingest:")
    
    for file_path in files:
        try:
            print(f"\n📄 Processing: {file_path.name}")
            
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            # Use filename without extension as document_id
            doc_id = file_path.stem
            
            # Ingest into vector store
            num_chunks = vector_store.ingest_document(
                document_text=content,
                document_id=doc_id,
                metadata={
                    "file_path": str(file_path.absolute()),
                    "filename": file_path.name,
                    "storage_type": "persistent"
                },
                chunk_size=500,
                chunk_overlap=50
            )
            
            print(f"   ✅ Ingested '{doc_id}' - Created {num_chunks} chunks")
            
        except Exception as e:
            print(f"   ❌ Failed to ingest {file_path.name}: {e}")
    
    print(f"\n🎉 Ingestion complete! Documents are now searchable.\n")

if __name__ == "__main__":
    print("=" * 60)
    print("PERSISTENT DOCUMENTS INGESTION")
    print("=" * 60)
    ingest_persistent_docs()
