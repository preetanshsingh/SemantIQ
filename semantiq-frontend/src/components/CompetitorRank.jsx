export default function CompetitorRank({ data }) {
    if (!data) return (
      <div className="empty-state">
        <div className="empty-emoji">🏆</div>
        <div className="empty-title">Paste a URL to see your rank</div>
        <div className="empty-sub">Switch to URL mode in the header</div>
      </div>
    )
  
    const {
      inferred_keyword,
      your_score,
      your_rank,
      total_competitors,
      competitors,
      content_gaps,
      top_missing_words,
    } = data
  
    const rankColor = your_rank === 1
      ? 'var(--teal)'
      : your_rank <= 3
      ? 'var(--violet)'
      : your_rank <= 5
      ? 'var(--amber)'
      : 'var(--rose)'
  
    // Build the full leaderboard — insert user at their estimated rank position
    const allEntries = [
      ...competitors.map(c => ({ ...c, is_you: false }))
    ]
    // Insert user entry at estimated rank
    const userEntry = {
      rank: your_rank,
      url: 'Your page',
      title: 'Your page',
      score: your_score,
      is_you: true,
    }
    allEntries.splice(your_rank - 1, 0, userEntry)
    // Re-number
    const leaderboard = allEntries.slice(0, total_competitors + 1).map((e, i) => ({
      ...e,
      displayRank: i + 1,
    }))
  
    return (
      <>
        {/* Keyword inferred */}
        <div style={{ marginBottom: 10 }}>
          <div style={{ fontSize: 8, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: .5, marginBottom: 3 }}>
            DETECTED KEYWORD
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--violet)' }}>
            {inferred_keyword}
          </div>
        </div>
  
        {/* Rank hero */}
        <div style={{
          background: `${rankColor}12`,
          border: `1px solid ${rankColor}33`,
          borderRadius: 10,
          padding: '10px 12px',
          marginBottom: 10,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}>
          <div style={{
            fontSize: 28,
            fontWeight: 900,
            color: rankColor,
            lineHeight: 1,
            minWidth: 36,
            textAlign: 'center',
          }}>
            #{your_rank}
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: rankColor }}>
              Your estimated rank
            </div>
            <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2 }}>
              Score {your_score}/100 · vs {total_competitors} competitors
            </div>
          </div>
        </div>
  
        {/* Leaderboard */}
        <div style={{ fontSize: 8, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: .5, marginBottom: 5 }}>
          LEADERBOARD
        </div>
        {leaderboard.map((entry, i) => (
          <div key={i} style={{
            display: 'flex',
            alignItems: 'center',
            gap: 7,
            padding: '6px 8px',
            marginBottom: 4,
            borderRadius: 7,
            background: entry.is_you ? `${rankColor}12` : 'var(--surface-0)',
            border: `1px solid ${entry.is_you ? rankColor + '44' : 'var(--border)'}`,
          }}>
            <div style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: entry.is_you ? rankColor : 'var(--surface-2)',
              color: entry.is_you ? '#fff' : 'var(--text-muted)',
              fontSize: 9,
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              {entry.displayRank}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: 10,
                fontWeight: entry.is_you ? 700 : 500,
                color: entry.is_you ? rankColor : 'var(--text-primary)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}>
                {entry.is_you ? '⭐ Your page' : entry.title}
              </div>
              {!entry.is_you && (
                <div style={{ fontSize: 8, color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {entry.url}
                </div>
              )}
            </div>
            {/* Score bar */}
            <div style={{ flexShrink: 0, textAlign: 'right' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: entry.is_you ? rankColor : 'var(--text-secondary)' }}>
                {entry.score}
              </div>
              <div style={{ width: 40, height: 3, borderRadius: 2, background: 'var(--border)', marginTop: 2 }}>
                <div style={{
                  height: '100%',
                  borderRadius: 2,
                  width: `${entry.score}%`,
                  background: entry.is_you ? rankColor : 'var(--border-strong)',
                  transition: 'width .5s ease',
                }} />
              </div>
            </div>
          </div>
        ))}
  
        {/* Content gaps */}
        {content_gaps && content_gaps.length > 0 && (
          <>
            <div style={{ fontSize: 8, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: .5, margin: '12px 0 5px' }}>
              TOP GAPS TO CLOSE
            </div>
            {content_gaps.map((gap, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 7,
                padding: '6px 8px',
                marginBottom: 4,
                borderRadius: 7,
                background: 'var(--surface-0)',
                border: '1px solid var(--border)',
              }}>
                <span style={{ fontSize: 11 }}>
                  {gap.type === 'word' ? '💡' : gap.type === 'paa' ? '❓' : '🏷️'}
                </span>
                <span style={{ fontSize: 10, flex: 1, color: 'var(--text-primary)', lineHeight: 1.4 }}>
                  {gap.value}
                </span>
                <span style={{
                  fontSize: 8,
                  fontWeight: 700,
                  padding: '2px 5px',
                  borderRadius: 4,
                  background: gap.impact === 'high'
                    ? 'var(--rose)' + '22'
                    : gap.impact === 'medium'
                    ? 'var(--amber)' + '22'
                    : 'var(--border)',
                  color: gap.impact === 'high'
                    ? 'var(--rose)'
                    : gap.impact === 'medium'
                    ? 'var(--amber)'
                    : 'var(--text-muted)',
                  flexShrink: 0,
                }}>
                  {gap.impact}
                </span>
              </div>
            ))}
          </>
        )}
      </>
    )
  }
  