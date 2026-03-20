"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useDashboard } from "@/lib/hooks"

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { label: "Autopilot", href: "/autopilot", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
  { label: "Resume", href: "/resume",    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { label: "Settings",  href: "/settings",  icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37a1.724 1.724 0 002.572-1.065z" },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { data } = useDashboard()

  const isOn = data?.autopilot_enabled && !data?.is_paused

  return (
    <aside className="w-64 border-r border-slate-200/60 bg-white flex flex-col h-screen sticky top-0 shadow-sm">
      <div className="p-8">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center shadow-indigo-200 shadow-lg group-hover:scale-105 transition-transform">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span className="text-xl font-bold tracking-tight text-slate-900">
            Jobly
          </span>
        </Link>
        <div className="mt-3 flex items-center gap-2 px-1">
          <span className={`w-1.5 h-1.5 rounded-full ${isOn ? "bg-emerald-500 animate-pulse" : "bg-slate-300"}`} />
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            {isOn ? "System Live" : "System Offline"}
          </p>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-1.5">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                active
                  ? "bg-indigo-50 text-indigo-600"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
              }`}
            >
              <svg className={`w-5 h-5 ${active ? "text-indigo-600" : "text-slate-400"}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} />
              </svg>
              {item.label}
              {active && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-600 shadow-indigo-200 shadow-lg" />
              )}
            </Link>
          )
        })}
      </nav>

      {data && (
        <div className="p-6">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <div className="flex justify-between items-end mb-2">
              <div>
                <p className="text-[10px] uppercase tracking-wider font-bold text-slate-400">
                  Total Output
                </p>
                <p className="text-xl font-bold text-slate-900 leading-none mt-1">
                  {data.stats.total_applied}
                </p>
              </div>
              <div className="text-right">
                <p className="text-[10px] font-bold text-emerald-600">
                  +12%
                </p>
              </div>
            </div>
            <div className="w-full bg-slate-200 h-1 rounded-full overflow-hidden">
              <div className="bg-indigo-600 h-full w-[40%]" />
            </div>
            <p className="text-[10px] text-slate-400 mt-2 font-medium">
              Daily quota: 12 / 50
            </p>
          </div>
        </div>
      )}
    </aside>
  )
}
