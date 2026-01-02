
# 📁 Storage Management Guide

## Overview
Your system uses three storage locations for organization and persistence:

```
Project Root
├── uploads/         # Temporary files (auto-cleanup after 24h)
├── persistent_docs/ # Permanent files (company policies, etc.)
└── chroma_db/       # Vector embeddings (independent of files)
```

## Storage Types

### uploads/
- Temporary chat uploads, one-time document queries
- Auto-deleted after 24 hours

### persistent_docs/
- Permanent storage for company policies, reference docs
- Manual cleanup only

### chroma_db/
- Persistent semantic embeddings for fast search
- Vectors remain even if source files are deleted

## Key Features

- **Automatic Cleanup:** Temporary uploads deleted after 24h (on startup or via API)
- **Persistent Documents:** Upload with `persistent=true` to store forever
- **Vector Store:** ChromaDB vectors always persist, even if files are deleted

## API Usage

### Upload File (Temporary)
```bash
curl -X POST "http://localhost:8000/upload" -F "file=@file.pdf"
# File goes to uploads/ and will be deleted after 24h
```

### Upload File (Persistent)
```bash
curl -X POST "http://localhost:8000/upload" -F "file=@file.pdf" -F "persistent=true"
# File goes to persistent_docs/ and stays forever
```

### Get Storage Info
```bash
curl http://localhost:8000/storage/info
```

### Manual Cleanup
```bash
curl -X POST "http://localhost:8000/storage/cleanup?max_age_hours=12"
# Removes temporary files older than 12 hours
```

## Vector Store Behavior

- Upload file → Vectors created in chroma_db/
- Delete source file → Vectors remain in chroma_db/
- Search works even if original file is gone
- To remove vectors, clear chroma_db/ manually

## Best Practices

- Use temporary storage for one-time analysis, personal uploads, testing
- Use persistent storage for policies, handbooks, SOPs, knowledge base
- Periodically clean chroma_db/ to free disk space

## Troubleshooting

- **Why can I still search deleted files?**
  - Vectors persist in ChromaDB by design
- **How do I free up disk space?**
  - Temporary files auto-delete; clear chroma_db/ for vectors
- **Change cleanup time?**
  - Edit `cleanup_old_uploads(max_age_hours=24)` in main.py
- **Duplicate uploads?**
  - Each upload gets a unique UUID filename; vectors stored by document_id

## Monitoring

Check usage regularly:
```bash
curl http://localhost:8000/storage/info
ls -lh uploads/
ls -lh persistent_docs/
du -sh chroma_db/
```

## Summary

- uploads/: Temporary, auto-cleanup (24h)
- persistent_docs/: Permanent, manual cleanup
- chroma_db/: Persistent vectors, independent of files
- Automatic and manual cleanup supported
- Storage info API for monitoring

Your multi-agent system now has production-ready storage management! 🚀
