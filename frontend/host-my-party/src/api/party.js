// src/api/party.js — party/urls.py + order/urls.py, host (JWT) side
import { apiFetch, guestFetch } from './client'

// ── Party ──────────────────────────────────────────────────────────────
export const listParties = () => apiFetch('/parties/')

export const createParty = (payload) =>
  apiFetch('/parties/', { method: 'POST', body: JSON.stringify(payload) })

export const getParty = (code) => apiFetch(`/parties/${code}/`)

export const updateParty = (code, payload) =>
  apiFetch(`/parties/${code}/`, { method: 'PATCH', body: JSON.stringify(payload) })

// ── Guests ─────────────────────────────────────────────────────────────
export const listGuests = (code) => apiFetch(`/parties/${code}/guests/`)

export const addGuest = (code, payload) =>
  apiFetch(`/parties/${code}/guests/`, { method: 'POST', body: JSON.stringify(payload) })

export const updateGuest = (code, guestId, payload) =>
  apiFetch(`/parties/${code}/guests/${guestId}/`, { method: 'PATCH', body: JSON.stringify(payload) })

export const removeGuest = (code, guestId) =>
  apiFetch(`/parties/${code}/guests/${guestId}/`, { method: 'DELETE' })

// ── Guest join flow (public) ──────────────────────────────────────────
export const getJoinInfo = (code) => apiFetch(`/join/${code}/`)

export const joinParty = (code, payload) =>
  apiFetch(`/join/${code}/`, { method: 'POST', body: JSON.stringify(payload) })

// ── Orders (host side, JWT) ───────────────────────────────────────────
export const listOrders = (code) => apiFetch(`/parties/${code}/orders/`)

export const createOrder = (code, payload) =>
  apiFetch(`/parties/${code}/orders/`, { method: 'POST', body: JSON.stringify(payload) })

export const updateOrder = (code, orderId, payload) =>
  apiFetch(`/parties/${code}/orders/${orderId}/`, { method: 'PATCH', body: JSON.stringify(payload) })

export const deleteOrder = (code, orderId) =>
  apiFetch(`/parties/${code}/orders/${orderId}/`, { method: 'DELETE' })

// ── Orders (guest self-service, GuestSession token) ───────────────────
export const guestCreateOrder = (guestToken, payload) =>
  guestFetch('/guest/orders/', guestToken, { method: 'POST', body: JSON.stringify(payload) })

export const guestGetRestaurants = (guestToken, category) =>
  guestFetch(
    `/ai/guest/restaurants/${category ? `?category=${encodeURIComponent(category)}` : ''}`,
    guestToken,
  )

// ── Booking (Dineout) ──────────────────────────────────────────────────
export const getBooking = (code) => apiFetch(`/parties/${code}/booking/`)

export const createBooking = (code, payload) =>
  apiFetch(`/parties/${code}/booking/`, { method: 'POST', body: JSON.stringify(payload) })

export const updateBooking = (code, payload) =>
  apiFetch(`/parties/${code}/booking/`, { method: 'PATCH', body: JSON.stringify(payload) })