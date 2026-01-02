
# 🦙 Ollama Setup Guide

## Overview
Ollama provides free, local LLM inference for agentic workflows. For best results, use a stable, capable model.

## Model Selection & Setup

### 1. List Available Models
```bash
ollama list
```

### 2. Pull a Recommended Model
- **Llama 3.2 (3B, fast, reliable):**
	```bash
	ollama pull llama3.2
	```
- **Qwen 2.5 (7B, good balance):**
	```bash
	ollama pull qwen2.5:7b
	```
- **Mistral (7B, popular):**
	```bash
	ollama pull mistral
	```

### 3. Update `.env`
```bash
OLLAMA_MODEL=llama3.2
# or any model from `ollama list`
```

### 4. Run Tests
```bash
uv run test_agents.py
```

## Troubleshooting

- **Model not found:**
	- Pull the model with `ollama pull <model>`
- **Want to use OpenAI/Google instead?**
	- Comment out Ollama lines in `.env`:
		```bash
		# OLLAMA_BASE_URL=http://localhost:11434
		# OLLAMA_MODEL=llama3.2
		```

## Quick Fix

Update `.env` to use a common model:
```bash
OLLAMA_MODEL=llama3.2
```
Then pull the model:
```bash
ollama pull llama3.2
```
Run your tests:
```bash
uv run test_agents.py
```

## Notes
- Larger models (7B+) require more RAM (8GB+ recommended)
- For best tool calling, avoid very small models (e.g., qwen3:0.6b)
- Ollama is free, local, and works offline

---

**Ollama is a great local fallback for agentic AI workflows!**
