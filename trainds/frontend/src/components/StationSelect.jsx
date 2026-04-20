import { useState, useEffect } from 'react'

export default function StationSelect({ label, value, onChange, stations }) {
  const [query, setQuery] = useState(value || '')
  const [open, setOpen] = useState(false)

  const filtered = (stations || [])
    .filter((s) => s && s.name)
    .filter((s) => {
      const q = typeof query === "string" ? query.toLowerCase().trim() : ""

      if (!q) return true

      return (
        s.name.toLowerCase().includes(q) ||
        (s.line || "").toLowerCase().includes(q)
      )
    })
    .slice(0, 20)

  useEffect(() => {
    if (value && value.name) {
      setQuery(`${value.name} — ${value.line}`)
    }
  }, [value])

  return (
    <div className="relative">
      {label && (
        <label className="section-label mb-1 block">{label}</label>
      )}

      <input
        className="input-base"
        value={query}
        placeholder={`Search ${label || 'station'}...`}
        onChange={(e) => {
          setQuery(e.target.value)
          setOpen(true)
          if (!e.target.value) onChange(null)
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
      />

      {open && filtered.length > 0 && (
        <ul className="absolute z-30 w-full mt-1 bg-white dark:bg-slate-800
                       border border-slate-200 dark:border-slate-600
                       rounded-xl shadow-lg max-h-52 overflow-y-auto">

          {filtered.map((s) => (
            <li
              key={`${s.name}-${s.line}`}
              onMouseDown={() => {
                onChange(s)
                setQuery(`${s.name} — ${s.line}`)
                setOpen(false)
              }}         
              className="px-4 py-2.5 text-sm cursor-pointer text-slate-700
                        dark:text-slate-200 hover:bg-brand-50
                        dark:hover:bg-slate-700 transition-colors"
            >
              {s.name} — {s.line}
            </li>
          ))}

        </ul>
      )}
    </div>
  )
}