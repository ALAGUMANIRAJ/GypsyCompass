import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds for AI responses
});

export const getRecommendations = (userPrefs) =>
  api.post('/recommendations/', userPrefs);

export const getDestinationDetails = (destinationName, userPrefs) =>
  api.post('/destination-details/', {
    destination_name: destinationName,
    user_prefs: userPrefs,
  });

export const getLocationSuggestions = (query) =>
  api.get('/location-suggestions/', { params: { q: query } });

export const checkHealth = () =>
  api.get('/health/');

export const sendContactMessage = (contactData) =>
  api.post('/contact/', contactData);

export default api;
