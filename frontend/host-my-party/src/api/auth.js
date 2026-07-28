

// src/api/auth.js
import {
  apiRequest,
  setAuthSession,
  clearAuthSession,
} from './client'

export async function signupPhone({ phone_number, password, name }) {
  const data = await apiRequest('/auth/signup/phone/', {
    method: 'POST',
    body: { phone_number, password, name },
  })

  setAuthSession(data)
  return data
}

export async function loginPhone({ phone_number, password }) {
  const data = await apiRequest('/auth/login/phone/', {
    method: 'POST',
    body: { phone_number, password },
  })

  setAuthSession(data)
  return data
}

export async function googleAuth(idToken) {
  const data = await apiRequest('/auth/google/', {
    method: 'POST',
    body: { id_token: idToken },
  })

  setAuthSession(data)
  return data
}

export async function logout() {
  try {
    await apiRequest('/auth/logout/', {
      method: 'POST',
    })
  } finally {
    clearAuthSession()
  }
}

export function refreshToken(refresh) {
  return apiRequest('/auth/refresh/', {
    method: 'POST',
    body: { refresh },
  })
}

export function updateProfile(payload) {
  return apiRequest('/auth/profile/', {
    method: 'PATCH',
    body: payload,
  })
}






