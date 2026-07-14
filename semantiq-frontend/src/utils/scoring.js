export const VIOLET = 'var(--violet)'
export const TEAL = 'var(--teal)'
export const AMBER = 'var(--amber)'
export const ROSE = 'var(--rose)'

export function scoreColor(score) {
  if (score >= 70) return 'var(--teal)'
  if (score >= 50) return 'var(--amber)'
  return 'var(--rose)'
}

export function scoreTier(score) {
  if (score >= 85) return { label: 'Excellent', color: 'var(--violet)' }
  if (score >= 70) return { label: 'Good', color: 'var(--teal)' }
  if (score >= 50) return { label: 'Average', color: 'var(--amber)' }
  return { label: 'Needs work', color: 'var(--rose)' }
}

export function nextTier(score) {
  if (score >= 85) return null
  if (score >= 70) return { label: 'Excellent', color: 'var(--violet)', needed: 85 - score }
  if (score >= 50) return { label: 'Good', color: 'var(--teal)', needed: 70 - score }
  return { label: 'Average', color: 'var(--amber)', needed: 50 - score }
}
