export default function EntityPanel({ entities }) {
  return (
    <>
      <p className="tab-intro">Detected via spaCy NER, linked to Wikidata / Google Knowledge Graph.</p>
      {entities.map((e) => (
        <div key={e.entity} className="entity-row">
          <div className="entity-dot" style={{ background: e.count > 0 ? 'var(--teal)' : 'var(--border-strong)' }} />
          <div className="entity-text">
            <span className="entity-name">{e.entity}</span>
            <span className="entity-type">{e.type}</span>
          </div>
          {e.inKG && <span className="kg-badge">KG</span>}
          <span className="entity-count" style={{ color: e.count > 0 ? 'var(--teal)' : 'var(--rose)' }}>
            {e.count > 0 ? `${e.count}×` : 'missing'}
          </span>
        </div>
      ))}
    </>
  )
}
