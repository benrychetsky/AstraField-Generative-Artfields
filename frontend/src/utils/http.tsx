/// <reference types="vite/client" />

export const API_BASE = "/api";


export async function getJSON<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export async function postForm<T>(
  endpoint: string,
  data: FormData
): Promise<T | Blob> {
  const res = await fetch(`${API_BASE}${endpoint}`, { method: "POST", body: data });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? (res.json() as Promise<T>) : res.blob();
}
