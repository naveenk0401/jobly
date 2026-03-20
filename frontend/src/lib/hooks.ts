"use client"
import { useState, useEffect, useCallback } from "react"
import { api } from "./api"
import type { Dashboard, User } from "./types"

export function useUserId(): string {
  // For MVP: store user_id in localStorage
  // Replace with proper auth in v2
  if (typeof window === "undefined") return ""
  return localStorage.getItem("jobly_user_id") || ""
}

export function setUserId(id: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("jobly_user_id", id)
  }
}

export function useDashboard() {
  const userId = useUserId()
  const [data, setData] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>("")

  const fetch = useCallback(async () => {
    if (!userId) {
      setLoading(false)
      return
    }
    try {
      setLoading(true)
      const d = await api.getDashboard(userId)
      setData(d)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    fetch()
    // Refresh every 30 seconds for live feel
    const interval = setInterval(fetch, 30000)
    return () => clearInterval(interval)
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useUser() {
  const userId = useUserId()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!userId) {
      setLoading(false)
      return
    }
    api.getUser(userId)
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [userId])

  return { user, loading }
}
