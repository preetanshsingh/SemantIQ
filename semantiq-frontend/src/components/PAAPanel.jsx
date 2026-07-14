export default function PAAPanel({ items }) {
  return (
    <>
      <p className="tab-intro">People Also Ask from SERP. Cover each to boost content depth score.</p>
      {items.map((p, i) => (
        <div key={i} className="paa-card" style={{ borderColor: p.answered ? 'var(--teal)' : 'var(--border)' }}>
          <div className="paa-row">
            <div className={`paa-check ${p.answered ? 'checked' : ''}`}>
              {p.answered && <span>✓</span>}
            </div>
            <div>
              <div className="paa-question" style={{ color: p.answered ? 'var(--text-secondary)' : 'var(--text-primary)' }}>
                {p.question}
              </div>
              {!p.answered && <div className="paa-missing">Not covered · +{p.points} pts</div>}
            </div>
          </div>
        </div>
      ))}
    </>
  )
}
