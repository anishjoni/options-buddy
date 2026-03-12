const BASE_URL = "http://localhost:8000"

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || "Request failed")
  }
  return res.json()
}

export const api = {
  get: (path) => request(path),
  patch: (path, body) => request(path, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }),
  post: (path, body) => request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }),
  uploadCSV: (file) => {
    const form = new FormData()
    form.append("file", file)
    return request("/import/csv", { method: "POST", body: form })
  },
}
