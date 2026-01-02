# 📁 Storage Management System

## Overview

The system now has **three separate storage locations** for better organization and persistence:

```
📂 Project Root
├── 📁 uploads/              ← Temporary files (auto-cleanup after 24h)
├── 📁 persistent_docs/      ← Permanent files (company policies, etc.)
└── 📁 chroma_db/           ← Vector embeddings (independent of files)
```

## Storage Locations

### 1. **uploads/** - Temporary Storage
- **Purpose:** Chat uploads, one-time document queries
- **Cleanup:** Automatically deleted after 24 hours
- **Use Case:** "What's in this PDF?" queries, temporary analysis

### 2. **persistent_docs/** - Permanent Storage  
- **Purpose:** Company policies, reference documents, knowledge base
- **Cleanup:** Manual only (files stay forever)
- **Use Case:** Remote work policy, employee handbook, SOPs

### 3. **chroma_db/** - Vector Store
- **Purpose:** Semantic embeddings for fast search
- **Persistence:** Independent of source files
- **Important:** Vectors stay even if source files are deleted!

## Key Features

### ✅ Automatic Cleanup
- Runs on server startup
- Removes temporary uploads older than 24 hours
- Keeps persistent_docs/ untouched
- **Vectors remain in ChromaDB** even after file deletion

### ✅ Persistent Documents
Upload files as "persistent" to keep them forever:

**API:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@company_policy.pdf" \
  -F "persistent=true"
```

**Response:**
```json
{
  "message": "File uploaded successfully (persistent)",
  "file_path": "D:\\...\\persistent_docs\\uuid.pdf",
  "storage_type": "persistent",
  "note": "Vectors stored persistently in ChromaDB"
}
```

### ✅ Storage Info API
Check storage usage:

```bash
GET /storage/info
```

**Response:**
```json
{
  "temporary_uploads": {
    "directory": "D:\\...\\uploads",
    "file_count": 5,
    "size_mb": 12.5,
    "cleanup_policy": "Files older than 24 hours are auto-deleted"
  },
  "persistent_documents": {
    "directory": "D:\\...\\persistent_docs",
    "file_count": 3,
    "size_mb": 8.2,
    "cleanup_policy": "Manual cleanup only"
  },
  "vector_store": {
    "directory": "D:\\...\\chroma_db",
    "size_mb": 2.1,
    "note": "Vectors persist independently of source files"
  }
}
```

### ✅ Manual Cleanup
Trigger cleanup manually:

```bash
POST /storage/cleanup?max_age_hours=12
```

Removes temporary files older than 12 hours.

## Usage Examples

### Temporary Upload (Default)
For one-time questions:

```javascript
// Frontend
const formData = new FormData();
formData.append('file', file);

const response = await axios.post('/upload', formData);
// File goes to uploads/ and will be deleted after 24h
```

### Persistent Upload
For company policies or reference docs:

```javascript
// Frontend - add persistent flag
const formData = new FormData();
formData.append('file', file);
formData.append('persistent', 'true');

const response = await axios.post('/upload', formData);
// File goes to persistent_docs/ and stays forever
```

## Vector Store Behavior

**Important:** ChromaDB vectors are **always persistent** regardless of file location!

- ✅ Upload file → Vectors created in chroma_db/
- ✅ Delete source file → **Vectors remain** in chroma_db/
- ✅ Search still works even if original file is gone
- ✅ To remove vectors, you must clear chroma_db/ manually

### Why This Matters

1. **Company policies** can be embedded once and queried forever
2. **Temporary chat uploads** get cleaned up but embeddings persist
3. **No need to re-upload** documents - vectors are cached
4. **Faster queries** - embeddings pre-computed

## File Lifecycle

### Scenario 1: Temporary Chat Upload
```
1. User uploads "invoice.pdf"
2. Saved to: uploads/uuid.pdf
3. Embedded to: chroma_db/ (document_id: uuid_pdf)
4. After 24 hours: uploads/uuid.pdf deleted
5. Vectors remain: chroma_db still has embeddings
6. Search still works: Can query "invoice" concepts
```

### Scenario 2: Persistent Policy Upload
```
1. HR uploads "remote_work_policy.pdf" with persistent=true
2. Saved to: persistent_docs/uuid.pdf (permanent)
3. Embedded to: chroma_db/ (document_id: uuid_pdf)
4. File stays forever in persistent_docs/
5. Vectors stay forever in chroma_db/
6. Always available for queries
```

## Best Practices

### ✅ Use Temporary Storage For:
- One-time document analysis
- Personal file uploads in chat
- Testing new documents
- Files you don't need long-term

### ✅ Use Persistent Storage For:
- Company policies
- Employee handbooks
- Standard operating procedures
- Reference documentation
- Knowledge base articles

### ✅ ChromaDB Management:
- Vectors accumulate over time
- Periodic manual cleanup recommended
- To clear: `rm -rf chroma_db/` (on startup it will recreate)
- Or use: `Remove-Item -Path "./chroma_db" -Recurse -Force` (Windows)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload file (persistent=false default) |
| `/upload?persistent=true` | POST | Upload to persistent storage |
| `/storage/info` | GET | Get storage statistics |
| `/storage/cleanup` | POST | Manually clean old temporary files |

## Configuration

Edit `main.py` to change defaults:

```python
# Storage directories
UPLOADS_DIR = Path("uploads")           # Temp uploads
PERSISTENT_DIR = Path("persistent_docs") # Permanent docs  
CHROMA_DB_DIR = Path("chroma_db")       # Vector store

# Cleanup on startup (24 hours default)
cleanup_old_uploads(max_age_hours=24)
```

## Troubleshooting

### Q: "Why can I still search deleted files?"
**A:** Vectors persist in ChromaDB even after source file deletion. This is by design for performance.

### Q: "How do I free up disk space?"
**A:** 
1. Temporary files auto-delete after 24h
2. Manual cleanup: `POST /storage/cleanup`
3. Clear vectors: Delete chroma_db/ folder

### Q: "Can I change cleanup time?"
**A:** Yes! Edit `cleanup_old_uploads(max_age_hours=24)` in main.py startup

### Q: "What if I upload the same file twice?"
**A:** Each upload gets unique UUID filename, so duplicates won't conflict. Vectors are stored separately by document_id.

## Monitoring

Check storage usage regularly:

```bash
# Get current usage
curl http://localhost:8000/storage/info

# View directories
ls -lh uploads/
ls -lh persistent_docs/
du -sh chroma_db/
```

## Summary

✅ **uploads/** = Temporary (auto-cleanup 24h)  
✅ **persistent_docs/** = Permanent (manual cleanup)  
✅ **chroma_db/** = Vector embeddings (independent of files)  
✅ Vectors persist even when files are deleted  
✅ Automatic cleanup on server startup  
✅ Manual cleanup via API  
✅ Storage info monitoring  

Your multi-agent system now has production-ready storage management! 🚀
