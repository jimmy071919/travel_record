// Environment configuration
export const isDevelopment = process.env.NODE_ENV === 'development'

// API configuration
export const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000'
  : 'https://api.your-travel-record.com'

// Mapbox configuration
export const MAPBOX_CONFIG = {
  accessToken: 'pk.eyJ1IjoieXVhbmNoZW5nY2hlbiIsImEiOiJjbHJhZGY2MjQwMnBnMmtueXE2NmZwMmZ5In0.YxjpIXCG-nVcuuGrGj_Jrw',
  defaultCenter: [121.5654, 25.0330], // 台北市中心
  defaultZoom: 13,
  style: 'mapbox://styles/mapbox/streets-v12',
  language: 'zh-TW', // 中文語言支援
  geocoding: {
    endpoint: 'https://api.mapbox.com/geocoding/v5/mapbox.places',
    types: ['place', 'address', 'poi'],
    country: 'TW',
    limit: 5
  }
}

// Record configuration
export const RECORD_CONFIG = {
  maxPhotoSize: 5 * 1024 * 1024, // 5MB
  allowedPhotoTypes: ['image/jpeg', 'image/png', 'image/webp'],
  recordsPerPage: 10
}

// UI configuration
export const UI_CONFIG = {
  dateFormat: 'YYYY-MM-DD HH:mm',
  mapPopupWidth: 300,
  mapPopupHeight: 200
}

if (!MAPBOX_CONFIG.accessToken) {
  console.error('Mapbox access token is not set')
}
