"use client"
import { useDashboard, useUserId } from "@/lib/hooks"
import MatchBadge from "@/components/MatchBadge"
import StatusChip from "@/components/StatusChip"
import { api } from "@/lib/api"
import { useState, useEffect } from "react"
import Link from "next/link"

export default function DashboardPage() {
  const userId             = useUserId()
  const [mounted, setMounted] = useState(false)
  const { data, loading,
          error, refetch } = useDashboard()
  const [matching, setMatching] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleMatch = async () => {
    if (!userId) return
    setMatching(true)
    try {
      await api.triggerMatch(userId, 50)
      setTimeout(refetch, 3000)
    } finally {
      setMatching(false)
    }
  }

  if (!mounted) return null

  if (!userId) {
    return (
      <div className="max-w-md mx-auto mt-20 text-center">
        <h1 className="text-2xl font-semibold mb-3">
          Welcome to Jobly
        </h1>
        <p className="text-gray-500 mb-6">
          Set up your account to start the autopilot.
        </p>
        <Link
          href="/settings"
          className="bg-gray-900 text-white px-5 py-2.5
                     rounded-lg text-sm hover:bg-gray-700
                     transition-colors"
        >
          Get started
        </Link>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="text-sm text-gray-400 mt-10">
        Loading dashboard...
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-sm text-red-500 mt-10">
        Error: {error}
      </div>
    )
  }

  const stats = data?.stats
  const feed  = data?.feed || []

  return (
    <div className="max-w-4xl mx-auto py-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-10">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Dashboard
          </h1>
          <div className="flex items-center gap-2 mt-1.5">
            <span className={`w-2 h-2 rounded-full ${
              data?.autopilot_enabled && !data?.is_paused
                ? "bg-emerald-500 animate-pulse"
                : "bg-slate-300"
            }`} />
            <p className="text-sm font-medium text-slate-500">
              {data?.autopilot_enabled && !data?.is_paused
                ? "Autopilot is active and discoverying jobs"
                : data?.is_paused
                ? "Autopilot is currently paused"
                : "Autopilot is offline"}
            </p>
          </div>
        </div>
        <button
          onClick={handleMatch}
          disabled={matching}
          className="flex items-center gap-2.5 px-6 py-2.5 bg-indigo-600 text-white rounded-xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 font-medium"
        >
          <svg className={`w-4 h-4 ${matching ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {matching ? "Matching..." : "Run discovery"}
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-4 gap-5 mb-12">
        {[
          {
            label: "Total sent",
            value: stats?.total_applied ?? 0,
            trend: "+12% this week",
            icon: "M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          },
          {
            label: "Daily focus",
            value: stats?.applied_today ?? 0,
            trend: "On track",
            icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          },
          {
            label: "Weekly output",
            value: stats?.applied_this_week ?? 0,
            trend: "Peak performance",
            icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
          },
          {
            label: "Match quality",
            value: stats?.avg_match_score
              ? `${Math.round(stats.avg_match_score)}%`
              : "—",
            trend: "Top 5% candidate",
            icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          },
        ].map((s) => (
          <div
            key={s.label}
            className="card-premium p-6 group"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-slate-50 text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-600 rounded-xl flex items-center justify-center transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={s.icon} />
                </svg>
              </div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">
                {s.label}
              </span>
            </div>
            <p className="text-3xl font-bold text-slate-900 mb-1">
              {s.value}
            </p>
            <p className="text-[10px] font-medium text-emerald-600">
              {s.trend}
            </p>
          </div>
        ))}
      </div>

      {/* Main Feed Container */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">
            Discovery Feed
          </h2>
          <div className="flex gap-2">
            <button className="px-3 py-1 text-xs font-semibold text-slate-500 bg-white border border-slate-200 rounded-lg hover:border-slate-300">
              Recent
            </button>
            <button className="px-3 py-1 text-xs font-semibold text-indigo-600 bg-indigo-50 border border-indigo-100 rounded-lg">
              Applying
            </button>
          </div>
        </div>

        {feed.length === 0 ? (
          <div className="card-premium p-16 text-center border-dashed bg-slate-50/50">
            <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-slate-200">
              <svg className="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <p className="text-slate-500 font-medium">
              Your discovery feed is empty
            </p>
            <p className="text-slate-400 text-sm mt-1 mb-6">
              Enable autopilot to begin autonomous job discovery
            </p>
            <Link
              href="/autopilot"
              className="inline-flex items-center gap-2 text-indigo-600 font-semibold text-sm hover:gap-3 transition-all underline decoration-2 underline-offset-4"
            >
              Set up autopilot →
            </Link>
          </div>
        ) : (
          <div className="grid gap-3">
            {feed.map((app) => (
              <div
                key={app.application_id}
                className="card-premium px-6 py-5 flex items-center gap-6"
              >
                <div className="w-12 h-12 bg-slate-50 rounded-xl flex items-center justify-center font-bold text-slate-400 border border-slate-100 text-lg">
                  {app.company.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-bold text-slate-900 truncate">
                    {app.job_title}
                  </p>
                  <p className="text-sm font-medium text-slate-400 mt-0.5">
                    {app.company} {app.location ? `· ${app.location}` : ""}
                  </p>
                </div>
                <div className="flex items-center gap-8">
                  <div className="text-right">
                    <MatchBadge score={app.match_score} />
                    <p className="text-[10px] font-bold text-slate-300 mt-1 uppercase tracking-tighter">
                      AI Match Score
                    </p>
                  </div>
                  <div className="w-px h-8 bg-slate-100" />
                  <StatusChip status={app.status} />
                  <a
                    href={app.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-9 h-9 border border-slate-200 rounded-xl flex items-center justify-center text-slate-400 hover:text-indigo-600 hover:border-indigo-200 transition-all hover:bg-indigo-50"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
