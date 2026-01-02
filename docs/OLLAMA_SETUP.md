# Ollama Configuration Guide

## Current Issue
Your `.env` has `OLLAMA_MODEL=gpt-oss:20b-cloud` but this model isn't available in your Ollama installation.

## Solutions

### Option 1: Pull the GPT-OSS model (Recommended if you want this specific model)
```bash
ollama pull gpt-oss:20b-cloud
```

### Option 2: Use a different model that's already available
Check what models you have:
```bash
ollama list
```

Then update your `.env` to use one of those models, for example:
```bash
OLLAMA_MODEL=llama3.2
# or
OLLAMA_MODEL=qwen2.5:7b
# or any other model from `ollama list`
```

### Option 3: Pull a popular lightweight model
```bash
# Pull Llama 3.2 (3B - lightweight)
ollama pull llama3.2

# OR pull Qwen 2.5 (7B - good balance)
ollama pull qwen2.5:7b

# OR pull Mistral (7B - popular)
ollama pull mistral
```

### Option 4: Disable Ollama temporarily
If you want to use only OpenAI or Google GenAI for now, comment out the Ollama lines in `.env`:
```bash
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=gpt-oss:20b-cloud
```

## Quick Fix
The fastest solution is to update `.env` line 12 to use a common model:
```bash
OLLAMA_MODEL=llama3.2
```

Then run:
```bash
ollama pull llama3.2
```

After that, run your tests again:
```bash
uv run test_agents.py
```
