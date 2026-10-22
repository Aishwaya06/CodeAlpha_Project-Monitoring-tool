import axios from 'axios'
export const api = axios.create({ baseURL: '/api', withCredentials: true, withXSRFToken: true, xsrfCookieName: 'csrftoken', xsrfHeaderName: 'X-CSRFToken' })
export function errorMessage(error) {
  if (!error.response) return 'Cannot reach the API. Start Django in the backend folder with: python manage.py runserver'
  const data = error.response.data
  if (data?.detail) return data.detail
  if (data && typeof data === 'object') return Object.values(data).flat().join(' ')
  return typeof data === 'string' ? data.slice(0, 240) : 'Request failed. Please try again.'
}
