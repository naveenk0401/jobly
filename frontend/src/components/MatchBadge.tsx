export default function MatchBadge({
  score,
}: {
  score: number | null
}) {
  if (score === null) return null

  const color =
    score >= 80
      ? "text-emerald-600"
      : score >= 60
      ? "text-indigo-600"
      : "text-amber-600"

  const bg =
    score >= 80
      ? "bg-emerald-50"
      : score >= 60
      ? "bg-indigo-50"
      : "bg-amber-50"

  return (
    <div className={`flex flex-col items-center justify-center w-12 h-12 rounded-xl border border-slate-100 ${bg}`}>
      <span className={`text-sm font-bold ${color}`}>
        {Math.round(score)}%
      </span>
    </div>
  )
}
