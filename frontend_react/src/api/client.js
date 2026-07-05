const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

export async function apiRequest(path, { token, method = "GET", body, isFormData = false } = {}) {
  const headers = {};
  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Request failed");
  }

  return response.json();
}
