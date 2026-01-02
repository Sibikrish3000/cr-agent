import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { 
  Send, 
  Paperclip, 
  Trash2, 
  Bot, 
  User, 
  AlertCircle, 
  FileText, 
  Loader2,
  Cloud,
  Calendar,
  Database,
  File,
  X,
  Plus,
  MessageSquare,
  History,
  Menu,
  HardDrive // Added icon for storage
} from 'lucide-react';
import './App.css';
import StorageManager from './components/StorageManager'; // Import StorageManager

function App() {
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem('chat_sessions');
    return saved ? JSON.parse(saved) : [];
  });
  const [currentSessionId, setCurrentSessionId] = useState(Date.now());
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your **Multi-Agent AI assistant**. I can help with:\n\n- 🌤️ **Weather information**\n- 📄 **Document analysis** (upload PDF/TXT/MD)\n- 📅 **Meeting scheduling** with weather checks\n- 💾 **Database queries** about meetings\n\nHow can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isPersistentUpload, setIsPersistentUpload] = useState(false); // State for persistent upload toggle
  const [showStorageManager, setShowStorageManager] = useState(false); // State to toggle Storage Manager view
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const textInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Save sessions to localStorage
  useEffect(() => {
    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
  }, [sessions]);

  // Update current session in sessions list
  useEffect(() => {
    if (messages.length <= 1 && !uploadedFile) return;

    setSessions(prev => {
      const existingIdx = prev.findIndex(s => s.id === currentSessionId);
      const title = messages.find(m => m.role === 'user')?.content.substring(0, 30) || 'New Chat';
      
      const sessionData = {
        id: currentSessionId,
        title: title.length >= 30 ? title + '...' : title,
        messages,
        uploadedFile,
        timestamp: new Date().toISOString()
      };

      if (existingIdx >= 0) {
        const newSessions = [...prev];
        newSessions[existingIdx] = sessionData;
        return newSessions;
      } else {
        return [sessionData, ...prev];
      }
    });
  }, [messages, uploadedFile, currentSessionId]);

  const createNewChat = () => {
    setCurrentSessionId(Date.now());
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m your **Multi-Agent AI assistant**. I can help with:\n\n- 🌤️ **Weather information**\n- 📄 **Document analysis** (upload PDF/TXT/MD)\n- 📅 **Meeting scheduling** with weather checks\n- 💾 **Database queries** about meetings\n\nHow can I help you today?'
      }
    ]);
    setUploadedFile(null);
    if (textInputRef.current) textInputRef.current.focus();
  };

  const loadSession = (session) => {
    setCurrentSessionId(session.id);
    setMessages(session.messages);
    setUploadedFile(session.uploadedFile);
  };

  const deleteSession = (e, id) => {
    e.stopPropagation();
    setSessions(prev => prev.filter(s => s.id !== id));
    if (currentSessionId === id) {
      createNewChat();
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    if (isPersistentUpload) {
      formData.append('persistent', 'true');
    }

    try {
      setIsLoading(true);
      const response = await axios.post('http://0.0.0.0:7860/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadedFile({
        name: file.name,
        path: response.data.file_path,
        size: response.data.file_size,
        isPersistent: isPersistentUpload
      });

      setMessages(prev => [...prev, {
        role: 'system',
        content: `📎 **File uploaded:** ${file.name} (${response.data.file_size}) ${isPersistentUpload ? '(Persistent)' : ''}\n\nYou can now ask questions about this document!`
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: `❌ File upload failed: ${error.response?.data?.detail || error.message}`
      }]);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const removeFile = (e) => {
    e.stopPropagation();
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setMessages(prev => [...prev, {
      role: 'system',
      content: '📎 File removed from context.'
    }]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://0.0.0.0:7860/chat', {
        query: userMessage,
        file_path: uploadedFile?.path || null
      });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: `❌ Error: ${error.response?.data?.detail || error.message}`
      }]);
    } finally {
      setIsLoading(false);
      setTimeout(() => textInputRef.current?.focus(), 100);
    }
  };

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: 'Chat cleared! How can I help you?'
    }]);
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (textInputRef.current) {
      textInputRef.current.focus();
    }
  };

  const handleExampleClick = (text) => {
    setInput(text);
    if (textInputRef.current) {
      textInputRef.current.focus();
    }
  };

  const exampleQueries = [
    { icon: <Cloud size={16} />, text: 'What\'s the weather in Chennai?' },
    { icon: <Calendar size={16} />, text: 'Schedule a team meeting tomorrow at 2pm' },
    { icon: <Database size={16} />, text: 'Show all meetings scheduled tomorrow' },
    { icon: <FileText size={16} />, text: 'What is the remote work policy?' }
  ];

  return (
    <div className={`App ${!isSidebarOpen ? 'sidebar-closed' : ''}`}>
      <aside className="sidebar">
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={createNewChat}>
            <Plus size={18} />
            <span>New Chat</span>
          </button>
        </div>
        
        <div className="sidebar-content">
          <div className="sidebar-section">
            <div className="section-title">
              <History size={14} />
              <span>Recent Chats</span>
            </div>
            <div className="sessions-list">
              {sessions.map(session => (
                <div 
                  key={session.id} 
                  className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
                  onClick={() => loadSession(session)}
                >
                  <MessageSquare size={16} />
                  <span className="session-title">{session.title}</span>
                  <button 
                    className="delete-session-btn" 
                    onClick={(e) => deleteSession(e, session.id)}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
              {sessions.length === 0 && (
                <div className="no-sessions">No past chats yet</div>
              )}
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">S</div>
            <div className="user-info">
              <span className="user-name">Sibi Krishnamoorthy</span>
              <span className="user-status">Online</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <div className="chat-container">
          <div className="chat-header">
            <div className="header-left">
              <button 
                className="btn-icon sidebar-toggle" 
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                title={isSidebarOpen ? "Close sidebar" : "Open sidebar"}
              >
                <Menu size={20} />
              </button>
              <div className="header-content">
                <h1><Bot className="header-icon" /> Multi-Agent AI Assistant</h1>
                <p>Weather • Documents • Meetings • SQL</p>
              </div>
            </div>
            <div className="header-actions">
              <button 
                className={`btn-icon ${showStorageManager ? 'active' : ''}`} 
                onClick={() => setShowStorageManager(!showStorageManager)}
                title="Storage Manager"
              >
                <HardDrive size={20} />
              </button>
              {uploadedFile && (
                <div className="uploaded-file-badge">
                  <File size={14} />
                  <span className="file-name">{uploadedFile.name}</span>
                  <button onClick={removeFile} className="remove-file-btn" title="Remove file">
                    <X size={12} />
                  </button>
                </div>
              )}
              <div className="upload-controls" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <label style={{ fontSize: '0.8em', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
                  <input 
                    type="checkbox" 
                    checked={isPersistentUpload} 
                    onChange={(e) => setIsPersistentUpload(e.target.checked)}
                  />
                  Persistent
                </label>
                <button onClick={() => fileInputRef.current?.click()} className="btn-icon" title="Upload file">
                  <Paperclip size={20} />
                </button>
              </div>
              <button onClick={clearChat} className="btn-icon" title="Clear current chat">
                <Trash2 size={20} />
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.md,.docx"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>

          {showStorageManager ? (
            <div className="storage-manager-container" style={{ padding: '20px', overflowY: 'auto' }}>
              <StorageManager />
            </div>
          ) : (
            <>
              <div className="messages-container">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? <User size={20} /> : 
                       msg.role === 'error' ? <AlertCircle size={20} /> : 
                       msg.role === 'system' ? <FileText size={20} /> : 
                       <Bot size={20} />}
                    </div>
                    <div className="message-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="message assistant">
                    <div className="message-avatar"><Bot size={20} /></div>
                    <div className="message-content loading">
                      <Loader2 className="spinner" size={20} />
                      <span>Thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="example-queries">
                {exampleQueries.map((query, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleExampleClick(query.text)}
                    className="example-query"
                    disabled={isLoading}
                  >
                    {query.icon}
                    <span>{query.text}</span>
                  </button>
                ))}
              </div>

              <form onSubmit={handleSubmit} className="input-container">
                <input
                  ref={textInputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about weather, meetings, documents, or upload a file..."
                  disabled={isLoading}
                  className="chat-input"
                />
                <button type="submit" disabled={isLoading || !input.trim()} className="send-button">
                  {isLoading ? <Loader2 className="spinner" size={20} /> : <Send size={20} />}
                </button>
              </form>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
