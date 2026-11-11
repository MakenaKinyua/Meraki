const apiUrl = import.meta.env.VITE_API_URL || ''

export class ApiError extends Error {
  constructor(status) {
    super(`Request failed with status ${status}`)
    this.status = status
  }
}

async function request(path, options) {
  const response = await fetch(`${apiUrl}/api/${path}`, options)
  if (!response.ok) throw new ApiError(response.status)
  return response.json()
}

export function fetchConversations() {
  return request('conversations')
}

export function fetchConversation(id) {
  return request(`conversations/${id}`)
}

export function createConversation() {
  return request('conversations', { method: 'POST' })
}
