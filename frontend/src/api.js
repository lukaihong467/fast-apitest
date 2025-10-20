const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/').replace(/\/$/, '/')

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const message = data?.detail || response.statusText
    throw new Error(message)
  }

  if (data && typeof data === 'object' && 'results' in data && Array.isArray(data.results)) {
    return data.results
  }

  return data
}

export { API_BASE, request }
