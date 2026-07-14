import { useEffect, useRef, useState } from 'react'
import Header from './components/Header.jsx'
import AnalysisProgress from './components/AnalysisProgress.jsx'
import Editor from './components/Editor.jsx'
import ScoreRing from './components/ScoreRing.jsx'
import TabBar from './components/TabBar.jsx'
import WordRecommendations from './components/WordRecommendations.jsx'
import PAAPanel from './components/PAAPanel.jsx'
import EntityPanel from './components/EntityPanel.jsx'
import ReadabilityPanel from './components/ReadabilityPanel.jsx'
import ContentBrief from './components/ContentBrief.jsx'
import CompetitorRank from './components/CompetitorRank.jsx'
import Toast from './components/Toast.jsx'

import {
  analyzeKeyword,
  analyzeURL,
  getScore,
  getRecommendations,
  getPAA,
  getEntities,
  getReadability,
  getBrief,
} from './services/api.js'

import {
  MOCK_RECOMMENDATIONS,
  MOCK_PAA,
  MOCK_ENTITIES,
  MOCK_READABILITY,
  MOCK_BRIEF,
  MOCK_SCORE_BREAKDOWN,
  DEMO_CONTENT,
  ANALYSIS_STEPS,
} from './data/mockData.js'

import './styles/app.css'

