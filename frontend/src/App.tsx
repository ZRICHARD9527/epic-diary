import React, { useState, useEffect, useMemo, useCallback, memo } from 'react';
import axios from 'axios';
import { Settings, Search, Wand2, Save, Trash2, Calendar, MapPin, Edit3, X, ChevronRight, AlertCircle, Loader2 } from 'lucide-react';
import './App.css';

const API_BASE = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000/api";

interface DiaryEntry {
  ts: string; weather: string; real: string; drama: string; emoji: string;
}

// --- 1. App Context for Global Preferences ---

const AppContext = React.createContext<any>(null);

const AppProvider = ({ children }: { children: React.ReactNode }) => {
  const [city, setCity] = useState("南京");
  const [showSidebar, setShowSidebar] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const value = useMemo(() => ({
    city, setCity, showSidebar, setShowSidebar, showSettings, setShowSettings, toast, showToast
  }), [city, showSidebar, showSettings, toast, showToast]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// --- 2. Custom Hooks for Elegance ---

const useWeaving = (apiBase: string) => {
  const [isWeaving, setIsWeaving] = useState(false);
  const [lastTaskId, setLastTaskId] = useState<string | null>(null);

  const startWeaving = async (a: string, city: string, onComplete: (date: string, ts: string) => void) => {
    if (!a.trim() || isWeaving) return;
    setIsWeaving(true);
    try {
      const res = await axios.post(`${apiBase}/save/magic`, { text: a, city });
      const { task_id, ts, date } = res.data;
      setLastTaskId(task_id);
      
      const poll = setInterval(async () => {
        try {
          const statusRes = await axios.get(`${apiBase}/tasks/${task_id}`);
          if (statusRes.data.status === "done") {
            clearInterval(poll);
            setIsWeaving(false);
            onComplete(date, ts);
          } else if (statusRes.data.status.startsWith("failed")) {
            clearInterval(poll);
            setIsWeaving(false);
          }
        } catch (e) {
          clearInterval(poll);
          setIsWeaving(false);
        }
      }, 2000);
    } catch (e) {
      setIsWeaving(false);
    }
  };

  return { isWeaving, startWeaving };
};

// --- 2. Error Boundary Implementation ---
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() { return { hasError: true }; }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback poetic-reveal">
          <div className="error-icon-wrapper">
            <Wand2 size={64} className="error-icon" />
          </div>
          <h2 className="poetic-title">记忆的丝线偶尔会缠绕</h2>
          <p className="poetic-text">
            时空的档案库正在静默。让我们稍微停留，<br />
            拂去岁月的尘埃，再次唤醒沉睡的历史。
          </p>
          <button className="btn-reconnect" onClick={() => window.location.reload()}>
            重新唤醒记忆
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// --- 3. Memoized Sub-components ---

const Sidebar = memo(({ 
  dates, selectedDate, setSelectedDate, entries, selectedTs, setSelectedTs, search, setSearch
}: any) => {
  const { showSettings, setShowSettings, city, setCity } = React.useContext(AppContext);

  // Memoize filtered entries to prevent recalculation on every render
  const filteredEntries = useMemo(() => 
    entries.filter((e: any) => e.real.toLowerCase().includes(search.toLowerCase())),
    [entries, search]
  );

  return (
    <div className="sidebar-body">
      <div className="sidebar-header-wrapper">
        <div className="logo-area">
          <h1 className="logo"><span>📜</span> 史诗档案库</h1>
          <Settings className="settings-icon" size={18} onClick={() => setShowSettings(!showSettings)} />
        </div>
        
        {showSettings && (
          <div className="settings-dropdown fade-in">
            <label>偏好城市</label>
            <input value={city} onChange={e => setCity(e.target.value)} />
            <button className="settings-close" onClick={() => setShowSettings(false)}>确定</button>
          </div>
        )}
      </div>

      <div className="widget-section">
        <div className="st-widget">
          <label>搜索</label>
          <div className="st-input-wrapper">
            <Search size={14} />
            <input placeholder="过滤片段..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
        </div>
        <div className="st-widget">
          <label>日期</label>
          <select className="st-select" value={selectedDate} onChange={e => setSelectedDate(e.target.value)}>
            {dates.map((d: string) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
      </div>

      <nav className="record-scroller">
        {filteredEntries.map((e: any, idx: number) => (
          <button 
            key={e.ts} 
            className={`record-card ${selectedTs === e.ts ? 'active' : ''} fade-in-staggered`}
            style={{ animationDelay: `${idx * 0.05}s` }}
            onClick={() => setSelectedTs(e.ts)}
          >
            <div className="record-top">
              <span>{e.ts}</span>
              <span>{e.emoji}</span>
            </div>
            <div className="record-preview">
              {e.real.length > 25 ? e.real.substring(0, 25) + "..." : e.real}
            </div>
          </button>
        ))}
      </nav>
    </div>
  );
});

const Editor = memo(({ input, setInput, isWeaving, handleMagicSave, handlePureSave, handleKeyDown, isFlashing }: any) => {
  const { city } = React.useContext(AppContext);
  return (
    <section className={`editor-card layout-fixed ${isFlashing ? 'shortcut-flash' : ''} ${isWeaving ? 'weaving-editor' : ''}`}>
      <textarea 
        placeholder="记录此时此刻，将瞬间凝结成史诗..." 
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <div className="editor-footer">
        <div className="location-info">📍 {city}</div>
        <div className="shortcut-hint">
          <span>Ctrl + Enter</span> 开启魔法
        </div>
        <div className="action-btns">
          <button className="btn-magic" onClick={handleMagicSave} disabled={isWeaving}>
            {isWeaving ? <><Loader2 className="animate-spin" size={14} style={{marginRight:'8px'}}/> 编织中...</> : "🪄 魔法转换"}
          </button>
          <button className="btn-pure" onClick={handlePureSave}>
            💾 纯净保存
          </button>
        </div>
      </div>
    </section>
  );
});

const DetailView = memo(({ currentEntry, selectedDate, handleDelete, isWeaving }: any) => {
  const [related, setRelated] = useState<any[]>([]);

  useEffect(() => {
    if (currentEntry && selectedDate) {
      axios.get(`${API_BASE}/entries/${selectedDate}/${currentEntry.ts.replace(/:/g, '-')}/related`)
        .then(res => setRelated(res.data))
        .catch(() => setRelated([]));
    }
  }, [currentEntry, selectedDate]);

  if (!currentEntry) {
    return (
      <div className="empty-placeholder fade-in">
        <div className="placeholder-icon">📜</div>
        <p>时光的尘埃尚未落下，请从左侧档案库唤醒一段沉睡的记忆</p>
      </div>
    );
  }

  return (
    <article className={`epic-card fade-in-misty ${isWeaving ? 'weaving-active' : ''}`} key={currentEntry.ts}>
      {isWeaving && <div className="weaving-glow-bar" />}
      <header className="card-header">
        <div className="card-meta">
          <span className="meta-item">📅 {selectedDate}</span>
          <span className="meta-item">⏰ {currentEntry.ts}</span>
          <span className="meta-item weather">{currentEntry.weather}</span>
        </div>
        <div className="card-emoji-large">{currentEntry.emoji}</div>
      </header>

      <div className="card-body">
        <div className="reality-segment">
          <label><Edit3 size={12} style={{marginRight:'6px'}}/> 现实回响</label>
          <p>{currentEntry.real || "[内容读取失败]"}</p>
        </div>

        <div className="drama-segment">
          <div className="drama-content">
            {currentEntry.drama ? `"${currentEntry.drama}"` : "✨ 史诗编织中..."}
          </div>
        </div>

        <div className="thematic-clues">
          {(currentEntry as any).tags ? (currentEntry as any).tags.split(',').map((tag: string) => (
            <span key={tag} className="clue-tag"># {tag.trim()}</span>
          )) : (
            <>
              <span className="clue-tag"># 碎片</span>
              <span className="clue-tag"># 时光</span>
              <span className="clue-tag"># 宿命</span>
            </>
          )}
        </div>

        {/* Visionary Feature: Fate Lines (Linked Memories) */}
        <div className="fate-lines">
          <label><Calendar size={12} style={{marginRight:'6px'}}/> 宿命交织</label>
          <div className="linked-memories">
            {related.length > 0 ? related.map((r, i) => (
              <div key={i} className="linked-item">
                <span className="link-date">{r.date}</span>
                <span className="link-preview">{r.preview}</span>
              </div>
            )) : (
              <div className="linked-item-placeholder">
                <span className="link-preview">✨ 此段记忆在时空中孤独漂浮</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <footer className="card-footer">
        <button className="btn-delete" onClick={handleDelete}>
          <Trash2 size={14} /> 抹除此段记忆
        </button>
      </footer>
    </article>
  );
});

// --- 4. Main App Content ---

const AppContent = () => {
  const { city, showSidebar, setShowSidebar, showToast } = React.useContext(AppContext);
  const [dates, setDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedTs, setSelectedTs] = useState<string | null>(null);
  const [entries, setEntries] = useState<DiaryEntry[]>([]);
  const [input, setInput] = useState("");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);

  const { isWeaving, startWeaving } = useWeaving(API_BASE);

  const fetchDates = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/dates`);
      setDates(res.data);
      return res.data.data || res.data;
    } catch(e) { console.error("Fetch dates failed", e); return []; }
  }, []);

  // 初始化获取日期
  useEffect(() => {
    fetchDates().then(d => {
      if (d.length > 0 && !selectedDate) setSelectedDate(d[0]);
    });
  }, [fetchDates]);

  const refreshEntries = useCallback(async (date: string, ts?: string) => {
    setIsLoading(true);
    try {
      const updated = await axios.get(`${API_BASE}/entries/${date}`);
      setEntries(updated.data.data || updated.data);
      if (ts) setSelectedTs(ts);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 切换日期获取条目
  useEffect(() => {
    if (selectedDate) refreshEntries(selectedDate);
  }, [selectedDate, refreshEntries]);

  const handleMagicSave = useCallback(() => {
    if (!input.trim()) {
      showToast("请输入一些内容", "error");
      return;
    }
    startWeaving(input, city, async (date, ts) => {
      setInput("");
      // Optimization: Only fetch dates if current date differs
      if (date !== selectedDate) {
        await fetchDates();
        setSelectedDate(date);
      }
      refreshEntries(date, ts);
      showToast("史诗已编织入册", "success");
    });
  }, [input, city, startWeaving, refreshEntries, fetchDates, showToast, selectedDate]);

  const handlePureSave = useCallback(async () => {
    if (!input.trim()) return;
    try {
      const res = await axios.post(`${API_BASE}/save/pure`, { text: input, city });
      setInput("");
      const today = new Date().toISOString().split('T')[0];
      // Optimization: Only fetch dates if today differs from selected
      if (today !== selectedDate) {
        await fetchDates();
        setSelectedDate(today);
      }
      refreshEntries(today, res.data.ts);
      showToast("记忆已尘封", "success");
    } catch(e) { showToast("保存失败", "error"); }
  }, [input, city, refreshEntries, fetchDates, showToast, selectedDate]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      setIsFlashing(true);
      setTimeout(() => setIsFlashing(false), 300);
      handleMagicSave();
    }
  }, [handleMagicSave]);

  const handleDelete = useCallback(async () => {
    if (!selectedDate || !selectedTs) return;
    if (window.confirm("确定要抹除这段记忆吗？")) {
      try {
        await axios.delete(`${API_BASE}/entries/${selectedDate}/${selectedTs.replace(/:/g, '-')}`);
        setSelectedTs(null);
        refreshEntries(selectedDate);
      } catch (e) { console.error("Delete failed", e); }
    }
  }, [selectedDate, selectedTs, refreshEntries]);

  const currentEntry = useMemo(() => entries.find(e => e.ts === selectedTs), [entries, selectedTs]);

  return (
    <div className="epic-app">
      <aside className={`sidebar ${!showSidebar ? 'sidebar-hidden' : ''}`}>
        <Sidebar 
          dates={dates} selectedDate={selectedDate} setSelectedDate={setSelectedDate}
          entries={entries} selectedTs={selectedTs} setSelectedTs={setSelectedTs}
          search={search} setSearch={setSearch}
        />
      </aside>

      <main className="main-content">
        <header className="page-header layout-fixed">
          <div className="header-top">
            <button className="sidebar-toggle" onClick={() => setShowSidebar(!showSidebar)}>
              {showSidebar ? <ChevronRight size={20} style={{transform:'rotate(180deg)'}} /> : <ChevronRight size={20} />}
            </button>
            <h1 className="title">📖 EpicDiary</h1>
          </div>
          <div className={`page-subtitle ${input ? 'zen-out' : ''}`}>
            {isWeaving ? "✨ 正在编织您的史诗..." : "✨ 记录此刻，成就史诗"}
          </div>
        </header>

        <Editor 
          input={input} setInput={setInput} isWeaving={isWeaving}
          handleMagicSave={handleMagicSave} handlePureSave={handlePureSave}
          handleKeyDown={handleKeyDown} isFlashing={isFlashing}
        />

        <div className="detail-wrapper layout-fixed">
          {isLoading ? (
            <div className="skeleton-card fade-in">
              <div className="skeleton-header" />
              <div className="skeleton-body" />
            </div>
          ) : (
            <DetailView 
              currentEntry={currentEntry} selectedDate={selectedDate}
              handleDelete={handleDelete} isWeaving={isWeaving}
            />
          )}
        </div>
      </main>
    </div>
  );
};

const Toast = () => {
  const { toast } = React.useContext(AppContext);
  if (!toast) return null;

  const Icon = toast.type === 'success' ? Wand2 : toast.type === 'error' ? AlertCircle : Loader2;

  return (
    <div className={`toast-notification ${toast.type}`}>
      <Icon size={18} />
      {toast.message}
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <AppContent />
        <Toast />
      </AppProvider>
    </ErrorBoundary>
  );
}

export default App;
