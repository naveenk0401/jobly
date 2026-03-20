const STATUS_STYLES: Record<string, string> = {
  applied:         "bg-emerald-50/80 text-emerald-700 border-emerald-100",
  pending:         "bg-indigo-50/80 text-indigo-700 border-indigo-100",
  failed:          "bg-rose-50/80 text-rose-700 border-rose-100",
  paused:          "bg-slate-100 text-slate-500 border-slate-200",
  below_threshold: "bg-slate-50 text-slate-400 border-slate-100",
}

export default function StatusChip({
  status,
}: {
  status: string
}) {
  const style =
    STATUS_STYLES[status] ||
    "bg-slate-100 text-slate-500 border-slate-200"

  return (
    <span
      className={`px-3 py-1 rounded-full text-[10px]
                  font-bold uppercase tracking-wider border ${style}`}
    >
      {status.replace("_", " ")}
    </span>
  )
}
