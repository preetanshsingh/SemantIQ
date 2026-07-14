export default function Header({ keyword, onKeywordChange, onAnalyze, analyzing, isLive }) {
  return (
    <div className="header-bar">
      <div className="logo">SemantIQ</div>
      <div className="divider" />
      <input
        value={keyword}
        onChange={(e) => onKeywordChange(e.target.value)}
        aria-label="Target keyword"
        placeholder="Target keyword..."
        className="keyword-input"
      />
      <select aria-label="Target country" className="country-select">
        <option>🇺🇸 US</option>
        <option>🇬🇧 UK</option>
        <option>🇮🇳 IN</option>
      </select>
      <button onClick={onAnalyze} disabled={analyzing} className="analyze-btn">
        {analyzing ? '⟳ Analyzing…' : '⚡ Analyze'}
      </button>
      {isLive && (
        <span className="live-badge">
          <span className="live-dot" />
          Live
        </span>
      )}
    </div>
  )
}
