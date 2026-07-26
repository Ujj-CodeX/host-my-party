// src/api/auth.js — thin wrappers around backend/account/urls.py
import { apiFetch, setAccessToken } from './client'

export async function signupPhone({ phone_number, password, name }) {
  const data = await apiFetch('/auth/signup/phone/', {
    method: 'POST',
    body: JSON.stringify({ phone_number, password, name }),
  })
  setAccessToken(data.access)
  return data.user
}

export async function loginPhone({ phone_number, password }) {
  const data = await apiFetch('/auth/login/phone/', {
    method: 'POST',
    body: JSON.stringify({ phone_number, password }),
  })
  setAccessToken(data.access)
  return data.user
}

export async function googleAuth(idToken) {
  const data = await apiFetch('/auth/google/', {
    method: 'POST',
    body: JSON.stringify({ id_token: idToken }),
  })
  setAccessToken(data.access)
  return data.user
}

export async function logout() {
  try {
    await apiFetch('/auth/logout/', { method: 'POST' })
  } finally {
    setAccessToken(null)
  }
}

export async function updateProfile(payload) {
  return apiFetch('/auth/profile/', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}