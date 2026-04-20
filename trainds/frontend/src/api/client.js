import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Automatically inject current language into all requests
client.interceptors.request.use((config) => {
  const lang = localStorage.getItem('lang') || 'en'
  
  // For GET requests, add to params
  if (config.method === 'get') {
    config.params = { ...config.params, lang }
  } 
  // For POST/PUT requests, add to body if it's JSON
  else if (config.data && typeof config.data === 'object' && !(config.data instanceof FormData)) {
    config.data = { ...config.data, lang }
  }
  // Also add to headers as a fallback
  config.headers['X-Language'] = lang
  
  return config
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.error || err.message || 'Something went wrong'
    return Promise.reject(new Error(message))
  }
)

export const routeAPI = {
  plan: (from, to) =>
    client.post('/route', { from, to }).then((r) => r.data),

  whatIf: (from, to) =>
    client.post('/route/what-if', { from, to }).then((r) => r.data),

  multiRoute: (source, destinations, mode = 'optimize') =>
    client.post('/multi-route', { source, destinations, mode }).then((r) => r.data),
}

export const delayAPI = {
  predict: (params) =>
    client.post('/predict-delay', params).then((r) => r.data),
}

export const liveAPI = {
  getTrains: (station) =>
    client.get('/live-train', { params: { station } }).then((r) => r.data),
}

export const megablockAPI = {
  getAll: () => client.get('/megablock').then((r) => r.data),
}

export const weatherAPI = {
  get: (city = 'Mumbai') =>
    client.get('/weather', { params: { city } }).then((r) => r.data),
}

export default client
