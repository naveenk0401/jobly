"use client"
import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { useUserId, setUserId } from "@/lib/hooks"
import Link from "next/link"

const PLATFORMS = ["greenhouse", "lever", "workday"]

export default function SettingsPage() {
  const userId = useUserId()
  const [mounted, setMounted] = useState(false)
  const [saving, setSaving]     = useState(false)
  const [message, setMessage]   = useState("")
  const [creating, setCreating] = useState(false)

  // New user form
  const [newEmail, setNewEmail] = useState("")
  const [newName, setNewName]   = useState("")

  // Preferences form
  const [roles, setRoles]           = useState("")
  const [locations, setLocations]   = useState("")
  const [companies, setCompanies]   = useState("")
  const [summary, setSummary]       = useState("")
  const [threshold, setThreshold]   = useState(65)
  const [platforms, setPlatforms]   = useState<string[]>([
    "greenhouse",
    "lever",
  ])

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted || !userId) return
    api.getUser(userId).then((user: any) => {
      setSummary(user.summary || "")
      const prefs = user.preferences || {}
      setRoles(prefs.roles?.join(", ") || "")
      setLocations(prefs.locations?.join(", ") || "")
      setCompanies(
        prefs.target_companies?.join(", ") || ""
      )
      setThreshold(prefs.match_threshold || 65)
      setPlatforms(
        prefs.platforms || ["greenhouse", "lever"]
      )
    })
  }, [userId])

  const handleCreateAccount = async () => {
    if (!newEmail || !newName) {
      setMessage("Email and name are required")
      return
    }
    setCreating(true)
    try {
      const result = await api.createUser({
        email: newEmail,
        name:  newName,
      })
      setUserId(result.user_id)
      setMessage(
        `Account created! Your ID: ${result.user_id}`
      )
      window.location.reload()
    } catch (e: any) {
      setMessage(e.message)
    } finally {
      setCreating(false)
    }
  }

  const handleSave = async () => {
    if (!userId) return
    setSaving(true)
    setMessage("")
    try {
      await api.updateUser(userId, {
        summary,
        preferences: {
          roles:            roles
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          locations:        locations
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          target_companies: companies
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          platforms,
          match_threshold: threshold,
        },
      })
      setMessage("Settings saved")
    } catch (e: any) {
      setMessage(`Error: ${e.message}`)
    } finally {
      setSaving(false)
    }
  }

  const togglePlatform = (p: string) => {
    setPlatforms((prev) =>
      prev.includes(p)
        ? prev.filter((x) => x !== p)
        : [...prev, p]
    )
  }

  if (!mounted) return null

  return (
    <div className="max-w-4xl mx-auto py-4">
      <div className="flex items-center gap-4 mb-2">
        <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37a1.724 1.724 0 002.572-1.065z" />
          </svg>
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Settings
          </h1>
          <p className="text-sm font-medium text-slate-400">
            Account & Autopilot Strategy
          </p>
        </div>
      </div>

      <p className="text-sm text-slate-500 mb-10 leading-relaxed max-w-md">
        Configure your professional identity and application parameters.
        Jobly uses these settings to target the right roles for you.
      </p>

      {message && (
        <div className={`text-sm font-medium rounded-2xl px-6 py-4 mb-8 flex items-center gap-3 animate-in fade-in slide-in-from-top-2 border ${
          message.startsWith("Error") 
            ? "bg-rose-50 border-rose-100 text-rose-600" 
            : "bg-emerald-50 border-emerald-100 text-emerald-700"
        }`}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={message.startsWith("Error") ? "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" : "M5 13l4 4L19 7"} />
          </svg>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left Column: Account Details */}
        <div className="md:col-span-4 space-y-6">
          <div className="card-premium p-6">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest mb-6 px-1">
              Identity
            </h3>
            
            {!userId ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-1.5 px-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                    placeholder="Alex Johnson"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-1.5 px-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                    placeholder="alex@example.com"
                  />
                </div>
                <button
                  onClick={handleCreateAccount}
                  disabled={creating}
                  className="w-full bg-indigo-600 text-white py-3.5 rounded-xl text-sm font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all disabled:opacity-50 mt-2"
                >
                  {creating ? "Initialising..." : "Create Account"}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 break-all">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-1">
                    Active User ID
                  </p>
                  <p className="text-sm font-mono text-indigo-600 font-bold">
                    {userId}
                  </p>
                </div>
                <p className="text-[10px] text-slate-400 text-center font-medium italic">
                  Saved securely in your browser cache
                </p>
              </div>
            )}
          </div>

          <div className="card-premium p-6">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest mb-4 px-1">
              Help & Resources
            </h3>
            <ul className="space-y-3">
              {["How matching works", "Connecting Gmail", "Career Bot Specs"].map((item) => (
                <li key={item}>
                  <a href="#" className="text-xs font-bold text-slate-400 hover:text-indigo-600 flex items-center gap-2 group">
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-200 group-hover:bg-indigo-400 transition-colors" />
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right Column: Preferences */}
        <div className="md:col-span-8">
          <div className="card-premium p-8">
            <h3 className="text-base font-bold text-slate-900 tracking-tight mb-8">
              Target Strategy
            </h3>

            <div className="space-y-8">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-2 px-1">
                    Target Roles
                  </label>
                  <input
                    type="text"
                    value={roles}
                    onChange={(e) => setRoles(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                    placeholder="Software Engineer, Product Manager"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-2 px-1">
                    Locations
                  </label>
                  <input
                    type="text"
                    value={locations}
                    onChange={(e) => setLocations(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                    placeholder="Remote, USA, London"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-2 px-1">
                   Target / Exclude Companies
                </label>
                <input
                  type="text"
                  value={companies}
                  onChange={(e) => setCompanies(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                  placeholder="Stripe, Vercel, Notion"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-2 px-1">
                  Professional Summary (AI Prompt)
                </label>
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  rows={4}
                  className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none leading-relaxed"
                  placeholder="I'm a senior full-stack engineer with 8 years of experience in React, Next.js, and Python..."
                />
              </div>

              <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                <div className="flex justify-between items-center mb-4">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">
                    Minimum Match Threshold
                  </label>
                  <span className="text-sm font-bold text-indigo-600 bg-white px-3 py-1 rounded-lg border border-slate-200">
                    {threshold}%
                  </span>
                </div>
                <input
                  type="range"
                  min="40"
                  max="90"
                  step="5"
                  value={threshold}
                  onChange={(e) => setThreshold(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <p className="text-[10px] text-slate-400 mt-4 leading-relaxed font-medium">
                  Higher threshold means fewer applications but higher compatibility.
                  We recommend <span className="text-indigo-500 font-bold">65%</span> for most users.
                </p>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-tight mb-4 px-1">
                  Connected Platforms
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {PLATFORMS.map((p) => {
                    const active = platforms.includes(p)
                    return (
                      <button
                        key={p}
                        onClick={() => togglePlatform(p)}
                        className={`py-3 rounded-xl text-xs font-bold capitalize transition-all border ${
                          active
                            ? "bg-indigo-600 text-white border-indigo-600 shadow-lg shadow-indigo-100"
                            : "bg-white text-slate-400 border-slate-200 hover:border-slate-300"
                        }`}
                      >
                        {p}
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="pt-6 border-t border-slate-100 flex justify-end">
                <button
                  onClick={handleSave}
                  disabled={saving || !userId}
                  className="px-10 py-3.5 bg-indigo-600 text-white rounded-2xl text-base font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
                >
                  {saving ? "Deploying Changes..." : "Save Configuration"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
