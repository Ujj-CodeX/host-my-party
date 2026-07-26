// src/api/client.js
//
// Single place that knows how to talk to the Django backend. Every view
// should go through apiFetch() / guestFetch() instead of calling fetch()
// directly, so auth headers, the refresh-token dance, and error shape are
// handled consistently everywhere (previously every view rolled its own
// fetch() + try/catch with a hardcoded API_BASE).

export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'
export const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000'

const ACCESS_TOKEN_KEY = 'hmp_access_token'

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function setAccessToken(token) {
  if (token) localStorage.setItem(ACCESS_TOKEN_KEY, token)
  else localStorage.removeItem(ACCESS_TOKEN_KEY)
}

export function isAuthenticated() {
  return !!getAccessToken()
}

class ApiError extends Error {
  constructor(message, status, body) {
    super(message)
    this.status = status
    this.body = body
  }
}

async function doFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  const hasBody = options.body !== undefined && !(options.body instanceof FormData)
  if (hasBody && !headers['Content-Type']) headers['Content-Type'] = 'application/json'

  const token = getAccessToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: 'include', // needed so the httpOnly refresh_token cookie travels
  })
}

let refreshInFlight = null

async function tryRefresh() {
  if (!refreshInFlight) {
    refreshInFlight = fetch(`${API_BASE}/auth/refresh/`, {
      method: 'POST',
      credentials: 'include',
    })
      .then(async (res) => {
        if (!res.ok) throw new Error('refresh_failed')
        const data = await res.json()
        setAccessToken(data.access)
        return data.access
      })
      .finally(() => {
        refreshInFlight = null
      })
  }
  return refreshInFlight
}

/**
 * apiFetch — for every JWT-authenticated (or AllowAny) host-facing endpoint.
 * Automatically retries once after a silent refresh if the access token
 * has expired (401), so callers don't need to think about token lifetime.
 */
export async function apiFetch(path, options = {}) {
  let res = await doFetch(path, options)

  if (res.status === 401 && getAccessToken()) {
    try {
      await tryRefresh()
      res = await doFetch(path, options)
    } catch {
      setAccessToken(null)
    }
  }

  if (!res.ok) {
    let body = null
    try {
      body = await res.json()
    } catch {
      /* non-JSON error body, ignore */
    }
    const message = body?.detail || JSON.stringify(body) || `Request failed (${res.status})`
    throw new ApiError(message, res.status, body)
  }

  if (res.status === 204) return null
  return res.json()
}

/**
 * guestFetch — for the guest-session-token endpoints (join flow / guest
 * ordering). Uses the "GuestSession <token>" scheme instead of "Bearer",
 * per party/authentication.py.
 */
export async function guestFetch(path, guestToken, options = {}) {
  const headers = { ...(options.headers || {}), Authorization: `GuestSession ${guestToken}` }
  const hasBody = options.body !== undefined
  if (hasBody && !headers['Content-Type']) headers['Content-Type'] = 'application/json'

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (!res.ok) {
    let body = null
    try {
      body = await res.json()
    } catch {
      /* ignore */
    }
    throw new ApiError(body?.detail || `Request failed (${res.status})`, res.status, body)
  }
  if (res.status === 204) return null
  return res.json()
}

export { ApiError }