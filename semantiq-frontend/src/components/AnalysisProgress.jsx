export default function AnalysisProgress({ steps, stepIndex }) {
  const step = steps[stepIndex]
  if (!step) return null

  return (
    <div className="analysis-progress">
      <span className="progress-icon">{step.icon}</span>
      <span>{step.label}</span>
      <div className="progress-dots">
        {[0, 1, 2].map((d) => (
          <span key={d} className="progress-dot" style={{ animationDelay: `${d * 0.2}s` }} />
        ))}
      </div>
    </div>
  )
}
