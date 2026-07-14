const TABS = [
  { id: 'recs', label: '💡 Words' },
  { id: 'paa', label: '❓ PAA' },
  { id: 'ent', label: '🏷️ Ent.' },
  { id: 'grade', label: '📖 Grade' },
  { id: 'brief', label: '✨ Brief' },
  { id: 'rank', label: '🏆 Rank' },
]

export default function TabBar({ activeTab, onChange, counts }) {
  return (
    <div className="tab-bar">
      {TABS.map((tab) => {
        const count = counts[tab.id] || 0
        const active = activeTab === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`tab-btn ${active ? 'active' : ''}`}
          >
            {tab.label}
            {count > 0 && <span className="tab-badge">{count}</span>}
          </button>
        )
      })}
    </div>
  )
}
