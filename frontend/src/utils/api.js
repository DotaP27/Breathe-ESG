const API_BASE = import.meta.env.VITE_API_BASE || 'https://breathe-esg-a273.onrender.com'

export { API_BASE }

function authHeaders(){
  const token = localStorage.getItem('access_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

export default {
  get: (path) => fetch(API_BASE + path, { headers: { ...authHeaders() } }),
  post: (path, body) => fetch(API_BASE + path, { method:'POST', headers:{ 'Content-Type':'application/json', ...authHeaders() }, body: JSON.stringify(body) }),
  put: (path, body) => fetch(API_BASE + path, { method:'PUT', headers:{ 'Content-Type':'application/json', ...authHeaders() }, body: JSON.stringify(body) }),
  postFile: (path, form) => fetch(API_BASE + path, { method:'POST', body: form, headers: { ...authHeaders() } }),
}
