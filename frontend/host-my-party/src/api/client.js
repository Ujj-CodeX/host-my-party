const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const ACCESS_TOKEN_KEY = 'hostMyParty.accessToken'
const USER_KEY = 'hostMyParty.user'
const GUEST_SESSION_KEY = 'hostMyParty.guestSession'

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function isAuthenticated() {
  return Boolean(getAccessToken())
}

export function getCurrentUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null

  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function setAuthSession(data) {
  if (data?.access) localStorage.setItem(ACCESS_TOKEN_KEY, data.access)
  if (data?.user) localStorage.setItem(USER_KEY, JSON.stringify(data.user))
}

export function clearAuthSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function setGuestSession(data) {
  localStorage.setItem(GUEST_SESSION_KEY, JSON.stringify(data))
}

export function getGuestSession() {
  const raw = localStorage.getItem(GUEST_SESSION_KEY)
  if (!raw) return null

  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function clearGuestSession() {
  localStorage.removeItem(GUEST_SESSION_KEY)
}

function getAuthHeader(guest) {
  if (guest) {
    const token = getGuestSession()?.session_token
    return token ? { Authorization: `GuestSession ${token}` } : {}
  }

  const token = getAccessToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function buildHeaders(headers = {}, guest = false) {
  return {
    'Content-Type': 'application/json',
    ...getAuthHeader(guest),
    ...headers,
  }
}

function parseErrorMessage(data) {
  if (!data) return 'Request failed'
  if (data.detail) return data.detail
  if (Array.isArray(data.non_field_errors)) return data.non_field_errors[0]

  const firstFieldError = Object.values(data).flat().find(Boolean)
  return firstFieldError || 'Request failed'
}

export async function apiRequest(path, { method = 'GET', body, headers, guest = false } = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: 'include',
    headers: buildHeaders(headers, guest),
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  })

  const text = await response.text()
  const data = text ? JSON.parse(text) : null

  if (!response.ok) {
    const error = new Error(parseErrorMessage(data))
    error.status = response.status
    error.data = data
    throw error
  }

  return data
}

export const authApi = {
  login(payload) {
    return apiRequest('/auth/login/phone/', { method: 'POST', body: payload }).then((data) => {
      setAuthSession(data)
      return data
    })
  },
  signup(payload) {
    return apiRequest('/auth/signup/phone/', { method: 'POST', body: payload }).then((data) => {
      setAuthSession(data)
      return data
    })
  },
  async logout() {
    try {
      await apiRequest('/auth/logout/', { method: 'POST' })
    } finally {
      clearAuthSession()
    }
  },
}

export { API_BASE }
