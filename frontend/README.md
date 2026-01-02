# Multi-Agent AI Chat Frontend

Beautiful React.js chat interface for the Multi-Agent AI backend.

## Features

✨ **Modern UI Design**
- Gradient backgrounds and smooth animations
- Responsive layout
- Real-time typing indicators
- Chat history with scrolling

🎯 **Core Functionality**
- Send queries to multi-agent backend
- Upload documents (PDF, TXT, MD, DOCX)
- Example queries for quick start
- Error handling with visual feedback
- Clear chat option

🤖 **Agent Capabilities**
- Weather information queries
- Document analysis with RAG
- Meeting scheduling with weather checks
- SQL database queries

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Backend
```bash
# In the parent directory
cd ..
uv run uvicorn main:app --reload
```

### 3. Start Frontend
```bash
# In the frontend directory
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Usage

### Asking Questions
Type your question in the input box and press Enter or click the send button (📤).

**Example queries:**
- "What's the weather in Chennai?"
- "Schedule a team meeting tomorrow at 2pm"
- "Show all meetings scheduled tomorrow"

### Uploading Documents
1. Click the folder icon (📁) in the header
2. Select a PDF, TXT, MD, or DOCX file
3. Ask questions about the uploaded document

**Example:**
- Upload: `company_policy.pdf`
- Ask: "What is the remote work equipment policy?"

### Example Query Buttons
Click any of the example query buttons to quickly populate the input field:
- 🌤️ Weather queries
- 📅 Meeting scheduling
- 💾 Database queries
- 📄 Document questions

## Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP
         │ /chat
         │ /upload
         ▼
┌─────────────────┐
│ FastAPI Backend │
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
[Weather] [Docs+RAG] [Meeting] [SQL]
```

## API Integration

The frontend communicates with the backend using two endpoints:

### POST /chat
```javascript
{
  "query": "What's the weather?",
  "file_path": "/path/to/file.pdf" // optional
}
```

### POST /upload
```javascript
FormData with 'file' field
```

## Customization

### Changing Colors
Edit `src/App.css` and modify the gradient colors:
```css
background: linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2);
```

### Adding Features
Edit `src/App.js` to add new functionality:
- Modify the `exampleQueries` array
- Add new UI components
- Enhance chat message rendering

## Troubleshooting

### Backend Connection Issues
- Ensure FastAPI backend is running on port 8000
- Check the proxy setting in `package.json`

### File Upload Fails
- Check file size limit (10MB default)
- Verify file type is supported (PDF, TXT, MD, DOCX)

### Chat Not Responding
- Check browser console for errors
- Verify backend is running and accessible

## Production Build

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

To serve the production build:
```bash
npx serve -s build
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

---

**Made with ❤️ for seamless AI interactions**
