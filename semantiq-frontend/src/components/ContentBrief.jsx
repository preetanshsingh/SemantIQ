export default function ContentBrief({ brief }) {
  return (
    <>
      <p className="tab-intro">RAG-generated from SERP top 3. Use this <em>before</em> you write, not after.</p>

      <div className="brief-section-label">SUGGESTED H1</div>
      <div className="brief-h1">{brief.h1}</div>

      <div className="brief-section-label">H2 STRUCTURE</div>
      <div className="brief-h2-list">
        {brief.h2s.map((h, i) => (
          <div key={i} className="brief-h2-row">
            <span className="brief-h2-num">{i + 1}</span>
            <span>{h}</span>
          </div>
        ))}
      </div>
    </>
  )
}
