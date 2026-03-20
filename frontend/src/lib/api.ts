import type { User, Job, Application, Dashboard } from "./types"

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Users
  createUser: (body: object) =>
    request<{ user_id: string }>("/user", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getUser: (userId: string) =>
    request<User>(`/user/${userId}`),

  updateUser: (userId: string, body: object) =>
    request<{ status: string }>(`/user/${userId}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  // Resume
  uploadResume: (userId: string, file: File) => {
    const form = new FormData()
    form.append("user_id", userId)
    form.append("file", file)
    return fetch(`${BASE}/resume`, {
      method: "POST",
      body: form,
    }).then((r) => r.json() as Promise<any>)
  },

  getResume: (userId: string) =>
    request<any>(`/resume/${userId}`),

  // Jobs
  getJobs: (params?: {
    skip?: number
    limit?: number
    source?: string
    company?: string
  }) => {
    const q = new URLSearchParams()
    if (params?.skip)    q.set("skip",    String(params.skip))
    if (params?.limit)   q.set("limit",   String(params.limit))
    if (params?.source)  q.set("source",  params.source)
    if (params?.company) q.set("company", params.company)
    return request<Job[]>(`/jobs?${q.toString()}`)
  },

  triggerScrape: (
    platform: string,
    company: string,
    userId: string
  ) =>
    request<{ status: string, task_id: string }>(
      `/jobs/scrape?platform=${platform}&company=${company}&user_id=${userId}`,
      { method: "POST" }
    ),

  // Autopilot
  enableAutopilot: (userId: string) =>
    request<{ status: string }>(`/autopilot/enable?user_id=${userId}`, {
      method: "POST",
    }),

  pauseAutopilot: (userId: string) =>
    request<{ status: string }>(`/autopilot/pause?user_id=${userId}`, {
      method: "POST",
    }),

  resumeAutopilot: (userId: string) =>
    request<{ status: string }>(`/autopilot/resume?user_id=${userId}`, {
      method: "POST",
    }),

  disableAutopilot: (userId: string) =>
    request<{ status: string }>(`/autopilot/disable?user_id=${userId}`, {
      method: "POST",
    }),

  getAutopilotStatus: (userId: string) =>
    request<any>(`/autopilot/status?user_id=${userId}`),

  // Applications
  getDashboard: (userId: string) =>
    request<Dashboard>(`/applications/dashboard?user_id=${userId}`),

  getApplications: (
    userId: string,
    status?: string,
    limit = 50
  ) => {
    const q = new URLSearchParams({ user_id: userId })
    if (status) q.set("status", status)
    q.set("limit", String(limit))
    return request<Application[]>(`/applications?${q.toString()}`)
  },

  triggerMatch: (userId: string, limit = 50) =>
    request<{ status: string, task_id: string }>(
      `/applications/match?user_id=${userId}&limit=${limit}`,
      { method: "POST" }
    ),

  applyToJob: (userId: string, jobId: string) =>
    request<{ status: string, application_id: string }>("/applications/apply", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        job_id: jobId,
      }),
    }),
}
