/**
 * Axios configuration for API requests.
 *
 * This file provides a centralized axios instance that can be configured
 * with a base URL for different environments (local, GitHub Pages, hosted backend).
 *
 * For GitHub Pages deployment, set VITE_API_BASE_URL environment variable
 * to point to your hosted backend API (e.g., https://api.example.com).
 *
 * If VITE_API_BASE_URL is not set, axios will use relative URLs which work
 * when the frontend and backend are on the same origin.
 */
import axios from 'axios'

// Get API base URL from environment variable
// Vite exposes env variables via import.meta.env
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Create axios instance with base URL if configured
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default apiClient
