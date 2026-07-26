// src/api/party.js
import { apiRequest } from './client'

// Party
export const listParties = () =>
  apiRequest('/parties/')

export const createParty = (payload) =>
  apiRequest('/parties/', {
    method: 'POST',
    body: payload,
  })

export const getParty = (code) =>
  apiRequest(`/parties/${code}/`)

export const updateParty = (code, payload) =>
  apiRequest(`/parties/${code}/`, {
    method: 'PATCH',
    body: payload,
  })

// Guests - host side
export const listGuests = (code) =>
  apiRequest(`/parties/${code}/guests/`)

export const addGuest = (code, payload) =>
  apiRequest(`/parties/${code}/guests/`, {
    method: 'POST',
    body: payload,
  })

export const updateGuest = (code, guestId, payload) =>
  apiRequest(`/parties/${code}/guests/${guestId}/`, {
    method: 'PATCH',
    body: payload,
  })

export const removeGuest = (code, guestId) =>
  apiRequest(`/parties/${code}/guests/${guestId}/`, {
    method: 'DELETE',
  })

// Public guest join
export const getJoinInfo = (code) =>
  apiRequest(`/join/${code}/`)

export const joinParty = (code, payload) =>
  apiRequest(`/join/${code}/`, {
    method: 'POST',
    body: payload,
  })

// Orders - host JWT
export const listOrders = (code) =>
  apiRequest(`/parties/${code}/orders/`)

export const createOrder = (code, payload) =>
  apiRequest(`/parties/${code}/orders/`, {
    method: 'POST',
    body: payload,
  })

export const updateOrder = (code, orderId, payload) =>
  apiRequest(`/parties/${code}/orders/${orderId}/`, {
    method: 'PATCH',
    body: payload,
  })

export const deleteOrder = (code, orderId) =>
  apiRequest(`/parties/${code}/orders/${orderId}/`, {
    method: 'DELETE',
  })

// Guest order - GuestSession auth
export const guestCreateOrder = (payload) =>
  apiRequest('/guest/orders/', {
    method: 'POST',
    body: payload,
    guest: true,
  })

// Booking
export const getBooking = (code) =>
  apiRequest(`/parties/${code}/booking/`)

export const createBooking = (code, payload) =>
  apiRequest(`/parties/${code}/booking/`, {
    method: 'POST',
    body: payload,
  })

export const updateBooking = (code, payload) =>
  apiRequest(`/parties/${code}/booking/`, {
    method: 'PATCH',
    body: payload,
  })