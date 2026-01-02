# 🎨 Frontend Setup Guide

## Overview

Beautiful React.js chat interface with gradient design, real-time updates, and full chat memory.

## Prerequisites

- Node.js 16+ and npm
- Backend running on port 8000

## Installation

### Option 1: Using npm (Recommended)

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will automatically open at [http://localhost:3000](http://localhost:3000)

### Option 2: Using yarn

```powershell
cd frontend
yarn install
yarn start
```

## Running Both Backend and Frontend

**Terminal 1 - Backend:**
```powershell
cd D:\python_workspace\multi-agent
uv run uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd D:\python_workspace\multi-agent\frontend
npm start
```

## Features Showcase

### 1. Chat Interface
- 💬 Modern gradient design
- 📜 Scrollable chat history
- ⚡ Real-time typing indicators
- 🎨 Different colors for user/assistant/error messages

### 2. File Upload
- 📁 Click folder icon to upload
- ✅ Supported: PDF, TXT, MD, DOCX
- 📎 File badge shows current upload
- 🔍 Ask questions about uploaded documents

### 3. Example Queries
- 🌤️ "What's the weather in Chennai?"
- 📅 "Schedule a team meeting tomorrow at 2pm"
- 💾 "Show all meetings scheduled tomorrow"
- 📄 "What is the remote work policy?"

### 4. Chat Memory
- ✅ Full conversation history maintained
- 🗑️ Clear chat button to start fresh
- 📌 System messages for file uploads

## Screenshots

```
┌─────────────────────────────────────────┐
│ 🤖 Multi-Agent AI Assistant             │
│ Weather • Documents • Meetings • SQL    │
└─────────────────────────────────────────┘
│                                         │
│ 🤖 Hello! I'm your Multi-Agent AI...   │
│                                         │
│            What's the weather? 👤        │
│                                         │
│ 🤖 The weather in Chennai is...        │
│                                         │
└─────────────────────────────────────────┘
│ 🌤️ Weather | 📅 Meetings | 💾 SQL      │
└─────────────────────────────────────────┘
│ Type your message...               📤  │
└─────────────────────────────────────────┘
```

## API Integration

The frontend uses axios to communicate with FastAPI:

### Chat Endpoint
```javascript
POST http://localhost:8000/chat
{
  "query": "user question",
  "file_path": "path/to/uploaded/file" // optional
}
```

### Upload Endpoint
```javascript
POST http://localhost:8000/upload
FormData: { file: File }
```

## Customization

### Change Theme Colors
Edit `frontend/src/App.css`:

```css
.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Change to your preferred gradient */
.chat-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
```

### Add More Example Queries
Edit `frontend/src/App.js`:

```javascript
const exampleQueries = [
  '🌤️ What\'s the weather in Chennai?',
  '📅 Schedule a team meeting tomorrow at 2pm',
  // Add your custom queries here
  '🔍 Search for AI trends',
];
```

## Production Deployment

### Build for Production
```powershell
cd frontend
npm run build
```

### Serve Static Build
```powershell
# Using Python
cd build
python -m http.server 3000

# Or using serve package
npm install -g serve
serve -s build -p 3000
```

### Deploy to Vercel (Free)
```powershell
npm install -g vercel
cd frontend
vercel
```

### Deploy to Netlify (Free)
1. Push to GitHub
2. Connect repo to Netlify
3. Set build command: `npm run build`
4. Set publish directory: `build`

## Troubleshooting

### "Cannot connect to backend"
**Solution:**
1. Check backend is running: `http://localhost:8000/docs`
2. Verify proxy setting in `package.json`: `"proxy": "http://localhost:8000"`

### "File upload failed"
**Reasons:**
- File too large (>10MB)
- Unsupported file type
- Backend not running

**Solution:** Check backend logs and file constraints

### "npm install fails"
**Solution:**
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
**Solution:**
```powershell
# Use different port
set PORT=3001 && npm start

# Or kill existing process
npx kill-port 3000
```

## Development Tips

### Hot Reload
Changes to React components automatically reload in browser

### React DevTools
Install [React Developer Tools](https://react.dev/learn/react-developer-tools) for debugging

### API Testing
Use the browser's Network tab to inspect API calls

## Architecture

```
Frontend (React)
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── App.js              # Main chat component
│   ├── App.css             # Styling
│   ├── index.js            # Entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies
└── README.md               # Documentation
```

## Next Steps

1. **Start both services:**
   - Backend: `uv run uvicorn main:app --reload`
   - Frontend: `cd frontend && npm start`

2. **Test the interface:**
   - Try weather queries
   - Upload a document
   - Schedule a meeting
   - Query the database

3. **Customize:**
   - Change colors in CSS
   - Add new features
   - Deploy to production

---

**Enjoy your beautiful AI chat interface! 🚀**
