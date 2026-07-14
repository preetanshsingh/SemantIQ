export default function Editor({ content, onChange, accepted }) {
  const wordCount = content.split(/\s+/).filter(Boolean).length

  return (
    <div className="editor-col">
      <div className="editor-meta">
        <span>Content Editor</span>
        <span className="meta-dot">·</span>
        <span>{wordCount} words</span>
        <span className="meta-dot">·</span>
        <span className="meta-good">Grade 8.4</span>
        <span className="meta-dot">·</span>
        <span>~{Math.max(1, Math.ceil(wordCount / 200))} min read</span>
      </div>

      <textarea
        value={content}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Content editor"
        placeholder="Paste or write your content here..."
        className="editor-textarea"
      />

      {accepted.length > 0 && (
        <div className="accepted-bar">
          <span className="accepted-label">ADDED</span>
          {accepted.map((w) => (
            <span key={w} className="accepted-chip">{w}</span>
          ))}
        </div>
      )}
    </div>
  )
}
