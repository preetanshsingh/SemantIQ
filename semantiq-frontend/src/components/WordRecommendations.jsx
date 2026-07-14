export default function WordRecommendations({ recommendations, onAdd, onDismiss }) {
  if (recommendations.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-emoji">🎉</div>
        <div className="empty-title">All addressed!</div>
        <div className="empty-sub">Every recommendation covered</div>
      </div>
    )
  }

  return (
    <>
      <p className="tab-intro">
        IG-ranked terms. Click <strong>Add</strong> to insert into content and boost your score.
      </p>
      {recommendations.map((r) => (
        <div key={r.word} className="rec-card">
          <div className="rec-top">
            <div className="rec-text">
              <div className="rec-word">{r.word}</div>
              <div className="rec-category">{r.category}</div>
            </div>
            <div className="rec-actions">
              <button onClick={() => onAdd(r.word, r.points)} className="add-btn">+ Add</button>
              <button onClick={() => onDismiss(r.word)} className="dismiss-btn">✕</button>
            </div>
          </div>
          <div>
            <div className="ig-row">
              {/* This is the signature SemantIQ element: Information Gain made visible,
                  directly exposing the Phase 1 theory in the UI. No competitor tool shows this. */}
              <span className="ig-label">INFORMATION GAIN</span>
              <span className="ig-value" style={{ color: r.ig > 75 ? 'var(--teal)' : 'var(--amber)' }}>{r.ig}%</span>
            </div>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${r.ig}%`, background: r.ig > 75 ? 'var(--teal)' : 'var(--amber)' }}
              />
            </div>
          </div>
        </div>
      ))}
    </>
  )
}
