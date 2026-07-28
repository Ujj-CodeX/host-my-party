// src/api/ai.js
import { apiRequest } from './client'

export const getRestaurants = (payload) =>
  apiRequest('/ai/restaurants/', {
    method: 'POST',
    body: payload,
  })

export const guestGetRestaurants = (category) => {
  const query = category
    ? `?category=${encodeURIComponent(category)}`
    : ''

  return apiRequest(`/ai/guest/restaurants/${query}`, {
    guest: true,
  })
}

export const scheduleLateOrder = (payload) =>
  apiRequest('/ai/schedule-late-order/', {
    method: 'POST',
    body: payload,
  })

export const getScheduledOrders = () =>
  apiRequest('/ai/scheduled-orders/')

export const budgetCheck = (payload) =>
  apiRequest('/ai/budget-check/', {
    method: 'POST',
    body: payload,
  })

export const mergeCheck = (payload) =>
  apiRequest('/ai/merge-check/', {
    method: 'POST',
    body: payload,
  })

export const dineoutRestaurants = (payload) =>
  apiRequest('/ai/dineout/restaurants/', {
    method: 'POST',
    body: payload,
  })

export const dineoutSlots = (payload) =>
  apiRequest('/ai/dineout/slots/', {
    method: 'POST',
    body: payload,
  })

export const dineoutBook = (payload) =>
  apiRequest('/ai/dineout/book/', {
    method: 'POST',
    body: payload,
  })