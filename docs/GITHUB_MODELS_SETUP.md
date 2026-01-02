
# 🚀 GitHub Models Setup (Recommended)

## Why Use GitHub Models?

- **Free tier**: No credit card required
- **Excellent tool calling**: More reliable than small local models
- **Stable cloud endpoint**: No disconnects
- **Fast responses**: 2-5 seconds per query
- **Easy setup**: Just need a GitHub personal access token

## Quick Setup

### 1. Get a GitHub Personal Access Token
- Go to [GitHub tokens](https://github.com/settings/tokens)
- Click "Generate new token (classic)"
- Name it (e.g., `Multi-Agent Backend Testing`)
- Select scopes: `repo` (if needed), `read:org` (optional)
- Click "Generate token" and copy it

### 2. Configure Environment
```powershell
notepad .env
# Add your token:
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Test Your Setup
```powershell
uv run test_agents.py
# Should see: Using GitHub Models: openai/gpt-5-mini via https://models.github.ai
```

## LLM Priority Order
1. GitHub Models (if `GITHUB_TOKEN` set)
2. OpenAI (if `OPENAI_API_KEY` set)
3. Google GenAI (if `GOOGLE_API_KEY` set)
4. Ollama (local fallback)

## Troubleshooting

- **Initialization failed**: Check token validity and format (`ghp_` or `github_pat_`, 40+ chars)
- **Rate limit exceeded**: Wait 1 minute or use another provider
- **Model not available**: List available models:
  ```powershell
  curl -H "Authorization: Bearer YOUR_TOKEN" -H "Accept: application/vnd.github+json" https://models.github.ai/models
  ```

## Alternative Models

If `gpt-5-mini` has issues, try:
- Claude: `anthropic/claude-3-5-sonnet`
- Llama: `meta-llama/Meta-Llama-3.1-8B-Instruct`
- GPT-4: `openai/gpt-4`
Edit `.env` or [agents.py](agents.py) to change the model.

## Comparison: GitHub Models vs Ollama

| Feature        | GitHub Models | Ollama (qwen3:0.6b) |
|--------------- |--------------|---------------------|
| Setup          | 2 min        | 10+ min             |
| Cost           | Free         | Free (local)        |
| Speed          | 2-5 sec      | 5-15 sec            |
| Reliability    | 98%          | 50% (disconnects)   |
| Tool Calling   | Excellent    | Poor                |
| RAM Usage      | 0 MB         | 1-2 GB              |
| GPU Needed     | No           | Optional            |
| Quality        | High         | Low                 |

## Production Deployment

- Use paid GitHub Models tier for higher limits
- OpenAI API for maximum reliability
- Azure OpenAI for enterprise features
Automatic fallback supported in codebase

## Reverting to Ollama

Comment out `GITHUB_TOKEN` in `.env` and set:
```powershell
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Summary

GitHub Models is the **recommended default** for this project:
- Free, easy, production-quality responses
- No local resource requirements
- Excellent tool calling for agentic workflows

[Get started in 2 minutes](https://github.com/settings/tokens)

🎉 Happy testing!
