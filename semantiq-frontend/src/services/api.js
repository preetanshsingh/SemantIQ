const BASE = import.meta.env.VITE_API_BASE_URL || '/api'

async function handleResponse(res) {
  if (!res.ok) {
    let message = `Server error (${res.status})`
    try {
      const data = await res.json()
      message = data.detail || message
    } catch (_) {}
    throw new Error(message)
  }
  return res.json()
}

export async function analyzeKeyword(keyword, country = 'US') {
  const res = await fetch(`${BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keyword, country }),
  })
  return handleResponse(res)
}

export async function getScore(content, keyword) {
  const res = await fetch(`${BASE}/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, keyword }),
  })
  return handleResponse(res)
}

export async function getRecommendations(keyword, content = '') {
  const params = new URLSearchParams({ keyword })
  if (content) params.append('content', content.slice(0, 1000))
  const res = await fetch(`${BASE}/recommendations?${params}`)
  return handleResponse(res)
}

export async function getPAA(keyword) {
  const params = new URLSearchParams({ keyword })
  const res = await fetch(`${BASE}/paa?${params}`)
  return handleResponse(res)
}

export async function getEntities(content) {
  const res = await fetch(`${BASE}/entities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return handleResponse(res)
}

export async function getReadability(content) {
  const res = await fetch(`${BASE}/readability`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return handleResponse(res)
}

export async function getBrief(keyword) {
  const params = new URLSearchParams({ keyword })
  const res = await fetch(`${BASE}/brief?${params}`)
  return handleResponse(res)
}
export async function analyzeURL(url, country = 'US') {
  const res = await fetch(`${BASE}/url-analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, country }),
  })
  return handleResponse(res)
}