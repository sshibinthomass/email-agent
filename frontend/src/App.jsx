import { useState, useEffect } from 'react';
import { 
  Mail, 
  Send, 
  History as HistoryIcon, 
  Trash2, 
  Settings, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Clock, 
  Copy, 
  Undo,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

function App() {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [provider, setProvider] = useState('openai');
  const [selectedLLM, setSelectedLLM] = useState('');
  const [threadId, setThreadId] = useState('');
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentResult, setCurrentResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('result');
  const [toast, setToast] = useState(null);

  // Load history & configuration on mount
  useEffect(() => {
    try {
      const storedHistory = localStorage.getItem('email_classifier_history');
      if (storedHistory) {
        setHistory(JSON.parse(storedHistory));
      }
    } catch (e) {
      console.error("Failed to load history from localStorage", e);
    }
    
    const storedApiUrl = localStorage.getItem('email_classifier_api_url');
    if (storedApiUrl) {
      setApiUrl(storedApiUrl);
    }
    
    // Generate initial thread ID
    setThreadId('thread_' + Math.random().toString(36).substring(2, 11));
  }, []);

  // Save history helper
  const saveHistory = (newHistory) => {
    setHistory(newHistory);
    localStorage.setItem('email_classifier_history', JSON.stringify(newHistory));
  };

  // Toast handler
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        setToast(null);
      }, 3500);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // Model placeholders based on provider selection
  const getModelPlaceholder = (p) => {
    switch(p) {
      case 'openai': return 'gpt-4.1-mini (default)';
      case 'groq': return 'llama-3.3-70b-versatile (default)';
      case 'ollama': return 'gemma3:1b (default)';
      case 'gemini': return 'gemini-2.5-flash (default)';
      case 'anthropic': return 'claude-haiku-4-5-20251001 (default)';
      case 'azure': return 'gpt-4o-mini (default)';
      default: return 'Default model';
    }
  };

  const handleRegenThreadId = () => {
    setThreadId('thread_' + Math.random().toString(36).substring(2, 11));
    showToast('New thread ID generated', 'info');
  };

  const handleSaveApiUrl = (e) => {
    const value = e.target.value;
    setApiUrl(value);
    localStorage.setItem('email_classifier_api_url', value);
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all classification history?')) {
      saveHistory([]);
      showToast('History cleared', 'info');
    }
  };

  const handleRestore = (item) => {
    setSubject(item.subject || '');
    setBody(item.body || '');
    setProvider(item.provider || 'openai');
    setSelectedLLM(item.selectedLLM || '');
    setThreadId(item.threadId || '');
    showToast('Parameters restored to form', 'success');
  };

  const handleCopyJson = (result) => {
    const cleanResult = {
      category: result.category,
      reason: result.reason,
      JudgeVerted: result.JudgeVerted,
      JudgeReasoning: result.JudgeReasoning,
      subject: result.subject,
      body: result.body,
      provider: result.provider,
      selectedLLM: result.selectedLLM,
      threadId: result.threadId,
      timestamp: result.timestamp
    };
    navigator.clipboard.writeText(JSON.stringify(cleanResult, null, 2));
    showToast('Response JSON copied!', 'success');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subject.trim() || !body.trim()) {
      showToast('Subject and Body are required', 'error');
      return;
    }

    setIsLoading(true);
    setCurrentResult(null);
    setActiveTab('result');

    try {
      const response = await fetch(`${apiUrl.replace(/\/+$/, '')}/api/classify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subject: subject.trim(),
          body: body.trim(),
          provider: provider,
          selected_llm: selectedLLM.trim() || null,
          thread_id: threadId.trim() || 'default-api-thread'
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      
      const newResult = {
        ...data,
        provider,
        selectedLLM: selectedLLM.trim() || null,
        threadId: threadId.trim(),
        timestamp: new Date().toISOString()
      };

      setCurrentResult(newResult);
      saveHistory([newResult, ...history]);
      showToast('Email classified successfully!', 'success');
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Connection failed. Ensure the FastAPI backend is running.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const getCategoryColorClass = (cat) => {
    if (!cat) return 'category-general';
    const lower = cat.toLowerCase();
    if (lower.includes('inquiry')) return 'category-inquiry';
    if (lower.includes('support')) return 'category-support';
    if (lower.includes('feedback')) return 'category-feedback';
    if (lower.includes('spam')) return 'category-spam';
    if (lower.includes('urgent') || lower.includes('verify_code')) return 'category-urgent';
    if (lower.includes('promotion') || lower.includes('updates') || lower.includes('social') || lower.includes('forum')) return 'category-support';
    return 'category-general';
  };

  const getHistoryBadgeClass = (cat) => {
    if (!cat) return 'history-badge-general';
    const lower = cat.toLowerCase();
    if (lower.includes('inquiry')) return 'history-badge-inquiry';
    if (lower.includes('support')) return 'history-badge-support';
    if (lower.includes('feedback')) return 'history-badge-feedback';
    if (lower.includes('spam')) return 'history-badge-spam';
    if (lower.includes('urgent') || lower.includes('verify_code')) return 'history-badge-urgent';
    if (lower.includes('promotion') || lower.includes('updates') || lower.includes('social') || lower.includes('forum')) return 'history-badge-support';
    return 'history-badge-general';
  };

  const formatTimestamp = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch (e) {
      return isoString;
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header>
        <div className="brand-section">
          <Mail className="brand-icon" size={32} />
          <div>
            <h1>Email Classifier AI</h1>
            <span className="brand-subtitle">Stateful LangGraph Classification Dashboard</span>
          </div>
        </div>
        <button 
          className="settings-btn"
          onClick={() => setShowSettings(!showSettings)}
          aria-label="Toggle settings"
        >
          <Settings size={18} />
          <span>Endpoint Config</span>
        </button>
      </header>

      {/* Main Grid */}
      <main className="main-grid">
        {/* Left Column - Input Form */}
        <section className="card">
          <h2 className="card-title">
            <Sparkles size={20} />
            <span>Classification Control Panel</span>
          </h2>

          {/* Endpoint configuration panel */}
          {showSettings && (
            <div className="settings-box">
              <label htmlFor="apiUrlInput">Backend Base URL</label>
              <input
                id="apiUrlInput"
                type="text"
                value={apiUrl}
                onChange={handleSaveApiUrl}
                placeholder="http://localhost:8000"
              />
              <span className="input-desc">Modify this if your FastAPI server is running on a custom port or domain.</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="subjectInput">Email Subject</label>
              <input
                id="subjectInput"
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. Action Required: Please verify your login attempt"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="bodyInput">Email Body</label>
              <textarea
                id="bodyInput"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="e.g. Your verification code is 849201. This code expires in 10 minutes. If you did not make this request, please ignore."
                required
              />
            </div>

            <div className="form-group-row">
              <div className="form-group">
                <label htmlFor="providerSelect">LLM Provider</label>
                <select
                  id="providerSelect"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                >
                  <option value="openai">OpenAI</option>
                  <option value="groq">Groq</option>
                  <option value="ollama">Ollama</option>
                  <option value="gemini">Gemini</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="azure">Azure OpenAI</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="llmInput">Model Name (Optional)</label>
                <input
                  id="llmInput"
                  type="text"
                  value={selectedLLM}
                  onChange={(e) => setSelectedLLM(e.target.value)}
                  placeholder={getModelPlaceholder(provider)}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="threadIdInput">LangGraph Thread ID</label>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <input
                  id="threadIdInput"
                  type="text"
                  value={threadId}
                  onChange={(e) => setThreadId(e.target.value)}
                  placeholder="e.g. thread_1a2b3c"
                />
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleRegenThreadId}
                  title="Generate dynamic Thread ID"
                >
                  <RefreshCw size={14} />
                  <span>Regen</span>
                </button>
              </div>
              <span className="input-desc">Maintains graph state history and checkpointer checkpointing on the server.</span>
            </div>

            <button 
              type="submit" 
              className="btn-primary" 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <RefreshCw className="spinner" size={18} />
                  <span>Running Classification Graph...</span>
                </>
              ) : (
                <>
                  <Send size={18} />
                  <span>Classify Email</span>
                </>
              )}
            </button>
          </form>
        </section>

        {/* Right Column - Results and Logs */}
        <section className="card output-pane">
          <nav className="tab-nav" aria-label="Output navigation">
            <button
              className={`tab-btn ${activeTab === 'result' ? 'active' : ''}`}
              onClick={() => setActiveTab('result')}
            >
              <Sparkles size={16} />
              <span>Current Result</span>
            </button>
            <button
              className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <HistoryIcon size={16} />
              <span>History Logs ({history.length})</span>
            </button>
          </nav>

          {/* Active Tab Panel */}
          {activeTab === 'result' ? (
            <div role="tabpanel" aria-label="Current Result Details">
              {isLoading ? (
                <div className="empty-state">
                  <RefreshCw className="spinner pulse-glow" size={48} />
                  <h3>Analyzing Email Content</h3>
                  <p>FastAPI workflow is building LLM-structured node context and persisting thread checkpoint details...</p>
                </div>
              ) : currentResult ? (
                <div className="result-display">
                  <div className="result-header">
                    <div>
                      <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Email Subject</h3>
                      <p style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.25rem' }}>{currentResult.subject}</p>
                    </div>
                  </div>

                  <div className="result-header" style={{ borderTop: '1px solid rgba(255,255,255,0.04)', paddingTop: '1.25rem' }}>
                    <div>
                      <h4 style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>Classified Category</h4>
                      <span className={`category-pill ${getCategoryColorClass(currentResult.category)}`}>
                        {currentResult.category}
                      </span>
                    </div>
                  </div>

                  <div className="reason-card">
                    <h4 className="reason-title">Classification Rationale</h4>
                    <p className="reason-text">{currentResult.reason}</p>
                  </div>

                  {currentResult.JudgeVerted && (
                    <div className={`judge-card ${currentResult.JudgeVerted === 'accept' ? 'judge-accepted' : 'judge-rejected'}`}>
                      <div className="judge-header">
                        {currentResult.JudgeVerted === 'accept' ? (
                          <CheckCircle2 className="judge-icon text-success" size={18} />
                        ) : (
                          <AlertCircle className="judge-icon text-danger" size={18} />
                        )}
                        <h4 className="judge-title">
                          LLM Judge: {currentResult.JudgeVerted === 'accept' ? 'APPROVED' : 'REJECTED'}
                        </h4>
                      </div>
                      <p className="judge-text">{currentResult.JudgeReasoning}</p>
                    </div>
                  )}

                  <div className="metadata-grid">
                    <div className="meta-item">
                      <span className="meta-label">LLM Provider</span>
                      <span className="meta-value" style={{ textTransform: 'capitalize' }}>{currentResult.provider}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Selected Model</span>
                      <span className="meta-value">{currentResult.selectedLLM || 'Provider Default'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Thread ID</span>
                      <span className="meta-value">{currentResult.threadId}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Timestamp</span>
                      <span className="meta-value">{formatTimestamp(currentResult.timestamp)}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                    <button
                      className="btn-secondary"
                      onClick={() => handleRestore(currentResult)}
                    >
                      <Undo size={14} />
                      <span>Copy Parameters back to Form</span>
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={() => handleCopyJson(currentResult)}
                    >
                      <Copy size={14} />
                      <span>Copy Raw JSON</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <Mail size={48} />
                  <h3>No Email Classified Yet</h3>
                  <p>Enter the email subject and body details in the control panel and trigger classification to view analysis details.</p>
                </div>
              )}
            </div>
          ) : (
            <div role="tabpanel" aria-label="History Logs">
              {history.length === 0 ? (
                <div className="empty-state">
                  <HistoryIcon size={48} />
                  <h3>No Persistent Logs</h3>
                  <p>Classification metrics and request details will persist here automatically using browser localStorage.</p>
                </div>
              ) : (
                <div>
                  <div className="history-controls">
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      Total persistent entries: <strong>{history.length}</strong>
                    </span>
                    <button className="btn-secondary" onClick={handleClearHistory} style={{ color: 'var(--color-spam)' }}>
                      <Trash2 size={12} />
                      <span>Clear Logs</span>
                    </button>
                  </div>

                  <div className="history-list">
                    {history.map((item, idx) => (
                      <div 
                        key={idx}
                        className={`history-item ${currentResult && currentResult.timestamp === item.timestamp ? 'active' : ''}`}
                        onClick={() => {
                          setCurrentResult(item);
                          setActiveTab('result');
                          showToast('Loaded classification from history', 'info');
                        }}
                      >
                        <div className="history-item-top">
                          <span className="history-subject">{item.subject}</span>
                          <span className={`history-badge ${getHistoryBadgeClass(item.category)}`}>
                            {item.category}
                          </span>
                        </div>
                        
                        <div className="history-meta-row">
                          <div className="history-meta-left">
                            <span style={{ textTransform: 'capitalize' }}>{item.provider}</span>
                            <span>•</span>
                            <span style={{ opacity: 0.8 }}>{item.selectedLLM || 'Default Model'}</span>
                          </div>
                          <span>{formatTimestamp(item.timestamp)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      {/* Toast Alert */}
      {toast && (
        <div className={`toast ${toast.type === 'error' ? 'error' : ''}`}>
          {toast.type === 'error' ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
}

export default App;
