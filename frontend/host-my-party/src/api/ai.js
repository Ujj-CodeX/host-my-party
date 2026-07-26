// src/api/ai.js — ai/urls.py (all under /api/ai/). These endpoints are
// currently AllowAny on the backend (no @permission_classes set for the
// host-facing ones), so apiFetch is used mainly for the consistent
// base-URL/error handling, not because a token is required.
import { apiFetch } from './client'

export const getRestaurants = (payload) =>
  apiFetch('/ai/restaurants/', { method: 'POST', body: JSON.stringify(payload) })

export const scheduleLateOrder = (payload) =>
  apiFetch('/ai/schedule-late-order/', { method: 'POST', body: JSON.stringify(payload) })

export const getScheduledOrders = () => apiFetch('/ai/scheduled-orders/')

export const budgetCheck = (payload) =>
  apiFetch('/ai/budget-check/', { method: 'POST', body: JSON.stringify(payload) })

export const mergeCheck = (payload) =>
  apiFetch('/ai/merge-check/', { method: 'POST', body: JSON.stringify(payload) })

export const dineoutRestaurants = (payload) =>
  apiFetch('/ai/dineout/restaurants/', { method: 'POST', body: JSON.stringify(payload) })