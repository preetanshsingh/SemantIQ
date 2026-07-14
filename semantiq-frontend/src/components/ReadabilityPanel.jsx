export default function ReadabilityPanel({ metrics }) {
  return (
    <>
      <p className="tab-intro">Readability via textstat + perplexity/burstiness for AI detection.</p>
      {metrics.map((r) => (
        <div key={r.label} className="readability-row">
          <span className="readability-label">{r.label}</span>
          <div style={{ textAlign: 'right' }}>
            <div className="readability-value" style={{ color: r.good ? 'var(--teal)' : 'var(--amber)' }}>{r.value}</div>
            <div className="readability-grade">{r.grade}</div>
          </div>
        </div>
      ))}
    </>
  )
}
