"use client"
import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { useUserId } from "@/lib/hooks"
import Link from "next/link"

export default function AutopilotPage() {
  const userId = useUserId()
  const [mounted, setMounted] = useState(false)
  const [status, setStatus]   = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving]   = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const fetchStatus = async () => {
    if (!userId) return
    try {
      const s = await api.getAutopilotStatus(userId)
      setStatus(s)
    } catch {
      setStatus(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [userId])

  const handleEnable = async () => {
    if (!userId) return
    setSaving(true)
    await api.enableAutopilot(userId)
    await fetchStatus()
    setSaving(false)
  }

  const handlePause = async () => {
    if (!userId) return
    setSaving(true)
    await api.pauseAutopilot(userId)
    await fetchStatus()
    setSaving(false)
  }

  const handleResume = async () => {
    if (!userId) return
    setSaving(true)
    await api.resumeAutopilot(userId)
    await fetchStatus()
    setSaving(false)
  }

  const handleDisable = async () => {
    if (!userId) return
    setSaving(true)
    await api.disableAutopilot(userId)
    await fetchStatus()
    setSaving(false)
  }

  if (!mounted) return null

  if (loading) {
    return (
      <div className="text-sm text-gray-400 mt-10">
        Loading...
      </div>
    )
  }

  const isOn     = status?.autopilot_enabled && !status?.is_paused
  const isPaused = status?.autopilot_enabled && status?.is_paused
  const isOff    = !status?.autopilot_enabled

  return (
    <div className="max-w-2xl mx-auto py-4">
      <div className="flex items-center gap-4 mb-2">
        <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Autopilot
          </h1>
          <p className="text-sm font-medium text-slate-400">
            Autonomous 24/7 job application agent
          </p>
        </div>
      </div>
      
      <p className="text-sm text-slate-500 mb-10 leading-relaxed max-w-md">
        When enabled, Jobly scans job boards every 6 hours,
        analyzes matches with your AI profile, and applies automatically.
      </p>

      {/* Big status card */}
      <div className={`rounded-3xl border-2 p-10 mb-8
                       text-center transition-all duration-300 relative overflow-hidden ${
        isOn
          ? "bg-emerald-50/50 border-emerald-200/60 shadow-lg shadow-emerald-100"
          : isPaused
          ? "bg-amber-50/50 border-amber-200/60 shadow-lg shadow-amber-100"
          : "bg-white border-slate-200/60 shadow-sm"
      }`}>
        {/* Subtle background decoration */}
        <div className="absolute -top-10 -right-10 w-32 h-32 bg-indigo-50/20 rounded-full blur-3xl" />
        
        <div className="flex justify-center mb-6">
          <div className={`p-4 rounded-2xl ${
            isOn ? "bg-emerald-100 text-emerald-600" : isPaused ? "bg-amber-100 text-amber-600" : "bg-slate-100 text-slate-400"
          }`}>
            <svg className={`w-8 h-8 ${isOn ? 'animate-pulse' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>

        <h2 className={`text-2xl font-bold mb-2 tracking-tight ${
          isOn ? "text-emerald-900" : isPaused ? "text-amber-900" : "text-slate-900"
        }`}>
          {isOn
            ? "Autopilot is Engaged"
            : isPaused
            ? "Service Paused"
            : "System Standby"}
        </h2>

        {status?.last_scraped_at ? (
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/50 backdrop-blur rounded-full border border-slate-200/50 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            Last Scan: {new Date(status.last_scraped_at).toLocaleTimeString()}
          </div>
        ) : (
          <p className="text-sm text-slate-400">Waiting for first scan...</p>
        )}

        {status?.stats && (
          <div className="grid grid-cols-3 gap-8
                           mt-10 pt-8 border-t border-slate-200/40">
            {[
              {
                label: "Applications Sent",
                value: status.stats.total_applied,
                color: "text-indigo-600"
              },
              {
                label: "Today's Limit",
                value: status.stats.applied_today,
                color: "text-slate-900"
              },
              {
                label: "Weekly Goal",
                value: status.stats.applied_this_week,
                color: "text-slate-900"
              },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <p className={`text-2xl font-bold ${s.color}`}>
                  {s.value}
                </p>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight mt-1">
                  {s.label}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-4">
        {isOff && (
          <button
            onClick={handleEnable}
            disabled={saving}
            className="flex-1 bg-indigo-600 text-white
                       py-4 rounded-2xl text-base font-bold
                       shadow-lg shadow-indigo-100 hover:bg-indigo-700 
                       hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50
                       transition-all"
          >
            {saving ? "Deploying..." : "Enable Autopilot"}
          </button>
        )}

        {isOn && (
          <button
            onClick={handlePause}
            disabled={saving}
            className="flex-1 border-2 border-amber-200
                       text-amber-700 py-4 rounded-2xl
                       text-base font-bold bg-amber-50/50
                       hover:bg-amber-50 disabled:opacity-50
                       transition-all"
          >
            {saving ? "Pausing..." : "Pause Autopilot"}
          </button>
        )}

        {isPaused && (
          <button
            onClick={handleResume}
            disabled={saving}
            className="flex-1 bg-emerald-600 text-white
                       py-4 rounded-2xl text-base font-bold
                       shadow-lg shadow-emerald-100 hover:bg-emerald-700
                       hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50
                       transition-all"
          >
            {saving ? "Resuming..." : "Resume Autopilot"}
          </button>
        )}

        {(isOn || isPaused) && (
          <button
            onClick={handleDisable}
            disabled={saving}
            className="px-8 py-4 rounded-2xl text-sm font-bold
                       text-slate-400 border-2 border-slate-100
                       hover:bg-slate-50 hover:text-slate-600 transition-all"
          >
            Deactivate
          </button>
        )}
      </div>

      {/* Preferences Preview */}
      {status?.preferences && (
        <div className="mt-10 card-premium p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest">
              Live Configuration
            </h3>
            <Link href="/settings" className="text-xs font-bold text-indigo-600 hover:underline">
              Modify Settings
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Threshold</p>
              <p className="text-lg font-bold text-slate-900">{status.preferences.match_threshold}%</p>
            </div>
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Sources</p>
              <p className="text-lg font-bold text-slate-900 capitalize">{status.preferences.platforms?.length || 0} Platforms</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
