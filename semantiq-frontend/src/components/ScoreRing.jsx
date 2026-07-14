import { useEffect, useRef, useState } from 'react'
import { scoreColor, scoreTier, nextTier } from '../utils/scoring'

const RADIUS = 40
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export default function ScoreRing({ score, breakdown }) {
  const [displayed, setDisplayed] = useState(0)
  const [glowing, setGlowing] = useState(false)
  const animRef = useRef(null)
  const prevScore = useRef(score)

  useEffect(() => {
    if (prevScore.current !== score) {
      setGlowing(true)
      const t = setTimeout(() => setGlowing(false), 900)
      prevScore.current = score
      return () => clearTimeout(t)
    }
  }, [score])

  useEffect(() => {
    let current = displayed
    clearInterval(animRef.current)
    animRef.current = setInterval(() => {
      const delta = score - current
      if (Math.abs(delta) < 1) {
        setDisplayed(score)
        clearInterval(animRef.current)
        return
      }
      current += delta * 0.16
      setDisplayed(Math.round(current))
    }, 22)
    return () => clearInterval(animRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [score])

  const tier = scoreTier(displayed)
  const nt = nextTier(displayed)
  const dashOffset = CIRCUMFERENCE - (displayed / 100) * CIRCUMFERENCE

  return (
    <div className="score-panel">
      <div className="score-ring-row">
        <div className="ring-wrap">
          <svg
            width="90"
            height="90"
            style={{
              transform: 'rotate(-90deg)',
              filter: glowing ? `drop-shadow(0 0 14px ${tier.color}) drop-shadow(0 0 5px ${tier.color})` : 'none',
              transition: 'filter .5s ease',
            }}
          >
            <circle cx="45" cy="45" r={RADIUS} fill="none" stroke="var(--border)" strokeWidth="6" />
            <circle
              cx="45"
              cy="45"
              r={RADIUS}
              fill="none"
              stroke={tier.color}
              strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={dashOffset}
              style={{ transition: 'stroke-dashoffset .6s cubic-bezier(.4,0,.2,1), stroke .4s' }}
            />
          </svg>
          <div className="ring-label">
            <div className="ring-score" style={{ color: tier.color }}>{displayed}</div>
            <div className="ring-max">/100</div>
          </div>
        </div>

        <div className="score-meta">
          <div className="tier-badge" style={{ background: `${tier.color}25`, borderColor: `${tier.color}44` }}>
            <span className="tier-dot" style={{ background: tier.color }} />
            <span style={{ color: tier.color }}>{tier.label}</span>
          </div>
          {nt && (
            <div className="next-tier-hint">
              <strong style={{ color: nt.color }}>+{nt.needed} pts</strong> to {nt.label}
            </div>
          )}
          {breakdown.slice(0, 4).map((b) => (
            <div key={b.label} className="breakdown-row">
              <div className="breakdown-labels">
                <span className="breakdown-label">{b.label}</span>
                <span className="breakdown-score" style={{ color: scoreColor(b.score) }}>{b.score}</span>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${b.score}%`, background: scoreColor(b.score) }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