export default function App() {
  // mode: 'keyword' | 'url'
  const [mode, setMode]             = useState('keyword')
  const [keyword, setKeyword]       = useState('diabetes management guide')
  const [urlInput, setUrlInput]     = useState('')
  const [content, setContent]       = useState(DEMO_CONTENT)
  const [activeTab, setActiveTab]   = useState('recs')
  const [score, setScore]           = useState(72)
  const [breakdown, setBreakdown]   = useState(MOCK_SCORE_BREAKDOWN)
  const [recs, setRecs]             = useState(MOCK_RECOMMENDATIONS)
  const [paaItems, setPaaItems]     = useState(MOCK_PAA)
  const [entities, setEntities]     = useState(MOCK_ENTITIES)
  const [readability, setReadability] = useState(MOCK_READABILITY)
  const [brief, setBrief]           = useState(MOCK_BRIEF)
  const [urlData, setUrlData]       = useState(null)
  const [analyzing, setAnalyzing]   = useState(false)
  const [analyzed, setAnalyzed]     = useState(false)
  const [stepIndex, setStepIndex]   = useState(0)
  const [accepted, setAccepted]     = useState([])
  const [dismissed, setDismissed]   = useState([])
  const [toast, setToast]           = useState(null)
  const [error, setError]           = useState(null)
  const debounceRef = useRef(null)

  const showToast = (msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 2500)
  }

  // Live scoring (keyword mode only)
  useEffect(() => {
    if (!analyzed || !content.trim() || mode === 'url') return
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      try {
        const result = await getScore(content, keyword)
        setScore(result.overall_score)
        setBreakdown(result.breakdown)
      } catch (e) {
        console.warn('Score update failed:', e.message)
      }
    }, 600)
    return () => clearTimeout(debounceRef.current)
  }, [content, keyword, analyzed, mode])

  // Keyword mode analyze
  const handleKeywordAnalyze = async () => {
    if (analyzing) return
    setAnalyzing(true)
    setAnalyzed(false)
    setError(null)
    setStepIndex(0)

    let s = 0
    const stepInterval = setInterval(() => {
      s += 1
      setStepIndex(Math.min(s, ANALYSIS_STEPS.length - 2))
    }, 420)

    try {
      await analyzeKeyword(keyword)
      const [recsData, paaData, entData, readData, briefData, scoreData] = await Promise.all([
        getRecommendations(keyword, content),
        getPAA(keyword),
        getEntities(content),
        getReadability(content),
        getBrief(keyword),
        getScore(content, keyword),
      ])
      setRecs(recsData.filter(r => !accepted.includes(r.word) && !dismissed.includes(r.word)))
      setPaaItems(paaData)
      setEntities(entData)
      setReadability(readData)
      setBrief(briefData)
      setScore(scoreData.overall_score)
      setBreakdown(scoreData.breakdown)
      clearInterval(stepInterval)
      setStepIndex(ANALYSIS_STEPS.length - 1)
      setTimeout(() => { setAnalyzing(false); setAnalyzed(true) }, 400)
    } catch (err) {
      clearInterval(stepInterval)
      setAnalyzing(false)
      setError(err.message)
      showToast('Analysis failed — check your API key')
    }
  }

  // URL mode analyze
  const handleURLAnalyze = async () => {
    if (analyzing || !urlInput.trim()) return
    if (!urlInput.startsWith('http')) {
      setError('Please enter a valid URL starting with http:// or https://')
      return
    }
    setAnalyzing(true)
    setAnalyzed(false)
    setError(null)
    setUrlData(null)
    setStepIndex(0)

    let s = 0
    const stepInterval = setInterval(() => {
      s += 1
      setStepIndex(Math.min(s, ANALYSIS_STEPS.length - 2))
    }, 500)

    try {
      const data = await analyzeURL(urlInput)
      setUrlData(data)
      // Also populate keyword-mode panels with the data from this URL
      setKeyword(data.inferred_keyword)
      setScore(data.your_score)
      setBreakdown(data.breakdown)
      setRecs(data.top_missing_words)
      setActiveTab('rank') // jump straight to the rank tab
      clearInterval(stepInterval)
      setStepIndex(ANALYSIS_STEPS.length - 1)
      setTimeout(() => { setAnalyzing(false); setAnalyzed(true) }, 400)
    } catch (err) {
      clearInterval(stepInterval)
      setAnalyzing(false)
      setError(err.message)
      showToast('URL analysis failed')
    }
  }

  const handleAnalyze = () => {
    if (mode === 'url') handleURLAnalyze()
    else handleKeywordAnalyze()
  }

  const handleAddWord = (word, points) => {
    setAccepted(prev => [...prev, word])
    setRecs(prev => prev.filter(r => r.word !== word))
    showToast(`+${points} pts`)
  }

  const handleDismissWord = (word) => {
    setDismissed(prev => [...prev, word])
    setRecs(prev => prev.filter(r => r.word !== word))
  }

  const unansweredPAA = paaItems.filter(p => !p.answered).length
  const tabCounts = { recs: recs.length, paa: unansweredPAA }

  return (
    <div className="app-shell">
      <Toast message={toast} />

      {/* ── Mode switcher + Header ── */}
      <div className="header-bar">
        <div className="logo">SemantIQ</div>
        <div className="divider" />

        {/* Mode toggle */}
        <div style={{ display: 'flex', gap: 2, background: 'var(--surface-2)', borderRadius: 7, padding: 2, flexShrink: 0 }}>
          {[{ id: 'keyword', label: '🔑 Keyword' }, { id: 'url', label: '🔗 URL' }].map(m => (
            <button
              key={m.id}
              onClick={() => { setMode(m.id); setError(null) }}
              style={{
                padding: '4px 10px',
                borderRadius: 5,
                border: 'none',
                background: mode === m.id ? 'var(--surface-0)' : 'transparent',
                color: mode === m.id ? 'var(--violet)' : 'var(--text-muted)',
                fontWeight: mode === m.id ? 700 : 400,
                fontSize: 11,
                cursor: 'pointer',
                boxShadow: mode === m.id ? '0 1px 4px rgba(0,0,0,.08)' : 'none',
                transition: 'all .15s',
              }}
            >
              {m.label}
            </button>
          ))}
        </div>

        {/* Input — keyword or URL */}
        {mode === 'keyword' ? (
          <input
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            aria-label="Target keyword"
            placeholder="Target keyword..."
            className="keyword-input"
          />
        ) : (
          <input
            value={urlInput}
            onChange={e => setUrlInput(e.target.value)}
            aria-label="Page URL"
            placeholder="https://yoursite.com/your-page"
            className="keyword-input"
            style={{ maxWidth: 320 }}
          />
        )}

        <select aria-label="Target country" className="country-select">
          <option>🇺🇸 US</option>
          <option>🇬🇧 UK</option>
          <option>🇮🇳 IN</option>
        </select>

        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="analyze-btn"
        >
          {analyzing ? '⟳ Analyzing…' : mode === 'url' ? '🔗 Analyze URL' : '⚡ Analyze'}
        </button>

        {analyzed && (
          <span className="live-badge">
            <span className="live-dot" />
            Live
          </span>
        )}
      </div>

      {analyzing && <AnalysisProgress steps={ANALYSIS_STEPS} stepIndex={stepIndex} />}

      {error && !analyzing && (
        <div style={{
          padding: '8px 16px',
          background: '#fff1f2',
          borderBottom: '1px solid #fecdd3',
          fontSize: 11,
          color: '#e11d48',
          flexShrink: 0,
        }}>
          ⚠️ {error}
        </div>
      )}

      <div className="app-body">
        {/* Hide editor in URL mode — the page content comes from the URL */}
        {mode === 'keyword' ? (
          <Editor content={content} onChange={setContent} accepted={accepted} />
        ) : (
          <div className="editor-col" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
            {urlData ? (
              <div style={{ padding: 32, maxWidth: 460 }}>
                <div style={{ fontSize: 22, marginBottom: 8 }}>🔗</div>
                <div style={{ fontWeight: 700, marginBottom: 4, color: 'var(--text-primary)' }}>
                  {urlData.inferred_keyword}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', wordBreak: 'break-all', marginBottom: 16 }}>
                  {urlData.url}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                  Your page scored <strong style={{ color: 'var(--violet)' }}>{urlData.your_score}/100</strong> and
                  ranks <strong style={{ color: 'var(--violet)' }}>#{urlData.your_rank}</strong> among {urlData.total_competitors} competitors.
                  See the <strong>🏆 Rank</strong> tab for the full breakdown and what to fix.
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 32 }}>
                <div style={{ fontSize: 32, marginBottom: 12 }}>🔗</div>
                <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Paste a URL above and click Analyze URL</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  We'll scrape your page, detect the keyword automatically,<br />
                  then rank you against your real Google competitors.
                </div>
              </div>
            )}
          </div>
        )}

        <div className="right-panel">
          <ScoreRing score={score} breakdown={breakdown} />

          <TabBar
            activeTab={activeTab}
            onChange={setActiveTab}
            counts={{ ...tabCounts, rank: urlData ? 1 : 0 }}
          />

          <div className="tab-content">
            {activeTab === 'recs'  && <WordRecommendations recommendations={recs} onAdd={handleAddWord} onDismiss={handleDismissWord} />}
            {activeTab === 'paa'   && <PAAPanel items={paaItems} />}
            {activeTab === 'ent'   && <EntityPanel entities={entities} />}
            {activeTab === 'grade' && <ReadabilityPanel metrics={readability} />}
            {activeTab === 'brief' && <ContentBrief brief={brief} />}
            {activeTab === 'rank'  && <CompetitorRank data={urlData} />}
          </div>
        </div>
      </div>
    </div>
  )
}
